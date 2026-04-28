<template>
  <div class="settings">
    <!-- 大标题 -->
    <div class="settings__hero">
      <h2 class="settings__title">系统<span class="text-brand">配置</span></h2>
      <p class="settings__desc">管理 SteamDT API 令牌、WebHook 推送地址以及终端偏好。</p>
    </div>

    <!-- API 访问令牌 -->
    <section class="settings__section">
      <div class="settings__section-header">
        <Zap class="w-4 h-4 text-brand" />
        <h3 class="settings__section-title">API 访问令牌</h3>
      </div>
      <div class="glass-card settings__section-card">
        <div class="settings__field">
          <label class="settings__field-label">SteamDT API Token</label>
          <div class="settings__token-row">
            <input
              type="password"
              :value="systemInfo?.api_token_masked || 'sk-xxxxxxxxxxxxxxxxxxxxxxxx'"
              class="settings__token-input font-mono-num"
              readonly
            />
            <button class="btn-outline px-6">配置令牌</button>
          </div>
        </div>
        <div class="settings__divider" />
        <div class="settings__toggle-row">
          <div>
            <div class="settings__toggle-title">数据库持久化 (SQLite)</div>
            <p class="settings__toggle-desc">启用后本地记录饰品历史价格数据。</p>
          </div>
          <div class="settings__toggle settings__toggle--on">
            <div class="settings__toggle-knob" />
          </div>
        </div>
      </div>
    </section>

    <!-- 消息通知配置 -->
    <section class="settings__section">
      <div class="settings__section-header">
        <Bell class="w-4 h-4 text-brand" />
        <h3 class="settings__section-title">消息通知配置</h3>
      </div>
      <div class="settings__notify-grid">
        <div class="glass-card settings__notify-card">
          <div class="settings__notify-header">
            <h4 class="settings__notify-name">Telegram Bot</h4>
            <div
              class="settings__status-dot"
              :class="isTelegramConfigured ? 'settings__status-dot--active' : ''"
            />
          </div>
          <p class="settings__notify-status">
            推送状态: {{ isTelegramConfigured ? '活跃' : '未启用' }}
          </p>
          <button class="btn-outline w-full py-2" @click="handleTest('telegram')">测试通道</button>
        </div>
        <div class="glass-card settings__notify-card">
          <div class="settings__notify-header">
            <h4 class="settings__notify-name">企业微信 / Server酱</h4>
            <div
              class="settings__status-dot"
              :class="isWecomConfigured ? 'settings__status-dot--active' : ''"
            />
          </div>
          <p class="settings__notify-status">
            推送状态: {{ isWecomConfigured ? '活跃' : '未启用' }}
          </p>
          <button class="btn-outline w-full py-2" @click="handleTest('wecom')">测试通道</button>
        </div>
      </div>
    </section>

    <!-- 界面显示效果 -->
    <section class="settings__section">
      <div class="settings__section-header">
        <LayoutGrid class="w-4 h-4 text-brand" />
        <h3 class="settings__section-title">界面显示效果</h3>
      </div>
      <div class="glass-card settings__display-card">
        <div class="settings__toggle-row">
          <div>
            <div class="settings__toggle-title">深色模式</div>
            <p class="settings__toggle-desc">启用暗色主题以减少眼部疲劳。</p>
          </div>
          <div
            class="settings__toggle"
            :class="{ 'settings__toggle--on': isDark }"
            @click="setTheme(isDark ? 'light' : 'dark')"
          >
            <div class="settings__toggle-knob" />
          </div>
        </div>
        <div class="settings__divider" />
        <div class="settings__toggle-row">
          <div>
            <div class="settings__toggle-title">等宽数字模式 (Tabular Nums)</div>
            <p class="settings__toggle-desc">饰品价格变动时，数字布局将保持绝对对齐。</p>
          </div>
          <div class="settings__toggle settings__toggle--on">
            <div class="settings__toggle-knob" />
          </div>
        </div>
      </div>
    </section>

    <!-- 涨跌颜色设置 -->
    <section class="settings__section">
      <div class="settings__section-header">
        <Palette class="w-4 h-4 text-brand" />
        <h3 class="settings__section-title">涨跌颜色习惯</h3>
      </div>
      <div class="glass-card settings__section-card">
        <div class="settings__rise-fall-selector">
          <div
            v-for="mode in riseFallModes"
            :key="mode.value"
            class="settings__rise-fall-option"
            :class="{ 'settings__rise-fall-option--active': riseFallMode === mode.value }"
            @click="setRiseFall(mode.value)"
          >
            <div class="settings__rise-fall-preview">
              <span :style="{ color: mode.upColor }">&#9650; +2.5%</span>
              <span :style="{ color: mode.downColor }">&#9660; -1.8%</span>
            </div>
            <div class="settings__rise-fall-label">{{ mode.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据管理 -->
    <section class="settings__section">
      <div class="settings__section-header">
        <Database class="w-4 h-4 text-brand" />
        <h3 class="settings__section-title">数据管理</h3>
      </div>
      <div class="glass-card settings__section-card">
        <div class="settings__data-info">
          <div class="settings__data-field">
            <span class="settings__data-label">数据库路径</span>
            <span class="settings__data-value font-mono-num">{{ systemInfo?.db_path || '—' }}</span>
          </div>
          <div class="settings__data-field">
            <span class="settings__data-label">数据库大小</span>
            <span class="settings__data-value font-mono-num">{{ systemInfo?.db_size_human || '—' }}</span>
          </div>
        </div>
        <div class="settings__data-actions">
          <button class="btn-outline" @click="handleExportDb">
            <Download class="w-4 h-4" />
            导出数据库
          </button>
        </div>
        <div class="settings__divider" />
        <div class="settings__danger">
          <div class="settings__danger-title">
            <AlertTriangle class="w-4 h-4" />
            危险操作
          </div>
          <button class="settings__danger-btn" @click="showClearConfirm = true">
            <Trash2 class="w-4 h-4" />
            清空所有监控数据
          </button>
        </div>
      </div>
    </section>

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
        <p class="settings__danger-warn">
          此操作将清空所有价格记录、告警记录和归档数据，但保留监控清单和追踪配置。该操作不可恢复！
        </p>
        <div class="mt-4">
          请输入 <strong>CONFIRM</strong> 以确认：
          <n-input v-model:value="clearConfirmText" class="mt-2" placeholder="CONFIRM" />
        </div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  NInput,
  NModal,
  useMessage,
} from 'naive-ui'
import {
  Zap,
  Bell,
  LayoutGrid,
  Database,
  Download,
  Trash2,
  AlertTriangle,
  Palette,
} from 'lucide-vue-next'
import api from '@/api'
import { useTheme } from '@/composables/useTheme'
import { toastSuccess, toastError } from '@/composables/useToast'

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
const { riseFallMode, isDark, setTheme, setRiseFall } = useTheme()
const testing = ref(false)
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
  api_token_masked?: string
} | null>(null)

const formData = ref({
  notify_channel: 'wecom',
  wecom_webhook_url: '',
  telegram_bot_token: '',
  telegram_chat_id: '',
  serverchan_sendkey: '',
})

const isTelegramConfigured = computed(() => {
  return !!formData.value.telegram_bot_token && !!formData.value.telegram_chat_id
})

const isWecomConfigured = computed(() => {
  return !!formData.value.wecom_webhook_url || !!formData.value.serverchan_sendkey
})

async function loadSettings() {
  try {
    const { data } = await api.getNotifySettings()
    formData.value = {
      notify_channel: data.notify_channel || 'wecom',
      wecom_webhook_url: data.wecom_webhook_url || '',
      telegram_bot_token: data.telegram_bot_token || '',
      telegram_chat_id: data.telegram_chat_id || '',
      serverchan_sendkey: data.serverchan_sendkey || '',
    }
  } catch {
    toastError('加载配置失败')
  }
}

async function loadSystemInfo() {
  try {
    const { data } = await api.systemInfo()
    systemInfo.value = data
  } catch (e) {
    console.error(e)
  }
}

async function handleTest(channel: string) {
  testing.value = true
  try {
    await api.testNotify(channel)
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
.settings {
  display: flex;
  flex-direction: column;
  gap: 3rem;
  max-width: 56rem;
  margin: 0 auto;
  padding-bottom: 5rem;
}

/* 大标题 */
.settings__hero {
  margin-bottom: 0;
}

.settings__title {
  font-size: 3rem;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: #ffffff;
  margin: 0;
}

.settings__desc {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin: 1rem 0 0 0;
}

/* Section */
.settings__section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.settings__section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.settings__section-title {
  font-size: 1.125rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.settings__section-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Field */
.settings__field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.settings__field-label {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

.settings__token-row {
  display: flex;
  gap: 0.75rem;
}

.settings__token-input {
  flex: 1;
  background: #0f0f12;
  border: 1px solid #1f1f23;
  padding: 0.625rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  color: #ffffff;
  outline: none;
}

.settings__divider {
  height: 1px;
  background: #1f1f23;
}

/* Toggle */
.settings__toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.settings__toggle-title {
  font-weight: 700;
  color: #ffffff;
  font-size: 0.875rem;
}

.settings__toggle-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
  margin: 0.25rem 0 0 0;
}

.settings__toggle {
  width: 3rem;
  height: 1.5rem;
  background: #2d2d35;
  border-radius: 9999px;
  position: relative;
  padding: 0.25rem;
  cursor: pointer;
  transition: background 200ms;
  flex-shrink: 0;
}

.settings__toggle--on {
  background: #6366f1;
}

.settings__toggle-knob {
  width: 1rem;
  height: 1rem;
  background: #ffffff;
  border-radius: 9999px;
  transition: transform 200ms;
}

.settings__toggle--on .settings__toggle-knob {
  transform: translateX(1.5rem);
}

/* Notify grid */
.settings__notify-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .settings__notify-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.settings__notify-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.settings__notify-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.settings__notify-name {
  font-weight: 700;
  color: #ffffff;
  font-size: 0.875rem;
  margin: 0;
}

.settings__status-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #94a3b8;
}

.settings__status-dot--active {
  background: #22c55e;
  box-shadow: 0 0 8px #22c55e;
}

.settings__notify-status {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  margin: 0;
}

/* Display card */
.settings__display-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Rise/fall selector */
.settings__rise-fall-selector {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.settings__rise-fall-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-radius: 0.75rem;
  border: 2px solid #1f1f23;
  cursor: pointer;
  transition: all 200ms;
  min-width: 160px;
}

.settings__rise-fall-option:hover {
  border-color: rgba(99, 102, 241, 0.5);
}

.settings__rise-fall-option--active {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.settings__rise-fall-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  font-weight: 600;
}

.settings__rise-fall-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #94a3b8;
}

.settings__rise-fall-option--active .settings__rise-fall-label {
  color: #6366f1;
  font-weight: 600;
}

/* Data */
.settings__data-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.settings__data-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.settings__data-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.settings__data-value {
  font-size: 0.875rem;
  color: #ffffff;
  word-break: break-all;
}

.settings__data-actions {
  display: flex;
  gap: 0.75rem;
}

.settings__danger {
  border: 1px solid #ef4444;
  border-radius: 0.75rem;
  padding: 1rem;
  background: rgba(239, 68, 68, 0.04);
}

.settings__danger-title {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ef4444;
  margin-bottom: 0.75rem;
}

.settings__danger-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #ef4444;
  background: transparent;
  color: #ef4444;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 200ms;
}

.settings__danger-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

.settings__danger-warn {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  background: rgba(239, 68, 68, 0.06);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
}

.clear-confirm-content {
  min-width: 320px;
}

/* 浅色模式 */
html:not(.dark) .settings__title {
  color: #0f172a;
}

html:not(.dark) .settings__desc {
  color: #64748b;
}

html:not(.dark) .settings__section-title {
  color: #0f172a;
}

html:not(.dark) .settings__toggle-title {
  color: #0f172a;
}

html:not(.dark) .settings__toggle-desc {
  color: #64748b;
}

html:not(.dark) .settings__toggle {
  background: #e2e8f0;
}

html:not(.dark) .settings__divider {
  background: #e2e8f0;
}

html:not(.dark) .settings__token-input {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #0f172a;
}

html:not(.dark) .settings__notify-name {
  color: #0f172a;
}

html:not(.dark) .settings__data-value {
  color: #0f172a;
}

html:not(.dark) .settings__field-label {
  color: #64748b;
}

html:not(.dark) .settings__notify-status {
  color: #64748b;
}

html:not(.dark) .settings__data-label {
  color: #64748b;
}

html:not(.dark) .settings__rise-fall-option {
  border-color: #e2e8f0;
}

html:not(.dark) .settings__rise-fall-label {
  color: #64748b;
}

html:not(.dark) .settings__rise-fall-option--active .settings__rise-fall-label {
  color: #6366f1;
}

html:not(.dark) .settings__danger-warn {
  color: #dc2626;
}
</style>
