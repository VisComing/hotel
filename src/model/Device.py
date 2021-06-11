from pydantic.errors import BoolError
from src.model.BaseModel import BaseModel
from peewee import *


class Device(BaseModel):
    roomID = CharField(primary_key=True)
    isPower = BooleanField()
    targetTemperature = IntegerField()
    currentTemperature = IntegerField()
    # 1表示低风、1表示中风、3表示高风
    windSpeed = IntegerField()
    isAskAir = BooleanField()
    isSupplyAir = BooleanField()
    cost = FloatField()

    class Meta:
        table_name = "tbDevice"
