from sqlalchemy import select

from core.models.database.employees import JobPosition
from core.storage.base_storage import _BaseStorage


class ArgumentError(Exception):
    pass


class JobPositionStorage(_BaseStorage[JobPosition]):
    async def list(self, **kwargs) -> list[JobPosition]:
        return list((await self.session.scalars(select(JobPosition))).all())

    async def get(self, *, id: int, **kwargs) -> JobPosition | None:
        return await self.session.get(JobPosition, id)
