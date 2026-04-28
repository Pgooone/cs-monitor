<template>
  <div class="sidebar-content">
    <!-- Logo 区 -->
    <div class="sidebar-header">
      <div class="sidebar-logo">
        <div class="sidebar-logo__icon">
          <Scan class="w-5 h-5 text-white" />
        </div>
        <div class="sidebar-logo__text">
          <h1 class="sidebar-logo__title">CS<span class="text-brand">MONITOR</span></h1>
          <p class="sidebar-logo__subtitle">Trading Terminal</p>
        </div>
      </div>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <button
        v-for="item in menuItems"
        :key="item.id"
        :class="activeKey === item.id ? 'nav-item-active' : 'nav-item'"
        @click="navigate(item.id)"
      >
        <component :is="item.icon" class="w-5 h-5 shrink-0" />
        <span class="sidebar-nav__label">{{ item.label }}</span>
      </button>
    </nav>

    <!-- 底部状态 -->
    <div class="sidebar-footer">
      <div class="sidebar-status">
        <div class="sidebar-status__dot" />
        <span class="sidebar-status__text">API 已连接</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  LayoutDashboard,
  ListOrdered,
  Zap,
  Bell,
  Settings,
  Scan,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const emit = defineEmits<{ (e: 'navigate'): void }>()

const activeKey = computed(() => route.name as string)

const menuItems = [
  { id: 'Dashboard', label: '实时监控', icon: LayoutDashboard },
  { id: 'Watchlist', label: '监控清单', icon: ListOrdered },
  { id: 'ExtremeTrack', label: '极致追踪', icon: Zap },
  { id: 'Alerts', label: '历史告警', icon: Bell },
  { id: 'Settings', label: '系统设置', icon: Settings },
]

function navigate(name: string) {
  router.push({ name })
  emit('navigate')
}
</script>

<style scoped>
.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  height: 5rem;
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.sidebar-logo__icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.75rem;
  background: #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
}

.sidebar-logo__title {
  font-size: 0.875rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.text-brand {
  color: #6366f1;
}

.sidebar-logo__subtitle {
  font-size: 10px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 700;
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 2rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sidebar-footer {
  padding: 1rem;
}

.sidebar-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 0.75rem;
}

.sidebar-status__dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.sidebar-status__text {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
}

html:not(.dark) .sidebar-logo__title {
  color: #0f172a;
}

html:not(.dark) .sidebar-logo__subtitle {
  color: #64748b;
}

html:not(.dark) .sidebar-status__text {
  color: #64748b;
}
</style>
