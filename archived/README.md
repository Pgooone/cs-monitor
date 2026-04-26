# Archived Code — 封存代码

此目录存放已移除但可能在未来重新启用的功能代码。

## 目录结构

```
archived/
├── auth/                        # 登录认证系统
│   ├── auth.store.ts.bak        # Pinia auth store（JWT token 管理）
│   └── (Login.vue, Setup.vue 已删除，如需恢复参考 git history)
│
├── websocket/                   # WebSocket 实时推送系统
│   ├── ws_manager.py            # 后端 WS 管理器（连接池、广播）
│   ├── websocket.ts             # 前端 WS 状态管理（Pinia store）
│   ├── ws.ts                    # 前端 WS 工具类（自动重连、心跳）
│   └── WsStatusPill.vue         # WS 状态指示器组件
│
└── README.md                    # 本文件
```

---

## 登录认证系统

**移除原因**：单用户自托管场景下，登录步骤冗余。

**包含功能**：
- JWT token 生成与验证
- 登录页面（用户名/密码）
- 首次登录强制改密
- axios 拦截器自动注入 token
- 401 自动跳转登录页

**恢复步骤**：
1. 恢复 `frontend/src/stores/auth.ts` 为完整版本
2. 恢复 `frontend/src/views/Login.vue` 和 `Setup.vue`（从 git history）
3. 恢复 `frontend/src/router/index.ts` 的 `requiresAuth` 守卫
4. 恢复 `web/deps.py` 的 `require_auth` JWT 验证
5. 恢复 `web/routers/auth.py` 的完整登录逻辑
6. 恢复 `frontend/src/api/index.ts` 的 auth API 和 401 拦截器
7. 恢复 `frontend/src/main.ts` 的 authStore 初始化

---

## WebSocket 实时推送系统

**移除原因**：实时推送增加了系统复杂度，当前轮询模式已满足需求。

**包含功能**：
- `/ws/alerts` — 实时告警推送频道
- `/ws/extreme-track/{name}/{platform}` — 极致追踪实时数据流
- 前端 WS 连接管理（自动重连、心跳 ping/pong）
- 右下角 WS 状态指示器（连接中/已连接/断开/错误）
- 后端 ws_manager 广播（从 APScheduler 线程安全推送）

**恢复步骤**：
1. 恢复 `web/ws_manager.py`
2. 恢复 `web/app.py` 中的 WS 端点代码
3. 恢复 `core/scheduler.py` 中的 WS 广播调用
4. 恢复 `frontend/src/stores/websocket.ts`
5. 恢复 `frontend/src/utils/ws.ts`
6. 恢复 `frontend/src/components/base/WsStatusPill.vue`
7. 恢复 Dashboard/ExtremeTrack 中的 WS 监听代码
8. 恢复 AppLayout.vue 中的 WsStatusPill 引用

---

## 相关 Git Commits

- `46a2ac4` — 移除前端登录认证
- `2d5240e` — 后端移除 JWT 认证
- `d6d0bbb` — 移除 WebSocket 认证（本次）
