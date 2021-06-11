from src.model.BaseModel import BaseModel
from peewee import *


class Order(BaseModel):
    userID = CharField()
    roomID = CharField()
    orderID = CharField(primary_key=True)
    createdTime = DateTimeField()
    finishedTime = DateTimeField()
    state = CharField()

    class Meta:
        table_name = "tbOrder"


Order.create_table(True)
