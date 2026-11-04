from sqlalchemy import select

from core.models.database.account import Employee

from .base_storage import _BaseStorage


class EmployeeStorage(_BaseStorage[Employee]):
    async def list(
        self, *, limit: int = 50, offset: int = 0, **kwargs
    ) -> list[Employee]:
        data = (
            await self.session.scalars(select(Employee).limit(limit).offset(offset))
        ).all()
        return list(data)

    async def get(self, *, id: int, **kwargs) -> Employee | None:
        return await self.session.get(Employee, id)
