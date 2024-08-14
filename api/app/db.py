from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import registry
from app.config import config
from app.models import Image

SQLALCHEMY_DATABASE_URL = str(config.PG_DSN)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine,
                                       autocommit=False,
                                       autoflush=False,
                                       expire_on_commit=False
                                       )
mapper_registry = registry()


class Base(DeclarativeBase):
    pass


async def get_tables():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.reflect)
    return


async def map_tables():
    await get_tables()
    db_table = Base.metadata.tables['Image']
    mapper_registry.map_imperatively(Image, db_table)


async def get_db_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
