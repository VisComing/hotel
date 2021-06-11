from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Device import Device


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


TargetTem.create_table(True)
