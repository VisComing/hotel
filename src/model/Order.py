from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Device import Device


class Order(BaseModel):
    userID = CharField()
    roomID = ForeignKeyField(
        Device, field="roomID", backref="Orders", db_column="roomID"
    )
    orderID = CharField(primary_key=True)
    createdTime = DateTimeField()
    finishedTime = DateTimeField()
    state = CharField()

    class Meta:
        table_name = "tbOrder"


Order.create_table(True)
