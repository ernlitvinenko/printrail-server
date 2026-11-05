from collections.abc import Sequence
from typing import Any, Unpack, overload

from sqlalchemy import select

from core.models.database.account import Employee
from core.models.database.dto.dto import EmployeeCreateDict

from .base_storage import _BaseStorage


class EmployeeStorage(_BaseStorage[Employee]):
    _model_cls = Employee

    @overload
    async def insert(self, item: Employee, /) -> Employee: ...

    @overload
    async def insert(self, **data: Unpack[EmployeeCreateDict]) -> Employee: ...

    async def insert(self, item: object | None = None, **data: Any) -> Employee:
        if item is not None and not isinstance(item, Employee):
            raise TypeError("item must be an Employee instance")
        return await self._insert(item, **data)

    async def findall(
        self, *, limit: int = 50, offset: int = 0, **kwargs
    ) -> Sequence[Employee]:
        data = (
            await self.session.scalars(select(Employee).limit(limit).offset(offset))
        ).all()
        return list(data)
