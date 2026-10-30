from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.environment import Config

_url = make_url(Config.DATABASE_URL)
if _url.drivername == "sqlite":
    _url = _url.set(drivername="sqlite+aiosqlite")
elif (
    _url.drivername == "postgresql"
    or _url.drivername == "asyncpg"
    or _url.drivername == "postgres"
):
    _url = _url.set(drivername="postgresql+asyncpg")

engine = create_async_engine(_url, echo=Config.ENVIRONMENT == "dev")

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
