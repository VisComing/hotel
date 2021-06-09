from .BaseModel import BaseModel
from peewee import *
from .Device import Device


class Scheduling(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="Schedulings", db_column="roomID"
    )
    time = TextField()

    class Meta:
        primary_key = CompositeKey("roomID", "time")
        tbale_name = "tbScheduling"
