<template>
  <div class="setup-page">
    <div class="setup-card">
      <div class="setup-header">
        <div class="setup-icon">
          <span class="i-carbon-warning-alt" />
        </div>
        <h1 class="setup-title">安全设置</h1>
        <p class="setup-desc">
          检测到您正在使用默认密码，为了保障系统安全，请立即修改管理员密码。
        </p>
      </div>

      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        class="setup-form"
        @submit.prevent="handleSubmit"
      >
        <n-form-item path="currentPassword" label="当前密码">
          <n-input
            v-model:value="formValue.currentPassword"
            type="password"
            placeholder="默认密码：admin"
            size="large"
            show-password-on="click"
            :input-props="{ 'aria-label': '当前密码' }"
          />
        </n-form-item>

        <n-form-item path="newPassword" label="新密码">
          <n-input
            v-model:value="formValue.newPassword"
            type="password"
            placeholder="请输入新密码（至少 6 位）"
            size="large"
            show-password-on="click"
            :input-props="{ 'aria-label': '新密码' }"
          />
        </n-form-item>

        <n-form-item path="confirmPassword" label="确认新密码">
          <n-input
            v-model:value="formValue.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            size="large"
            show-password-on="click"
            :input-props="{ 'aria-label': '确认新密码' }"
            @keyup.enter="handleSubmit"
          />
        </n-form-item>

        <n-alert
          v-if="authStore.error"
          type="error"
          :show-icon="true"
          class="setup-error"
        >
          {{ authStore.error }}
        </n-alert>

        <div class="setup-actions">
          <n-button
            type="primary"
            size="large"
            block
            :loading="authStore.isLoading"
            :disabled="authStore.isLoading"
            @click="handleSubmit"
          >
            确认修改
          </n-button>

          <n-button
            quaternary
            size="small"
            class="skip-btn"
            @click="handleSkip"
          >
            暂不修改，进入系统
          </n-button>
        </div>
      </n-form>
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
  NAlert,
  useMessage,
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref<FormInst | null>(null)

const formValue = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const rules: FormRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' },
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string) => {
        return value === formValue.value.newPassword
      },
      message: '两次输入的密码不一致',
      trigger: 'blur',
    },
  ],
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  const result = await authStore.changePassword(
    formValue.value.currentPassword,
    formValue.value.newPassword,
  )

  if (result.success) {
    message.success('密码已修改，请使用新密码重新登录')
    router.push('/login')
  } else {
    message.error(result.message || '修改失败')
  }
}

function handleSkip() {
  authStore.requiresPasswordChange = false
  router.push('/')
}
</script>

<style scoped>
.setup-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1.5rem;
  background: var(--n-body-color);
}

.setup-card {
  width: 100%;
  max-width: 440px;
  padding: 2.5rem;
  border-radius: 1rem;
  background: var(--n-card-color);
  box-shadow: var(--n-box-shadow);
}

.setup-header {
  text-align: center;
  margin-bottom: 2rem;
}

.setup-icon {
  width: 3.5rem;
  height: 3.5rem;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--n-action-color);
  font-size: 1.5rem;
  color: var(--n-warning-color);
}

.setup-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  color: var(--n-text-color-base);
}

.setup-desc {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--n-text-color-3);
  margin: 0;
}

.setup-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setup-error {
  margin: 0.5rem 0;
}

.setup-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.skip-btn {
  align-self: center;
  color: var(--n-text-color-3);
}
</style>
