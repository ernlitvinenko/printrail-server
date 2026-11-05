"""Tests for the storage layer: CRUD, soft deletes, typed kwargs validation."""

import pytest

from core.models.database.account import Role
from core.storage.base_storage import ArgumentError
from core.storage.roles_storage import RoleStorage
from core.storage.employee_storage import EmployeeStorage
from core.models.database.employees import Employee


@pytest.fixture
def role_storage(db_session):
    return RoleStorage(db_session, username="tester")


@pytest.fixture
def employee_storage(db_session):
    return EmployeeStorage(db_session, username="tester")


async def test_insert_and_get_role(role_storage):
    await role_storage.insert(Role(id=1, name="admin", is_system=True))
    role = await role_storage.get(id=1)
    assert role is not None
    assert role.name == "admin"
    assert role.is_system is True


async def test_list_roles(role_storage):
    await role_storage.add_all_roles(
        [
            {"id": 1, "name": "admin", "is_system": True},
            {"id": 2, "name": "user", "is_system": True},
        ]
    )
    roles = await role_storage.list()
    assert {r.name for r in roles} == {"admin", "user"}


async def test_get_without_id_raises(role_storage):
    with pytest.raises(ArgumentError):
        await role_storage.get()


async def test_get_with_bad_id_type_raises(role_storage):
    with pytest.raises(ArgumentError):
        await role_storage.get(id="not-an-int")


async def test_soft_delete(role_storage):
    role = await role_storage.insert(Role(id=5, name="temp"))
    await role_storage.delete(role)
    assert role.is_del is True
    # Row still present in DB (soft delete, not hard).
    assert await role_storage.session.get(Role, 5) is not None


async def test_hard_delete_requires_soft_flag(role_storage):
    role = await role_storage.insert(Role(id=6, name="temp"))
    with pytest.raises(ValueError):
        await role_storage.delete_admin(role)


async def test_employee_crud(employee_storage):
    from datetime import date

    from core.models.database.employees import GenderType, JobPosition

    position = JobPosition(name="Оператор")
    employee_storage.session.add(position)
    await employee_storage.session.flush()

    employee = await employee_storage.insert(
        Employee(
            full_name="Иванов Иван",
            position_id=position.id,
            date_approved=date(2024, 1, 15),
            date_of_birth=date(1990, 5, 1),
            gender=GenderType.MALE,
        )
    )
    assert employee.id is not None
    fetched = await employee_storage.get(id=employee.id)
    assert fetched.full_name == "Иванов Иван"
    listed = await employee_storage.list()
    assert len(listed) == 1
