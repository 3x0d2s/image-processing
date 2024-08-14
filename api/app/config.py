from pydantic import SecretStr, PostgresDsn, AmqpDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PG_DSN: PostgresDsn
    REDIS_DSN: RedisDsn
    REDIS_STREAM_NAME: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
