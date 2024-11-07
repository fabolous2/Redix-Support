from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    SUPERGROUP_ID: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

