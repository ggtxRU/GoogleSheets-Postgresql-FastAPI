from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Orders(models.Model):
    id = fields.IntField(pk=True)
    order_number = fields.IntField()
    price_usd = fields.IntField()
    price_rub = fields.IntField()
    delivery_date = fields.TextField()

    def __str__(self):
        return self.order_number


OrderSchema = pydantic_model_creator(Orders)
