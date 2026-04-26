<template>
  <div class="login-page" :class="{ dark: isDark }">
    <!-- 左侧品牌宣传区 -->
    <div class="login-brand">
      <div class="brand-bg" />
      <div class="brand-grid" />
      <div class="brand-glow" />
      <div class="brand-content">
        <div class="brand-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
          <span class="logo-text">CS2 Monitor</span>
        </div>
        <h1 class="brand-slogan">CS2 饰品价格<br>智能监控平台</h1>
        <p class="brand-desc">
          实时监控饰品价格波动，智能分析市场趋势<br>
          多平台数据聚合，极速告警推送
        </p>
        <div class="brand-features">
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1v14M1 8h14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </div>
            <span>多平台价格实时监控</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 12l4-4 3 3 5-7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <span>智能波动分析与告警</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/><rect x="9" y="2" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/><rect x="2" y="9" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/><rect x="9" y="9" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.2"/></svg>
            </div>
            <span>K 线图表与趋势预测</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-section">
      <div class="form-wrapper">
        <div class="form-header">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-subtitle">请登录您的管理员账户</p>
        </div>

        <n-form
          ref="formRef"
          :model="formValue"
          :rules="rules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <n-form-item path="username" label="用户名">
            <n-input
              v-model:value="formValue.username"
              placeholder="admin"
              size="large"
              readonly
              :input-props="{ 'aria-label': '用户名' }"
            >
              <template #prefix>
                <span class="i-carbon-user" />
              </template>
            </n-input>
          </n-form-item>

          <n-form-item path="password" label="密码">
            <n-input
              v-model:value="formValue.password"
              type="password"
              placeholder="请输入管理员密码"
              size="large"
              show-password-on="click"
              :input-props="{ 'aria-label': '密码' }"
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <span class="i-carbon-password" />
              </template>
            </n-input>
          </n-form-item>

          <div class="form-options">
            <n-checkbox v-model:checked="rememberMe">
              记住我
            </n-checkbox>
          </div>

          <n-button
            type="primary"
            size="large"
            block
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
            class="login-btn"
            @click="handleLogin"
          >
            登录
          </n-button>
        </n-form>

        <div class="form-footer">
          <p class="security-tips">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style="flex-shrink:0"><path d="M8 1L2 4v4c0 3.5 2.5 6.5 6 7.5 3.5-1 6-4 6-7.5V4L8 1z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/><path d="M6 8l2 2 3-4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            首次登录请使用默认密码 admin，登录后建议立即修改
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NForm,
  NFormItem,
  NInput,
  NButton,
  NCheckbox,
  useMessage,
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const { isDark } = useTheme()

const formRef = ref<FormInst | null>(null)
const rememberMe = ref(localStorage.getItem('cs_monitor_remember') === '1')

const formValue = ref({
  username: 'admin',
  password: '',
})

const rules: FormRules = {
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

async function handleLogin() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  const result = await authStore.login(formValue.value.password, rememberMe.value)

  if (result.success) {
    message.success('登录成功')
    if (result.requiresPasswordChange) {
      router.push('/setup')
    } else {
      router.push('/')
    }
  } else {
    message.error(result.message || '登录失败')
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: var(--n-body-color);
}

/* ===== 左侧品牌区 ===== */
.login-brand {
  position: relative;
  display: none;
  width: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #0a0f1e 0%, #131b3a 40%, #1a2550 70%, #0d1320 100%);
}

.brand-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 30% 70%, rgba(74, 92, 242, 0.15) 0%, transparent 60%),
    radial-gradient(ellipse at 70% 30%, rgba(249, 115, 22, 0.08) 0%, transparent 50%);
}

/* 网格线纹理 */
.brand-grid {
  position: absolute;
  inset: 0;
  opacity: 0.04;
  background-image:
    linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px);
  background-size: 40px 40px;
}

/* 呼吸光效 */
.brand-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(107, 127, 248, 0.12) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: brand-glow-pulse 6s ease-in-out infinite;
}

@keyframes brand-glow-pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
  50% { transform: translate(-50%, -50%) scale(1.3); opacity: 1; }
}

.brand-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  padding: 3rem;
  color: #fff;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2.5rem;
}

.logo-icon {
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.625rem;
  background: rgba(107, 127, 248, 0.15);
  border: 1px solid rgba(107, 127, 248, 0.2);
}

.logo-icon svg {
  width: 1.25rem;
  height: 1.25rem;
  color: #6b7ff8;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #b8c9e2, #6b7ff8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-slogan {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 1.25rem;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #f0f4fa 0%, #8da4c8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-desc {
  font-size: 0.9375rem;
  line-height: 1.75;
  color: #5a7ba5;
  margin: 0 0 3rem;
  max-width: 400px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #8da4c8;
}

.feature-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: rgba(107, 127, 248, 0.08);
  border: 1px solid rgba(107, 127, 248, 0.1);
  color: #6b7ff8;
  flex-shrink: 0;
}

/* ===== 右侧表单区 ===== */
.login-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.form-wrapper {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 2rem;
  text-align: center;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.375rem;
  color: var(--n-text-color-base);
  letter-spacing: -0.02em;
}

.form-subtitle {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin: 0.25rem 0 0.75rem;
}

.login-btn {
  height: 44px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.security-tips {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--n-text-color-3);
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  background: var(--n-action-color);
  line-height: 1.4;
}

/* ===== 响应式 ===== */
@media (min-width: 1024px) {
  .login-brand {
    display: flex;
  }
}

@media (min-width: 1280px) {
  .brand-content {
    padding: 4rem;
  }
  .brand-slogan {
    font-size: 2.75rem;
  }
}
</style>
