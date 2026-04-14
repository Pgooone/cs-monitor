# SteamDT API 开发参考

## 官方文档入口

- **LLMs 优化文档（推荐）**: https://doc.steamdt.com/llms.txt
- **完整 API 文档**: https://doc.steamdt.com/

> **开发提示**：如果在实现 API 封装时遇到接口定义不清、参数不确定、响应格式不明等问题，**优先查阅 https://doc.steamdt.com/llms.txt**，该文档专为 AI 阅读优化，包含接口列表和关键限制。

---

## 核心接口列表（本项目需要）

### 1. 获取 Steam 饰品基础信息
- **限制**：**每天只能调用 1 次**，必须本地缓存返回数据到 SQLite
- **用途**：初始化时建立本地饰品数据库（`items` 表）
- **提示**：首次运行或数据库为空时调用，之后从本地读取

### 2. 通过 marketHashName 批量查询饰品价格
- **用途**：普通监控模式的核心接口，定时批量查价
- **输入**：多个 `marketHashName`
- **输出**：各平台当前价格

### 3. 通过 MarketHashName 查询所有平台近 7 天均价
- **用途**：获取波动判断的基准价格
- **输入**：单个 `marketHashName`
- **输出**：各平台 7 天均价

### 4. 查询 Steam 饰品 K 线数据
- **用途**：趋势分析（P2 进阶功能，可选实现）
- **输入**：`marketHashName` + 时间范围等参数

---

## 通用限制与注意事项

1. **频率限制**
   - 基础信息接口：每日 1 次
   - 其他接口：请参考 [接口权限列表](https://doc.steamdt.com/)
   - 建议在请求间加入 **1-3 秒随机延迟**，避免触发风控

2. **认证方式**
   - 所有接口调用需携带 **API Key**
   - 通过 `.env` 文件的 `STEAMDT_API_KEY` 管理

3. **数据缓存策略**
   - 饰品基础信息 → **永久缓存**（每日更新）
   - 价格数据 → **每次采集写入 SQLite**
   - 7 天均价 → **按需查询**（可作为基准价缓存）

4. **异常处理建议**
   - API 调用失败时重试 3 次，间隔 10 秒
   - 连续失败 5 次发送错误通知
   - 遇到 `429 Too Many Requests` 时，启用自动降频（主要在极致追踪模式）

---

## 数据类型速查（来自 llms.txt）

- `PlatformPriceVO` — 平台价格信息
- `BatchPlatformPriceVO` — 批量价格查询结果
- `PlatformAveragePriceVO` / `AveragePriceVO` — 均价信息
- `ItemKlineAO` — K 线数据请求/响应
- `WebApiRes*` — 统一的 API 响应包装类型

---

## 开发时遇到问题？

**第一步**：打开 https://doc.steamdt.com/llms.txt 让 Claude 阅读。

**第二步**：如果 llms.txt 信息不足，再查阅具体接口的 markdown 文档。

**第三步**：如果接口行为与文档不符，在 `progress.txt` 中记录问题，并在实现代码中加入防御性处理（如默认值、空值检查、try-except 等）。
