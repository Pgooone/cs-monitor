# CS2 Monitor — Agent 开发规范

## 项目概述

CS2 饰品价格监控平台 — Python/FastAPI 后端 + Vue 3 前端。

## 编码规范

### Python
- Python 3.12+，使用 type hints
- HTTP: `httpx`，日志: `loguru`，配置: `dataclass` + `python-dotenv`
- API 模型: Pydantic v2
- 函数控制在 50 行内

### TypeScript/Vue
- Vue 3 Composition API + `<script setup>`
- 状态管理: Pinia，UI: Naive UI，CSS: UnoCSS
- 图表: ECharts（按需引入）
- 所有颜色/间距/圆角来自 `styles/tokens.ts`

## 常用命令

```bash
./init.sh                          # 初始化环境
python main.py                     # 启动服务（:8080）
python -m pytest tests/            # 运行测试
cd frontend && npm run build       # 构建前端
```

## 关键规则

1. 测试外部 API 时使用 mock
2. SQLite 启用 WAL 模式
3. 前端同时验证 light/dark 主题
4. `npm run build` vendor chunk gzip < 200KB
