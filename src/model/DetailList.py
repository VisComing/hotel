from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Order import Order


class DetailList(BaseModel):
    orderID = ForeignKeyField(
        Order, field="orderID", backref="DetailLists", db_column="orderID"
    )
    DetailListID = TextField()
    startTime = DateTimeField()
    endtime = DateTimeField()
    # 0表示低风、1表示中风、2表示高风
    windSpeed = IntegerField()
    cost = FloatField()
    billingRate = FloatField()

    class Meta:
        primary_key = CompositeKey("DetailList", "startTime")
        table_name = "tbDetailList"
