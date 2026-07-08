from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    secret_key: str = "default-secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


app = FastAPI()


@app.get("/secret")
async def root(settings: Settings = Depends(get_settings)) -> str:
    return (settings.secret_key[:4] + "...")