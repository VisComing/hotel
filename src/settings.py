from pydantic import BaseSettings


class WebsocketsConfig(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 18000


websocketsConfig = WebsocketsConfig()


class MySQLDatabaseConfig(BaseSettings):
    DBNAME: str = "hotel"
    DBHOST: str = "localhost"
    DBPORT: int = 3306
    DBUSERNAME: str = "work"
    DBPASSWORD: str = "password"


mySQLDatabaseConfig = MySQLDatabaseConfig()


class AdminErrorCode(BaseSettings):
    CREATE_ORDER_INVALID_USER_ID: int = 40101
    CREATE_ORDER_INVALID_ROOM_ID: int = 40102
    CREATE_ORDER_ROOM_UNAVAILABLE: int = 40103
    FETCH_ORDER_INVALID_ORDER_ID: int = 40301
    FETCH_ORDER_INVALID_ORDER_STATE: int = 40302
    GET_BILL_INVALID_ORDER_ID: int = 40401
    FET_BILL_INVALID_ORDER_STATE: int = 40402
    MAKE_PAYMENT_INVALID_ORDER_ID: int = 40501
    MAKE_PAYMENT_INVALID_ORDER_STATE: int = 40502
    GET_DETAILED_LIST_INVALID_ORDER_ID: int = 40601
    GET_DETAILED_LIST_INVALID_ORDER_STATE: int = 40602
    START_SYSTEM_SYSTEM_IS_RUNNING: int = 40801
    STOP_SYSTEM_SYSTEM_IS_NOT_RUNNING: int = 40901
    SET_SYS_CONFIG_PROHIBIT_CONFIGURATION_AT_RUNTIME: int = 41101


adminErrorCode = AdminErrorCode()
