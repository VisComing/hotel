import asyncio
import peewee
from peewee_async import Manager, MySQLDatabase
import logging

db = MySQLDatabase(
    "hotel",
    host="localhost",
    port=3306,
    user="work",
    password="password",
    autocommit=True,
)
DBManager = Manager(db, loop=asyncio.get_event_loop())
DBManager.database.allow_sync = logging.ERROR


class BaseModel(peewee.Model):
    class Meta:
        database = db
