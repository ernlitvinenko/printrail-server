from collections.abc import Sequence
from typing import Any, Unpack, overload

from sqlalchemy import select

from core.models.database.account import Role

from ..models.database.dto.typedict.dto import RoleCreateDict
from .base_storage import _BaseStorage


class RoleStorage(_BaseStorage[Role]):
    _model_cls = Role

    async def findall(self, **kwargs) -> Sequence[Role]:
        roles = (await self.session.scalars(select(Role))).all()
        return list(roles)

    @overload
    async def insert(self, item: Role, /) -> Role: ...

    @overload
    async def insert(self, **data: Unpack[RoleCreateDict]) -> Role: ...

    async def insert(self, item: object | None = None, **data: Any) -> Role:
        if item is not None and not isinstance(item, Role):
            raise TypeError("item must be a Role instance")
        return await self._insert(item, **data)

    async def add_all_roles(self, roles: Sequence[RoleCreateDict | Role]) -> None:
        if len(roles) == 0:
            return

        input_data: list[Role] = []

        for role in roles:
            if isinstance(role, Role):
                input_data.append(role)
                continue
            if isinstance(role, dict):
                input_data.append(Role(**role))

        self.session.add_all(input_data)
        await self.session.flush()
