from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Image(Base):
    __tablename__ = "Image"
    #
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(length=200), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
