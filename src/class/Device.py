from .BaseModel import BaseModel, database
from peewee import *


class Device(BaseModel):
    roomID = TextField(primary_key=True)
    isPower = IntegerField()
    targetTemperature = IntegerField()
    currentTemperature = IntegerField()
    windSpeed = IntegerField()
    isAskAir = IntegerField()
    isSupplyAir = IntegerField()
    cost = FloatField()

    class Meta:
        table_name = "tbDevice"
