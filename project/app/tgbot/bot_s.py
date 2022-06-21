"""Telegram bot"""
import asyncio
import datetime
import os

import httpx

from ..models.tortoise import Orders


async def activate_tg_bot():
    """
    Check whether there are orders with an overdue delivery date.
    If True, send a tg-message.
    """
    try:
        order_delivery_date = (
            await Orders.filter(delivery_date__lte=datetime.datetime.now())
            .all()
            .values()
        )
    except:
        await asyncio.sleep(3.5)
        order_delivery_date = (
            await Orders.filter(delivery_date__lte=datetime.datetime.now())
            .all()
            .values()
        )
    for _ in order_delivery_date:
        TOKEN = str(os.environ.get("TG_BOT_TOKEN"))
        CHAT_ID = str(os.environ.get("CHAT_ID"))
        message = f"Order number *{_['order_number']}* is later!\nThe relevant delivery date *{_['delivery_date']}* is overdue."
        tg_msg = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(API_URL, json=tg_msg)

    await asyncio.sleep(int(os.environ.get("TIME_INTERVAL_TG_BOT")))
    return asyncio.create_task(activate_tg_bot())
