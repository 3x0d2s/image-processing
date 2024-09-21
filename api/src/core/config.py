from pydantic import PostgresDsn, RedisDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_DSN: PostgresDsn = Field(alias="API_PG_DSN")
    REDIS_DSN: RedisDsn
    REDIS_STREAM_TO_IMAGE_HANDLER_NAME: str
    MEDIA_ROOT: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


config = Settings()
