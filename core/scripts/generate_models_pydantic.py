"""Generate Pydantic 2 models from the SQLAlchemy declarative registry.

The generated models contain both table columns and SQLAlchemy relationships.
Relationships are represented by references to the generated DTO classes, so
the result can be used directly with ``model_validate(sqlalchemy_object)``.
"""

import re
import types
from pathlib import Path
from typing import Any, Union, get_args, get_origin, get_type_hints

from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import DeclarativeBase, Mapped

from core.models.database import Base


def _is_union(type_hint: Any) -> bool:
    return get_origin(type_hint) in (Union, types.UnionType)


def _is_optional(type_hint: Any) -> bool:
    if get_origin(type_hint) is Mapped:
        args = get_args(type_hint)
        return bool(args) and _is_optional(args[0])
    return _is_union(type_hint) and type(None) in get_args(type_hint)


def extract_custom_types(type_hint: Any) -> set[type]:
    """Return non-builtin types used by a potentially nested annotation."""
    found: set[type] = set()
    origin = get_origin(type_hint)

    if origin is Mapped:
        args = get_args(type_hint)
        return extract_custom_types(args[0]) if args else found

    if origin is not None:
        for arg in get_args(type_hint):
            found.update(extract_custom_types(arg))
    elif isinstance(type_hint, type) and type_hint.__module__ != "builtins":
        found.add(type_hint)

    return found


def format_type_name(type_hint: Any, model_names: set[str]) -> str:
    """Format a Python annotation for the generated source file."""
    origin = get_origin(type_hint)

    if origin is Mapped:
        args = get_args(type_hint)
        return format_type_name(args[0], model_names) if args else "Any"

    if _is_union(type_hint):
        args = get_args(type_hint)
        non_none_args = [arg for arg in args if arg is not type(None)]
        result = " | ".join(format_type_name(arg, model_names) for arg in non_none_args)
        return f"{result} | None" if len(non_none_args) != len(args) else result

    if origin is not None:
        origin_name = getattr(origin, "__name__", str(origin).replace("typing.", ""))
        args = get_args(type_hint)
        if args:
            return f"{origin_name}[{', '.join(format_type_name(arg, model_names) for arg in args)}]"
        return origin_name

    if isinstance(type_hint, type):
        # SQLAlchemy model annotations must point to DTOs, not ORM objects.
        return (
            f"{type_hint.__name__}DTO"
            if type_hint.__name__ in model_names
            else type_hint.__name__
        )

    return str(type_hint).replace("typing.", "")


def _get_models(base_class: type[DeclarativeBase]) -> list[type[DeclarativeBase]]:
    """Find mapped classes, including classes nested under custom base classes."""
    result: list[type[DeclarativeBase]] = []
    stack = list(base_class.__subclasses__())
    while stack:
        cls = stack.pop()
        stack.extend(cls.__subclasses__())
        if getattr(cls, "__tablename__", None) is not None:
            result.append(cls)
    return sorted(set(result), key=lambda model: model.__name__)


def generate_pydantic_models(
    base_class: type[DeclarativeBase], output_path: str | Path = "generated_schemas.py"
) -> None:
    models = _get_models(base_class)
    model_names = {model.__name__ for model in models}
    model_by_name = {model.__name__: model for model in models}
    out_path = Path(output_path)
    existing_output = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
    existing_dto_names = set(
        re.findall(r"^class\s+([A-Za-z_]\w*DTO)\s*\(", existing_output, re.MULTILINE)
    )

    needed_imports: dict[str, set[str]] = {}
    class_definitions: list[str] = []

    for model in models:
        # Do not overwrite an existing DTO: it may have been edited manually
        # or may contain a deliberately smaller relationship tree.
        if f"{model.__name__}DTO" in existing_dto_names:
            continue

        type_hints = get_type_hints(model)
        mapper = sa_inspect(model)
        class_lines = [
            f"class {model.__name__}DTO(BaseModel):",
            "    model_config = ConfigDict(from_attributes=True)",
        ]
        fields_written: set[str] = set()

        # Scalar database columns.
        for col in mapper.columns:
            attr_name = col.key
            hint = type_hints.get(attr_name, Any)
            for custom_type in extract_custom_types(hint):
                if (
                    custom_type.__name__ not in model_names
                    and custom_type is not Any
                    and custom_type.__module__ not in {"typing", "types"}
                ):
                    needed_imports.setdefault(custom_type.__module__, set()).add(
                        custom_type.__name__
                    )

            type_repr = format_type_name(hint, model_names)
            has_default = col.default is not None or col.server_default is not None
            is_optional = (
                col.nullable or has_default or (col.primary_key and col.autoincrement)
            )
            if is_optional and not _is_optional(hint):
                type_repr = f"{type_repr} | None"
            default = " = None" if is_optional else ""
            class_lines.append(f"    {attr_name}: {type_repr}{default}")
            fields_written.add(attr_name)

        # SQLAlchemy relationships, converted to generated DTO references.
        for relation in mapper.relationships:
            attr_name = relation.key
            if attr_name in fields_written:
                continue
            related_model = relation.mapper.class_
            related_name = related_model.__name__
            if related_name not in model_by_name:
                continue
            if relation.uselist:
                type_repr = f"list[{related_name}DTO]"
                default = " = Field(default_factory=list)"
            else:
                # A relationship may be unloaded or absent on a partially built ORM object.
                type_repr = f"{related_name}DTO | None"
                default = " = None"
            class_lines.append(f"    {attr_name}: {type_repr}{default}")
            fields_written.add(attr_name)

        if not fields_written:
            class_lines.append("    pass")
        class_definitions.append("\n".join(class_lines))

    if not class_definitions:
        if existing_output:
            print(f"ℹ️ Новых схем нет, файл не изменён: {output_path}")
        else:
            print(f"ℹ️ Модели для генерации не найдены: {output_path}")
        return

    if existing_output:
        output = _append_missing_models(
            existing_output,
            class_definitions,
            needed_imports,
        )
    else:
        header_lines = [
            "# AUTOGENERATED FILE. DO NOT EDIT DIRECTLY.",
            "from __future__ import annotations",
            "from typing import Any",
            "from pydantic import BaseModel, ConfigDict, Field",
        ]
        header_lines.extend(_format_imports(needed_imports))
        output = (
            "\n".join(header_lines) + "\n\n" + "\n\n".join(class_definitions) + "\n"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    print(f"✅ Добавлено новых схем: {len(class_definitions)}. Файл: {output_path}")


def _format_imports(needed_imports: dict[str, set[str]]) -> list[str]:
    return [
        f"from {module_path} import {', '.join(sorted(names))}"
        for module_path, names in sorted(needed_imports.items())
    ]


def _append_missing_models(
    existing_output: str,
    class_definitions: list[str],
    needed_imports: dict[str, set[str]],
) -> str:
    """Keep the generated file intact and append only missing DTO classes.

    Imports are merged into the existing import block, instead of being
    appended after class declarations where they could be too late for runtime
    annotation resolution.
    """
    output = existing_output.rstrip() + "\n\n" + "\n\n".join(class_definitions) + "\n"

    if not needed_imports:
        return output

    first_class = re.search(r"^class\s+", output, re.MULTILINE)
    import_lines = "\n".join(_format_imports(needed_imports)) + "\n"
    insert_at = first_class.start() if first_class else 0
    prefix = output[:insert_at]
    suffix = output[insert_at:]

    # Avoid adding a line that already exists in a manually maintained header.
    missing_lines = [
        line
        for line in import_lines.splitlines()
        if line and line not in prefix.splitlines()
    ]
    if missing_lines:
        prefix = prefix.rstrip() + "\n" + "\n".join(missing_lines) + "\n\n"
    return prefix + suffix


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "models" / "database" / "dto" / "models.py"
    generate_pydantic_models(Base, output_path=path)
