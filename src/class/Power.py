from .BaseModel import BaseModel
from peewee import *
from .Device import Device


class Power(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="Powers", db_column="roomID"
    )
    startTime = DateTimeField()
    endTime = DateTimeField()
    powerState = IntegerField()

    class Meta:
        primary_key = CompositeKey("roomID", "startTime")
        table_name = "tbPower"
