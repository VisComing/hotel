import logging
from jsonrpcserver import method, async_dispatch as dispatch
from src.settings import adminErrorCode
from jsonrpcserver.exceptions import ApiError
from src.model import *
from src.admin.SystemStatusHandler import SystemStatusHandler


class SysConfigHandler:
    async def run(self, message: str, websocket) -> None:
        response = await dispatch(message)
        if response.wanted:
            await websocket.send(str(response))

    @method
    async def getSysConfig() -> dict:
        # TODO @Jun丶
        """
        getSysConfig 获取系统配置

        Returns:
            dict:
            {
                "temperatureControlMode": 温控模式 (`heating` 表示制热，`cooling` 表示制冷),
                "targetTemperatureRange": {
                "heating": {
                    "min": 最低温度 (单位：摄氏度),
                    "max": 最高温度 (单位：摄氏度)
                },
                "cooling": {
                    "min": 最低温度 (单位：摄氏度),
                    "max": 最高温度 (单位：摄氏度)
                }
                },
                "defaultTemperature": 缺省温度 (单位：摄氏度),
                "electricityPrice": 计费标准 (单位：元/度),
                "electricityConsumptionRate": {
                    "low": 低风速下的耗电速率 (单位：度/分钟),
                    "medium": 中风速下的耗电速率 (单位：度/分钟),
                    "high": 高风速下的耗电速率 (单位：度/分钟)
                },
                "maxNumOfClientsToServe": 最大可服务对象数
            }
        """
        logging.info("get system config...")

        # 使用get有问题，用select代替
        settings = await DBManager.execute(Settings.select())
        settings = list(settings)
        settings = settings[0]

        result = {
            "temperatureControlMode": settings.temperatureControlMode,
            "targetTemperatureRange": {
                "heating": {
                    "min": settings.minHeatTemperature,
                    "max": settings.maxHeatTemperature,
                },
                "cooling": {
                    "min": settings.minCoolTemperature,
                    "max": settings.maxCoolTemperature,
                },
            },
            "defaultTemperature": settings.defaultTemperature,
            "electricityPrice": settings.electricityPrice,
            "electricityConsumptionRate": {
                "low": settings.lowRate,
                "medium": settings.midRate,
                "high": settings.highRate,
            },
            "maxNumOfClientsToServe": settings.maxNumOfClientsToServe,
        }
        return result

    @method
    async def setSysConfig(newConfigration: dict) -> None:
        # TODO @Jun丶
        """
        setSysConfig 设置系统配置

        Args:
            newConfigration (dict):
            {
                "temperatureControlMode": 温控模式 (`heating` 表示制热，`cooling` 表示制冷),
                "targetTemperatureRange": {
                "heating": {
                    "min": 最低温度 (单位：摄氏度),
                    "max": 最高温度 (单位：摄氏度)
                },
                "cooling": {
                    "min": 最低温度 (单位：摄氏度),
                    "max": 最高温度 (单位：摄氏度)
                }
                },
                "defaultTemperature": 缺省温度 (单位：摄氏度),
                "electricityPrice": 计费标准 (单位：元/度),
                "electricityConsumptionRate": {
                    "low": 低风速下的耗电速率 (单位：度/分钟),
                    "medium": 中风速下的耗电速率 (单位：度/分钟),
                    "high": 高风速下的耗电速率 (单位：度/分钟)
                },
                "maxNumOfClientsToServe": 最大可服务对象数
            }


        Returns:
            null
        """
        logging.info("set system config...")

        if SystemStatusHandler.status == True:
            raise ApiError(
                "禁止在运行时设置系统配置",
                code=adminErrorCode.SET_SYS_CONFIG_PROHIBIT_CONFIGURATION_AT_RUNTIME,
            )

        await DBManager.create(
            Settings,
            temperatureControlMode=newConfigration["temperatureControlMode"],
            minHeatTemperature=newConfigration["targetTemperatureRange"]["heating"][
                "min"
            ],
            maxHeatTemperature=newConfigration["targetTemperatureRange"]["heating"][
                "max"
            ],
            minCoolTemperature=newConfigration["targetTemperatureRange"]["cooling"][
                "min"
            ],
            maxCoolTemperature=newConfigration["targetTemperatureRange"]["cooling"][
                "max"
            ],
            defaultTemperature=newConfigration["defaultTemperature"],
            electricityPrice=newConfigration["electricityPrice"],
            lowRate=newConfigration["electricityConsumptionRate"]["low"],
            midRate=newConfigration["electricityConsumptionRate"]["medium"],
            highRate=newConfigration["electricityConsumptionRate"]["high"],
            maxNumOfClientsToServe=newConfigration["maxNumOfClientsToServe"],
        )
        return None
        
