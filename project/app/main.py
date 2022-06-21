"""
Start application
"""


import asyncio

from fastapi import FastAPI
from loguru import logger

from .api import orders, welcome
from .db import init_db
from .logs.loguru_config import init_logging
from .sheets.run import activate_checking
from .tgbot.bot_s import activate_tg_bot


def create_application() -> FastAPI:
    """Create our FastAPI application, include routers, return FastAPI instance."""
    init_logging()
    logger.info("Initializing application ...")
    application = FastAPI()  # fastapi instance
    application.include_router(welcome.router, tags=["Welcome!"])  # including routers
    application.include_router(orders.router, prefix="/order", tags=["Orders"])
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    When application will be start, first thing which will be executed is initialize Postgres.
    Next, we run an infinite loop that will track changes in Google Sheets document,
                            and make changes to the database according to the received data.
    Also Telegram bot will be running to track overdue delivery dates and send notification.
    """
    logger.info("Application hase been started")
    init_db(app)  # initialize db
    asyncio.create_task(activate_checking())
    asyncio.create_task(activate_tg_bot())
