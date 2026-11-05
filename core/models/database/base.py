from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.sql import expression

_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Attach convention to the metadata object
metadata_obj = MetaData(naming_convention=_convention)


class Base(DeclarativeBase):
    metadata = metadata_obj


class ServiceFieldsMixin:
    is_del: Mapped[bool] = mapped_column(
        server_default=expression.false(), nullable=False, comment="Пометка удаления"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата создания",
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def __table_args__(cls) -> dict:
        return {"info": {"has_audit_trigger": True}}
