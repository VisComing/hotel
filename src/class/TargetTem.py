from .BaseModel import BaseModel
from peewee import *
from .Device import Device


class TargetTem(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="TargetTems", db_column="roomID"
    )
    startTime = DateTimeField()
    endTime = DateTimeField()
    targetTem = IntegerField()

    class Meta:
        primary_key = CompositeKey("roomID", "startTime")
        table_name = "tbTargetTem"
