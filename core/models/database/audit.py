import enum
from datetime import datetime
from typing import Any

from sqlalchemy import Integer, String, Enum, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class AuditAction(str, enum.Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    table_name: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action", native_enum=True),
        nullable=False
    )
    row_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="ID измененной записи")

    # Снапшоты данных до и после операции
    old_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    new_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    changed_by: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Имя пользователя / session context"
    )

    __table_args__ = (
        Index("ix_audit_log_table_row", "table_name", "row_id"),
    )