<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="200"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
    >
      <div class="flex items-center justify-center h-16 font-bold text-lg">
        <span v-if="!collapsed">CS2监控</span>
        <span v-else>CS2</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
      />
    </n-layout-sider>
    <n-layout>
      <n-layout-header bordered class="h-16 flex items-center px-6">
        <h2 class="m-0 text-lg">{{ pageTitle }}</h2>
      </n-layout-header>
      <n-layout-content class="p-6 bg-gray-50">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { NLayout, NLayoutSider, NLayoutHeader, NLayoutContent, NMenu } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import { RouterLink } from 'vue-router'

const collapsed = ref(false)
const route = useRoute()

const activeKey = computed(() => route.name as string)
const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    Dashboard: 'Dashboard',
    Watchlist: '监控清单',
    ExtremeTrack: '极致追踪',
    Alerts: '告警记录',
    Settings: '系统设置',
  }
  return titles[route.name as string] || 'Dashboard'
})

function renderIcon(_icon: string) {
  return () => h('span', { class: 'text-base' }, _icon)
}

const menuOptions: MenuOption[] = [
  {
    label: () => h(RouterLink, { to: { name: 'Dashboard' } }, { default: () => 'Dashboard' }),
    key: 'Dashboard',
    icon: renderIcon('📊'),
  },
  {
    label: () => h(RouterLink, { to: { name: 'Watchlist' } }, { default: () => '监控清单' }),
    key: 'Watchlist',
    icon: renderIcon('📋'),
  },
  {
    label: () => h(RouterLink, { to: { name: 'ExtremeTrack' } }, { default: () => '极致追踪' }),
    key: 'ExtremeTrack',
    icon: renderIcon('🎯'),
  },
  {
    label: () => h(RouterLink, { to: { name: 'Alerts' } }, { default: () => '告警记录' }),
    key: 'Alerts',
    icon: renderIcon('🔔'),
  },
  {
    label: () => h(RouterLink, { to: { name: 'Settings' } }, { default: () => '系统设置' }),
    key: 'Settings',
    icon: renderIcon('⚙️'),
  },
]
</script>
