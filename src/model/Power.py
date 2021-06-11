from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Device import Device


class Power(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="Powers", db_column="roomID"
    )
    startTime = DateTimeField()
    endTime = DateTimeField()
    powerState = BooleanField()

    class Meta:
        primary_key = CompositeKey("roomID", "startTime")
        table_name = "tbPower"


Power.create_table(True)
