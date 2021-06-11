import asyncio
import peewee
from peewee_async import Manager, MySQLDatabase
import logging
from src.settings import MySQLDatabaseConfig

mySQLDatabaseConfig = MySQLDatabaseConfig()
print(mySQLDatabaseConfig.USERNAME)
db = MySQLDatabase(
    mySQLDatabaseConfig.DBNAME,
    host=mySQLDatabaseConfig.HOST,
    port=mySQLDatabaseConfig.PORT,
    user=mySQLDatabaseConfig.USERNAME,
    password=mySQLDatabaseConfig.PASSWORD,
    autocommit=True,
)
DBManager = Manager(db, loop=asyncio.get_event_loop())
# # 如果使用同步的方式操作数据库，就报error
# DBManager.database.allow_sync = logging.ERROR


class BaseModel(peewee.Model):
    class Meta:
        database = db
