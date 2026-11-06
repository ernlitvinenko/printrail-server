from dataclasses import dataclass, fields

from sqlalchemy.ext.asyncio import AsyncSession

from core.storage.base_storage import _BaseStorage

from .account_storage import AccountStorage
from .employee_storage import EmployeeStorage
from .job_position_storage import JobPositionStorage
from .roles_storage import RoleStorage


@dataclass
class SessionStorages:
    session: AsyncSession
    account_storage: AccountStorage
    employee_storage: EmployeeStorage
    job_position_storage: JobPositionStorage
    roles_storage: RoleStorage


def build_storages(session: AsyncSession) -> SessionStorages:
    return SessionStorages(
        session=session,
        account_storage=AccountStorage(session),
        employee_storage=EmployeeStorage(session),
        job_position_storage=JobPositionStorage(session),
        roles_storage=RoleStorage(session),
    )


def set_session_username(storages: SessionStorages, username: str):
    for attr in fields(storages):
        attr_name = attr.name
        storage = getattr(storages, attr_name)
        if isinstance(storage, _BaseStorage):
            storage.set_username(username)
