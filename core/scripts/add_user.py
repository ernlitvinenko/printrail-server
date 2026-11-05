import asyncio
import getpass
import json
from datetime import datetime
from pathlib import Path

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from core.environment import Config
from core.helpers.auth import generate_password_hash
from core.internal.database import async_session
from core.models.database.employees import GenderType
from core.storage import (
    AccountStorage,
    EmployeeStorage,
    JobPositionStorage,
    RoleStorage,
)


async def __read_builtin_json[T](filename: str) -> list[T]:
    builtin_path = Path(__file__).parent.parent / "builtins"
    async with aiofiles.open(builtin_path / filename, "r") as f:
        string_data = await f.read()
        return json.loads(string_data)


async def _add_default_roles(session: AsyncSession | None = None):
    default_roles = await __read_builtin_json("system-roles.json")
    if session is None:
        async with async_session() as impl_session, impl_session.begin():
            role_storage = RoleStorage(impl_session)
            return await role_storage.add_all_roles(default_roles)

    role_storage = RoleStorage(session)
    return await role_storage.add_all_roles(default_roles)


async def _add_default_job_positions(session: AsyncSession):
    default_job_positions = await __read_builtin_json("system-job-positions.json")

    if session is None:
        async with async_session() as impl_session, impl_session.begin():
            job_storage = JobPositionStorage(impl_session)
            return await job_storage.insert_default_job_positions(default_job_positions)
    return await RoleStorage(session).add_all_roles(default_job_positions)


async def _gen_superuser():
    # Так как еще не было создано ни одного пользователя мы используем логин пользователя ОС для аудит-лога
    username = getpass.getuser()
    async with async_session() as session, session.begin():
        role_storage = RoleStorage(session, username)
        employee_storage = EmployeeStorage(session, username)
        job_position_storage = JobPositionStorage(session, username)
        account_storage = AccountStorage(session, username)

        # Получаем админскую роль
        admin_role = await role_storage.get(id=1)
        if (
            admin_role is None or admin_role.name != "admin"
        ):  # Если роли нет = создаем ее
            await _add_default_roles(session)
            admin_role = await role_storage.get(id=1)

        position = await job_position_storage.get(id=1)
        if position is None or position.name != "Администратор":
            await _add_default_job_positions(session)
            position = await job_position_storage.get(id=1)

        # Финальная проверка всех инстансов
        if position is None:
            raise ValueError("JobPosition should not be None")

        # Создаем сотрудника
        sotr = await employee_storage.insert(
            id=1,
            full_name="Админов Админ Админович",
            position_id=position.id,
            date_approved=datetime.now(),
            date_of_birth=datetime.now(),
            gender=GenderType.MALE,
        )

        # Добавляем аккаунт админ пользователя
        await account_storage.insert(
            id=1,
            employee_id=sotr.id,
            login=Config.ADMIN_EMAIL,
            password=generate_password_hash(Config.ADMIN_PASSWORD),
        )


def gen_superuser():
    return asyncio.run(_gen_superuser())
