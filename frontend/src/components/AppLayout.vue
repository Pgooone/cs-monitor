<template>
  <n-layout has-sider style="height: 100vh">
    <Sidebar
      :collapsed="collapsed"
      :is-mobile="isMobile"
      :mobile-drawer-open="mobileDrawerOpen"
      @update:mobile-drawer-open="mobileDrawerOpen = $event"
    />
    <n-layout>
      <TopBar
        :collapsed="collapsed"
        :is-mobile="isMobile"
        @toggle-collapse="toggleCollapse"
        @toggle-mobile-drawer="mobileDrawerOpen = !mobileDrawerOpen"
      />
      <n-layout-content
        class="app-layout__content"
        :native-scrollbar="false"
      >
        <div class="app-layout__main">
          <router-view />
        </div>
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { NLayout, NLayoutContent } from 'naive-ui'
import Sidebar from '@/components/layout/Sidebar.vue'
import TopBar from '@/components/layout/TopBar.vue'

const isMobile = ref(false)
const collapsed = ref(false)
const mobileDrawerOpen = ref(false)

function updateLayout() {
  const w = window.innerWidth
  if (w < 640) {
    isMobile.value = true
    collapsed.value = false
  } else if (w < 1024) {
    isMobile.value = false
    collapsed.value = true
  } else {
    isMobile.value = false
    collapsed.value = false
  }
}

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

onMounted(() => {
  updateLayout()
  window.addEventListener('resize', updateLayout)
})
onUnmounted(() => {
  window.removeEventListener('resize', updateLayout)
})
</script>

<style>
.app-layout__content {
  background: var(--n-body-color);
}

.app-layout__main {
  padding: 1.5rem;
  min-height: 100%;
  max-width: 1440px;
  margin: 0 auto;
  transition: padding 200ms ease;
}

@media (max-width: 639px) {
  .app-layout__main {
    padding: 1rem;
  }
}

@media (min-width: 1536px) {
  .app-layout__main {
    max-width: 1440px;
    margin: 0 auto;
  }
}
</style>
