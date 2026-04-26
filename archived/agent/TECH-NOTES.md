# 超长时间自动编程 Agent 技术笔记

本文档记录本项目所基于的自动编程 Agent 方法论，来源为研究分析 SamuelQZQ 的 `auto-coding-agent-demo` 项目及其引用的 Anthropic 文章《Effective Harnesses for Long-Running Agents》。

---

## 1. 核心问题：为什么 AI 无法一次性完成复杂项目？

复杂项目的开发往往超过 LLM 的上下文窗口限制。当对话历史过长时，AI 会出现：
- **遗忘早期需求**
- **迷失当前任务方向**
- **重复修改已经写好的代码**
- **无法正确理解项目的整体架构**

Claude 等模型虽然有 **上下文压缩（compaction）** 机制，但 Anthropic 明确指出：

> **"Compaction isn't sufficient... even with compaction, which doesn't always pass perfectly clear instructions to the next agent."**
> 
> （上下文压缩本身是不够的，因为压缩后的信息并不总是能清晰传递给下一个 Agent。）

因此，**超长时间自动编程的核心不是「让 AI 一次跑很久」，而是「让每个新 session 都能快速、无损地恢复现场」。**

---

## 2. Anthropic 的解决方案：Effective Harnesses

Anthropic 提出了一种 **双组件 harness** 架构：

### 2.1 Initializer Agent（初始化 Agent）
- 在首次运行时设置环境
- 创建后续会话所需的基础结构：
  - `init.sh` 环境恢复脚本
  - `feature_list.json` / `tests.json` 任务清单
  - `claude-progress.txt` 进度日志
  - 初始 git commit

### 2.2 Coding Agent（编码 Agent）
- 在每个后续会话中做增量进展
- 每次只处理**一个**功能/任务
- 为下一个会话留下清晰的产物
- 会话结束时代码应达到 **"可以合并到主分支"** 的质量

---

## 3. SamuelQZQ 项目的本土化改造

SamuelQZQ 的 `auto-coding-agent-demo` 是对 Anthropic 原文的工程化落地，针对中文环境和 Claude Code CLI 做了大量适配。

### 3.1 文件结构对比

| 功能 | Anthropic 原文 | SamuelQZQ 项目 | 本项目（cs-monitor）|
|------|---------------|----------------|-------------------|
| 固定流程提示词 | 内嵌在 harness 中 | `CLAUDE.md` | `CLAUDE.md` |
| 任务清单 | `feature_list.json` / `tests.json` | `task.json` | `task.json` |
| 进度日志 | `claude-progress.txt` | `progress.txt` | `progress.txt` |
| 环境恢复脚本 | `init.sh` | `init.sh` | `init.sh` |
| 浏览器自动化 | Puppeteer MCP | Playwright MCP | 不适用（后端项目）|

### 3.2 关键差异

1. **任务粒度更粗**：原文拆到 200+ 项功能，SamuelQZQ 只用了 31 项。这在实际落地中更合理——太细的粒度会导致 session 切换 overhead 过高。
2. **测试与任务合并**：原文用独立的测试清单，SamuelQZQ 把验收标准直接写在 `task.json` 的 `steps` 里，降低了文件管理复杂度。
3. **增加了阻塞处理规范**：原文未重点提及阻塞情况，而 `CLAUDE.md` 中专门定义了「禁止提交、记录阻塞、停止任务」的规则。这是实际开发中非常重要的补充。
4. **自动化脚本的工程化**：`run-automation.sh` 是一个完整的 bash 自动化循环，带有日志记录和任务计数，这是原文没有提供的。

---

## 4. 上下文管理方案：不靠压缩，靠「环境产物」

这是整套系统最核心的设计。项目用 **4 个环境文件** 替代了依赖 LLM 的上下文压缩来传递状态：

```
├── CLAUDE.md      # 固定流程（不变，类似系统提示词）
├── task.json      # 结构化任务清单（单一事实来源）
├── progress.txt   # 动态进度日志（每个 session 追加）
└── init.sh        # 环境恢复脚本（标准化启动流程）
```

每次新 session 启动时：
1. 运行 `./init.sh` 恢复环境（装依赖、起服务）
2. 读 `task.json` 找 `passes: false` 的任务
3. 读 `progress.txt` 和 `git log` 了解历史
4. 执行一个任务 → 测试 → 更新 `progress.txt` + `task.json` → `git commit`

**新 session 的启动成本极低**，且不需要依赖 LLM 的上下文压缩能力。

---

## 5. Git 在自动编程 Agent 中的作用

在这套系统中，**Git 不是「版本控制工具」，而是「跨会话上下文传递机制」**。

### 5.1 Git 作为上下文的替代方案

新 session 不靠「压缩后的对话历史」来恢复状态，而是靠：
- `git log` → 了解代码变更历史
- `progress.txt` → 了解每个 session 的具体工作和测试结果
- `task.json` → 找到下一个待完成的任务

Git commit 历史在这里充当了 **技术层面的记忆体**。

### 5.2 强制 commit 规则

每个 session 结束时必须：
```bash
git add .
git commit -m "[task description] - completed"
```

**关键约束：**
- 一个 task 的所有产物（代码 + `progress.txt` + `task.json`）必须在**同一个 commit** 中
- 永远不要删除或修改 `task.json` 中的任务描述
- 永远不要从列表中移除任务

### 5.3 Git 作为「开发纪录片」

> "除 2 个人工提交的 markdown 修改外，其余所有的 git 提交都是由 AI 完成的。"
> "你在 git commit 记录里能看到 10 个小时我让 AI 做的所有事。"

- 每个 commit ≈ 一个 Agent session 的输出
- Commit message ≈ 完成了什么任务
- Diff ≈ 具体改了哪些代码
- **整个 git history 就是 AI 自动编程的完整审计日志**

### 5.4 阻塞时的「禁止提交」规则

遇到阻塞时（如缺少 API Key、外部服务不可用）：

**禁止：**
- ❌ 提交 git commit
- ❌ 将 task.json 的 passes 设为 true
- ❌ 假装任务已完成

**必须：**
- ✅ 只在 `progress.txt` 中记录进度和阻塞原因
- ✅ 输出阻塞信息并停止

这确保了 git history 中**不会包含半成品或虚假完成的代码**。

### 5.5 没有复杂分支策略

项目使用的是**最简单的线性历史**：
- 没有 feature branch
- 没有 PR/MR
- 没有 rebase 或 merge
- 就是主分支上一个个连续的 commit

这种简化是刻意为之的——降低 Agent 的认知负担。

---

## 6. 三种运行模式

| 模式 | 命令 | 适用场景 |
|------|------|----------|
| 手动模式 | `claude` | 最稳妥，人工确认每个工具调用 |
| 半自动模式 | `claude -p --dangerously-skip-permissions` | 最常用的实验模式，作者跑 10 小时用的就是这个 |
| 全自动模式 | `./run-automation.sh 10` | 无人值守循环，风险最高 |

**推荐实践：**
- 前 1-2 个任务用手动模式，验证 Agent 对工作流的理解
- 跑顺后切换到半自动模式
- 全自动模式只在人不在电脑边时使用

---

## 7. 为什么这比单纯用 Claude Code 的 "/compact" 更可靠？

Claude Code 本身有上下文压缩机制，但它的局限在于：
- 压缩是**有损的**，可能会丢掉关键细节
- 压缩后的指令不一定能清晰指导下一个 session

而 SamuelQZQ 的方案是 **「无压缩」**：每个新 session 的上下文窗口里，对话历史很短，但它能通过读取环境产物快速、无损地恢复现场。

这才是这套系统能稳定跑 10 小时的核心原因。

---

## 8. 参考链接

- SamuelQZQ 项目：https://github.com/SamuelQZQ/auto-coding-agent-demo
- Anthropic 文章：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
