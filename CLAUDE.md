# CS2 饰品价格波动监控系统 — Agent 开发工作流

## Project Context

一个基于 Python 3.12+ / FastAPI / Vue 3 的 CS2 饰品价格监控平台，使用 SteamDT API、APScheduler、SQLite 和 loguru。支持 CLI 后台监控 + Web 仪表盘双模式。

> Note: 详细的产品需求定义在 `architecture.md` 中，开发任务清单定义在 `task.json` 中。

---

## MANDATORY: Agent Workflow

Every new agent session MUST follow this workflow:

### Step 1: Initialize Environment

```bash
./init.sh
```

This will:
- Create Python virtual environment (`.venv`) if not exists
- Install all Python dependencies from `requirements.txt`
- Check Node.js / npm availability for frontend tasks (if needed)
- Verify Python 3.12+ is available

**DO NOT skip this step.** Ensure the environment is ready before proceeding.

### Step 2: Select Next Task

Read `task.json` and select **ONE** task to work on.

Selection criteria (in order of priority):
1. Choose a task where `passes: false`
2. Consider dependencies — foundational modules should be done first
3. Pick the highest-priority incomplete task (lower id usually means higher priority)

### Step 3: Implement the Task

- Read the task description and steps carefully
- Implement the functionality to satisfy all steps
- Follow existing code patterns and conventions
- Use type hints where appropriate
- Keep functions focused and testable
- **If implementing API-related tasks (Task 2 or tasks touching `api/steamdt.py`), refer to `api/API_REFERENCE.md` and https://doc.steamdt.com/llms.txt for SteamDT API details**

### Step 4: Test Thoroughly

After implementation, verify ALL steps in the task:

**强制测试要求（Testing Requirements - MANDATORY）：**

1. **核心逻辑修改**（API 封装、数据分析、调度器、通知模块）：
   - **必须运行相关单元测试！** 使用 `python -m pytest tests/` 或 `python -m unittest`
   - 验证边界条件（空数据、API 失败、阈值边界等）
   - 使用 mock 测试外部依赖

2. **Web API 任务**（Task 11+ 涉及 web/ 目录）：
   - 使用 `python -m py_compile` 检查语法
   - 启动服务后用 curl 或浏览器测试端点
   - 运行 `python -m pytest tests/test_web_api.py` 如有新增测试

3. **前端任务**（Task 15+ 涉及 frontend/ 目录）：
   - 运行 `cd frontend && npm run build` 检查编译
   - 运行 `cd frontend && npm run lint` 检查代码规范（如有配置）

4. **小幅度代码修改**（修复 bug、调整日志、添加辅助函数）：
   - 可以使用 `python -m py_compile` 检查语法
   - 运行 `ruff check .` 或 `mypy` 检查代码规范（如已安装）

5. **所有修改必须通过**：
   - `python -m py_compile <modified_files>` 无语法错误
   - 相关单元测试通过
   - 核心流程可以正常启动（如修改了 main.py，运行 `python main.py` 测试初始化）

**测试清单：**
- [ ] 代码没有语法错误
- [ ] 新增/修改的逻辑有测试覆盖（核心模块）
- [ ] 单元测试通过
- [ ] 主程序能正常初始化（运行 `python main.py` 不报错退出）
- [ ] Web API 可正常访问（如修改了 web/，curl /api/health 返回 200）

### Step 5: Update Progress

Write your work to `progress.txt`:

```markdown
## [Date] - Task: [task description]

### What was done:
- [specific changes made]

### Testing:
- [how it was tested]

### Notes:
- [any relevant notes for future agents]
```

### Step 6: Commit Changes (包含 task.json 更新)

**IMPORTANT: 所有更改必须在同一个 commit 中提交，包括 task.json 的更新！**

流程：
1. 更新 `task.json`，将任务的 `passes` 从 `false` 改为 `true`
2. 更新 `progress.txt` 记录工作内容
3. 一次性提交所有更改：

```bash
git add .
git commit -m "[task title] - completed"
```

**规则:**
- 只有在所有步骤都验证通过后才标记 `passes: true`
- 永远不要删除或修改任务描述
- 永远不要从列表中移除任务
- **一个 task 的所有内容（代码、progress.txt、task.json）必须在同一个 commit 中提交**

---

## ⚠️ 阻塞处理（Blocking Issues）

**如果任务无法完成测试或需要人工介入，必须遵循以下规则：**

### 需要停止任务并请求人工帮助的情况：

1. **缺少环境配置**：
   - `.env` 需要填写真实的 SteamDT API Key
   - 通知渠道的 Webhook URL / Bot Token 需要人工配置
   - 外部 API 服务需要开通账号或购买套餐
   - 前端任务需要 Node.js 18+ 环境未安装

2. **外部依赖不可用**：
   - SteamDT API 服务宕机或无法访问
   - 通知渠道（企微/Telegram）服务异常
   - 需要付费升级 API 套餐
   - npm 包安装失败（网络问题）

3. **测试无法进行**：
   - 需要真实的 API Key 才能运行集成测试
   - 功能依赖外部系统尚未部署
   - 网络环境限制（如防火墙）
   - 前端构建工具链配置异常

4. **API 定义不明确**：
   - 如果在实现 SteamDT API 封装时对接口参数、响应格式有疑问，先查阅 `api/API_REFERENCE.md` 和 https://doc.steamdt.com/llms.txt
   - 若文档与实际行为不符，采用防御性编程（默认值、空值检查、try-except）

5. **前后端数据不同步**：
   - `config.py` 中的 watchlist 与 DB 表数据不一致
   - 修改了 DB schema 但前端未同步适配
   - WebSocket 连接无法建立（端口冲突、防火墙）

### 阻塞时的正确操作：

**DO NOT（禁止）：**
- ❌ 提交 git commit
- ❌ 将 task.json 的 passes 设为 true
- ❌ 假装任务已完成

**DO（必须）：**
- ✅ 在 progress.txt 中记录当前进度和阻塞原因
- ✅ 输出清晰的阻塞信息，说明需要人工做什么
- ✅ 停止任务，等待人工介入

### 阻塞信息格式：

```markdown
🚫 任务阻塞 - 需要人工介入

**当前任务**: [任务名称]

**已完成的工作**:
- [已完成的代码/配置]

**阻塞原因**:
- [具体说明为什么无法继续]

**需要人工帮助**:
1. [具体的步骤 1]
2. [具体的步骤 2]
...

**解除阻塞后**:
- 运行 [命令] 继续任务
```

---

## Project Structure

```
/
├── CLAUDE.md          # This file - workflow instructions
├── architecture.md    # Architecture design document
├── task.json          # Task definitions (source of truth)
├── progress.txt       # Progress log from each session
├── init.sh            # Initialization script
├── .env               # Environment variables (sensitive, not committed)
├── .env.example       # Environment variables template
├── config.py          # Configuration dataclasses
├── main.py            # Application entry point (scheduler + FastAPI)
├── requirements.txt   # Python dependencies
├── api/               # SteamDT API client
├── core/              # Monitor, analyzer, scheduler, extreme tracker
├── notify/            # Notification channels
├── storage/           # SQLite database operations
├── web/               # FastAPI web layer (routers, schemas, deps, ws)
├── frontend/          # Vue 3 frontend (Vite + TypeScript + Naive UI)
├── utils/             # Logger and utilities
├── data/              # SQLite database files
└── tests/             # Unit tests
```

## Commands

```bash
# Initialize environment
./init.sh

# Run the application (starts scheduler + FastAPI on port 8080)
python main.py

# Run backend tests
python -m pytest tests/
# or
python -m unittest discover tests/

# Run frontend dev server
cd frontend && npm run dev          # http://localhost:5173

# Build frontend
cd frontend && npm run build        # output to frontend/dist

# Check syntax
python -m py_compile main.py config.py api/*.py core/*.py notify/*.py storage/*.py web/*.py web/routers/*.py

# Check frontend build
cd frontend && npm run build

# Code linting
ruff check .
mypy main.py config.py api/ core/ notify/ storage/ web/
```

## Coding Conventions

### Python (Backend)
- Python 3.12+ with type hints
- Use `httpx` for HTTP requests (not `requests`)
- Use `loguru` for logging (not standard `logging`)
- Use `dataclass` for configuration and data models
- Use Pydantic v2 models for API request/response schemas
- Keep functions under 50 lines where possible
- Write docstrings for public methods
- Use `pathlib` instead of `os.path`
- Prefer `async`/`await` only where it provides clear benefit

### TypeScript/Vue (Frontend)
- Vue 3 Composition API with `<script setup>`
- TypeScript strict mode
- Use Pinia for state management
- Use Naive UI components where possible
- Use UnoCSS for utility-first CSS
- ECharts charts wrapped in reusable components
- API calls centralized in `frontend/src/api/index.ts`

## Key Rules

1. **One task per session** - Focus on completing one task well
2. **Test before marking complete** - All steps must pass
3. **Mock external APIs in tests** - Do not make real API calls in unit tests
4. **Document in progress.txt** - Help future agents understand your work
5. **One commit per task** - 所有更改（代码、progress.txt、task.json）必须在同一个 commit 中提交
6. **Never remove tasks** - Only flip `passes: false` to `true`
7. **Stop if blocked** - 需要人工介入时，不要提交，输出阻塞信息并停止
8. **DB优先策略** - watchlist 和 extreme_track_config 从 config.py 迁移到 DB 后，DB 数据优先，config.py 仅作初始默认值
9. **不破坏 CLI** - 新增 Web 功能时不得破坏已有的 CLI 监控能力
10. **SQLite WAL 模式** - 新数据库连接启用 WAL 模式以支持并发读写
