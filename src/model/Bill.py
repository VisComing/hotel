from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Order import Order


class Bill(BaseModel):
    orderID = ForeignKeyField(
        Order, field="orderID", backref="Bills", db_column="orderID"
    )
    billID = CharField(primary_key=True)
    totalCost = FloatField()

    class Meta:
        table_name = "tbBill"
