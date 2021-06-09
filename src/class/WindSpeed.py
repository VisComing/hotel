from class.BaseModel import BaseModel
from peewee import *
from class.Device import Device

class WindSpeed(BaseModel):
    roomID = ForeignKeyField(Device, field='roomID', backref='WindSpeeds', db_column='roomID')
    startTime = DateTimeField()
    endTime = DateTimeField()
    windSpeed = IntegerField()
    class Meta:
        primary_key = CompositeKey('roomID', 'startTime')
        table_name = 'tbWindSpeed'
        