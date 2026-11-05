from typing import Any, Unpack, overload

from sqlalchemy import select

from core.models.database.account import Account
from core.models.database.dto.dto import AccountCreateDict
from core.storage.base_storage import _BaseStorage


class AccountStorage(_BaseStorage[Account]):
    _model_cls = Account

    async def list(self, **kwargs):
        roles = (await self.session.scalars(select(Account))).all()
        return list(roles)

    @overload
    async def insert(self, item: Account, /) -> Account: ...

    @overload
    async def insert(self, **data: Unpack[AccountCreateDict]) -> Account: ...

    async def insert(self, item: object | None = None, **data: Any) -> Account:
        if item is not None and not isinstance(item, Account):
            raise TypeError("item must be an Account instance")
        return await self._insert(item, **data)
