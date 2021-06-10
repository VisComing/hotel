import mysql.connector
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

con = mysql.connector.connect(host="localhost", user="work", passwd="password")
cur = con.cursor()
cur.execute("show databases;")
data = cur.fetchall()
hasHotelDB = False
for x in data:
    if "hotel" in x:
        hasHotelDB = True
        break
if hasHotelDB:
    logging.warning("hotel exists, do you want to delete it and create a new one? y/n")
    if input() == "y":
        logging.warning(
            "are you sure? if you want to drop this database, please input n and continue"
        )
        if input() == "n":
            cur.execute("drop database hotel")
        else:
            exit()
    else:
        exit()
cur.execute("create database hotel;")
cur.execute("use hotel;")
logging.info("create and connect to totel.db;")
create_sql_list = list()
CREATE_TABEL_DEVICE = """create table tbDevice(
    roomID             varchar(200),
    isPower            integer,
    targetTemperature  integer,
    currentTemperature integer,
    windSpeed          integer,
    isAskAir           integer,
    isSupplyAir        integer,
    cost               float,
    primary            key(roomID)
);"""
create_sql_list.append(CREATE_TABEL_DEVICE)
CREATE_TABEL_ORDER = """create table tbOrder(
    userID       varchar(200),
    roomID       varchar(200),
    orderID      varchar(200),
    createdTime  datetime,
    finishedTime datetime,
    state        varchar(200),
    primary      key(orderID)

);"""
create_sql_list.append(CREATE_TABEL_ORDER)
CREATE_TABEL_BILL = """create table tbBill(
    orderID   varchar(200),
    billID    varchar(200),
    totalCost float,
    primary   key(billID),
    foreign   key(orderID) references tbOrder(orderID)
);"""
create_sql_list.append(CREATE_TABEL_BILL)
CREATE_TABEL_DETAILLIST = """create table tbDetailList(
    orderID     varchar(200),
    DetailList  varchar(200),
    startTime   datetime,
    endtime     datetime,
    widSpeed    int,
    cost        float,
    billingRate float,
    primary     key(DetailList, startTime),
    foreign     key(orderID) references tbOrder(orderID)
);"""
create_sql_list.append(CREATE_TABEL_DETAILLIST)
CREATE_TABEL_USAGERECORD = """create table tbUsageRecord(
    orderID     varchar(200),
    startTime   datetime,
    endTime     datetime,
    windSpeed   integer,
    cost        float,
    billingRate float,
    primary     key(orderID, startTime),
    foreign     key(orderID) references tbOrder(orderID)
);"""
create_sql_list.append(CREATE_TABEL_USAGERECORD)
CREATE_TABEL_POWER = """create table tbPower(
    roomID     varchar(200),
    startTime  datetime,
    endTime    datetime,
    powerState integer,
    primary    key(roomID, startTime),
    foreign    key(roomID) references tbDevice(roomID)
);"""
create_sql_list.append(CREATE_TABEL_POWER)
CREATE_TABEL_TARGETTEM = """create table tbTargetTem(
    roomID     varchar(200),
    startTime  datetime,
    endTime    datetime,
    targetTem  integer,
    primary    key(roomID, startTime),
    foreign    key(roomID) references tbDevice(roomID)
);"""
create_sql_list.append(CREATE_TABEL_TARGETTEM)
CREATE_TABEL_REACHTEM = """create table tbReachTem(
    roomID  varchar(200),
    time    datetime,
    primary key(roomID, time),
    foreign key(roomID) references tbDevice(roomID)
);"""
create_sql_list.append(CREATE_TABEL_REACHTEM)
CREATE_TABEL_WINDSPEED = """create table tbWindSpeed(
    roomID    varchar(200),
    startTime datetime,
    endTime   datetime,
    windSpeed integer,
    primary   key(roomID, startTime),
    foreign   key(roomID) references tbDevice(roomID)
);"""
create_sql_list.append(CREATE_TABEL_WINDSPEED)
CREATE_TABEL_SCHEDULING = """create table tbScheduling(
    roomID  varchar(200),
    time    datetime,
    primary key(roomID, time),
    foreign key(roomID) references tbDevice(roomID)
);"""
create_sql_list.append(CREATE_TABEL_SCHEDULING)

logging.info("start create tables...")
for create_sql in create_sql_list:
    cur = con.cursor()
    logging.info("create table " + create_sql.split(" ")[2][:-2])
    cur.execute(create_sql)
    con.commit()
logging.info("all table created...")
