# 分布式空调系统管理后台通信协议

版本：`0.0.3-alpha`

[TOC]

## 协议基础

- 通信对象
  - 后台管理端
  - 后端服务器

- 协议功能
  - 管理订单
  - 系统控制
  - 房间监控

- 底层信道：[WebSocket](https://en.wikipedia.org/wiki/WebSocket)
- 基本格式：[json-rpc](https://www.jsonrpc.org/specification)
- 数据格式描述：[json-schema](https://json-schema.org)

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
  "method": "getSum",

  // 方法参数
  "params": {
    "a": 1,
    "b": 2
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
    "sum": 3
  }
}
```

#### 错误

如果请求发生错误，则响应中不含 `result` 字段，而含 `error` 字段

```json
{
  // JSON-RPC 版本，必须是 2.0
  "jsonrpc": "2.0",

  // id，表示是对哪个请求的响应
  "id": 1,

  // 错误（只有请求失败时有此属性）
  "error": {
    // 错误代码
    "code": 233,

    // 可读的错误信息
    "message": "加法运算溢出",

    // 错误相关数据
    "data": {
      "max": 2147483647
    }
  }
}
```

本协议中使用这样的错误码格式：`XAABB`，其中：
- `X`: 错误类型
  - `4` 代表错误在于客户端
- `AA`: 方法编码
- `BB`: 错误编码，从 `01` 开始自增

此外，使用 `99999` 代表所有其他没有在协议中说明的未知错误

#### 通知

一种特殊的请求，不含 `id` 字段，不需要响应，代表一种事件或通知

### json-schema 简介

本协议中数据传输使用 `json`，`json-schema` 则用于形式化地、严格地描述 `json` 数据的格式

通常为了直观会用例子去描述接口的格式，例如，我们说，某个接口的输入数据像这样：

```json
{
  "productId": 1,
  "productName": "A green door",
  "price": 12,
  "tags": ["home", "green"]
}
```

但是这样的描述比较模糊，有很多不清楚的地方：

- `productId`, `price` 这些属性都是什么意思？
- `productName` 属性是必需的吗？
- `price` 可以为 0 吗？可以为小数吗？
- `tags` 中的所有元素都是字符串吗？

`json-schema` 提供了一种方法可以让我们去严谨的描述数据格式，可以将其类比成编程语言中的类型定义或者 SQL 中的表定义

例如，用下面这个 `json-schema` 去描述上面的接口数据：

```json
{
  "description": "A product from Acme's catalog",
  "type": "object", // 类型是对象
  "required": ["productId", "productName", "price"], // 这三个属性是必需的，其他则是可选的
  "properties": { // properties 中列出对象的所有属性及其定义
    "productId": {
      "description": "The unique identifier for a product", // productId 属性的含义
      "type": "integer" // productId 类型必须是整数
    },
    "productName": {
      "description": "Name of the product",
      "type": "string" // productName 类型必须是字符串
    },
    "price": {
      "description": "The price of the product",
      "type": "number", // price 类型必须是数字
      "exclusiveMinimum": 0 // price 最小值是 0 (不含)
    },
    "tags": {
      "description": "Tags for the product",
      "type": "array", // tags 类型是数组
      "items": {
        "type": "string" // tags 的数组元素类型是字符串
      },
      "minItems": 1, // tags 中至少要有一个元素
      "uniqueItems": true // tags 中元素必须是唯一的
    }
  }
}
```

这样数据格式就可以很清楚的描述出来了，关于 `json-schema` 具体的语法和含义，可以阅读 [官方文档](https://json-schema.org)

阅读下面文档时 example 和 schema 要结合起来看，example 是实际发送/接受数据的样子，据此形成直观理解，schema 则是比较严格的定义，涉及的各种情况都需要考虑

## 方法 (从客户端到服务器)

### `createOrder`

> 创建新「订单」

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "createOrder",
  "params": {
    "userID": "Alice",
    "roomID": "01-32-34"
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": {
    "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
  }
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "userID",
    "roomID"
  ],
  "properties": {
    "userID": {
      "description": "用户 ID",
      "type": "string",
      "example": "Alice"
    },
    "roomID": {
      "description": "房间 ID",
      "type": "string",
      "example": "01-32-34"
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "type": "object",
  "required": [
    "orderID"
  ],
  "properties": {
    "orderID": {
      "description": "订单 ID",
      "type": "string",
      "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
    }
  }
}
```

#### 错误格式说明

##### `40101` - 无效的用户 ID

> 客户端提供的「用户 ID」格式错误或不存在

- 错误代码：`40101`
- 命名：`INVALID_USER_ID`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40101,
    "message": "无效的用户 ID"
  }
}
```

##### `40102` - 无效的房间 ID

> 客户端提供的「房间 ID」格式错误或不存在

- 错误代码：`40102`
- 命名：`INVALID_ROOM_ID`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40102,
    "message": "无效的房间 ID"
  }
}
```

##### `40103` - 房间不可用

> 客户端指定的房间处于不可用状态 (被其他用户使用中、维护中)

- 错误代码：`40103`
- 命名：`ROOM_UNAVAILABLE`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40103,
    "message": "房间不可用"
  }
}
```

### `fetchOrders`

> 获取「订单」列表

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "fetchOrders",
  "params": {
    "filter": {
      "userID": "Alice",
      "roomID": "01-32-34",
      "state": "using"
    }
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": {
    "orders": [
      {
        "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e",
        "userID": "Alice",
        "roomID": "01-32-34",
        "createdTime": 1622516073,
        "finishedTime": 1622725792,
        "state": "using"
      }
    ]
  }
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "filter"
  ],
  "properties": {
    "filter": {
      "description": "过滤条件",
      "type": "object",
      "properties": {
        "userID": {
          "description": "用户 ID",
          "type": "string",
          "example": "Alice"
        },
        "roomID": {
          "description": "房间 ID",
          "type": "string",
          "example": "01-32-34"
        },
        "state": {
          "description": "订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)",
          "type": "string",
          "enums": [
            "using",
            "unpaid",
            "completed"
          ]
        }
      }
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "type": "object",
  "required": [
    "orders"
  ],
  "properties": {
    "orders": {
      "description": "符号条件的订单列表",
      "type": "array",
      "items": {
        "description": "订单",
        "type": "object",
        "required": [
          "orderID",
          "userID",
          "roomID",
          "createdTime",
          "finishedTime",
          "state"
        ],
        "properties": {
          "orderID": {
            "description": "订单 ID",
            "type": "string",
            "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
          },
          "userID": {
            "description": "用户 ID",
            "type": "string",
            "example": "Alice"
          },
          "roomID": {
            "description": "房间 ID",
            "type": "string",
            "example": "01-32-34"
          },
          "createdTime": {
            "description": "订单的创建时间 (以 Unix 时间戳形式表示)",
            "type": "number",
            "example": 1622516073
          },
          "finishedTime": {
            "description": "订单的结束时间 (以 Unix 时间戳形式表示)",
            "example": 1622725792,
            "type": "number"
          },
          "state": {
            "description": "订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)",
            "type": "string",
            "enums": [
              "using",
              "unpaid",
              "completed"
            ]
          }
        }
      }
    }
  }
}
```

### `finishOrder`

> 结束「订单」

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "finishOrder",
  "params": {
    "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": null
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "orderID"
  ],
  "properties": {
    "orderID": {
      "description": "订单 ID",
      "type": "string",
      "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "type": "null"
}
```

#### 错误格式说明

##### `40301` - 无效的订单 ID

> 客户端提供的「订单 ID」格式错误或不存在

- 错误代码：`40301`
- 命名：`INVALID_ORDER_ID`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40301,
    "message": "无效的订单 ID"
  }
}
```

##### `40302` - 非法的订单状态

> 指定订单的状态不允许进行「结束」操作

- 错误代码：`40302`
- 命名：`INVALID_ORDER_STATE`
- 错误数据描述：

```json
{
  "type": "object",
  "required": [
    "state"
  ],
  "properties": {
    "state": {
      "description": "订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)",
      "type": "string",
      "enums": [
        "using",
        "unpaid",
        "completed"
      ]
    }
  }
}
```

- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40302,
    "message": "非法的订单状态",
    "data": {
      "state": "using"
    }
  }
}
```

### `getBill`

> 获取「账单」

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "getBill",
  "params": {
    "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": {
    "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e",
    "billID": "7bc878cb-74a6-4281-823e-f61d5887bc05",
    "totalCost": 2434
  }
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "orderID"
  ],
  "properties": {
    "orderID": {
      "description": "订单 ID",
      "type": "string",
      "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "description": "账单",
  "type": "object",
  "required": [
    "orderID",
    "billID",
    "totalCost"
  ],
  "properties": {
    "orderID": {
      "description": "订单 ID",
      "type": "string",
      "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
    },
    "billID": {
      "description": "账单 ID",
      "type": "string",
      "example": "7bc878cb-74a6-4281-823e-f61d5887bc05"
    },
    "totalCost": {
      "type": "number",
      "description": "总费用",
      "example": 2434
    }
  }
}
```

#### 错误格式说明

##### `40401` - 无效的订单 ID

> 客户端提供的「订单 ID」格式错误或不存在

- 错误代码：`40401`
- 命名：`INVALID_ORDER_ID`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40401,
    "message": "无效的订单 ID"
  }
}
```

##### `40402` - 非法的订单状态

> 指定订单的状态不允许进行「获取账单」操作

- 错误代码：`40402`
- 命名：`INVALID_ORDER_STATE`
- 错误数据描述：

```json
{
  "type": "object",
  "required": [
    "state"
  ],
  "properties": {
    "state": {
      "description": "订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)",
      "type": "string",
      "enums": [
        "using",
        "unpaid",
        "completed"
      ]
    }
  }
}
```

- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40402,
    "message": "非法的订单状态",
    "data": {
      "state": "using"
    }
  }
}
```

### `makePayment`

> 为账单付款

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "makePayment",
  "params": {
    "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": null
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "orderID"
  ],
  "properties": {
    "orderID": {
      "description": "订单 ID",
      "type": "string",
      "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "type": "null"
}
```

#### 错误格式说明

##### `40501` - 无效的订单 ID

> 客户端提供的「订单 ID」格式错误或不存在

- 错误代码：`40501`
- 命名：`INVALID_ORDER_ID`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40501,
    "message": "无效的订单 ID"
  }
}
```

##### `40502` - 非法的订单状态

> 指定订单的状态不允许进行「付款」操作

- 错误代码：`40502`
- 命名：`INVALID_ORDER_STATE`
- 错误数据描述：

```json
{
  "type": "object",
  "required": [
    "state"
  ],
  "properties": {
    "state": {
      "description": "订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)",
      "type": "string",
      "enums": [
        "using",
        "unpaid",
        "completed"
      ]
    }
  }
}
```

- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40502,
    "message": "非法的订单状态",
    "data": {
      "state": "using"
    }
  }
}
```

### `getDetailedList`

> 获取「详单」

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "getDetailedList",
  "params": {
    "orderID": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": {
    "items": [
      {
        "startTime": 1622516073,
        "endTime": 1622541697,
        "windSpeed": "low",
        "billingRate": 0.5
      }
    ]
  }
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "orderID"
  ],
  "properties": {
    "orderID": {
      "description": "订单 ID",
      "type": "string",
      "example": "027de49d-11f2-437b-b4bd-1a06a4f0df6e"
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "description": "详单",
  "type": "object",
  "required": [
    "items"
  ],
  "properties": {
    "items": {
      "type": "array",
      "items": {
        "description": "详单条目",
        "type": "object",
        "required": [
          "startTime",
          "endTime",
          "windSpeed",
          "billingRate"
        ],
        "properties": {
          "startTime": {
            "description": "开始时间 (以 Unix 时间戳形式表示)",
            "type": "number",
            "example": 1622516073
          },
          "endTime": {
            "description": "结束时间 (以 Unix 时间戳形式表示)",
            "example": 1622541697,
            "type": "number"
          },
          "windSpeed": {
            "description": "该时间段的风速",
            "type": "string",
            "enums": [
              "low",
              "medium",
              "high"
            ]
          },
          "billingRate": {
            "description": "该时间段的计费速率 (单位：元/秒)",
            "type": "number",
            "example": 0.5
          }
        }
      }
    }
  }
}
```

#### 错误格式说明

##### `40601` - 无效的订单 ID

> 客户端提供的「订单 ID」格式错误或不存在

- 错误代码：`40601`
- 命名：`INVALID_ORDER_ID`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40601,
    "message": "无效的订单 ID"
  }
}
```

##### `40602` - 非法的订单状态

> 指定订单的状态不允许进行「获取详单」操作

- 错误代码：`40602`
- 命名：`INVALID_ORDER_STATE`
- 错误数据描述：

```json
{
  "type": "object",
  "required": [
    "state"
  ],
  "properties": {
    "state": {
      "description": "订单状态 (`using` 代表「使用中」，`unpaid` 代表「未付款」，`completed` 代表「已完成」)",
      "type": "string",
      "enums": [
        "using",
        "unpaid",
        "completed"
      ]
    }
  }
}
```

- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40602,
    "message": "非法的订单状态",
    "data": {
      "state": "using"
    }
  }
}
```

### `getStatistics`

> 获取统计报表

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "getStatistics",
  "params": {
    "startTime": 1622726063,
    "endTime": 1622812463
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": {
    "statistics": [
      {
        "roomID": "01-32-34",
        "airConditionerUsedTimes": 98,
        "mostFrequentlyUsedTargetTemperature": 23,
        "mostFrequentlyUsedWindSpeed": "low",
        "targetTemperatureReachedTimes": 42,
        "scheduledTimes": 233,
        "numberOfdetailedListRecords": 2434,
        "totalCost": 2080000
      }
    ]
  }
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "startTime",
    "endTime"
  ],
  "properties": {
    "startTime": {
      "description": "开始时间 (Unix 时间戳)",
      "example": 1622726063,
      "type": "number"
    },
    "endTime": {
      "description": "结束时间 (Unix 时间戳)",
      "example": 1622812463
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "type": "object",
  "required": [
    "statistics"
  ],
  "properties": {
    "statistics": {
      "description": "所有房间的统计报表",
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "roomID",
          "airConditionerUsedTimes",
          "mostFrequentlyUsedTargetTemperature",
          "mostFrequentlyUsedWindSpeed",
          "targetTemperatureReachedTimes",
          "scheduledTimes",
          "numberOfdetailedListRecords",
          "totalCost"
        ],
        "properties": {
          "roomID": {
            "description": "房间 ID",
            "type": "string",
            "example": "01-32-34"
          },
          "airConditionerUsedTimes": {
            "description": "空调使用次数",
            "type": "number",
            "example": 98
          },
          "mostFrequentlyUsedTargetTemperature": {
            "description": "最常用目标温度 (单位：摄氏度)",
            "type": "number",
            "example": 23
          },
          "mostFrequentlyUsedWindSpeed": {
            "description": "最常用风速",
            "type": "string",
            "enums": [
              "low",
              "medium",
              "high"
            ]
          },
          "targetTemperatureReachedTimes": {
            "description": "达到目标温度次数",
            "type": "number",
            "example": 42
          },
          "scheduledTimes": {
            "description": "被调度次数",
            "type": "number",
            "example": 233
          },
          "numberOfdetailedListRecords": {
            "description": "详单记录数",
            "type": "number",
            "example": 2434
          },
          "totalCost": {
            "description": "总费用 (单位：元)",
            "type": "number",
            "example": 2080000
          }
        }
      }
    }
  }
}
```

### `getSystemStatus`

> 获取系统状态

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "getSystemStatus"
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": {
    "started": true
  }
}

```

#### 响应数据格式说明

```json
{
  "type": "object",
  "required": [
    "started"
  ],
  "properties": {
    "started": {
      "type": "boolean",
      "description": "系统是否已启动"
    }
  }
}
```

### `startSystem`

> 启动系统

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "startSystem"
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": null
}

```

#### 响应数据格式说明

```json
{
  "type": "null"
}
```

#### 错误格式说明

##### `40801` - 系统已经在运行中

> 试图启动运行中的系统

- 错误代码：`40801`
- 命名：`SYSTEM_IS_RUNNING`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40801,
    "message": "系统已经在运行中"
  }
}
```

### `stopSystem`

> 停止系统

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "stopSystem"
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": null
}

```

#### 响应数据格式说明

```json
{
  "type": "null"
}
```

#### 错误格式说明

##### `40901` - 系统尚未启动

> 试图停止未运行的系统

- 错误代码：`40901`
- 命名：`SYSTEM_IS_NOT_RUNNING`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 40901,
    "message": "系统尚未启动"
  }
}
```

### `getSysConfig`

> 获取系统配置

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "getSysConfig"
}

// 响应
{
  "jsonrpc": "2.0.0",
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
    "defaultTemperature": 26,
    "electricityPrice": 1,
    "electricityConsumptionRate": {
      "low": 1,
      "medium": 2,
      "high": 3
    },
    "maxNumOfClientsToServe": 3
  }
}

```

#### 响应数据格式说明

```json
{
  "type": "object",
  "required": [
    "temperatureControlMode",
    "targetTemperatureRange",
    "defaultTemperature",
    "electricityPrice",
    "electricityConsumptionRate",
    "maxNumOfClientsToServe"
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
    },
    "electricityPrice": {
      "description": "计费标准 (单位：元/度)",
      "type": "number",
      "example": 1
    },
    "electricityConsumptionRate": {
      "description": "耗电速率",
      "type": "object",
      "properties": {
        "low": {
          "description": "低风速下的耗电速率 (单位：度/分钟)",
          "type": "number",
          "example": 1
        },
        "medium": {
          "description": "中风速下的耗电速率 (单位：度/分钟)",
          "type": "number",
          "example": 2
        },
        "high": {
          "description": "高风速下的耗电速率 (单位：度/分钟)",
          "type": "number",
          "example": 3
        }
      }
    },
    "maxNumOfClientsToServe": {
      "description": "最大可服务对象数",
      "type": "number",
      "example": 3
    }
  }
}
```

### `setSysConfig`

> 设置系统配置

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "method": "setSysConfig",
  "params": {
    "newConfigration": {
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
      "defaultTemperature": 26,
      "electricityPrice": 1,
      "electricityConsumptionRate": {
        "low": 1,
        "medium": 2,
        "high": 3
      },
      "maxNumOfClientsToServe": 3
    }
  }
}

// 响应
{
  "jsonrpc": "2.0.0",
  "id": 1,
  "result": null
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "required": [
    "newConfigration"
  ],
  "properties": {
    "newConfigration": {
      "required": [],
      "type": "object",
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
        },
        "electricityPrice": {
          "description": "计费标准 (单位：元/度)",
          "type": "number",
          "example": 1
        },
        "electricityConsumptionRate": {
          "description": "耗电速率",
          "type": "object",
          "properties": {
            "low": {
              "description": "低风速下的耗电速率 (单位：度/分钟)",
              "type": "number",
              "example": 1
            },
            "medium": {
              "description": "中风速下的耗电速率 (单位：度/分钟)",
              "type": "number",
              "example": 2
            },
            "high": {
              "description": "高风速下的耗电速率 (单位：度/分钟)",
              "type": "number",
              "example": 3
            }
          }
        },
        "maxNumOfClientsToServe": {
          "description": "最大可服务对象数",
          "type": "number",
          "example": 3
        }
      }
    }
  }
}
```

#### 响应数据格式说明

```json
{
  "type": "null"
}
```

#### 错误格式说明

##### `41101` - 禁止在运行时设置系统配置

> 禁止在运行时设置系统配置

- 错误代码：`41101`
- 命名：`PROHIBIT_CONFIGURATION_AT_RUNTIME`
- 错误示例：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": 41101,
    "message": "禁止在运行时设置系统配置"
  }
}
```

## 方法 (从服务器到客户端)

### `roomInformationUpdate`

> 房间信息更新

#### 正常请求示例

```json
// 请求
{
  "jsonrpc": "2.0.0",
  "method": "roomInformationUpdate",
  "params": {
    "infos": [
      {
        "roomID": "01-32-34",
        "isStarted": true,
        "roomTemperature": 28,
        "targetTemperature": 21,
        "windSpeed": "low",
        "isSupplyingWind": true
      }
    ]
  }
}

```

#### 请求数据格式说明

```json
{
  "type": "object",
  "properties": {
    "infos": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "roomID",
          "isStarted"
        ],
        "properties": {
          "roomID": {
            "description": "房间 ID",
            "type": "string",
            "example": "01-32-34"
          },
          "isStarted": {
            "description": "房间空调是否已启动",
            "type": "boolean"
          },
          "roomTemperature": {
            "description": "房间温度 (单位：摄氏度)",
            "type": "number",
            "example": 28
          },
          "targetTemperature": {
            "description": "目标温度 (单位：摄氏度)",
            "type": "number",
            "example": 21
          },
          "windSpeed": {
            "description": "风速 (`low` 代表「低风速」，`medium` 代表「中风速」，`high` 代表「高风速」)",
            "type": "string",
            "enums": [
              "low",
              "medium",
              "high"
            ]
          },
          "isSupplyingWind": {
            "description": "是否正在送风",
            "type": "boolean"
          }
        }
      }
    }
  }
}
```
