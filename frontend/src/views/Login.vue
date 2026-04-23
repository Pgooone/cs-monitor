<template>
  <div class="login-page" :class="{ dark: isDark }">
    <!-- 左侧品牌宣传区 -->
    <div class="login-brand">
      <div class="brand-bg" />
      <div class="brand-content">
        <div class="brand-logo">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M12 2L2 7L12 12L22 7L12 2Z"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M2 17L12 22L22 17"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M2 12L12 17L22 12"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
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
            <div class="feature-dot" />
            <span>多平台价格实时监控</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot" />
            <span>智能波动分析与告警</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot" />
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
            @click="handleLogin"
          >
            登录
          </n-button>
        </n-form>

        <div class="form-footer">
          <p class="security-tips">
            <span class="i-carbon-security" />
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
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%);
}

.brand-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.06) 0%, transparent 40%);
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
  margin-bottom: 2rem;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(8px);
}

.logo-icon svg {
  width: 1.5rem;
  height: 1.5rem;
  color: #fff;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.brand-slogan {
  font-size: 2.25rem;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 1rem;
  letter-spacing: -0.02em;
}

.brand-desc {
  font-size: 1rem;
  line-height: 1.75;
  opacity: 0.85;
  margin: 0 0 2.5rem;
  max-width: 400px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9375rem;
}

.feature-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,0.7);
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
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: var(--n-text-color-base);
}

.form-subtitle {
  font-size: 0.9375rem;
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

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.security-tips {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--n-text-color-3);
  margin: 0;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: var(--n-action-color);
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

/* dark 模式下的品牌区 */
.dark .login-brand {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1d4ed8 100%);
}
</style>
