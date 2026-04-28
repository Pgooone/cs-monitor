<template>
  <!-- 移动端遮罩 + 抽屉 -->
  <div
    v-if="isMobile && mobileDrawerOpen"
    class="sidebar-overlay"
    @click="$emit('update:mobileDrawerOpen', false)"
  />
  <aside
    v-if="!isMobile || mobileDrawerOpen"
    class="sidebar"
    :class="{ 'sidebar--mobile': isMobile }"
  >
    <SidebarContent
      :collapsed="collapsed"
      @navigate="$emit('update:mobileDrawerOpen', false)"
    />
  </aside>
</template>

<script setup lang="ts">
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
.sidebar {
  width: 5rem;
  height: 100vh;
  flex-shrink: 0;
  border-right: 1px solid #1f1f23;
  background: rgba(5, 5, 5, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: flex;
  flex-direction: column;
  z-index: 50;
  transition: all 300ms;
}

@media (min-width: 1024px) {
  .sidebar {
    width: 16rem;
  }
}

.sidebar--mobile {
  position: fixed;
  left: 0;
  top: 0;
  width: 16rem;
  z-index: 1000;
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

html:not(.dark) .sidebar {
  border-right-color: #e2e8f0;
  background: rgba(255, 255, 255, 0.8);
}
</style>
