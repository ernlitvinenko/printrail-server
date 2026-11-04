from typing import TypedDict, Unpack

from sqlalchemy import select

from core.models.database.account import Role

from .base_storage import ArgumentError, _BaseStorage


class _GetKwargsType(TypedDict):
    id: int


class RoleDict(TypedDict):
    id: int
    name: str
    is_system: bool | None
    is_del: bool | None


class RoleStorage(_BaseStorage[Role]):
    async def list(self, **kwargs) -> list[Role]:
        roles = (await self.session.scalars(select(Role))).all()
        return list(roles)

    async def get(self, **kwargs: Unpack[_GetKwargsType]) -> Role | None:
        role_id = kwargs.get("id", None)
        if role_id is None:
            raise ArgumentError("keyword argument `id` should be proivided")
        if not isinstance(role_id, int):
            raise ArgumentError("Argument `id` should be valid integer")

        return await self.session.get(Role, role_id)

    async def add_all_roles(self, roles: list[RoleDict] | list[Role]):
        if len(roles) == 0:
            return

        input_data: list[Role] = []

        for role in roles:
            if isinstance(role, Role):
                input_data.append(role)
                continue
            if isinstance(role, dict):
                input_data.append(Role(**role))

        self.session.add_all(input_data)
        await self.session.flush()
