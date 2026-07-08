from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    my_app_name: str = "Simple App"


@lru_cache
def get_settings() -> Settings:
    return Settings()


app = FastAPI()


@app.get("/name")
async def root(cfg: Settings = Depends(get_settings)) -> dict:
    return {"my_app_name": cfg.my_app_name}