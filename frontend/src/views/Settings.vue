<template>
  <div class="settings-page">
    <page-header title="系统设置" />

    <div class="settings-layout">
      <!-- 左侧子导航 -->
      <div class="settings-nav">
        <n-menu
          v-model:value="activeSection"
          :options="menuOptions"
          :collapsed-width="64"
          :icon-size="20"
          @update:value="activeSection = $event"
        />
      </div>

      <!-- 右侧内容 -->
      <div class="settings-content">
        <!-- 通用 -->
        <div v-if="activeSection === 'general'">
          <n-card title="外观设置" class="settings-card">
            <!-- 主题模式 -->
            <div class="setting-section">
              <div class="setting-section__label">主题模式</div>
              <div class="theme-selector">
                <div
                  v-for="mode in themeModes"
                  :key="mode.value"
                  class="theme-option"
                  :class="{ 'theme-option--active': themeMode === mode.value }"
                  @click="setTheme(mode.value)"
                >
                  <div class="theme-option__icon" :style="{ background: mode.bg, color: mode.color }"">
                    <component :is="mode.icon" />
                  </div>
                  <div class="theme-option__label">{{ mode.label }}</div>
                </div>
              </div>
            </div>

            <n-divider />

            <!-- 涨跌颜色 -->
            <div class="setting-section">
              <div class="setting-section__label">涨跌颜色</div>
              <div class="rise-fall-selector">
                <div
                  v-for="mode in riseFallModes"
                  :key="mode.value"
                  class="rise-fall-option"
                  :class="{ 'rise-fall-option--active': riseFallMode === mode.value }"
                  @click="setRiseFall(mode.value)"
                >
                  <div class="rise-fall-option__preview">
                    <span class="rise-fall-option__up" :style="{ color: mode.upColor }"
                    >&#9650; +2.5%</span>
                    <span class="rise-fall-option__down" :style="{ color: mode.downColor }"
                    >&#9660; -1.8%</span>
                  </div>
                  <div class="rise-fall-option__label">{{ mode.label }}</div>
                </div>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 通知 -->
        <div v-if="activeSection === 'notify'">
          <n-card title="通知配置">
            <!-- 步骤条 -->
            <n-steps :current="notifyStep" size="small" class="mb-6">
              <n-step title="选择渠道" />
              <n-step title="填写配置" />
              <n-step title="测试发送" />
            </n-steps>

            <div class="notify-layout">
              <div class="notify-form">
                <n-spin :show="loading">
                  <n-form
                    ref="notifyFormRef"
                    :model="formData"
                    label-placement="left"
                    label-width="120"
                  >
                    <!-- Step 1 -->
                    <div v-if="notifyStep === 0">
                      <n-form-item label="默认渠道">
                        <n-radio-group v-model:value="formData.notify_channel">
                          <n-space vertical>
                            <n-radio value="wecom">
                              <span class="radio-with-icon">
                                <ChatbubbleOutline class="radio-icon" />
                                企业微信机器人
                              </span>
                            </n-radio>
                            <n-radio value="telegram">
                              <span class="radio-with-icon">
                                <PaperPlaneOutline class="radio-icon" />
                                Telegram Bot
                              </span>
                            </n-radio>
                            <n-radio value="serverchan">
                              <span class="radio-with-icon">
                                <NotificationsOutline class="radio-icon" />
                                Server 酱
                              </span>
                            </n-radio>
                          </n-space>
                        </n-radio-group>
                      </n-form-item>
                    </div>

                    <!-- Step 2 -->
                    <div v-if="notifyStep === 1">
                      <div v-if="formData.notify_channel === 'wecom'">
                        <n-form-item label="Webhook URL">
                          <n-input
                            v-model:value="formData.wecom_webhook_url"
                            type="textarea"
                            placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
                            :rows="2"
                          />
                        </n-form-item>
                      </div>

                      <div v-else-if="formData.notify_channel === 'telegram'">
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
                      </div>

                      <div v-else-if="formData.notify_channel === 'serverchan'">
                        <n-form-item label="SendKey">
                          <n-input
                            v-model:value="formData.serverchan_sendkey"
                            placeholder="SCTxxxxx..."
                          />
                        </n-form-item>
                      </div>
                    </div>

                    <!-- Step 3 -->
                    <div v-if="notifyStep === 2">
                      <n-alert type="info" title="测试通知" class="mb-4">
                        配置完成后，点击下方按钮发送一条测试消息，确认通知渠道正常工作。
                      </n-alert>
                      <n-button
                        :loading="testing"
                        type="primary"
                        block
                        @click="handleTest"
                      >
                        <template #icon><SendOutline /></template>
                        发送测试通知
                      </n-button>
                    </div>
                  </n-form>
                </n-spin>

                <n-space class="mt-4" justify="space-between">
                  <n-space>
                    <n-button v-if="notifyStep > 0" @click="notifyStep--">上一步</n-button>
                  </n-space>
                  <n-space>
                    <n-button v-if="notifyStep < 2" type="primary" @click="notifyStep++">下一步</n-button>
                    <n-button
                      v-else
                      :loading="saving"
                      type="primary"
                      @click="handleSave"
                    >
                      保存配置
                    </n-button>
                  </n-space>
                </n-space>
              </div>

              <!-- 实时预览 -->
              <div class="notify-preview">
                <div class="preview-label">配置预览</div>
                <div class="preview-card">
                  <div class="preview-header">
                    <span class="preview-channel">{{ channelLabel }}</span>
                    <n-tag
                      :type="isChannelConfigured ? 'success' : 'warning'"
                      size="small"
                      round
                    >
                      {{ isChannelConfigured ? '已配置' : '未配置' }}
                    </n-tag>
                  </div>
                  <div class="preview-body">
                    <div v-if="formData.notify_channel === 'wecom'">
                      <div class="preview-field">
                        <span class="preview-field-label">Webhook</span>
                        <span class="preview-field-value">
                          {{ maskSecret(formData.wecom_webhook_url) || '未填写' }}
                        </span>
                      </div>
                    </div>
                    <div v-else-if="formData.notify_channel === 'telegram'">
                      <div class="preview-field">
                        <span class="preview-field-label">Token</span>
                        <span class="preview-field-value">
                          {{ maskSecret(formData.telegram_bot_token) || '未填写' }}
                        </span>
                      </div>
                      <div class="preview-field">
                        <span class="preview-field-label">Chat ID</span>
                        <span class="preview-field-value">
                          {{ formData.telegram_chat_id || '未填写' }}
                        </span>
                      </div>
                    </div>
                    <div v-else-if="formData.notify_channel === 'serverchan'">
                      <div class="preview-field">
                        <span class="preview-field-label">SendKey</span>
                        <span class="preview-field-value">
                          {{ maskSecret(formData.serverchan_sendkey) || '未填写' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 监控 -->
        <div v-if="activeSection === 'monitor'">
          <n-card title="监控概览">
            <div v-if="systemLoading" class="space-y-4">
              <skeleton-card v-for="i in 2" :key="i" />
            </div>
            <div v-else class="monitor-stats">
              <div class="stat-item">
                <div class="stat-value">{{ systemInfo?.watchlist_count || 0 }}</div>
                <div class="stat-label">监控清单项</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ systemInfo?.extreme_track_count || 0 }}</div>
                <div class="stat-label">极致追踪项</div>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 数据 -->
        <div v-if="activeSection === 'data'">
          <n-card title="数据目录">
            <div v-if="systemLoading" class="space-y-4">
              <skeleton-card />
            </div>
            <div v-else
              >
              <div class="data-info">
                <div class="data-field">
                  <span class="data-field-label">数据库路径</span>
                  <span class="data-field-value">{{ systemInfo?.db_path || '—' }}</span>
                </div>
                <div class="data-field">
                  <span class="data-field-label">数据目录</span>
                  <span class="data-field-value">{{ systemInfo?.data_dir || '—' }}</span>
                </div>
                <div class="data-field">
                  <span class="data-field-label">数据库大小</span>
                  <span class="data-field-value">{{ systemInfo?.db_size_human || '—' }}</span>
                </div>
              </div>

              <n-space class="mt-4">
                <n-button @click="handleExportDb">
                  <template #icon><DownloadOutline /></template>
                  导出数据库
                </n-button>
              </n-space>

              <n-divider />

              <!-- 危险操作 -->
              <div class="danger-zone">
                <div class="danger-title"><WarningOutline /> 危险操作</div>
                <n-button
                  type="error"
                  ghost
                  @click="showClearConfirm = true"
                >
                  <template #icon><TrashOutline /></template>
                  清空所有监控数据
                </n-button>
              </div>
            </div>
          </n-card>
        </div>

        <!-- 关于 -->
        <div v-if="activeSection === 'about'">
          <n-card title="关于 CS2 Monitor">
            <div class="about-content">
              <div class="about-logo">
                <div class="about-logo-icon">CM</div>
              </div>
              <div class="about-version">版本 {{ systemInfo?.version || '1.0.0' }}</div>
              <div class="about-desc">
                CS2 饰品价格波动监控系统 — 基于 SteamDT API 的价格监控工具，支持 CLI 监控 + Web 仪表盘双模式。
              </div>
              <n-divider />
              <div class="about-links">
                <n-button text tag="a" href="https://github.com" target="_blank">
                  <template #icon><LogoGithub /></template>
                  GitHub
                </n-button>
              </div>
            </div>
          </n-card>
        </div>
      </div>
    </div>

    <!-- 清空确认弹窗 -->
    <n-modal
      v-model:show="showClearConfirm"
      preset="dialog"
      title="确认清空数据"
      type="error"
      positive-text="确认清空"
      negative-text="取消"
      :positive-loading="clearing"
      @positive-click="handleClearDb"
    >
      <div class="clear-confirm-content">
        <n-alert type="error">
          此操作将清空所有价格记录、告警记录和归档数据，但保留监控清单和追踪配置。该操作不可恢复！
        </n-alert>
        <div class="mt-4">
          请输入 <strong>CONFIRM</strong> 以确认：
          <n-input v-model:value="clearConfirmText" class="mt-2" placeholder="CONFIRM" />
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, markRaw } from 'vue'
import {
  NCard,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NSpace,
  NRadio,
  NRadioGroup,
  NTag,
  NMenu,
  NSteps,
  NStep,
  NSpin,
  NDivider,
  NAlert,
  NModal,
  useMessage,
} from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  SunnyOutline,
  MoonOutline,
  DesktopOutline,
  ChatbubbleOutline,
  PaperPlaneOutline,
  NotificationsOutline,
  SendOutline,
  DownloadOutline,
  WarningOutline,
  TrashOutline,
  LogoGithub,
  SettingsOutline,
  PulseOutline,
  FolderOpenOutline,
  InformationCircleOutline,
} from '@vicons/ionicons5'
import { h } from 'vue'
import api from '@/api'
import { useTheme } from '@/composables/useTheme'
import { toastSuccess, toastError } from '@/composables/useToast'
import PageHeader from '@/components/layout/PageHeader.vue'
import SkeletonCard from '@/components/base/SkeletonCard.vue'

const themeModes = [
  {
    value: 'light' as const,
    label: '浅色',
    icon: markRaw(SunnyOutline),
    bg: '#fef3c7',
    color: '#d97706',
  },
  {
    value: 'dark' as const,
    label: '深色',
    icon: markRaw(MoonOutline),
    bg: '#1e1b4b',
    color: '#a5b4fc',
  },
  {
    value: 'system' as const,
    label: '跟随系统',
    icon: markRaw(DesktopOutline),
    bg: '#e0e7ff',
    color: '#4f46e5',
  },
]

const riseFallModes = [
  {
    value: 'china' as const,
    label: '中国（红涨绿跌）',
    upColor: '#ef4444',
    downColor: '#10b981',
  },
  {
    value: 'international' as const,
    label: '国际（绿涨红跌）',
    upColor: '#10b981',
    downColor: '#ef4444',
  },
]

const message = useMessage()
const { themeMode, riseFallMode, setTheme, setRiseFall } = useTheme()

const activeSection = ref('general')
const notifyStep = ref(0)

const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const systemLoading = ref(false)
const clearing = ref(false)
const showClearConfirm = ref(false)
const clearConfirmText = ref('')

const systemInfo = ref<{
  version: string
  db_path: string
  db_size: number
  db_size_human: string
  data_dir: string
  watchlist_count: number
  extreme_track_count: number
} | null>(null)

const formData = ref({
  notify_channel: 'wecom',
  wecom_webhook_url: '',
  telegram_bot_token: '',
  telegram_chat_id: '',
  serverchan_sendkey: '',
})

const menuOptions: MenuOption[] = [
  {
    label: '通用',
    key: 'general',
    icon: () => h(SettingsOutline),
  },
  {
    label: '通知',
    key: 'notify',
    icon: () => h(NotificationsOutline),
  },
  {
    label: '监控',
    key: 'monitor',
    icon: () => h(PulseOutline),
  },
  {
    label: '数据',
    key: 'data',
    icon: () => h(FolderOpenOutline),
  },
  {
    label: '关于',
    key: 'about',
    icon: () => h(InformationCircleOutline),
  },
]

const channelLabel = computed(() => {
  const map: Record<string, string> = {
    wecom: '企业微信',
    telegram: 'Telegram',
    serverchan: 'Server 酱',
  }
  return map[formData.value.notify_channel] || formData.value.notify_channel
})

const isChannelConfigured = computed(() => {
  if (formData.value.notify_channel === 'wecom') return !!formData.value.wecom_webhook_url
  if (formData.value.notify_channel === 'telegram') return !!formData.value.telegram_bot_token && !!formData.value.telegram_chat_id
  if (formData.value.notify_channel === 'serverchan') return !!formData.value.serverchan_sendkey
  return false
})

function maskSecret(str: string): string {
  if (!str) return ''
  if (str.length <= 12) return '***'
  return str.slice(0, 6) + '...' + str.slice(-4)
}

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
    toastError('加载配置失败')
  } finally {
    loading.value = false
  }
}

async function loadSystemInfo() {
  systemLoading.value = true
  try {
    const { data } = await api.systemInfo()
    systemInfo.value = data
  } catch (e) {
    console.error(e)
  } finally {
    systemLoading.value = false
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
    toastSuccess('配置已保存')
  } catch (e: any) {
    toastError(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleTest() {
  testing.value = true
  try {
    await api.testNotify(formData.value.notify_channel)
    toastSuccess('测试通知已发送')
  } catch (e: any) {
    toastError(e?.response?.data?.detail || '测试通知发送失败')
  } finally {
    testing.value = false
  }
}

function handleExportDb() {
  window.open('/api/settings/db/export', '_blank')
}

async function handleClearDb() {
  if (clearConfirmText.value !== 'CONFIRM') {
    message.error('请输入 CONFIRM 以确认操作')
    return
  }
  clearing.value = true
  try {
    await api.clearDb()
    toastSuccess('数据已清空')
    showClearConfirm.value = false
    clearConfirmText.value = ''
    loadSystemInfo()
  } catch (e: any) {
    toastError(e?.response?.data?.detail || '清空失败')
  } finally {
    clearing.value = false
  }
}

onMounted(() => {
  loadSettings()
  loadSystemInfo()
})
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
}

.settings-layout {
  display: flex;
  gap: 1.5rem;
}

.settings-nav {
  flex-shrink: 0;
  width: 200px;
}

.settings-content {
  flex: 1;
  min-width: 0;
}

.settings-card {
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
  border-radius: 1rem;
}

/* ===== 设置项区域 ===== */
.setting-section {
  padding: 0.5rem 0;
}

.setting-section__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--cs-text-primary);
  margin-bottom: 1rem;
}

/* ===== 主题选择器 ===== */
.theme-selector {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 0.875rem;
  border: 2px solid var(--cs-border-light);
  background: var(--cs-bg-card);
  cursor: pointer;
  transition: all var(--cs-transition-fast);
  min-width: 100px;
}

.theme-option:hover {
  border-color: var(--cs-brand-primary);
  transform: translateY(-1px);
}

.theme-option--active {
  border-color: var(--cs-brand-primary);
  box-shadow: 0 0 0 3px rgba(46, 91, 255, 0.15);
}

.theme-option__icon {
  width: 40px;
  height: 40px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.theme-option__label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--cs-text-secondary);
}

.theme-option--active .theme-option__label {
  color: var(--cs-brand-primary);
  font-weight: 600;
}

/* ===== 涨跌颜色选择器 ===== */
.rise-fall-selector {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.rise-fall-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 0.875rem;
  border: 2px solid var(--cs-border-light);
  background: var(--cs-bg-card);
  cursor: pointer;
  transition: all var(--cs-transition-fast);
  min-width: 160px;
}

.rise-fall-option:hover {
  border-color: var(--cs-brand-primary);
  transform: translateY(-1px);
}

.rise-fall-option--active {
  border-color: var(--cs-brand-primary);
  box-shadow: 0 0 0 3px rgba(46, 91, 255, 0.15);
}

.rise-fall-option__preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  font-weight: 600;
}

.rise-fall-option__up,
.rise-fall-option__down {
  transition: color var(--cs-transition-fast);
}

.rise-fall-option__label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--cs-text-secondary);
}

.rise-fall-option--active .rise-fall-option__label {
  color: var(--cs-brand-primary);
  font-weight: 600;
}

.notify-layout {
  display: flex;
  gap: 1.5rem;
}

.notify-form {
  flex: 1;
  min-width: 0;
}

.notify-preview {
  flex-shrink: 0;
  width: 260px;
}

.preview-label {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.preview-card {
  background: var(--cs-bg-hover);
  border-radius: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--cs-border-light);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.preview-channel {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--cs-text-primary);
}

.preview-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-field {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.preview-field-label {
  font-size: 0.6875rem;
  color: var(--cs-text-muted);
}

.preview-field-value {
  font-size: 0.8125rem;
  color: var(--cs-text-secondary);
  font-family: 'JetBrains Mono', monospace;
  word-break: break-all;
}

.monitor-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}

.stat-item {
  background: var(--cs-bg-hover);
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: center;
  border: 1px solid var(--cs-border-light);
  transition: transform var(--cs-transition-fast);
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--cs-brand-primary);
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
  margin-top: 0.25rem;
}

.data-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.data-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.data-field-label {
  font-size: 0.75rem;
  color: var(--cs-text-muted);
}

.data-field-value {
  font-size: 0.875rem;
  color: var(--cs-text-secondary);
  font-family: 'JetBrains Mono', monospace;
  word-break: break-all;
}

.danger-zone {
  border: 1px solid #ef4444;
  border-radius: 0.75rem;
  padding: 1rem;
  background: rgba(239, 68, 68, 0.04);
}

.danger-title {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ef4444;
  margin-bottom: 0.75rem;
}

.about-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 0;
}

.about-logo {
  margin-bottom: 1rem;
}

.about-logo-icon {
  width: 64px;
  height: 64px;
  border-radius: 1rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.about-version {
  font-size: 1rem;
  font-weight: 600;
  color: var(--cs-text-primary);
}

.about-desc {
  font-size: 0.875rem;
  color: var(--cs-text-muted);
  max-width: 400px;
  margin-top: 0.5rem;
  line-height: 1.6;
}

.about-links {
  margin-top: 1rem;
}

.clear-confirm-content {
  min-width: 320px;
}

@media (max-width: 1023px) {
  .settings-layout {
    flex-direction: column;
  }
  .settings-nav {
    width: 100%;
  }
  .notify-layout {
    flex-direction: column;
  }
  .notify-preview {
    width: 100%;
  }
  .theme-selector,
  .rise-fall-selector {
    justify-content: center;
  }
}
</style>
