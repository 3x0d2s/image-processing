from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Image
from typing import Sequence


class ImageCrud:

    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def get_image(self, image_id: int) -> Image:
        query = select(Image).filter(Image.id == image_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_images(self, limit: int | None = None, offset: int | None = None) -> Sequence[Image]:
        query = select(Image).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()
