from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    token: str

    model_config = SettingsConfigDict(env_prefix="bot_")


class ChessSettings(BaseSettings):
    stockfish_path: str
    stockfish_hash: int = 4096
    stockfish_threads: int = 3

    model_config = SettingsConfigDict(env_prefix="chess_")


class DbSettings(BaseSettings):
    user: str
    password: SecretStr
    host: str
    port: int = 5432
    db: str
    scheme: str = "postgresql+asyncpg"

    model_config = SettingsConfigDict(env_prefix="db_")

    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=self.scheme,
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password.get_secret_value(),
                path=self.db,
            )
        )
