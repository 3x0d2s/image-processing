from pydantic import PostgresDsn, RedisDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_DSN: PostgresDsn = Field(alias="DB_SAVER_PG_DSN")
    REDIS_DSN: RedisDsn
    REDIS_STREAM_TO_DB_SAVER_NAME: str
    REDIS_DB_SAVER_GROUP_KEY: str
    REDIS_DB_SAVER_CONSUMER_NAME: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


config = Settings()
