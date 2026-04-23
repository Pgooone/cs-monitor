<template>
  <div>
    <!-- 外观设置 -->
    <n-card title="外观设置" style="margin-bottom: 16px">
      <n-form label-placement="left" label-width="140" style="max-width: 600px">
        <n-form-item label="主题模式">
          <n-radio-group :value="themeMode" @update:value="setTheme">
            <n-space>
              <n-radio value="light">浅色</n-radio>
              <n-radio value="dark">深色</n-radio>
              <n-radio value="system">跟随系统</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="涨跌颜色">
          <n-radio-group :value="riseFallMode" @update:value="setRiseFall">
            <n-space>
              <n-radio value="china">中国（红涨绿跌）</n-radio>
              <n-radio value="international">国际（绿涨红跌）</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 通知设置 -->
    <n-card title="通知设置">
      <n-spin :show="loading">
        <n-form
          ref="formRef"
          :model="formData"
          label-placement="left"
          label-width="140"
          style="max-width: 600px"
        >
          <n-form-item label="默认通知渠道">
            <n-radio-group v-model:value="formData.notify_channel">
              <n-space>
                <n-radio value="wecom">企业微信</n-radio>
                <n-radio value="telegram">Telegram</n-radio>
                <n-radio value="serverchan">Server 酱</n-radio>
              </n-space>
            </n-radio-group>
          </n-form-item>

          <n-divider />

          <!-- 企业微信 -->
          <n-form-item label="企微 Webhook">
            <n-input
              v-model:value="formData.wecom_webhook_url"
              type="textarea"
              placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
              :rows="2"
            />
          </n-form-item>

          <!-- Telegram -->
          <n-form-item label="Bot Token">
            <n-input
              v-model:value="formData.telegram_bot_token"
              placeholder="123456:ABC-DEF..."
            />
          </n-form-item>
          <n-form-item label="Chat ID">
            <n-input
              v-model:value="formData.telegram_chat_id"
              placeholder="如 @channelname 或 数字 ID"
            />
          </n-form-item>

          <!-- Server 酱 -->
          <n-form-item label="SendKey">
            <n-input
              v-model:value="formData.serverchan_sendkey"
              placeholder="SCTxxxxx..."
            />
          </n-form-item>

          <n-space justify="end">
            <n-button :loading="saving" type="primary" @click="handleSave">
              保存配置
            </n-button>
            <n-button :loading="testing" @click="handleTest">
              测试通知
            </n-button>
          </n-space>
        </n-form>
      </n-spin>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  NCard,
  NSpin,
  NForm,
  NFormItem,
  NInput,
  NRadio,
  NRadioGroup,
  NSpace,
  NButton,
  NDivider,
  useMessage,
} from 'naive-ui'
import api from '@/api'
import { useTheme } from '@/composables/useTheme'

const message = useMessage()
const { themeMode, riseFallMode, setTheme, setRiseFall } = useTheme()

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)

const formData = ref({
  notify_channel: 'wecom',
  wecom_webhook_url: '',
  telegram_bot_token: '',
  telegram_chat_id: '',
  serverchan_sendkey: '',
})

async function loadSettings() {
  loading.value = true
  try {
    const { data } = await api.getNotifySettings()
    formData.value = {
      notify_channel: data.notify_channel || 'wecom',
      wecom_webhook_url: data.wecom_webhook_url || '',
      telegram_bot_token: data.telegram_bot_token || '',
      telegram_chat_id: data.telegram_chat_id || '',
      serverchan_sendkey: data.serverchan_sendkey || '',
    }
  } catch (e) {
    message.error('加载配置失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await api.updateNotifySettings({
      notify_channel: formData.value.notify_channel,
      wecom_webhook_url: formData.value.wecom_webhook_url,
      telegram_bot_token: formData.value.telegram_bot_token,
      telegram_chat_id: formData.value.telegram_chat_id,
      serverchan_sendkey: formData.value.serverchan_sendkey,
    })
    message.success('配置已保存')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleTest() {
  testing.value = true
  try {
    await api.testNotify(formData.value.notify_channel)
    message.success('测试通知已发送')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '测试通知发送失败')
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>
