# CS2 饰品价格监控 Web 仪表盘 (cs-monitor)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3-4FC08D.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个轻量级、可自托管的 **CS2 饰品价格监控平台**，基于 [SteamDT](https://doc.steamdt.com/) 开放平台 API，支持 **CLI 后台监控** 和 **Web 仪表盘** 双模式。用户可通过浏览器完成所有监控操作：查看价格、管理清单、分析趋势、接收告警，**无需修改任何配置文件**。

> 本项目采用 AI Agent 驱动开发，核心开发规范定义在 [`CLAUDE.md`](CLAUDE.md) 中。你可以在此基础上自由改造和扩展。

---

## 核心功能

### 1. Web 仪表盘（v2.0 新增）
打开浏览器即可管理所有监控操作：
- **Dashboard 首页**：系统概览、统计卡片、价格概览表、最近告警
- **监控清单管理**：Web UI 添加/编辑/删除/启停监控饰品
- **饰品详情页**：各平台价格对比 + 价格走势折线图
- **极致追踪管理**：Web UI 配置追踪项、启停控制
- **告警历史**：可筛选/搜索的告警记录列表
- **系统设置**：通知渠道配置、测试通知

### 2. 普通监控模式
批量巡检多个饰品，默认每 **30 分钟**自动采集一次价格，对比 **7 天均价**检测波动：
- 涨幅 ≥ 阈值% → 触发 `price_surge` 涨价告警
- 跌幅 ≤ -阈值% → 触发 `price_drop` 跌价告警
- 同一饰品同一方向 **4 小时内只告警 1 次**（冷却机制）

### 3. 极致追踪模式
单品高频狙击，自定义秒级轮询，追踪指定平台的**价格**和**在售数量**变动：
- 支持 `any`（任何变动通知）和 `percent`（超百分比通知）双模式
- 429 限流时**自动降频**（间隔翻倍，最大 1 小时），连续成功 10 次后逐步恢复
- 支持**免打扰时段** (`quiet_hours`) 和**自定义冷却期**
- 价格 & 数量同时变动时**合并为一条通知**

### 4. 多渠道通知
- 企业微信机器人 Webhook（P0 已完整实现）
- Telegram Bot（P1）
- Server 酱（P1）

### 5. SQLite 持久化
零配置本地数据库，自动记录价格历史和告警日志。v2.0 新增监控清单和极致追踪配置持久化到数据库。

---

## 项目架构

```
cs-monitor/
├── main.py                 # 主程序入口（调度器 + FastAPI Web 服务）
├── config.py               # 配置类（dataclass，默认值兜底）
├── requirements.txt        # Python 依赖
├── .env.example            # 环境变量模板
├── .gitignore
├── CLAUDE.md               # AI Agent 开发工作流规范
├── architecture.md         # 架构设计文档
├── PRD.md                  # 产品需求文档
├── task.json               # 开发任务清单
├── progress.txt            # 开发进度日志
├── api/
│   └── steamdt.py          # SteamDT API 封装（重试、延迟、异常处理）
├── core/
│   ├── monitor.py          # 普通监控：价格采集
│   ├── analyzer.py         # 波动分析 + 告警检测
│   ├── scheduler.py        # APScheduler 定时任务管理
│   └── extreme_tracker.py  # 极致追踪：高频单品狙击
├── web/                    # 🆕 FastAPI Web 层
│   ├── app.py              # FastAPI 应用入口
│   ├── schemas.py          # Pydantic 模型
│   ├── ws_manager.py       # WebSocket 管理
│   └── routers/            # RESTful API 路由
├── frontend/               # 🆕 Vue 3 前端
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── views/          # 页面（Dashboard/Watchlist/Alerts/...）
│       ├── components/     # 组件（StatCard/PriceTable/PriceChart/...）
│       ├── stores/         # Pinia 状态管理
│       └── api/            # axios 封装
├── notify/
│   ├── base.py             # 通知渠道抽象基类
│   ├── manager.py          # 通知管理器（格式化 + 路由）
│   ├── wecom.py            # 企业微信机器人
│   ├── telegram.py         # Telegram Bot
│   └── serverchan.py       # Server 酱
├── storage/
│   ├── models.py           # 数据库表结构定义
│   └── database.py         # SQLite 连接与 CRUD 封装
├── utils/
│   └── logger.py           # loguru 日志配置
├── data/
│   └── logs/               # 日志文件输出目录
└── tests/
    ├── test_api.py
    ├── test_monitor.py
    ├── test_analyzer.py
    ├── test_extreme_tracker.py
    ├── test_notify.py
    ├── test_storage.py
    └── test_web_api.py     # 🆕 Web API 测试
```

---

## 快速开始

### 1. 环境准备

需要 **Python 3.12+** 和 **Node.js 18+**（用于前端开发）。

```bash
cd cs-monitor
./init.sh
```

`init.sh` 会创建 `.venv` 虚拟环境、安装 Python 依赖，并自动安装前端 npm 依赖。

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写以下内容：
# - STEAMDT_API_KEY（从 https://doc.steamdt.com/ 获取）
# - 至少一种通知渠道（WECOM_WEBHOOK_URL / TELEGRAM_BOT_TOKEN / SERVERCHAN_SENDKEY）
```

### 3. 运行主程序

```bash
# 先构建前端（仅需执行一次，或前端代码更新后重新构建）
cd frontend && npm run build && cd ..

# 启动主程序
python main.py
```

首次启动会立即执行一次价格采集，随后：
- **后台调度器**按设定间隔运行 CLI 监控
- **FastAPI Web 服务**在 `http://localhost:8080` 提供 Web 仪表盘

构建完成后，直接在浏览器打开 **`http://localhost:8080`** 即可访问 Web 仪表盘，无需额外启动前端服务器。

按 `Ctrl+C` 可优雅退出。

### 4. 开发模式（前端热更新）

如需修改前端代码并实时预览：

```bash
# 终端 1：启动后端
python main.py

# 终端 2：启动前端开发服务器
cd frontend
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`，通过 Vite 代理访问后端 API。开发完成后记得运行 `npm run build` 重新构建，使生产环境生效。

### 5. 运行测试

```bash
# Python 后端测试
python -m pytest tests/ -v

# 前端构建检查
cd frontend && npm run build
```

---

## 配置说明

### 监控清单

v2.0 后监控清单已迁移到数据库，可通过 **Web 仪表盘** 或 **API** 管理，无需修改配置文件。

如需查看/修改默认值，参考 `config.py` 中的 `watchlist`：

```python
watchlist = [
    {"name": "AK-47 | Redline (Field-Tested)", "threshold": 5.0},
    {"name": "AWP | Asiimov (Field-Tested)", "threshold": 5.0},
]
```

首次启动时，如果数据库中的 watchlist 表为空，系统会自动从 `config.py` 导入默认值。

### 极致追踪

同样已迁移到数据库。参考 `config.py` 中的 `extreme_track_list` 查看默认配置格式。

---

## 改造指引

如果你想在此基础上继续开发，建议从以下几个方面入手：

1. **更多通知渠道**：钉钉、Discord、Bark 等
2. **套利价差提醒**：对比同一饰品在不同平台的价格差（Phase 2 已规划）
3. **K 线趋势分析**：接入 `get_item_kline()` 做更复杂的技术分析（Phase 2 已规划）
4. **Docker 部署**：添加 Dockerfile 和 docker-compose.yml（Phase 3 已规划）
5. **多用户支持**：扩展 JWT 认证为多用户模式
6. **数据归档**：自动归档 90 天以上的历史价格数据

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端语言 | Python 3.12+ | 类型提示、dataclass |
| Web 框架 | FastAPI | 异步高性能、OpenAPI 文档 |
| HTTP 客户端 | httpx | 同步请求 + 重试机制 |
| 调度 | APScheduler | BackgroundScheduler 定时任务 |
| 数据库 | SQLite (WAL) | 零配置，支持并发读写 |
| 前端框架 | Vue 3 + Vite + TypeScript | 组件化、响应式 |
| UI 组件库 | Naive UI | 中文文档完善 |
| 图表库 | ECharts 5 | K线/折线/柱状图全覆盖 |
| 状态管理 | Pinia | 轻量替代 Vuex |
| CSS | UnoCSS | 原子化 CSS |
| 日志 | loguru | 彩色控制台 + 文件日志 |
| 配置 | python-dotenv | `.env` 环境变量管理 |
| 测试 | pytest | 36+ 个单元测试 |

---

## 开发规范

本项目由 AI Agent 按 `CLAUDE.md` 中的规范逐步开发完成。如果你想用同样的方式继续迭代：

1. 阅读 `CLAUDE.md` 了解工作流
2. 查看 `task.json` 了解已完成的任务（v1.0 共 10 个，v2.0 新增 12 个）
3. 在 `task.json` 中按顺序完成下一个 `passes: false` 的任务
4. 遵循"**一个 task 一个 commit**"的原则

---

## License

MIT License - 可自由修改和商用。
