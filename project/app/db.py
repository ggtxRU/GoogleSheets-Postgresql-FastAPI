"""
Initialize DB and Schemas 

"""

import os

from fastapi import FastAPI
from loguru import logger
from tortoise import Tortoise, run_async
from tortoise.contrib.fastapi import register_tortoise

from app.logs.loguru_config import init_logging

TORTOISE_ORM = {
    "connections": {"default": os.environ.get("DATABASE_URL")},
    "apps": {
        "models": {
            "models": [".models.tortoise", "aerich.models"],
            "default_connection": "default",
        },
    },
}

init_logging()


def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise"]},
        generate_schemas=True,
        add_exception_handlers=True,
    )


async def generate_schema() -> None:
    logger.info("Initializing Tortoise ...")

    await Tortoise.init(
        db_url=os.environ.get("DATABASE_URL"),
        modules={"models": ["app.models.tortoise"]},
    )
    logger.info("Generating database schema via Tortoise ...")
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()
    logger.info("Initializing Tortoise [COMPLETE]")
    return 1


if __name__ == "__main__":
    run_async(generate_schema())
