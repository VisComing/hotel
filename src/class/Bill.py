from class.BaseModel import BaseModel
from peewee import *
from class.Order import Order

class Bill(BaseModel):
    orderID = ForeignKeyField(Order, field='orderID', backref='Bills', db_column='orderID')
    billID = TextField(primary_key=True)
    totalCost = FloatField()
    class Meta:
        table_name = 'tbBill'
