from src.model.BaseModel import BaseModel, database
from peewee import *


class Device(BaseModel):
    roomID = TextField(primary_key=True)
    isPower = IntegerField()
    targetTemperature = IntegerField()
    currentTemperature = IntegerField()
    # 0表示低风、1表示中风、2表示高风
    windSpeed = IntegerField()
    isAskAir = IntegerField()
    isSupplyAir = IntegerField()
    cost = FloatField()

    class Meta:
        table_name = "tbDevice"
