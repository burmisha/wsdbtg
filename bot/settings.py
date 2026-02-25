from pathlib import Path

from pydantic import SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding='utf-8')

    telegram_bot_token: SecretStr
    logging_level: str = 'INFO'

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = 'db'
    postgres_port: int = 5432

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f'postgresql://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )
