from typing import Any, Unpack, overload

from sqlalchemy import delete, select

from core.models.database.account import Account, RefreshToken
from core.models.database.dto.typedict.dto import AccountCreateDict
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

    async def find_by_login(self, login: str) -> Account | None:
        account = (
            await self.session.scalars(select(Account).where(Account.login == login))
        ).one_or_none()
        return account

    async def get_refresh_token(self, account_id: int) -> RefreshToken | None:
        return (
            await self.session.scalars(
                select(RefreshToken).where(RefreshToken.account_id == account_id)
            )
        ).one_or_none()

    async def is_refresh_token_exists(self, account_id: int) -> bool:
        stmt = (
            select(RefreshToken).where(RefreshToken.account_id == account_id).exists()
        )
        is_exists = await self.session.scalar(select(stmt))
        return is_exists is True

    async def add_refresh_token(self, account_id: int, token: str) -> RefreshToken:
        db_token = RefreshToken(refresh_token=token, account_id=account_id)
        self.session.add(db_token)
        await self.session.flush()
        return db_token

    async def drop_refresh_token(self, account_id: int) -> None:
        await self.session.execute(
            delete(RefreshToken).where(RefreshToken.account_id == account_id)
        )

    async def rotate_refresh_tokens(self, account_id: int, token: str) -> None:
        """
        Ротация refresh-токенов
        """

        await self.drop_refresh_token(account_id)
        await self.add_refresh_token(account_id, token)
