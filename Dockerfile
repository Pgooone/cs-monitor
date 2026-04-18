# =============================================================================
# CS2 饰品价格波动监控系统 — Docker 多阶段构建
# Stage 1: 构建前端（Node.js）
# Stage 2: 构建后端镜像（Python）
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: 前端构建
# -----------------------------------------------------------------------------
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# 先复制依赖文件，利用 Docker 层缓存
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# 复制前端源码并构建
COPY frontend/ .
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Python 后端运行时
# -----------------------------------------------------------------------------
FROM python:3.12-slim

# 安装系统依赖（curl 用于健康检查）
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先复制依赖文件，利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端源码
COPY . .

# 将前端构建产物复制到正确位置（与 web/app.py 查找路径一致）
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 数据目录（SQLite 数据库文件挂载点）
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fs http://localhost:8080/api/health || exit 1

# 启动命令
CMD ["python", "main.py"]
