from pydantic.errors import BoolError
from src.model.BaseModel import BaseModel
from peewee import *


class Device(BaseModel):
    roomID = CharField(primary_key=True)
    isPower = BooleanField(default=False)
    targetTemperature = IntegerField(default=25)
    currentTemperature = FloatField(default=25)
    # 1表示低风、2表示中风、3表示高风
    windSpeed = IntegerField(default=1)
    isAskAir = BooleanField(default=False)
    isSupplyAir = BooleanField(default=False)
    cost = FloatField(default=0)
    supplyTime = IntegerField(default=0)

    class Meta:
        table_name = "tbDevice"
