# CS2 饰品价格波动监控系统 (cs-monitor)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个轻量级、可自托管的 CS2 饰品价格监控工具，基于 [SteamDT](https://doc.steamdt.com/) 开放平台 API，支持**普通批量监控**和**极致追踪**两种模式。

> 本项目采用 AI Agent 驱动开发，核心开发规范定义在 [`CLAUDE.md`](CLAUDE.md) 中。你可以在此基础上自由改造和扩展。

---

## 核心功能

### 1. 普通监控模式
批量巡检多个饰品，默认每 **30 分钟**自动采集一次价格，对比 **7 天均价**检测波动：
- 涨幅 ≥ 阈值% → 触发 `price_surge` 涨价告警
- 跌幅 ≤ -阈值% → 触发 `price_drop` 跌价告警
- 同一饰品同一方向 **4 小时内只告警 1 次**（冷却机制）

### 2. 极致追踪模式
单品高频狙击，自定义秒级轮询，追踪指定平台的**价格**和**在售数量**变动：
- 支持 `any`（任何变动通知）和 `percent`（超百分比通知）双模式
- 429 限流时**自动降频**（间隔翻倍，最大 1 小时），连续成功 10 次后逐步恢复
- 支持**免打扰时段** (`quiet_hours`) 和**自定义冷却期**
- 价格 & 数量同时变动时**合并为一条通知**

### 3. 多渠道通知
- 企业微信机器人 Webhook（P0 已完整实现）
- Telegram Bot（P1）
- Server 酱（P1）

### 4. SQLite 持久化
零配置本地数据库，自动记录价格历史和告警日志。

---

## 项目架构

```
cs-monitor/
├── main.py                 # 主程序入口
├── config.py               # 配置类（dataclass）
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
    └── test_storage.py
```

---

## 快速开始

### 1. 环境准备

需要 **Python 3.12+**。

```bash
cd cs-monitor
./init.sh
```

`init.sh` 会创建 `.venv` 虚拟环境并安装依赖。

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写以下内容：
# - STEAMDT_API_KEY（从 https://doc.steamdt.com/ 获取）
# - 至少一种通知渠道（WECOM_WEBHOOK_URL / TELEGRAM_BOT_TOKEN / SERVERCHAN_SENDKEY）
```

### 3. 运行主程序

```bash
python main.py
```

首次启动会立即执行一次价格采集，随后调度器按设定间隔运行。

按 `Ctrl+C` 可优雅退出。

### 4. 运行测试

```bash
python -m pytest tests/ -v
```

---

## 配置说明

### 监控清单 (`watchlist`)

在 `config.py` 中配置：

```python
watchlist = [
    {"name": "AK-47 | Redline (Field-Tested)", "threshold": 5.0},
    {"name": "AWP | Asiimov (Field-Tested)", "threshold": 5.0},
]
```

### 极致追踪 (`extreme_track_list`)

```python
extreme_track_list = [
    {
        "market_hash_name": "AK-47 | Redline (Field-Tested)",
        "platform": "BUFF",
        "interval_seconds": 60,
        "price_track_enabled": True,
        "price_change_mode": "any",          # "any" 或 "percent"
        "price_threshold_percent": 0.0,
        "quantity_track_enabled": True,
        "quantity_change_mode": "any",
        "quantity_threshold_percent": 0.0,
        "alert_cooldown_seconds": 0,
        "quiet_hours_start": "02:00",
        "quiet_hours_end": "08:00",
    },
]
```

---

## 改造指引

如果你想在此基础上继续开发，建议从以下几个方面入手：

1. **Web 仪表盘**：基于 Flask/FastAPI + 前端框架，可视化价格曲线
2. **监控清单持久化**：将 `watchlist` 和 `extreme_track_list` 从 `config.py` 迁移到数据库或 Web UI
3. **更多通知渠道**：钉钉、Discord、Bark 等
4. **套利价差提醒**：对比同一饰品在不同平台的价格差
5. **K 线趋势分析**：接入 `get_item_kline()` 做更复杂的技术分析
6. **Docker 部署**：添加 Dockerfile 和 docker-compose.yml

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.12+ | 类型提示、dataclass |
| HTTP | httpx | 同步请求 + 重试机制 |
| 调度 | APScheduler | BackgroundScheduler 定时任务 |
| 数据库 | SQLite | 零配置，自动建表 |
| 日志 | loguru | 彩色控制台 + 文件日志 |
| 配置 | python-dotenv | `.env` 环境变量管理 |
| 测试 | pytest | 36 个单元测试全覆盖 |

---

## 开发规范

本项目由 AI Agent 按 `CLAUDE.md` 中的规范逐步开发完成。如果你想用同样的方式继续迭代：

1. 阅读 `CLAUDE.md` 了解工作流
2. 查看 `task.json` 了解已完成的任务
3. 在 `task.json` 中追加新任务，或在现有代码上直接修改
4. 遵循"**一个 task 一个 commit**"的原则

---

## License

MIT License - 可自由修改和商用。
