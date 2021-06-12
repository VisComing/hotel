from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Order import Order


class UsageRecord(BaseModel):
    orderID = ForeignKeyField(
        Order, field="orderID", backref="UsageRecords", db_column="orderID"
    )
    startTime = DateTimeField()
    endTime = DateTimeField()
    # 1表示低风、2表示中风、3表示高风
    windSpeed = IntegerField()
    cost = FloatField()
    billingRate = FloatField()

    class Meta:
        primary_key = CompositeKey("orderID", "startTime")
        table_name = "tbUsageRecord"
