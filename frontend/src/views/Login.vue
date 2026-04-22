<template>
  <div class="login-container">
    <n-card title="CS2 Monitor 登录" class="login-card">
      <n-form
        ref="formRef"
        :model="formValue"
        :rules="rules"
        @submit.prevent="handleLogin"
      >
        <n-form-item label="密码" path="password">
          <n-input
            v-model:value="formValue.password"
            type="password"
            placeholder="请输入管理员密码"
            @keyup.enter="handleLogin"
          />
        </n-form-item>
        <n-form-item>
          <n-button
            type="primary"
            size="large"
            block
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import api from '@/api/index'

const router = useRouter()
const message = useMessage()
const formRef = ref<FormInst | null>(null)
const loading = ref(false)

const formValue = ref({
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

  loading.value = true
  try {
    const res = await api.login(formValue.value.password)
    const token = res.data.access_token
    localStorage.setItem('cs_monitor_token', token)
    message.success('登录成功')
    router.push('/')
  } catch (err: any) {
    const msg = err.response?.data?.detail || '登录失败'
    message.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: #f5f7fb;
}
.login-card {
  width: 360px;
}
</style>
