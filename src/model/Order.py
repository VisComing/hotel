from src.model.BaseModel import BaseModel
from peewee import *


class Order(BaseModel):
    userID = TextField()
    roomID = TextField()
    orderID = TextField(primary_key=True)
    createdTime = DateTimeField()
    finishedTime = DateTimeField()
    state = TextField()

    class Meta:
        table_name = "tbOrder"
