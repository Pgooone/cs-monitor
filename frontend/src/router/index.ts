import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useNProgress } from '@/composables/useNProgress'
import { toastError } from '@/composables/useToast'

const { start, done } = useNProgress()

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
        },
        {
          path: 'watchlist',
          name: 'Watchlist',
          component: () => import('@/views/Watchlist.vue'),
        },
        {
          path: 'item/:name',
          name: 'ItemDetail',
          component: () => import('@/views/ItemDetail.vue'),
        },
        {
          path: 'extreme-track',
          name: 'ExtremeTrack',
          component: () => import('@/views/ExtremeTrack.vue'),
        },
        {
          path: 'alerts',
          name: 'Alerts',
          component: () => import('@/views/Alerts.vue'),
        },
        {
          path: 'stats',
          name: 'Stats',
          component: () => import('@/views/StatsView.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings.vue'),
        },
      ],
    },
  ],
})

// 路由守卫：仅处理进度条
router.beforeEach((_to, _from, next) => {
  start()
  next()
})

router.afterEach(() => {
  done()
})

router.onError((err) => {
  done()
  toastError(`页面加载失败：${err.message}`)
  console.error('[Router] 导航错误:', err)
})

export default router
