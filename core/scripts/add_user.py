import asyncio
import json
from pathlib import Path

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.database import async_session
from core.models.database.employees import Employee
from core.storage.employee_storage import EmployeeStorage
from core.storage.roles_storage import RoleStorage


async def _add_default_roles(session: AsyncSession | None = None):
    builtin_path = Path(__file__).parent.parent / "builtins"

    async with aiofiles.open(builtin_path / "system-roles.json", "r") as f:
        string_data = await f.read()
        default_roles = json.loads(string_data)

    if session is None:
        async with async_session() as impl_session, impl_session.begin():
            role_storage = RoleStorage(impl_session)
            return await role_storage.add_all_roles(default_roles)

    role_storage = RoleStorage(session)
    return await role_storage.add_all_roles(default_roles)


async def _gen_superuser():
    async with async_session() as session, session.begin():
        role_storage = RoleStorage(session)
        employee_storage = EmployeeStorage(session)

        # Получаем список всех ролей
        all_roles = await role_storage.list()
        if len(all_roles) == 0:
            # Если нет ролей - добавляем их
            await _add_default_roles(session)

        # admin_role = await role_storage.get(id=1)

        await employee_storage.insert(Employee(full_name="Админов Админ Админович"))


def gen_superuser():
    return asyncio.run(_gen_superuser())
