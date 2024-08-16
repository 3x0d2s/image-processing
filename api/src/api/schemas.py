import datetime

from pydantic import BaseModel


class ImageRead(BaseModel):
    id: int
    dt: datetime.datetime
    description: str
