# CS2 饰品价格波动监控系统 — 产品 PRD

<aside>
📌

**文档信息**

- **产品名称**：CS2 饰品价格波动监控通知系统（cs-monitor）
- **版本**：v1.1
- **作者**：树 树
- **创建日期**：2026-04-13
- **开发工具**：Claude Code（CLI）
- **技术栈**：Python 3.12+
</aside>

---

## 1. 产品概述

### 1.1 背景

CS2（Counter-Strike 2）拥有庞大的饰品交易市场，饰品价格受供需、赛事、更新等因素影响频繁波动。玩家和交易者需要一个自动化工具来实时监控关注饰品的价格变化，及时捕捉买入/卖出时机。

### 1.2 产品定位

一个**轻量级、可自托管**的 CS2 饰品价格监控工具，基于 SteamDT 开放平台 API，定时采集价格数据，自动检测异常波动并推送通知。

### 1.3 目标用户

- CS2 饰品收藏玩家
- 饰品交易者（低买高卖）
- 想学习 API 开发的编程新手

---

## 2. 核心功能需求

### 2.1 功能列表

| **功能模块** | **优先级** | **功能描述** | **MVP** |
| --- | --- | --- | --- |
| F1 监控清单管理 | P0 | 用户可添加/移除想要监控的饰品 | ✅ |
| F2 定时价格采集 | P0 | 按设定间隔自动从 SteamDT 拉取各平台价格 | ✅ |
| F3 价格波动检测 | P0 | 对比当前价与基准价，超过阈值触发告警 | ✅ |
| F4 通知推送 | P0 | 通过企微/Telegram/Server酱等渠道推送告警 | ✅ |
| F5 历史价格存储 | P0 | 将每次采集的价格数据持久化到本地数据库 | ✅ |
| F6 7天均价基准 | P1 | 获取近7天均价作为波动判断基准线 | ✅ |
| F7 K线趋势分析 | P2 | 连续N天涨跌趋势检测，辅助决策 |  |
| F8 多平台价差提醒 | P2 | 同一饰品不同平台价差超阈值时提醒套利机会 |  |
| F9 Web 仪表盘 | P3 | 可视化展示价格曲线和监控状态 |  |
| **F10 极致追踪模式** | **P0** | **高频盯死单品，追踪指定平台价格变动和在售数量变化，任何波动立即推送** | **✅** |

---

## 3. 详细功能设计

### 3.1 F1 监控清单管理

**描述**：用户维护一个想要监控的饰品列表

**数据结构**：

```python
# watchlist 条目
{
    "market_hash_name": "AK-47 | Redline (Field-Tested)",
    "display_name": "AK-47 红线 久经沙场",       # 可选中文别名
    "threshold_percent": 5.0,                     # 波动阈值百分比
    "enabled": True,                               # 是否启用监控
    "added_at": "2026-04-13T00:00:00"
}
```

**MVP 实现**：在 `config.py` 中以列表形式配置，后续可迁移到 JSON 文件或数据库。

### 3.2 F2 定时价格采集

**描述**：按照用户设定的时间间隔，批量调用 SteamDT API 获取监控清单中所有饰品的当前价格

**调用接口**：

- `通过 marketHashName 批量查询饰品价格`
- `通过 MarketHashName 查询所有平台近7天均价`

**定时策略**：

- 默认每 **30 分钟** 执行一次（可在 config 中配置）
- 需遵守 SteamDT API 频率限制
- 首次启动时立即执行一次

**容错处理**：

- API 调用失败时重试 3 次，间隔 10 秒
- 连续失败 5 次发送错误通知
- 记录所有 API 调用日志

### 3.3 F3 价格波动检测

**描述**：对比当前价格与基准价格，判断是否触发告警

**波动计算公式**：

```
波动率 = (当前价格 - 基准价格) / 基准价格 × 100%
```

**基准价格来源（优先级）**：

1. **7 天均价**（推荐，通过 API 获取）
2. **上一次采集价格**（兜底方案）

**告警规则**：

| **规则** | **条件** | **通知内容** |
| --- | --- | --- |
| 价格暴涨 | 波动率 ≥ +阈值% | 🔴 [饰品名] 价格暴涨 X%，当前 ¥XX |
| 价格暴跌 | 波动率 ≤ -阈值% | 🟢 [饰品名] 价格暴跌 X%，当前 ¥XX（买入机会？） |
| 防重复通知 | 同一饰品同一方向 4h 内只通知 1 次 | — |

### 3.4 F4 通知推送

**描述**：将告警信息推送到用户选择的通知渠道

**支持渠道**（MVP 至少实现 1 个）：

| **渠道** | **实现方式** | **优先级** |
| --- | --- | --- |
| 企业微信机器人 | Webhook POST JSON | P0（推荐首选） |
| Server 酱 | HTTP GET/POST | P1 |
| Telegram Bot | Bot API sendMessage | P1 |
| 邮件 | Python smtplib | P2 |

**通知消息模板**：

```
⚠️ CS2 饰品价格波动提醒

📦 饰品：AK-47 | Redline (Field-Tested)
💰 当前价格：¥128.50
📊 7天均价：¥120.00
📈 波动幅度：+7.08%
🏪 最低平台：BUFF ¥125.00
🕐 时间：2026-04-13 23:30
```

### 3.5 F5 历史价格存储

**描述**：持久化存储每次采集的价格数据

**技术方案**：SQLite（轻量、无需额外服务）

**数据库表设计**：

```sql
-- 饰品基础信息表
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 价格记录表
CREATE TABLE price_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,          -- buff / igxe / c5 / steam 等
    price REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (market_hash_name) REFERENCES items(market_hash_name)
);

-- 告警记录表
CREATE TABLE alert_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,         -- 'price_surge' / 'price_drop'
    current_price REAL,
    baseline_price REAL,
    change_percent REAL,
    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.6 F10 极致追踪模式 🔥

<aside>
🎯

**核心理念**：盯死一个饰品，盯死一个平台，任何风吹草动立即通知。与 F2/F3 的「批量巡检」不同，极致追踪是**单品高频狙击模式**。

</aside>

#### 3.6.1 功能描述

用户可以针对 **单个饰品 + 单个平台**（如悠悠有品）开启极致追踪，系统以用户自定义的高频间隔持续轮询，追踪两个核心维度：

1. **价格变动**：只要在售价格发生任何变化（或超过设定百分比），立即推送
2. **在售数量变动**：在售数量增加或减少（或变化超过设定百分比），立即推送

#### 3.6.2 追踪配置数据结构

```python
@dataclass
class ExtremeTrackItem:
    # === 基础配置 ===
    market_hash_name: str              # 饰品 marketHashName
    display_name: str = ""             # 中文别名
    platform: str = "youpin"           # 盯死的平台：youpin / buff / igxe / c5 / steam
    enabled: bool = True

    # === 轮询频率 ===
    interval_seconds: int = 60         # 轮询间隔（秒），默认 60 秒
    # 建议值：
    #   - 激进模式：30-60 秒（需确认 API 套餐支持）
    #   - 标准模式：3-5 分钟
    #   - 保守模式：10-30 分钟

    # === 价格追踪 ===
    price_track_enabled: bool = True
    price_change_mode: str = "any"     # "any" = 任何变动都通知 | "percent" = 超过百分比才通知
    price_threshold_percent: float = 0.0  # 当 mode="percent" 时生效，0 表示任何变动

    # === 在售数量追踪 ===
    quantity_track_enabled: bool = True
    quantity_change_mode: str = "any"  # "any" = 任何变动都通知 | "percent" = 超过百分比才通知
    quantity_threshold_percent: float = 0.0  # 当 mode="percent" 时生效

    # === 通知控制 ===
    alert_cooldown_seconds: int = 0    # 通知冷却（秒），0 = 不冷却，每次变动都通知
    quiet_hours_start: str = ""        # 免打扰开始时间 "02:00"，留空不启用
    quiet_hours_end: str = ""          # 免打扰结束时间 "08:00"
```

#### 3.6.3 轮询频率设计

<aside>
⚠️

**频率需根据 SteamDT API 套餐限制设计**，请先查阅 [接口权限列表](https://doc.steamdt.com/6369437m0.md) 确认你的每日/每分钟调用上限。

</aside>

| **模式** | **轮询间隔** | **每小时请求数** | **适用场景** |
| --- | --- | --- | --- |
| 🔴 激进 | 30 秒 | 120 次/h | 重大赛事/更新期间抢先机 |
| 🟡 标准 | 3 分钟 | 20 次/h | 日常重点饰品监控（推荐） |
| 🟢 保守 | 10 分钟 | 6 次/h | 长期持有品关注趋势 |

**自动降频保护**：当检测到 API 返回频率限制错误时，自动将间隔翻倍，恢复后自动回调。

```python
# 自动降频逻辑伪代码
current_interval = config.interval_seconds

if api_response.status == 429:  # Too Many Requests
    current_interval = min(current_interval * 2, 3600)  # 最大不超过 1 小时
    log.warning(f"API 限流，间隔自动调整为 {current_interval}s")
    notify("⚠️ 极致追踪频率已自动降低，API 可能接近限额")
elif consecutive_success >= 10:
    current_interval = max(config.interval_seconds, current_interval // 2)  # 逐步恢复
```

#### 3.6.4 波动检测逻辑

**价格波动**：

```python
def check_price_change(current_price, last_price, config):
    if last_price is None or last_price == 0:
        return None  # 首次采集，不告警

    change = current_price - last_price
    change_percent = (change / last_price) * 100

    if config.price_change_mode == "any" and change != 0:
        return Alert(type="price", change=change, percent=change_percent)
    elif config.price_change_mode == "percent":
        if abs(change_percent) >= config.price_threshold_percent:
            return Alert(type="price", change=change, percent=change_percent)
    return None
```

**在售数量波动**：

```python
def check_quantity_change(current_qty, last_qty, config):
    if last_qty is None:
        return None

    change = current_qty - last_qty
    if last_qty > 0:
        change_percent = (change / last_qty) * 100
    else:
        change_percent = 100.0 if change > 0 else 0

    if config.quantity_change_mode == "any" and change != 0:
        return Alert(type="quantity", change=change, percent=change_percent)
    elif config.quantity_change_mode == "percent":
        if abs(change_percent) >= config.quantity_threshold_percent:
            return Alert(type="quantity", change=change, percent=change_percent)
    return None
```

#### 3.6.5 通知消息模板

**价格变动通知**：

```
🎯 [极致追踪] 价格变动

📦 饰品：AK-47 | Redline (Field-Tested)
🏪 平台：悠悠有品
💰 当前价格：¥128.50
💰 上次价格：¥125.00
📈 变动：+¥3.50（+2.80%）
📊 在售数量：42 件
🕐 时间：2026-04-14 13:30:00
⏱️ 距上次变动：12 分钟
```

**在售数量变动通知**：

```
🎯 [极致追踪] 在售数量变动

📦 饰品：AK-47 | Redline (Field-Tested)
🏪 平台：悠悠有品
📉 当前在售：38 件
📊 上次在售：42 件
🔻 变动：-4 件（-9.52%）
💰 当前价格：¥128.50
🕐 时间：2026-04-14 13:30:00
💡 提示：数量减少可能意味着有人在买入
```

**价格 + 数量同时变动通知**（合并推送）：

```
🎯 [极致追踪] 价格 & 数量同时变动！

📦 饰品：AK-47 | Redline (Field-Tested)
🏪 平台：悠悠有品

💰 价格：¥125.00 → ¥128.50（+2.80%）
📦 数量：42 件 → 38 件（-9.52%）

🕐 时间：2026-04-14 13:30:00
💡 量跌价涨，市场可能在抢货
```

#### 3.6.6 数据库扩展

新增两张表支持极致追踪：

```sql
-- 极致追踪快照表（高频记录，每次轮询都写入）
CREATE TABLE extreme_track_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    price REAL,
    quantity INTEGER,                -- 在售数量
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为查询性能添加索引
CREATE INDEX idx_snapshot_item_time
    ON extreme_track_snapshots(market_hash_name, platform, recorded_at DESC);

-- 极致追踪告警记录表
CREATE TABLE extreme_track_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_hash_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    alert_type TEXT NOT NULL,         -- 'price_change' / 'quantity_change' / 'both'
    prev_price REAL,
    curr_price REAL,
    price_change_percent REAL,
    prev_quantity INTEGER,
    curr_quantity INTEGER,
    quantity_change_percent REAL,
    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.6.7 与普通监控的关系

| **对比项** | **普通监控（F2/F3）** | **极致追踪（F10）** |
| --- | --- | --- |
| 监控目标 | 多个饰品批量巡检 | 单品高频狙击 |
| 轮询频率 | 30 分钟 | 30 秒 ~ 30 分钟（可自定义） |
| 触发条件 | 偏离 7 天均价超阈值 | 任何价格/数量变动或超设定百分比 |
| 追踪维度 | 仅价格 | 价格 + 在售数量 |
| 平台选择 | 所有平台 | 指定单个平台 |
| 通知冷却 | 4 小时 | 可设为 0（不冷却） |
| API 消耗 | 低 | 高（需注意套餐限制） |

两个模式**独立运行、互不影响**，同一饰品可以同时在普通监控清单中（看大盘）和极致追踪中（盯单品）。

---

## 3.7 业务流程图

### 全局流程：系统启动 → 双模式并行运行

```mermaid
flowchart TD
    START(["\U0001f680 系统启动"]) --> INIT["\u2699\ufe0f 初始化<br>加载配置 / 初始化 DB / 验证 API Key"]
    INIT --> FIRST_RUN["\U0001f4e1 首次运行<br>调用『获取饰品基础信息』<br>缓存到本地 SQLite"]
    FIRST_RUN --> SPLIT{"\U0001f500 启动双模式调度"}

    SPLIT --> MODE_A["\u23f0 普通监控模式<br>每 30 分钟一次"]
    SPLIT --> MODE_B["\U0001f3af 极致追踪模式<br>每 N 秒一次"]

    style START fill:#4CAF50,color:#fff
    style MODE_A fill:#2196F3,color:#fff
    style MODE_B fill:#f44336,color:#fff
```

### 流程 A：普通监控模式（批量巡检）

```mermaid
flowchart TD
    A_START(["\u23f0 定时触发<br>每 30 分钟"]) --> A1["\U0001f4e1 批量查询饰品价格<br>SteamDT API"]
    A1 --> A1_CHECK{"API 调用成功?"}
    A1_CHECK -->|\u5931\u8d25| A1_RETRY{"\u91cd\u8bd5 < 3 \u6b21?"}
    A1_RETRY -->|\u662f| A1_WAIT["\u7b49\u5f85 10s"] --> A1
    A1_RETRY -->|\u5426| A1_ERR["\U0001f6a8 发送错误通知<br>记录日志"] --> A_END

    A1_CHECK -->|\u6210\u529f| A2["\U0001f4be 存储价格数据<br>写入 price_records 表"]
    A2 --> A3["\U0001f4ca 获取 7 天均价<br>作为基准线"]
    A3 --> A4{"\U0001f9ee 计算波动率<br>当前价 vs 均价"}

    A4 --> A5_UP{"\u6da8\u5e45 \u2265 +\u9608\u503c%?"}
    A4 --> A5_DOWN{"\u8dcc\u5e45 \u2264 -\u9608\u503c%?"}

    A5_UP -->|\u662f| A6_COOL_UP{"4h 内\u5df2\u901a\u77e5?"}
    A5_DOWN -->|\u662f| A6_COOL_DOWN{"4h 内\u5df2\u901a\u77e5?"}
    A5_UP -->|\u5426| A_LOG
    A5_DOWN -->|\u5426| A_LOG

    A6_COOL_UP -->|\u5426| A7_NOTIFY_UP["\U0001f534 推送涨价通知<br>记录 alert_logs"]
    A6_COOL_UP -->|\u662f| A_LOG
    A6_COOL_DOWN -->|\u5426| A7_NOTIFY_DOWN["\U0001f7e2 推送跌价通知<br>记录 alert_logs"]
    A6_COOL_DOWN -->|\u662f| A_LOG

    A7_NOTIFY_UP --> A_LOG["\U0001f4dd 记录日志"]
    A7_NOTIFY_DOWN --> A_LOG
    A_LOG --> A_END(["\u23f3 等待下一次触发"])

    style A_START fill:#2196F3,color:#fff
    style A7_NOTIFY_UP fill:#f44336,color:#fff
    style A7_NOTIFY_DOWN fill:#4CAF50,color:#fff
```

### 流程 B：极致追踪模式（单品狙击）

```mermaid
flowchart TD
    B_START(["\U0001f3af 高频触发<br>每 N 秒"]) --> B1["\U0001f4e1 查询单品价格<br>指定平台（如悠悠有品）"]
    B1 --> B1_CHECK{"API 调用成功?"}

    B1_CHECK -->|"429 限流"| B_DEGRADE["\u26a0\ufe0f 自动降频<br>间隔 x2\uff08最大 1h\uff09<br>通知用户降频"] --> B_END
    B1_CHECK -->|"\u5176\u4ed6\u5931\u8d25"| B_RETRY{"\u91cd\u8bd5 < 3\u6b21?"}
    B_RETRY -->|\u662f| B_WAIT["\u7b49\u5f85 10s"] --> B1
    B_RETRY -->|\u5426| B_ERR["\U0001f6a8 记录错误日志"] --> B_END

    B1_CHECK -->|\u6210\u529f| B_RECOVER{"\u8fde\u7eed\u6210\u529f \u226510?"}
    B_RECOVER -->|"\u662f & \u5df2\u964d\u9891"| B_RECOVER_ACT["\u2705 逐步恢复频率<br>间隔 /2"] --> B2
    B_RECOVER -->|\u5176\u4ed6| B2

    B2["\U0001f4f8 写入快照<br>extreme_track_snapshots"] --> B3{"\U0001f50d 对比上次快照"}

    B3 --> B4_PRICE{"\U0001f4b0 价格有变动?"}
    B3 --> B4_QTY{"\U0001f4e6 数量有变动?"}

    B4_PRICE -->|\u662f| B5_PRICE_MODE{"\u6a21\u5f0f\u5224\u65ad"}
    B4_PRICE -->|\u5426| B_PRICE_OK["\u2714\ufe0f 价格未变"]

    B5_PRICE_MODE -->|"any 模式"| B6_PRICE_ALERT["\U0001f4b0 价格告警"]
    B5_PRICE_MODE -->|"percent 模式"| B5_PRICE_PCT{"\u8d85\u8fc7\u9608\u503c%?"}
    B5_PRICE_PCT -->|\u662f| B6_PRICE_ALERT
    B5_PRICE_PCT -->|\u5426| B_PRICE_OK

    B4_QTY -->|\u662f| B5_QTY_MODE{"\u6a21\u5f0f\u5224\u65ad"}
    B4_QTY -->|\u5426| B_QTY_OK["\u2714\ufe0f 数量未变"]

    B5_QTY_MODE -->|"any 模式"| B6_QTY_ALERT["\U0001f4e6 数量告警"]
    B5_QTY_MODE -->|"percent 模式"| B5_QTY_PCT{"\u8d85\u8fc7\u9608\u503c%?"}
    B5_QTY_PCT -->|\u662f| B6_QTY_ALERT
    B5_QTY_PCT -->|\u5426| B_QTY_OK

    B6_PRICE_ALERT --> B7_MERGE{"\u4ef7\u683c & \u6570\u91cf<br>\u540c\u65f6\u53d8\u52a8?"}
    B6_QTY_ALERT --> B7_MERGE
    B_PRICE_OK --> B_CHECK_ANY{"\u4efb\u4f55\u544a\u8b66?"}
    B_QTY_OK --> B_CHECK_ANY

    B7_MERGE -->|\u662f| B8_BOTH["\U0001f525 发送合并通知<br>价格 + 数量同时变动"]
    B7_MERGE -->|"\u4ec5\u4ef7\u683c"| B8_PRICE["\U0001f4b0 发送价格变动通知"]
    B7_MERGE -->|"\u4ec5\u6570\u91cf"| B8_QTY["\U0001f4e6 发送数量变动通知"]

    B8_BOTH --> B9["\U0001f4dd 记录 extreme_track_alerts"]
    B8_PRICE --> B9
    B8_QTY --> B9
    B_CHECK_ANY -->|\u65e0\u544a\u8b66| B_LOG["\U0001f4dd 无变动，记录日志"]

    B9 --> B_END(["\u23f3 等待下一次轮询"])
    B_LOG --> B_END

    style B_START fill:#f44336,color:#fff
    style B8_BOTH fill:#ff9800,color:#fff
    style B8_PRICE fill:#ff5722,color:#fff
    style B8_QTY fill:#9C27B0,color:#fff
    style B_DEGRADE fill:#FFC107,color:#333
```

### 流程 C：通知推送流程

```mermaid
flowchart TD
    C_START(["\U0001f4e2 收到告警"]) --> C1{"\U0001f319 当前在免打扰时段?"}
    C1 -->|\u662f| C_QUEUE["\U0001f4e5 入队\u7b49\u5f85<br>免\u6253\u6270\u7ed3\u675f\u540e\u53d1\u9001"] --> C_END
    C1 -->|\u5426| C2{"\u2744\ufe0f 还\u5728\u51b7\u5374\u671f?"}
    C2 -->|\u662f| C_SKIP["\u23e9 跳\u8fc7\u672c\u6b21\u901a\u77e5"] --> C_END
    C2 -->|\u5426| C3{"\U0001f4f1 选\u62e9\u901a\u77e5\u6e20\u9053"}

    C3 --> C4_WECOM["\U0001f4ac 企业微信\u673a\u5668\u4eba<br>Webhook POST"]
    C3 --> C4_TG["\U0001f916 Telegram Bot<br>sendMessage"]
    C3 --> C4_SC["\U0001f4e8 Server \u9171<br>HTTP POST"]
    C3 --> C4_EMAIL["\u2709\ufe0f \u90ae\u4ef6<br>smtplib"]

    C4_WECOM --> C5{"\u53d1\u9001\u6210\u529f?"}
    C4_TG --> C5
    C4_SC --> C5
    C4_EMAIL --> C5

    C5 -->|\u6210\u529f| C6["\u2705 更新冷却计时器"] --> C_END
    C5 -->|\u5931\u8d25| C7{"\u91cd\u8bd5 < 3\u6b21?"}
    C7 -->|\u662f| C8["\u7b49\u5f85 5s"] --> C3
    C7 -->|\u5426| C9["\U0001f6a8 通知发送失败<br>记录错误日志"] --> C_END

    C_END(["\u2705 完成"])

    style C_START fill:#FF9800,color:#fff
    style C4_WECOM fill:#07C160,color:#fff
    style C4_TG fill:#0088cc,color:#fff
```

---

## 4. 技术架构

### 4.1 架构图

```mermaid
flowchart TD
    A["⏰ 定时调度器<br>APScheduler"] --> B["📡 API 模块<br>SteamDT API 调用"]
    B --> C["💾 存储模块<br>SQLite 持久化"]
    B --> D["🧠 分析模块<br>波动检测 + 趋势分析"]
    D --> E{"超过阈值?"}
    E -->|是| F["📢 通知模块<br>企微 / TG / Server酱"]
    E -->|否| G["📝 记录日志"]
    H["⚙️ 配置文件<br>config.py"] --> A
    H --> B
    H --> D
    I["🎯 极致追踪调度器<br>独立高频轮询"] --> B
    B --> J["📸 快照存储<br>extreme_track_snapshots"]
    J --> K["🔍 实时对比<br>价格 & 数量变动"]
    K --> L{"有变动?"}
    L -->|是| F
    L -->|否| G
    H --> I
    H --> K
```

### 4.2 技术选型

| **组件** | **技术选型** | **选型理由** |
| --- | --- | --- |
| 编程语言 | Python 3.12+ | 生态丰富，新手友好，API 调用方便 |
| HTTP 客户端 | httpx（推荐）或 requests | 支持异步，性能好；requests 更简单 |
| 定时调度 | APScheduler | 功能完善，支持 cron/interval 多种模式 |
| 数据存储 | SQLite | 零配置，文件级数据库，适合单机部署 |
| 日志 | loguru | 开箱即用，比标准 logging 更易用 |
| 配置管理 | python-dotenv + dataclass | 环境变量管理敏感信息，dataclass 做类型校验 |

### 4.3 项目目录结构

```jsx
cs-monitor/
├── .env                    # 环境变量（API Key、Webhook URL 等敏感信息）
├── .env.example            # 环境变量模板
├── config.py               # 配置类（阈值、间隔、监控清单）
├── main.py                 # 入口：初始化 + 启动调度器
├── api/
│   ├── __init__.py
│   └── steamdt.py          # SteamDT API 封装
├── core/
│   ├── __init__.py
│   ├── monitor.py          # 价格采集调度逻辑（普通模式）
│   ├── extreme_tracker.py  # 🆕 极致追踪模块（高频单品追踪）
│   ├── analyzer.py         # 波动检测 + 趋势分析
│   └── scheduler.py        # 定时任务管理
├── notify/
│   ├── __init__.py
│   ├── base.py             # 通知基类（接口抽象）
│   ├── wecom.py            # 企业微信机器人
│   ├── telegram.py         # Telegram Bot
│   └── serverchan.py       # Server 酱
├── storage/
│   ├── __init__.py
│   ├── database.py         # SQLite 连接与操作
│   └── models.py           # 数据模型定义
├── utils/
│   ├── __init__.py
│   └── logger.py           # 日志配置
├── data/
│   └── prices.db           # SQLite 数据库文件（自动生成）
├── tests/
│   ├── test_api.py
│   ├── test_analyzer.py
│   └── test_notify.py
├── requirements.txt        # 依赖清单
└── README.md               # 项目说明
```

---

## 5. API 接口使用规范

<aside>
⚠️

**重要限制**：

- 「获取 Steam 饰品基础信息」接口**每天只能调用 1 次**，必须本地缓存返回数据
- 所有接口调用需携带 API Key，注意保密（使用 `.env` 管理）
- 严格遵守套餐的频率限制，超频可能被封禁
- 建议在请求间加入随机延迟（1-3 秒），避免触发风控
</aside>

**需要用到的接口**：

1. **获取 Steam 饰品基础信息** — 初始化调用，建立本地饰品数据库
2. **通过 marketHashName 批量查询饰品价格** — 核心接口，定时批量查价
3. **通过 MarketHashName 查询所有平台近 7 天均价** — 获取基准价格
4. **查询 Steam 饰品 K 线数据** — 进阶功能，趋势分析用

---

## 6. 配置项设计

```python
# config.py 示例
from dataclasses import dataclass, field

@dataclass
class MonitorConfig:
    # === API 配置 ===
    api_key: str = ""                          # 从 .env 读取
    api_base_url: str = "https://api.steamdt.com"
    request_timeout: int = 30                   # 请求超时（秒）
    request_retry: int = 3                      # 失败重试次数

    # === 监控配置 ===
    check_interval_minutes: int = 30            # 价格检查间隔（分钟）
    default_threshold_percent: float = 5.0      # 默认波动阈值（%）
    alert_cooldown_hours: int = 4               # 同一饰品告警冷却时间（小时）

    # === 通知配置 ===
    notify_channel: str = "wecom"               # wecom / telegram / serverchan / email
    wecom_webhook_url: str = ""                 # 企微机器人 Webhook
    telegram_bot_token: str = ""                # TG Bot Token
    telegram_chat_id: str = ""                  # TG Chat ID

    # === 监控清单 ===
    watchlist: list = field(default_factory=lambda: [
        {"name": "AK-47 | Redline (Field-Tested)", "threshold": 5.0},
        {"name": "AWP | Asiimov (Field-Tested)", "threshold": 5.0},
        {"name": "M4A4 | Howl (Factory New)", "threshold": 3.0},
    ])

    # === 🆕 极致追踪配置 ===
    extreme_track_list: list = field(default_factory=lambda: [
        {
            "name": "AK-47 | Redline (Field-Tested)",
            "display_name": "AK-47 红线",
            "platform": "youpin",            # 盯死悠悠有品
            "interval_seconds": 60,           # 每 60 秒查一次
            "price_change_mode": "any",       # 任何价格变动都通知
            "quantity_track_enabled": True,    # 追踪在售数量
            "quantity_change_mode": "any",    # 任何数量变动都通知
            "alert_cooldown_seconds": 0,       # 不冷却
        },
    ])
```

---

## 7. Claude Code 开发指南

<aside>
🤖

以下是使用 **Claude Code** 开发此项目的推荐步骤和提示词模板，帮助你高效完成开发。

</aside>

### 7.1 开发流程

1. **初始化项目**

```bash
mkdir cs-monitor && cd cs-monitor
claude
```

1. **分模块逐步开发**（每次让 Claude Code 完成一个模块）

### 7.2 推荐 Prompt 顺序

**Step 1 — 项目脚手架**

```
帮我初始化一个 Python 项目 cs-monitor：
- 创建上面 PRD 中的目录结构
- 生成 requirements.txt（httpx, apscheduler, loguru, python-dotenv）
- 创建 .env.example 模板
- 创建 config.py 配置类
- 创建 README.md
```

**Step 2 — API 封装**

```
基于 SteamDT 开放平台文档，帮我封装 api/steamdt.py：
- 实现 SteamDTClient 类
- 支持以下接口：批量查询饰品价格、查询7天均价、查询K线数据、获取饰品基础信息
- 统一错误处理和重试逻辑
- 从 .env 读取 API Key
```

**Step 3 — 数据存储**

```
帮我实现 storage/ 模块：
- 使用 SQLite 作为存储
- 按照 PRD 中的表结构创建 items、price_records、alert_logs 三张表
- 封装 CRUD 操作
- 首次运行时自动建表
```

**Step 4 — 核心监控逻辑**

```
帮我实现 core/ 模块：
- monitor.py：定时调用 API 批量查价，结果存入数据库
- analyzer.py：对比当前价和7天均价，超过阈值返回告警列表
- 支持告警冷却（同一饰品同一方向4小时内只告警1次）
```

**Step 4.5 — 极致追踪模块** 🆕

```jsx
帮我实现 core/extreme_tracker.py 极致追踪模块：
- 按照 PRD 中 F10 的设计，实现单品高频追踪
- 支持自定义轮询间隔（秒级）
- 每次轮询写入 extreme_track_snapshots 表
- 对比上一次快照，检测价格和在售数量变动
- 支持两种模式：any（任何变动通知）和 percent（超百分比通知）
- 实现自动降频保护：API 返回 429 时自动翻倍间隔，恢复后逐步回调
- 价格和数量同时变动时合并为一条通知
- 在 scheduler.py 中为极致追踪注册独立的定时任务
```

**Step 5 — 通知模块**

```
帮我实现 notify/ 模块：
- 定义通知基类 base.py（send 方法）
- 实现企业微信机器人推送 wecom.py
- 按照 PRD 中的消息模板格式化通知内容
- 支持通过 config 切换通知渠道
```

**Step 6 — 主程序串联**

```
帮我实现 main.py 入口：
- 加载配置
- 初始化数据库
- 启动 APScheduler 定时任务
- 首次启动立即执行一次
- 优雅退出处理（Ctrl+C）
```

**Step 7 — 测试**

```
帮我写 tests/ 下的单元测试：
- test_api.py：mock API 响应，测试解析逻辑
- test_analyzer.py：测试波动检测阈值判断
- test_notify.py：测试消息格式化
```

---

## 8. 验收标准

### MVP 验收（v1.0）

- [ ]  能通过配置文件设定监控饰品列表
- [ ]  每 30 分钟自动获取一次价格数据
- [ ]  价格数据持久化存储到 SQLite
- [ ]  价格波动超过阈值时推送通知（至少支持 1 个渠道）
- [ ]  同一饰品同方向告警有冷却期，不重复轰炸
- [ ]  **极致追踪：能盯死单品+单平台，自定义轮询间隔**
- [ ]  **极致追踪：价格变动实时推送通知**
- [ ]  **极致追踪：在售数量变动实时推送通知**
- [ ]  **极致追踪：API 限流自动降频保护**
- [ ]  程序可稳定后台运行，异常自动恢复
- [ ]  有基本的日志输出

### 进阶验收（v2.0）

- [ ]  K 线趋势分析，连续涨跌提醒
- [ ]  多平台价差套利提醒
- [ ]  Web 仪表盘查看价格曲线
- [ ]  支持通过 Notion 数据库动态管理监控清单

---

## 9. 风险与注意事项

| **风险** | **影响** | **应对措施** |
| --- | --- | --- |
| API 频率限制 | 请求被拒绝，无法获取数据 | 严格控制调用频率 + 本地缓存 + 请求间随机延迟 |
| API Key 泄露 | 账号安全风险 | 使用 .env 管理，.gitignore 排除 |
| SteamDT 服务不可用 | 数据断流 | 重试机制 + 错误通知 + 本地缓存兜底 |
| 价格数据异常 | 误触发告警 | 加入合理性校验（价格 > 0、波动 < 50% 等） |
| 长期运行稳定性 | 进程崩溃、内存泄漏 | 异常捕获 + 日志 + 可选 systemd/pm2 守护 |