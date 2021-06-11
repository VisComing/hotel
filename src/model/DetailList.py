from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Order import Order


class DetailListItem(BaseModel):
    orderID = ForeignKeyField(
        Order, field="orderID", backref="DetailListItems", db_column="orderID"
    )
    detailListID = CharField()
    startTime = DateTimeField()
    endtime = DateTimeField()
    # 0表示低风、1表示中风、2表示高风
    windSpeed = IntegerField()
    cost = FloatField()
    billingRate = FloatField()

    class Meta:
        primary_key = CompositeKey("detailListID", "orderID")
        table_name = "tbDetailListItem"


DetailListItem.create_table(True)
