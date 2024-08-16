from typing import Iterator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import registry
from src.core.config import config

SQLALCHEMY_DATABASE_URL = str(config.PG_DSN)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine,
                                       autocommit=False,
                                       autoflush=False,
                                       expire_on_commit=False
                                       )
mapper_registry = registry()


class Base(DeclarativeBase):
    pass


async def get_db_session() -> Iterator[AsyncSession]:
    async with AsyncSessionLocal() as async_session:
        yield async_session
