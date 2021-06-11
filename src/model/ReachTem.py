from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Device import Device


class ReachTem(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="ReachTems", db_column="roomID"
    )
    time = DateTimeField()

    class Meta:
        primary_key = CompositeKey("roomID", "time")
        table_name = "tbReachTem"


ReachTem.create_table(True)
