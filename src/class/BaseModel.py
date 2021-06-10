import logging
import asyncio
import peewee
import peewee_async
from peewee_async import Manager, MySQLDatabase

db = peewee_async.MySQLDatabase(
    "hotle",
    max_connections=20,
    host="localhost",
    port=3306,
    user="work",
    password="password",
    autocommit=True,
)
database = Manager(db, asyncio.get_event_loop())


class BaseModel(peewee.Model):
    class Meta:
        database = db
