import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

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

// 路由守卫：未登录且非公开页面则重定向到登录页
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('cs_monitor_token')
  if (!token && !to.meta.public) {
    next('/login')
  } else if (token && to.path === '/login') {
    next('/')
  } else {
    next()
  }
})

export default router
