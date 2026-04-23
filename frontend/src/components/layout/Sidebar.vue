<template>
  <!-- 移动端抽屉 -->
  <n-drawer
    v-if="isMobile"
    :show="mobileDrawerOpen"
    placement="left"
    :width="240"
    :auto-focus="false"
    @update:show="$emit('update:mobileDrawerOpen', $event)"
  >
    <n-drawer-content body-content-style="padding: 0">
      <sidebar-content
        :collapsed="false"
        :show-tooltip="false"
        @navigate="$emit('update:mobileDrawerOpen', false)"
      />
    </n-drawer-content>
  </n-drawer>

  <!-- 桌面端侧边栏 -->
  <n-layout-sider
    v-else
    bordered
    collapse-mode="width"
    :collapsed-width="64"
    :width="240"
    :collapsed="collapsed"
    :show-trigger="false"
    class="app-sidebar"
  >
    <sidebar-content :collapsed="collapsed" :show-tooltip="true" />
  </n-layout-sider>
</template>

<script setup lang="ts">
import { NLayoutSider, NDrawer, NDrawerContent } from 'naive-ui'
import SidebarContent from './SidebarContent.vue'

defineProps<{
  collapsed: boolean
  isMobile: boolean
  mobileDrawerOpen: boolean
}>()

defineEmits<{
  (e: 'update:mobileDrawerOpen', v: boolean): void
}>()
</script>

<style scoped>
.app-sidebar {
  transition: width 200ms ease;
}
</style>
