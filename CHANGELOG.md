# Changelog

本文件遵循 [Keep a Changelog](https://keepachangelog.com/) 规范，记录所有用户可感知的项目变更。

---

## [3.0.0] — 2026-04-28

大型 UI 重构，项目从"Trading Terminal Pro"全面升级为"极客终端"视觉风格，对齐 [Gemini 设计的 React 参考项目](https://github.com/Pgooone/cs-)。

### Added
- **饰品图片功能**：通过 Steam 社区市场 API 自动获取饰品图标，前端新增 `SteamItemImage` 组件展示，支持加载失败时 emoji fallback
- **数据分析页面 (StatsView)**：全新占位页，扫描线动画和 LineChart 图标，为后续市场趋势分析功能预留入口
- `GET /items/{name}/icon` API 端点：查询单个饰品图标
- `POST /items/icons/sync` API 端点：批量同步所有监控项饰品图标
- 数据库 `items` 表新增 `icon_url` 列
- 支持 `TELEGRAM_PROXY` 环境变量代理访问 Steam 社区 API

### Changed
- **设计系统全面重写**：配色从"深空蓝 + 电光橙"切换为"极客黑 + Indigo 品牌紫 (#6366f1)"；背景 #050505，卡片 #0f0f12，边框 #1f1f23
- **玻璃拟态系统**：新增 `.glass-card`、`.btn-primary`、`.btn-outline`、`.nav-item`、`.nav-item-active` 等 CSS 类，全局 shimmer 扫光动画
- **Dashboard 页面重构**：改为"终端概览"布局，大卡片 + 柱状图动画 + 核心功能快捷按钮 + API 生命周期状态
- **Watchlist 页面重构**：纯卡片视图（去除表格/双视图切换），glass-card + 悬停动画 + Sparkline 迷你走势 + 平台价格标签
- **ExtremeTrack 页面重构**：雷达强度进度条 + shimmer 动画 + 内存快照实时数据 + 品牌色光效
- **Alerts 页面重构**：极客表格风格，红涨/绿跌/琥珀量类型标签；去除 Tab 切换、筛选器、柱状图、详情抽屉
- **Settings 页面重构**：三段式纵向布局（去除左侧子导航），紫色圆形开关滑块，通知渠道状态灯
- **Sidebar 重构**：响应式宽度（小屏仅图标 w-20，大屏展开 w-64），Logo + lucide-vue-next 图标 + API 状态灯
- **TopBar 重构**：上下文感知，根据当前路由动态切换标题/搜索框/操作按钮
- **AppLayout 重构**：背景装饰光晕效果 + 页面切换动画（300ms 淡入 + 上移）
- **图标库迁移**：`@vicons/ionicons5` → `lucide-vue-next`，与 React 参考项目图标系统保持一致
- **深色模式增强**：完整 light / dark 浅色主题适配

### Fixed
- ItemDetail 页面 trends 请求独立容错，避免一个趋势 API 失败导致整页崩溃
- Alerts 查询 SQL 列名歧义修复：LEFT JOIN 后 `market_hash_name` 未限定表别名导致 500 错误

### Removed
- Naive UI 的 `NMenu`、`NLayoutSider` 等布局组件，改为纯 HTML + CSS 实现
- Watchlist 表格视图（双视图切换入口）
- Alerts 页面的 Tab 切换、筛选器、柱状图、详情抽屉
- Settings 页面左侧子导航
- `@vicons/ionicons5` 图标库

---

## [2.1.0] — 2026-04-26

前端视觉升级与功能完善。

### Added
- **Trading Terminal Pro 设计系统**：深空蓝 + 电光橙配色（参考 BUFF.163.com 专业交易平台风格），CSS 变量驱动的主题切换
- **Watchlist BUFF 风格卡片视图**：饰品卡片布局、Sparkline 迷你走势图、平台价格对比
- **Dashboard 饰品搜索框**：支持在首页直接搜索和查看价格
- **Telegram Bot 通知渠道**：支持通过 HTTP 代理访问（中国大陆可用）
- **通知测试功能**：设置页可直接测试各渠道通知推送
- **创建/刷新端点**：`POST /refresh` API，前端刷新按钮，支持手动触发数据采集

### Changed
- 后端移除 JWT 认证，API 全部对外开放（无需登录即可使用 Web 仪表盘）
- WebSocket 实时推送改为轮询机制（解决 403 问题）
- 前端展示优先使用中文名称（`display_name`）
- 配置项 `WECOM_WEBHOOK_URL` 拆分为 `WECOM_WEBHOOK_MONITOR_URL` 和 `WECOM_WEBHOOK_EXTREME_URL`

### Fixed
- Dashboard 今日采集次数显示为 0
- Watchlist 重复行、告警零价、Settings 500 三个 P1 级 Bug
- 搜索结果排序优化（武器优先于贴纸）+ 无分隔符匹配（`ak47` → AK-47）
- 极致追踪平台名称大小写不敏感比较

---

## [2.0.0] — 2026-04-24

Web 仪表盘从零到一，项目从纯 CLI 工具进化为完整的 Web 应用。

### Added
- **FastAPI Web 服务**：RESTful API（价格、监控清单、告警、极致追踪、K 线、趋势、搜索）
- **Vue 3 前端 SPA**：Vite + TypeScript + Naive UI + ECharts
- **Dashboard 首页**：KPI 统计卡片 + 组合价值曲线 + 实时告警流 + 热度榜 + 采集状态
- **监控清单管理页**：表格式管理，支持添加/删除/编辑监控项
- **饰品详情页**：ECharts K 线图（OHLC + MA 均线 + 成交量），平台多维度对比
- **极致追踪管理页**：卡片网格、极值进度条、运行状态徽章、实时面板
- **告警历史页**：卡片化展示、日期分组、详情抽屉
- **系统设置页**：通知配置、数据目录管理、主题切换
- **WebSocket 实时推送**：告警和极致追踪数据实时推送
- **全量饰品搜索**：本地 39,000+ 饰品数据库，中英文模糊匹配
- **Docker 一键部署**：`docker-compose up -d`，内置健康检查
- **数据归档功能**：历史价格自动归档清理
- **JWT 用户认证**：登录保护
- SQLite WAL 模式：支持并发读写

### Changed
- 监控清单从 `config.py` 迁移到 SQLite 数据库，可通过 API 动态管理
- 极致追踪配置持久化到数据库

---

## [1.0.0] — 2026-04-22

首个正式版本，CLI 后台监控核心功能。

### Added
- **普通监控模式**：批量巡检多个饰品，每 30 分钟采集价格，7 天均价波动检测
- **极致追踪模式**：单品高频狙击，秒级轮询，429 自动降频，免打扰时段
- **企业微信机器人通知**：涨价/跌价告警，同一饰品同一方向 4 小时冷却
- **SQLite 持久化**：自动记录价格历史和告警日志
- SteamDT API 封装（重试、延迟、异常处理）
- 单元测试覆盖（共 86+ 个用例）
- 优雅退出机制（SIGINT/SIGTERM）
