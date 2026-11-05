from typing import Any, Unpack, overload

from sqlalchemy import select

from core.models.database.dto.dto import JobPositionCreateDict
from core.models.database.employees import JobPosition
from core.storage.base_storage import _BaseStorage


class JobPositionStorage(_BaseStorage[JobPosition]):
    _model_cls = JobPosition

    @overload
    async def insert(self, item: JobPosition, /) -> JobPosition: ...

    @overload
    async def insert(self, **data: Unpack[JobPositionCreateDict]) -> JobPosition: ...

    async def insert(self, item: object | None = None, **data: Any) -> JobPosition:
        if item is not None and not isinstance(item, JobPosition):
            raise TypeError("item must be a JobPosition instance")
        return await self._insert(item, **data)

    async def findall(self, **kwargs) -> list[JobPosition]:
        return list((await self.session.scalars(select(JobPosition))).all())

    async def insert_default_job_positions(
        self, positions: list[JobPosition] | list[JobPositionCreateDict]
    ) -> None:
        if len(positions) == 0:
            return

        input_data: list[JobPosition] = []

        for position in positions:
            if isinstance(position, JobPosition):
                input_data.append(position)
                continue
            if isinstance(position, dict):
                input_data.append(JobPosition(**position))

        self.session.add_all(input_data)
        await self.session.flush()
