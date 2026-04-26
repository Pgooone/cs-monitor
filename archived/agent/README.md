# Agent 自动化循环文件

此目录存放 AI Agent 自动循环开发所需的文件。

## 文件说明

| 文件 | 用途 |
|------|------|
| `run-automation.sh` | Linux/macOS 自动循环脚本 |
| `run-automation.ps1` | Windows PowerShell 自动循环脚本 |
| `next-task.txt` | 下一个待执行任务的提示文件 |
| `task.json` | 任务清单（当前 30 个任务全部完成） |
| `progress.txt` | Agent 开发进度日志 |
| `CLAUDE.md.original` | 原始 Agent 工作流规范（完整版） |

## 如何重新启用 Agent 自动循环

1. 将文件复制回项目根目录：
   ```bash
   cp archived/agent/run-automation.sh .
   cp archived/agent/run-automation.ps1 .
   cp archived/agent/next-task.txt .
   ```

2. 在 `task.json` 中添加新的任务（`passes: false`）

3. 运行自动循环：
   ```bash
   # Linux/macOS
   ./run-automation.sh 10

   # Windows PowerShell
   .\run-automation.ps1 -Iterations 10
   ```

## 注意事项

- 运行前确保 `.env` 已配置好 API Key
- 建议前 1-2 个任务用手动模式验证 Agent 理解工作流
- 半自动模式（`claude -p --dangerously-skip-permissions`）最常用
- 全自动模式只在人不在电脑边时使用
