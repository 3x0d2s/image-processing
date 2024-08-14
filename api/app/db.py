from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import config

SQLALCHEMY_DATABASE_URL = str(config.PG_DSN)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine,
                                       autocommit=False,
                                       autoflush=False,
                                       expire_on_commit=False
                                       )


class Base(DeclarativeBase):
    pass


async def get_db_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
