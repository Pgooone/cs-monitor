import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useNProgress } from '@/composables/useNProgress'
import { toastError } from '@/composables/useToast'

const { start, done } = useNProgress()

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { public: true },
    },
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
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings.vue'),
        },
      ],
    },
  ],
})

// 路由切换时自动显示/隐藏 NProgress 加载条
router.beforeEach((to, _from, next) => {
  start()
  const token = localStorage.getItem('cs_monitor_token')
  if (!token && !to.meta.public) {
    next('/login')
  } else if (token && to.path === '/login') {
    next('/')
  } else {
    next()
  }
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
