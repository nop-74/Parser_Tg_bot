import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DOWNLOAD_DIR: str = BASE_DIR + "/download_files"
    DB_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/db.sqlite3"
    BOT_TOKEN: str

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


settings = Settings()
