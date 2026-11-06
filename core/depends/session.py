from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.database import async_session
from core.storage import *
from core.storage.session_storage_type import SessionStorages, build_storages


async def _get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session, session.begin():
        yield session


async def _get_storages(
    session: Annotated[AsyncSession, Depends(_get_session)],
) -> SessionStorages:
    return build_storages(session)


Session = Annotated[AsyncSession, Depends(_get_session)]
Storages = Annotated[SessionStorages, Depends(_get_storages)]
