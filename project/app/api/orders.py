from fastapi import APIRouter, HTTPException
from typing import Optional

from ..models.tortoise import OrderSchema
from . import crud

router = APIRouter()


@router.get("/{id}/", response_model=Optional[OrderSchema])
async def get_order(id: int) -> Optional[OrderSchema]:
    order = await crud.get(id)
    if order:
         return order
    return HTTPException(status_code=404, detail=f"Order with id {id} not found")
