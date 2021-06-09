from class.BaseModel import BaseModel
from peewee import *
from class.Order import Order

class DetailList(BaseModel):
    orderID = ForeignKeyField(Order, field='orderID', backref='DetailLists', db_column='orderID')
    DetailList = TextField()
    startTime = DateTimeField()
    endtime = DateTimeField()
    widSpeed = IntegerField()
    cost = FloatField()
    billingRate = FloatField()
    class Meta:
        primary_key = CompositeKey('DetailList', 'startTime')
        table_name = 'tbDetailList'