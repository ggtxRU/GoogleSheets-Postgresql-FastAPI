import os
from functools import lru_cache

from loguru import logger
from pydantic import AnyUrl, BaseSettings

from .logs.loguru_config import init_logging


class Settings(BaseSettings):
    init_logging()
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)
    database_url: AnyUrl = os.environ.get("DATABASE_URL")
    logger.info("Loading settings --- COMPLETE ---")


@lru_cache
def get_settings() -> BaseSettings:
    logger.info("Loading config settings ...")
    return Settings()
