import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useNProgress } from '@/composables/useNProgress'
import { toastError } from '@/composables/useToast'
import { useAuthStore } from '@/stores/auth'

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
      path: '/setup',
      name: 'Setup',
      component: () => import('@/views/Setup.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
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

// 路由守卫：认证检查 + 默认密码跳转
router.beforeEach((to, _from, next) => {
  start()
  const authStore = useAuthStore()
  const isLoggedIn = authStore.isLoggedIn

  // 未登录且访问非公开页面 -> 跳转登录
  if (!isLoggedIn && !to.meta.public) {
    next('/login')
    return
  }

  // 已登录且访问登录页 -> 跳转首页
  if (isLoggedIn && to.path === '/login') {
    next('/')
    return
  }

  // 已登录且使用默认密码 -> 强制跳转 setup（除非是已经在 setup 页面）
  if (isLoggedIn && authStore.requiresPasswordChange && to.path !== '/setup') {
    next('/setup')
    return
  }

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
