from pydantic import RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_DSN: RedisDsn

    REDIS_INCOMING_STREAM_KEY: str
    REDIS_GROUP_KEY: str
    REDIS_CONSUMER_NAME: str
    REDIS_OUTGOING_STREAM_KEY: str

    FONT_SIZE: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
