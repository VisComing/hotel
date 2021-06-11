from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Order import Order


class DetailListItem(BaseModel):
    orderID = ForeignKeyField(
        Order, field="orderID", backref="DetailListItems", db_column="orderID"
    )
    detailListID = CharField(primary_key=True)
    startTime = DateTimeField()
    endtime = DateTimeField()
    # 1表示低风、2表示中风、3表示高风
    windSpeed = IntegerField()
    cost = FloatField()
    billingRate = FloatField()

    class Meta:
        table_name = "tbDetailListItem"


DetailListItem.create_table(True)
