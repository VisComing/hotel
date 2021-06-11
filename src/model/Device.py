from pydantic.errors import BoolError
from src.model.BaseModel import BaseModel, database
from peewee import *


class Device(BaseModel):
    roomID = CharField(primary_key=True)
    isPower = BooleanField()
    targetTemperature = IntegerField()
    currentTemperature = IntegerField()
    # 0表示低风、1表示中风、2表示高风
    windSpeed = IntegerField()
    isAskAir = BooleanField()
    isSupplyAir = BooleanField()
    cost = FloatField()

    class Meta:
        table_name = "tbDevice"


Device.create_table(True)
