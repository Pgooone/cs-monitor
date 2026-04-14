# CS2 饰品价格波动监控系统 (cs-monitor)

一个轻量级、可自托管的 CS2 饰品价格监控工具，基于 SteamDT 开放平台 API，支持普通批量监控和极致追踪两种模式。

## 核心功能

- **普通监控模式**：批量巡检多个饰品，每 30 分钟自动采集价格，对比 7 天均价检测波动
- **极致追踪模式**：单品高频狙击，自定义秒级轮询，追踪指定平台的价格和在售数量变动
- **多渠道通知**：支持企业微信机器人、Telegram Bot、Server 酱
- **SQLite 持久化**：零配置本地数据库，记录价格历史和告警日志

## 快速开始

### 1. 环境准备

需要 Python 3.12+。

```bash
# 克隆项目后进入目录
cd cs-monitor

# 运行初始化脚本
./init.sh
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填写你的 SteamDT API Key 和通知渠道配置
```

### 3. 运行

```bash
python main.py
```

### 4. 运行测试

```bash
python -m pytest tests/
```

## 开发说明

本项目采用 AI Agent 驱动的开发方式，核心开发规范定义在 `CLAUDE.md` 中。
