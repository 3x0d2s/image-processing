from datetime import datetime

import pytest

from database.models import Image
from tests.conftest import client, async_session_maker


@pytest.fixture(autouse=True, scope="session")
async def async_example_orm():
    async with async_session_maker() as async_db_session:
        example = Image(dt=datetime.utcnow(),
                        description='test_image_1',
                        file_path='/tmp/media/image_2024-08-14_16-07-42.060792.jp'
                        )
        async_db_session.add(example)
        await async_db_session.commit()
        await async_db_session.refresh(example)
        yield example
        pass


def test_get_images(async_example_orm) -> None:
    responce = client.get("/api/images")
    data = responce.json()
    assert responce.status_code == 200
    assert len(data) > 0
