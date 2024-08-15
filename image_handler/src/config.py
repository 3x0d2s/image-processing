from pydantic import RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_DSN: RedisDsn

    REDIS_STREAM_TO_IMAGE_HANDLER_NAME: str
    REDIS_IMAGE_HANDLER_GROUP_KEY: str
    REDIS_IMAGE_HANDLER_CONSUMER_NAME: str
    REDIS_STREAM_TO_DB_SAVER_NAME: str

    FONT_NAME: str
    FONT_SIZE: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


config = Settings()
