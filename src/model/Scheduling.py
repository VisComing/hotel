from src.model.BaseModel import BaseModel
from peewee import *
from src.model.Device import Device


class Scheduling(BaseModel):
    roomID = ForeignKeyField(
        Device, field="roomID", backref="Schedulings", db_column="roomID"
    )
    time = CharField()

    class Meta:
        primary_key = CompositeKey("roomID", "time")
        tbale_name = "tbScheduling"


Scheduling.create_table(True)
