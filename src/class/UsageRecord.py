from class.BaseModel import BaseModel
from peewee import *
from class.Order import Order

class UsageRecord(BaseModel):
    orderID = ForeignKeyField(Order, field='orderID', backref='UsageRecords', db_column='orderID')
    startTime = DateTimeField()
    endTime = DateTimeField()
    windSpeed = IntegerField()
    cost = FloatField()
    billingRate = FloatField()
    class Meta:
        primary_key = CompositeKey('orderID, startTime')
        table_name = 'tbUsageRecord'
