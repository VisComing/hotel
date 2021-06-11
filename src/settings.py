from pydantic import BaseSettings


class WebsocketsConfig(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 18000


websocketsConfig = WebsocketsConfig()


class MySQLDatabaseConfig(BaseSettings):
    DBNAME: str = "hotel"
    HOST: str = "localhost"
    PORT: int = 3306
    USERNAME: str = "work"
    PASSWORD: str = "password"


mySQLDatabaseConfig = MySQLDatabaseConfig()
