from typing import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from starlette.testclient import TestClient

from core.config import config

from database.db import Base, get_db_session
from src.main import app

SQLALCHEMY_DATABASE_URL = str(config.PG_DSN_FOR_TESTS)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    bind=engine
)


# drop all database every time when test complete
@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_async_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_db_session] = override_get_async_session
#
#
# @pytest.fixture(scope="session")
# async def ac() -> AsyncIterator[AsyncClient]:
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         yield ac


client = TestClient(app, base_url="http://test")

# @pytest.fixture
# async def async_example_orm(async_db_session: AsyncSession):
#     example = Image(dt=datetime.utcnow(),
#                     description='test_image_1',
#                     file_path='/tmp/media/image_2024-08-14_16-07-42.060792.jp'
#                     )
#     async_db_session.add(example)
#     await async_db_session.commit()
#     await async_db_session.refresh(example)
#     yield example
