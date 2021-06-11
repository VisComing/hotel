# 主从空调通信协议 (1.0.1)

- 版本：`1.0.1`
- 作者：刘广凯

[TOC]

## 协议基础

- 通信对象
  - 房间空调 (实际上表现为用户控制空调的客户端、app、小程序等)
  - 中央空调 (实际上表现为后端服务器)

- 协议功能
  - 信息交换：如房间空调上报温度信息，中央空调下放计费信息
  - 控制：如目标温度调整、风速调节、送风控制

- 底层信道：[WebSocket](https://en.wikipedia.org/wiki/WebSocket)
- 基本格式：[json-rpc](https://www.jsonrpc.org/specification)

### WebSocket 简介

client 向 server 请求建立连接后，形成 **双向**、**基于消息** 的信道

通俗来说：一方可以随时向另一方发送消息（消息其实就是个字符串）

```
--> "hello, i'm a message sent from client to server"
<-- "hi, i'm a message sent from server to client"

<-- "messages can be pushed from the server to the client at any time"
```

我们发送的消息使用 JSON 格式的字符串去表示

### JSON-RPC 简介

一个轻量级的远程过程调用协议，其实就是个简单的消息格式

#### 请求

```json
{
  // JSON-RPC 版本，必须是 2.0
  "jsonrpc": "2.0",

  // id，标识本次请求
  "id": 1,

  // 方法名（也可称作过程名、函数名、消息名）
  "method": "methodName",

  // 方法参数
  "params": {
    "someKey": "someValue"
  }
}
```

#### 响应

```json
{
  // JSON-RPC 版本，必须是 2.0
  "jsonrpc": "2.0",

  // id，表示是对哪个请求的响应
  "id": 1,

  // 结果（只有请求成功时有此属性）
  "result": {
    "someKey": "someValue"
  },

  // 错误（只有请求失败时有此属性）
  "error": {
    // 错误代码
    "code": 233,

    // 可读的错误信息
    "message": "No Permission",

    // 错误相关数据
    "data": {
      "someKey": "someValue"
    }
  }
}
```

#### 通知

一种特殊的请求，不含 `id` 字段，表示不需要响应，代表一种事件或通知

我们协议中主要使用通知类信息，如有需要可以添加请求-响应类信息

## 协议约定

### 房间 ID 编码方式

楼号 - 楼层号 - 房间号，每个部分两位数字，如

```
03-03-33
01-05-47
```

### 目标温度范围

最低 18 度（含），最高 30 度（含）

## 消息定义

> 注意：仅描述消息中的 `method` 和 `params` 字段，通用的 `jsonrpc` 与 `id` 字段不再重复（但不可省略）

### `publish` Operation

从「房间空调」发往「中央空调」的信息


#### Message `GetConfiguration`

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | GetConfiguration |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |

##### Response

响应数据格式较复杂，以 `jsonschema` 形式化描述其中的 `result` 域：

```json
{
  "type": "object",
  "required": [
    "temperatureControlMode",
    "targetTemperatureRange",
    "defaultTemperature"
  ],
  "properties": {
    "temperatureControlMode": {
      "description": "温控模式 (`heating` 表示制热，`cooling` 表示制冷)",
      "type": "string",
      "enums": [
        "heating",
        "cooling"
      ]
    },
    "targetTemperatureRange": {
      "description": "温控范围",
      "type": "object",
      "properties": {
        "heating": {
          "description": "制热模式下的温控范围",
          "type": "object",
          "properties": {
            "min": {
              "description": "最低温度 (单位：摄氏度)",
              "type": "number",
              "example": 18
            },
            "max": {
              "description": "最高温度 (单位：摄氏度)",
              "type": "number",
              "example": 26
            }
          }
        },
        "cooling": {
          "description": "制冷模式下的温控范围",
          "type": "object",
          "properties": {
            "min": {
              "description": "最低温度 (单位：摄氏度)",
              "type": "number",
              "example": 26
            },
            "max": {
              "description": "最高温度 (单位：摄氏度)",
              "example": 30
            }
          }
        }
      }
    },
    "defaultTemperature": {
      "description": "缺省温度 (单位：摄氏度)",
      "type": "number",
      "example": 26
    }
  }
}
```

##### Example

请求：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "GetConfiguration",
  "params": {
    "roomID": "03-03-33"
  }
}
```

响应：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "temperatureControlMode": "heating",
    "targetTemperatureRange": {
      "heating": {
        "min": 18,
        "max": 26
      },
      "cooling": {
        "min": 26,
        "max": 30
      }
    },
    "defaultTemperature": 26
  }
}
```


#### Message `PowerOn`

「房间空调」开机

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | PowerOn |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "PowerOn",
  "params": {
    "roomID": "03-03-33"
  }
}
```


#### Message `PowerOff`

「房间空调」关机

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | PowerOff |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "PowerOff",
  "params": {
    "roomID": "03-03-33"
  }
}
```


#### Message `AdjustTargetTemperature`

用户调整「房间空调」的「目标温度」

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | AdjustTargetTemperature |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |
| `params.targetTemperature` **(required)** | `integer` | 温度（以摄氏度为单位） | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "AdjustTargetTemperature",
  "params": {
    "roomID": "03-03-33",
    "targetTemperature": 25
  }
}
```


#### Message `AdjustWindSpeed`

用户调整「房间空调」的「风速」

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | AdjustWindSpeed |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |
| `params.windSpeed` **(required)** | `string` | 风速 > - `low` 低风速 - `medium` 中风速 - `high` 高风速 | low, medium, high |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "AdjustWindSpeed",
  "params": {
    "roomID": "03-03-33",
    "windSpeed": "low"
  }
}
```


#### Message `ResumeWindSupply`

「房间空调」请求送风

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | ResumeWindSupply |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "ResumeWindSupply",
  "params": {
    "roomID": "03-03-33"
  }
}
```


#### Message `SuspendWindSupply`

「房间空调」请求暂停送风

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | SuspendWindSupply |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "SuspendWindSupply",
  "params": {
    "roomID": "03-03-33"
  }
}
```


#### Message `RoomTemperatureUpdate`

「房间空调」向「中央空调」周期性上报「房间温度」

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | RoomTemperatureUpdate |
| `params.roomID` **(required)** | `string` | 房间 ID | _Any_ |
| `params.roomTemperature` **(required)** | `integer` | 温度（以摄氏度为单位） | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "RoomTemperatureUpdate",
  "params": {
    "roomID": "03-03-33",
    "roomTemperature": 25
  }
}
```



### `subscribe` Operation

从「中央空调」发往「房间空调」的信息


#### Message `BillingInformationUpdate`

「中央空调」周期性向「房间空调」发放计费信息

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | BillingInformationUpdate |
| `params.billingRate` **(required)** | `number` | 当前计费速率（单位：元/秒） | _Any_ |
| `params.totalCost` **(required)** | `number` | 该房间空调的累计费用（单位：元） | _Any_ |
| `params.totalServiceTime` **(required)** | `number` | 该房间空调的总服务时间（单位：秒） | _Any_ |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "BillingInformationUpdate",
  "params": {
    "billingRate": 0.1,
    "totalCost": 7.21,
    "totalServiceTime": 42
  }
}
```


#### Message `WindSupplyResumed`

「中央空调」恢复向「房间空调」送风

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | WindSupplyResumed |
| `params.windSpeed` **(required)** | `string` | 风速 > - `low` 低风速 - `medium` 中风速 - `high` 高风速 | low, medium, high |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "WindSupplyResumed",
  "params": {
    "windSpeed": "low"
  }
}
```


#### Message `WindSupplySuspended`

「中央空调」暂停向「房间空调」送风

##### Payload

| Name | Type | Description | Accepted values |
|-|-|-|-|
| `method` **(required)** | `string` | - | WindSupplySuspended |
| `params.reason` **(required)** | `string` | 停止送风的原因 > - `client-requested` 房间空调主动要求停止送风 - `scheduling` 中央空调服务能力不足，依照调度算法暂停该房间送风 | client-requested, scheduling |

##### Example

```json
{
  "jsonrpc": "2.0",
  "method": "WindSupplySuspended",
  "params": {
    "reason": "client-requested"
  }
}
```
