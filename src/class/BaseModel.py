import logging
from peewee import *
db = SqliteDatabase('hotel.db', pragmas={'foreign_keys':1})
class BaseModel(Model):
    def Insert(self):
        if self.save(force_insert=True) != 1:
            logging.error('insert failed')
    def Delete(self):
        self.delete_instance()
    def Update(self):
        if self.save(force_insert=True) != 1:
            logging.error('update failed')
    class Meta:
        database = db