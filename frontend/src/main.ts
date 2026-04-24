import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import 'virtual:uno.css'

import App from './App.vue'
import router from './router'
import { i18n } from './i18n'
import { useAuthStore } from '@/stores/auth'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(naive)

// 在挂载前初始化登录状态
const authStore = useAuthStore()
authStore.initFromStorage()

app.mount('#app')
