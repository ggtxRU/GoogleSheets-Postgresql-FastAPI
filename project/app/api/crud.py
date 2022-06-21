from typing import Optional

from app.models.tortoise import Orders


async def get(id: int) -> Optional[dict]:
    order = await Orders.get_or_none(id=id).values()
    if order:
        return order
