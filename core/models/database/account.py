from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from .base import Base, ServiceFieldsMixin
from .employees import Employee


class Account(Base, ServiceFieldsMixin):
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(
        primary_key=True, comment="Идентификатор пользователя"
    )
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employee.id"), comment="Идентификатор сотрудника организации"
    )
    employee: Mapped[Employee] = relationship()
    login: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Логин входа (эл. почта)"
    )
    password: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Зашифрованный Пароль в формате bcrypt"
    )

    refresh_tokens: Mapped["RefreshToken"] = relationship(back_populates="account")


class RefreshToken(Base):
    __tablename__ = "refresh_token"
    refresh_token: Mapped[str] = mapped_column(Text, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), primary_key=True)
    account: Mapped[Account] = relationship()


class Role(Base, ServiceFieldsMixin):
    __tablename__ = "role"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_system: Mapped[bool] = mapped_column(server_default=expression.false())
