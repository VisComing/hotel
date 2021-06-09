from class.BaseModel import BaseModel
from peewee import *
from class.Device import Device

class ReachTem(BaseModel):
    roomID = ForeignKeyField(Device, field='roomID', backref='ReachTems', db_column='roomID')
    time = DateTimeField()
    class Meta:
        primary_key = CompositeKey('roomID', 'time')
        table_name = 'tbReachTem'
        