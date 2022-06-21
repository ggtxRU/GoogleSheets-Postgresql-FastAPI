from datetime import date

from pydantic import BaseModel


class OrdersPayloadSchema(BaseModel):
    id: int
    order_number: int
    price_usd: float
    price_rub: float
    delivery_date: date  # ???


class OrdersResponseSchema(OrdersPayloadSchema):
    id: int
