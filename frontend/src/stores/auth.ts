/**
 * Auth Store — 登录状态管理
 *
 * 管理 token、登录状态、用户信息、默认密码检测。
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '@/api/index'

const TOKEN_KEY = 'cs_monitor_token'
const REMEMBER_KEY = 'cs_monitor_remember'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const username = ref<string>('admin')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const requiresPasswordChange = ref(false)

  // Getters
  const isLoggedIn = computed(() => !!token.value)

  // Actions
  async function login(password: string, remember: boolean = false) {
    isLoading.value = true
    error.value = null
    try {
      const res = await api.login(password)
      const newToken = res.data.access_token
      const needsChange = res.data.requires_password_change

      token.value = newToken
      requiresPasswordChange.value = needsChange

      localStorage.setItem(TOKEN_KEY, newToken)
      localStorage.setItem(REMEMBER_KEY, remember ? '1' : '0')

      // 获取用户信息
      await fetchMe()

      return { success: true, requiresPasswordChange: needsChange }
    } catch (err: any) {
      const msg = err.response?.data?.detail || '登录失败'
      error.value = msg
      return { success: false, message: msg }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await api.me()
      username.value = res.data.username || 'admin'
    } catch {
      // 静默失败，不破坏用户体验
    }
  }

  async function changePassword(currentPassword: string, newPassword: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.changePassword(currentPassword, newPassword)
      // 修改成功后需要重新登录
      logout()
      return { success: true }
    } catch (err: any) {
      const msg = err.response?.data?.detail || '修改密码失败'
      error.value = msg
      return { success: false, message: msg }
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    token.value = null
    username.value = 'admin'
    error.value = null
    requiresPasswordChange.value = false
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REMEMBER_KEY)
  }

  function initFromStorage() {
    const savedToken = localStorage.getItem(TOKEN_KEY)
    if (savedToken) {
      token.value = savedToken
      fetchMe()
    }
  }

  return {
    token,
    username,
    isLoading,
    error,
    requiresPasswordChange,
    isLoggedIn,
    login,
    fetchMe,
    changePassword,
    logout,
    initFromStorage,
  }
})
