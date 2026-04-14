# 快速开始指南（换机迁移版）

本指南帮助你在另一台电脑上快速启动 CS2 饰品价格波动监控系统的 AI Agent 开发。

---

## 1. 环境要求

- **Python 3.12+**
- **Claude Code CLI**（安装方式：https://claude.ai/code）
- **Git**（用于 Agent 提交进度）
- **Bash**（Windows 上可用 Git Bash、MSYS2 或 WSL）

---

## 2. 解压项目

将打包的 `cs-monitor.zip` 解压到你希望存放代码的目录：

```bash
unzip cs-monitor.zip -d ~/Projects/
cd ~/Projects/cs-monitor
```

或者 Windows 下直接用解压软件右键解压。

---

## 3. 初始化环境

在项目根目录运行：

```bash
./init.sh
```

这个脚本会：
- 检查 Python 版本（要求 3.12+）
- 创建 `.venv` 虚拟环境
- 安装 `requirements.txt` 中的所有依赖
- 创建 `data/` 目录
- 检查 `.env` 文件是否存在

**首次运行后，你需要手动创建 `.env` 文件。**

---

## 4. 配置环境变量

```bash
cp .env.example .env
```

然后编辑 `.env`，填写你的真实配置：

```env
# 必填：SteamDT API Key
STEAMDT_API_KEY=your_steamdt_api_key_here

# 必填：至少配置一种通知渠道
NOTIFY_CHANNEL=wecom
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key_here
```

---

## 5. 初始化 Git（必须！这是 Agent 工作流的核心）

```bash
git init
git add .
git commit -m "Initial commit: project scaffold and agent workflow"
```

**注意**：Git 是这套自动编程 Agent 的「记忆系统」。每个 task 完成后，Agent 会提交 commit。没有 Git，Agent 无法正确传递上下文。

---

## 6. 开始 AI Agent 开发

### 方式一：手动模式（推荐前 1-2 个任务使用）

```bash
claude
```

进入 Claude Code 后，输入：

```
请按照 CLAUDE.md 中的工作流，完成 task.json 中的下一个任务。
```

### 方式二：半自动模式（跑顺后推荐）

```bash
claude -p --dangerously-skip-permissions
```

然后输入同样的 prompt。这种方式下，AI 会自动执行 `./init.sh`、编辑文件、运行测试、提交 git commit，无需你逐一手动确认。

### 方式三：全自动脚本（无人值守）

项目已自带 `run-automation.sh`，这是专为 CS2 Monitor 改造的全自动循环脚本，适配 Windows / Linux / macOS 环境。

**使用方式：**

```bash
./run-automation.sh 10    # 自动循环运行 10 次
```

这个脚本会：
- 自动统计 `task.json` 中剩余未完成的任务
- 每次启动一个 Claude Code session 完成下一个任务
- 自动记录运行日志到 `automation-logs/` 目录
- 检测任务完成情况，如果全部完成则提前退出
- 每次运行间隔 5 秒

**警告**：这是风险最高的模式，最容易浪费 API 额度。建议先用手动/半自动模式跑顺前几个任务后再使用。

**查看运行日志：**

```bash
ls automation-logs/
cat automation-logs/automation-YYYYmmdd_HHMMSS.log
```

---

## 7. 开发任务清单

当前 `task.json` 中定义了 10 个任务，按顺序开发：

1. 项目脚手架与基础配置
2. SteamDT API 封装模块
3. 数据存储模块（SQLite）
4. 核心监控逻辑：价格采集与调度
5. 核心监控逻辑：波动分析与告警检测
6. 极致追踪模块（高频单品狙击）
7. 通知推送模块
8. 主程序入口与优雅退出
9. 单元测试
10. 最终集成测试与优化

每个任务完成后，Agent 会自动：
- 更新 `task.json` 将该任务标记为 `passes: true`
- 更新 `progress.txt` 记录工作内容
- 提交 `git commit`

---

## 8. 如何查看进度

### 查看还剩多少任务

```bash
grep -c '"passes": false' task.json
```

### 查看开发历史

```bash
cat progress.txt
# 或
git log --oneline
```

### 查看当前任务详情

```bash
cat task.json | python -m json.tool
```

---

## 9. 阻塞处理

如果某个任务因为缺少 API Key、外部服务不可用等原因无法继续，Agent 会：
- **不提交 git commit**
- **不将 task.json 标记为完成**
- 在 `progress.txt` 中记录阻塞原因
- 输出阻塞信息并停止

这时你需要：
1. 根据阻塞信息解决问题（如填写 `.env`、开通 API 套餐）
2. 重新运行 Claude Code，让 Agent 继续同一个任务

---

## 10. 相关文档

| 文档 | 说明 |
|------|------|
| `PRD.md` | 原始产品需求文档 |
| `architecture.md` | 技术架构设计文档 |
| `CLAUDE.md` | **AI Agent 工作流规范（必读）** |
| `task.json` | 开发任务清单 |
| `TECH-NOTES.md` | 超长时间自动编程 Agent 的技术原理 |
| `QUICKSTART.md` | 本文档 |

---

## 11. 常用命令速查

```bash
# 初始化环境
./init.sh

# 运行主程序
.venv/Scripts/python.exe main.py        # Windows
# 或
.venv/bin/python main.py                # macOS/Linux

# 运行测试
.venv/Scripts/python.exe -m pytest tests/    # Windows
# 或
.venv/bin/python -m pytest tests/            # macOS/Linux

# 代码检查
ruff check .
mypy main.py config.py api/ core/ notify/ storage/ utils/
```

---

祝你开发顺利！
