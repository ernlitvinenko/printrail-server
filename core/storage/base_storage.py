from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Concatenate, Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import text


class _SqlalchemyModel(Protocol):
    is_del: Mapped[bool]


class ArgumentError(Exception):
    pass


def setup_postgres_settings[**P, R, SelfT: _BaseStorage](
    func: Callable[Concatenate[SelfT, P], Awaitable[R]],
) -> Callable[Concatenate[SelfT, P], Awaitable[R]]:
    """
    Декоратор установки имени пользователя в аудит-логе. Используется только для методов изменения. Не используется для чтения
    """

    @wraps(func)
    async def wrapper(self: SelfT, *args: P.args, **kwargs: P.kwargs) -> R:
        if (
            self.username is not None
            and self.session.bind is not None
            and self.session.bind.dialect.name != "sqlite"
        ):
            # PostgreSQL: set per-transaction user for audit triggers.
            # SQLite (tests): no set_config — audit attribution is PG-only.
            await self.session.execute(
                text(f"SELECT set_config('app.current_user', '{self.username}', true)")
            )
        return await func(self, *args, **kwargs)

    return wrapper


class _BaseStorage[T: _SqlalchemyModel](ABC):
    def __init__(self, session: AsyncSession, username: str | None = None) -> None:
        super().__init__()
        self._session = session
        self.username = username

    @property
    def session(self):
        return self._session

    @abstractmethod
    async def list(self, **kwargs) -> list[T]:
        """
        Возвращает список элементов класса
        """

    @abstractmethod
    async def get(self, **kwargs) -> T | None:
        """
        Возвращает элемент по признакам
        """

    @setup_postgres_settings
    async def insert(self, item: T) -> T:
        """
        Добавляет элемент в Базу данных
        """
        self.session.add(item)
        await self.session.flush()
        return item

    @setup_postgres_settings
    async def delete(self, item: T) -> T:
        """
        Помечает элемент удаленным
        """
        item.is_del = True
        await self.session.flush()
        return item

    @setup_postgres_settings
    async def update(self, item: T) -> T:
        """
        Обновляет элемент
        """
        await self.session.flush()
        return item

    @setup_postgres_settings
    async def delete_admin(self, item: T) -> bool:
        """
        Удаляет элемент из БД
        """
        if not item.is_del:
            raise ValueError("Can not fully delete item without `is_del=True` flag")
        await self.session.delete(item)
        await self.session.flush()
        return True
