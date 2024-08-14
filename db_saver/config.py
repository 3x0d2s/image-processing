from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_DSN: PostgresDsn
    REDIS_DSN: RedisDsn
    REDIS_INCOMING_STREAM_KEY: str
    REDIS_GROUP_KEY: str
    REDIS_CONSUMER_NAME: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
