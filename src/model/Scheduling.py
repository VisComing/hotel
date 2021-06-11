from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Device import Device


class Scheduling(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="Schedulings", db_column="roomID"
    )
    timePoint = CharField()

    class Meta:
        primary_key = CompositeKey("roomID", "timePoint")
        tbale_name = "tbScheduling"
