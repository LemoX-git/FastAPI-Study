from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    max_connections: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


app = FastAPI()


@app.get("/db")
async def root(settings: Settings = Depends(get_settings)) -> dict:
    return {"database_url": settings.database_url, "max_connections": settings.max_connections}