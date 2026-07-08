from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    api_version: str = "v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


app = FastAPI()


@app.get("/info")
async def root(settings: Settings = Depends(get_settings)) -> dict:
    return {"app_name": settings.app_name, "api_version": settings.api_version}