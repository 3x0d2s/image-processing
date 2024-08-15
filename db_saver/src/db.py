from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from config import config

SQLALCHEMY_DATABASE_URL = str(config.PG_DSN)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine,
                            autocommit=False,
                            autoflush=False,
                            expire_on_commit=False
                            )


class Base(DeclarativeBase):
    pass
