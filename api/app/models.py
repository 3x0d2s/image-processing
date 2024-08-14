from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base


class Images(Base):
    __tablename__ = "Images"
    #
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    description: Mapped[str] = mapped_column(String(length=200), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
