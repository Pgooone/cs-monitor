# CS2 Monitor — Bug 审查与修复方案 20260426

<aside>
📌

**审查时间**：2026年4月26日
**审查人**：Claude Code（浏览器实测 + 数据库分析 + 代码审查）
**审查范围**：`cs-monitor/` 全部前端页面（浏览器实测）+ 后端 API + SQLite 数据库
**前置文档**：[CS2 Monitor — Bug 审查与修复方案 20260421](CS2%20Monitor%20%E2%80%94%20Bug%20%E5%AE%A1%E6%9F%A5%E4%B8%8E%E4%BF%AE%E5%A4%8D%E6%96%B9%E6%A1%88%2020260421.md)（Bug 编号 B-01 ~ B-35）

</aside>

---

## 审查方法说明

本次审查采用 **浏览器实测 + 数据库直查 + 代码走读** 三结合方式：

1. **浏览器实测**：通过 Chrome DevTools MCP 访问 `http://localhost:8080`，逐页截图、抓取 DOM 快照和网络请求
2. **数据库直查**：直接查询 `data/prices.db` 中的 items / price_records / alert_logs / watchlist 表，核实数据一致性
3. **代码走读**：对照用户反馈和浏览器观察，定位后端 API 和前端组件的实现缺陷

---

## 审查结论总览

| 优先级 | 新发现数 | 说明 |
|--------|---------|------|
| **P0** 功能性故障 | **2** | 搜索功能完全不工作、告警数据异常 |
| **P1** 显著体验问题 | **3** | WebSocket 连接失败、监控清单数据不一致、告警流标题渲染异常 |
| **P2** 数据 / 可维护 | **2** | 采集停滞无自动恢复、items 表缺少全量饰品缓存 |
| **合计** | **7** | — |

---

## P0 — 功能性故障（2项）

### B-36 饰品搜索功能完全不工作 — 输入关键词无任何匹配结果

- **文件**：`web/routers/prices.py:16-54` + `frontend/src/components/business/ItemSearch.vue:79-101`
- **复现步骤**：
  1. 打开 Dashboard 首页
  2. 在搜索框输入 `ak47`
  3. 点击搜索或按回车
- **实际结果**：提示"未找到 'ak47' 的价格数据，请检查饰品名称是否正确"
- **根因分析**：

搜索端点 `GET /api/prices/search?q=ak47` 的实现直接将用户输入作为 `marketHashName` 传给 SteamDT 批量查询接口：

```python
# web/routers/prices.py:35
response = client.get_items_batch([q.strip()])  # 把 "ak47" 当精确名称传给 API
```

而 SteamDT `get_items_batch` 接口要求传入**精确的** `marketHashName`（如 `"AK-47 | Redline (Field-Tested)"`），不支持模糊搜索。

根据 SteamDT API 文档（`cs监控需求整理.md`），平台共 9 个接口，**没有任何搜索/建议接口**。唯一能获取全量饰品列表的是 `GET /open/cs2/v1/base`（每天限调 1 次），返回所有饰品的 `name` 和 `marketHashName`。

- **影响**：用户无法通过关键词搜索饰品，必须知道完整的 `marketHashName` 才能使用，搜索功能形同虚设。
- **修复方案**：

1. 启动时（或每天首次）调用 `get_all_items()` 获取全量饰品数据，存入本地 `items` 表（含 `name` 和 `market_hash_name`）
2. 新增 `GET /api/items/search?q=xxx` 端点，在本地 SQLite 做 `LIKE '%xxx%'` 模糊匹配，返回候选列表（限 20 条）
3. 前端 `ItemSearch.vue` 改为输入时防抖调用搜索 API，展示候选下拉列表，用户选择后再查实时价格
4. `items` 表增加 `name` 字段（中文名/英文名），支持中英文搜索

---

### B-37 历史告警全部为 -100%，current_price 为 0 — 告警数据异常污染 Dashboard

- **文件**：`core/analyzer.py:100-105`（过滤逻辑）+ `core/monitor.py:72-79`（数据写入）
- **现象**：

数据库 `alert_logs` 表共 19 条告警，**全部**为 `current_price: 0.0, change_percent: -100.0%`：

| 时间 | 饰品 | current_price | baseline_price | change_percent |
|------|------|--------------|----------------|----------------|
| 04-24 06:48 | AWP Asiimov | 0.0 | 911.83 | -100.0% |
| 04-24 06:47 | AK-47 Redline | 0.0 | 244.27 | -100.0% |
| 04-23 13:48 | AWP Asiimov | 0.0 | 1128.38 | -100.0% |
| ... | ... | 0.0 | ... | -100.0% |

- **根因分析**：

当前代码 `analyzer.py:101` 已有零价过滤：`valid_prices = [r["price"] for r in platform_records if r["price"] > 0]`，理论上不会产生 `current_price=0` 的告警。

这些历史告警（04-22 ~ 04-24）说明在早期版本中，该过滤逻辑尚未实现，或 API 当时对所有平台返回了 0 价格而代码未做防御。

- **影响**：
  - Dashboard 告警流全部显示 `-100.00%`，视觉冲击大且无参考价值
  - 24h 波动热度榜无法正常计算（依赖告警数据）
  - 告警统计图表被 -100% 数据主导，无法反映真实波动

- **修复方案**：
  1. 清理历史脏数据：`DELETE FROM alert_logs WHERE current_price = 0`
  2. 在 `monitor.py` 的 `collect_prices` 中增加防御：如果 API 返回的所有平台价格均为 0，记录警告日志但不传给 analyzer
  3. 在 `analyzer.py` 的 `analyze` 入口增加断言：`assert current_price > 0`，防止 0 价格写入告警

---

## P1 — 显著体验问题（3项）

### B-38 WebSocket 连接始终处于"连接中..."状态，实时推送不工作

- **文件**：`frontend/src/stores/websocket.ts` + `web/app.py:75-107`
- **现象**：Dashboard 左下角 WS 状态 pill 和告警流旁的状态指示器始终显示"连接中..."（黄色），从未变为"已连接"（绿色）
- **根因分析**：

WebSocket 连接使用 `?token=xxx` 认证。可能原因：
1. 前端 WS 连接时 token 未正确附加到 URL
2. JWT token 过期后 WS 重连未刷新 token
3. 浏览器 console 中 WS 错误被静默 catch

需要检查 `stores/websocket.ts` 中建连逻辑和 `web/app.py` 中 `_ws_auth` 函数的 token 校验。

- **影响**：告警实时推送和极致追踪实时数据流均不工作，用户只能手动刷新页面查看最新数据。
- **修复**：
  1. 检查 WS 建连 URL 是否正确携带 `?token=xxx`
  2. WS 断开后重连时重新从 localStorage 获取最新 token
  3. 在 `_ws_auth` 中增加详细日志，记录认证失败原因

---

### B-39 监控清单页面显示 3 行但数据库只有 1 条记录 — 数据来源不一致

- **文件**：`web/routers/watchlist.py` + `frontend/src/views/Watchlist.vue`
- **现象**：

| 数据源 | 记录 |
|--------|------|
| `watchlist` 表 | 仅 1 条：`AK-47 | Bloodsport (Field-Tested)` |
| Watchlist 页面 | 显示 3 行：AK-47 Redline、AK-47 Bloodsport、AWP Asiimov |

- **根因分析**：

Watchlist 页面可能从 `/api/watchlist` 获取数据时，后端查询逻辑 JOIN 了 `items` 表或 `price_records` 表，导致已从 watchlist 删除但 items 表中仍存在的饰品也被返回。

或者前端 Pinia store `watchlist.ts` 中有额外的数据合并逻辑，将 `items` 表的数据混入了 watchlist 列表。

- **影响**：用户看到的监控清单与实际 DB 数据不一致，删除操作可能无效。
- **修复**：检查 `GET /api/watchlist` 的 SQL 查询，确保只返回 `watchlist` 表中 `enabled=1` 的记录，不 JOIN items 表。

---

### B-40 Dashboard 告警流标题渲染异常 — 显示 "今日告警流 1 1 1 9 9 9"

- **文件**：`frontend/src/views/Dashboard.vue` + `frontend/src/components/business/AlertFeed.vue`
- **现象**：DOM 快照中告警流标题为 `heading "今日告警流 1 1 1 9 9 9"`，数字部分重复且含义不明
- **根因分析**：

可能是 NBadge 组件的数量与标题文本拼接时出现了重复渲染。告警流卡片的 `#header` 插槽中，NBadge 的 value 绑定可能在数据更新时产生了多次渲染。

- **影响**：视觉混乱，用户无法理解数字含义。
- **修复**：检查 Dashboard.vue 中告警流卡片的 header 插槽实现，确保 NBadge 只渲染一次且数量正确。

---

## P2 — 数据 / 可维护性（2项）

### B-41 采集停滞后无自动恢复机制 — 最后更新停留在 4/25 17:25

- **文件**：`core/scheduler.py` + `core/monitor.py`
- **现象**：Dashboard 显示"最后更新 4/25 17:25"，但当前时间已是 4/26。采集已停滞超过 24 小时，调度器未自动恢复。
- **根因分析**：

APScheduler 的 `BackgroundScheduler` 在后台线程运行。如果某次采集因未捕获的异常导致线程崩溃，调度器会静默停止，不会自动重启。

当前 `_run_monitor()` 方法虽然有 try/except，但如果异常发生在 APScheduler 内部调度逻辑中（而非用户代码），线程可能直接退出。

- **影响**：采集停滞意味着不会产生新的价格数据和告警，监控功能完全失效，但用户可能不知道。
- **修复**：
  1. 在 `main.py` 中添加 watchdog 线程，定期检查调度器状态（`scheduler.running`），如果停止则自动重启
  2. Dashboard 采集状态区增加"停滞警告"：如果最后采集时间超过 2 个采集间隔，显示红色警告
  3. 增加心跳机制：调度器每 5 分钟写入 `system_config` 表的 `last_heartbeat` 字段，前端可检测

---

### B-42 items 表仅有 3 条记录 — 缺少全量饰品缓存，搜索和自动补全无法实现

- **文件**：`storage/database.py` + `core/monitor.py`
- **现象**：

`items` 表只有 3 条记录，均为被监控饰品（AK-47 Redline、AWP Asiimov、AK-47 Bloodsport），是 `monitor.py` 在采集时通过 `insert_item()` 写入的。

但 SteamDT `get_all_items()` 接口可返回**全量**饰品数据（数千条），目前从未被调用。

- **影响**：没有全量饰品数据，B-36 的搜索功能无法实现，也无法提供饰品名称自动补全。
- **修复**：
  1. 在 `main.py` 启动时检查 `items` 表是否为空或上次同步时间超过 24 小时
  2. 如果需要同步，调用 `get_all_items()` 并批量写入 `items` 表
  3. `items` 表增加 `name` 字段（饰品中文名）和 `last_synced_at` 字段
  4. 在 `scheduler.py` 中添加每日凌晨 4 点的 `get_all_items()` 同步任务（每天限 1 次）

---

## 统计摘要

| **优先级** | **数量** | **Bug 编号** |
|-----------|---------|-------------|
| P0 功能性故障 | 2 | B-36, B-37 |
| P1 显著体验 | 3 | B-38, B-39, B-40 |
| P2 数据/可维护 | 2 | B-41, B-42 |
| **总计** | **7** | B-36 ~ B-42 |

---

## 修复路线图

### 阶段一：立刻修复（影响核心功能）

| 顺序 | Bug | 文件 | 预估时间 | 说明 |
|------|-----|------|---------|------|
| 1 | **B-42** items 全量缓存 | `main.py`, `storage/database.py` | 30 分钟 | B-36 的前置依赖 |
| 2 | **B-36** 搜索功能重写 | `web/routers/prices.py`, `frontend/src/components/business/ItemSearch.vue` | 60 分钟 | 依赖 B-42 的全量数据 |
| 3 | **B-37** 清理脏告警数据 | 数据库清理 + `core/analyzer.py` 防御 | 15 分钟 | 一条 SQL + 代码加固 |

### 阶段二：v2.1 范围内修复

| Bug | 说明 |
|-----|------|
| **B-38** WebSocket 连接修复 | 检查 token 传递和重连逻辑 |
| **B-39** Watchlist 数据源一致性 | 检查后端 SQL 查询 |
| **B-40** 告警流标题渲染修复 | 检查 Vue 组件绑定 |

### 阶段三：后续迭代

| Bug | 说明 |
|-----|------|
| **B-41** 采集 watchdog | 增加心跳和自动恢复机制 |

---

## 附录：数据库现状快照（2026-04-26 审查时）

```
items 表：3 条记录
  - AK-47 | Redline (Field-Tested)
  - AWP | Asiimov (Field-Tested)
  - AK-47 | Bloodsport (Field-Tested)

watchlist 表：1 条记录（enabled=1）
  - AK-47 | Bloodsport (Field-Tested)

price_records 表：1044 条记录
  - 每个饰品 8 个平台，部分平台价格为 0（SKINPORT、WAXPEER、DMARKET、CSMONEY）

alert_logs 表：19 条记录
  - 全部为 current_price=0, change_percent=-100%（历史脏数据）
```
