from src.model.BaseModel import BaseModel
from peewee import *

# 表中只有一行数据，无主键
class Settings(BaseModel):
    # 取值为heating/cooling
    temperatureControlMode = TextField()
    minHeatTemperature = IntegerField()
    maxHeatTemperature = IntegerField()
    minCoolTemperature = IntegerField()
    maxCoolTemperature = IntegerField()
    defaultTemperature = IntegerField()
    electricityPrice = DoubleField()
    lowRate = DoubleField()
    midRate = DoubleField()
    highRate = DoubleField()
    maxNumOfClientsToServe = IntegerField()

    class Meta:
        table_name = "tbSettings"
