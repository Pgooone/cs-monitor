<template>
  <div>
    <page-header title="极致追踪">
      <template #actions>
        <n-button type="primary" @click="openCreateModal">
          <template #icon><AddOutline /></template>
          添加追踪
        </n-button>
      </template>
    </page-header>

    <!-- 空态 -->
    <div v-if="store.loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <skeleton-card v-for="i in 4" :key="i" />
    </div>

    <div v-else-if="store.items.length === 0" class="empty-state">
      <n-empty description="暂无追踪配置" size="huge">
        <template #icon>
          <TrailSignOutline style="font-size: 48px; opacity: 0.4" />
        </template>
        <template #extra>
          <n-button type="primary" @click="openCreateModal">添加第一个追踪</n-button>
        </template>
      </n-empty>
    </div>

    <!-- 卡片网格 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
        v-for="item in store.items"
        :key="rowKey(item)"
        class="track-card"
        :class="{ 'track-card--disabled': !item.enabled }"
      >
        <div class="track-card__header">
          <div class="track-card__title">
            {{ item.display_name || item.market_hash_name }}
          </div>
          <n-tag
            :type="item.enabled ? 'success' : 'default'"
            size="small"
            round
          >
            {{ item.enabled ? '运行中' : '已停止' }}
          </n-tag>
        </div>

        <div class="track-card__platform">
          <span class="platform-badge">{{ item.platform }}</span>
          <span class="interval-text">{{ item.interval_seconds }}s 轮询</span>
        </div>

        <!-- 追踪强度进度条 -->
        <div class="track-card__progress">
          <div class="progress-label">
            <span>追踪强度</span>
            <span>{{ intensityPercent(item) }}%</span>
          </div>
          <n-progress
            :percentage="intensityPercent(item)"
            :show-indicator="false"
            :color="item.enabled ? '#3b82f6' : '#a3a3a3'"
            :height="6"
            :border-radius="3"
          />
        </div>

        <!-- 价格追踪配置 -->
        <div class="track-card__config">
          <div class="config-row">
            <span class="config-label">价格追踪</span>
            <span class="config-value">
              {{ item.price_track_enabled ? (item.price_change_mode === 'any' ? '任何变动' : `超 ${item.price_threshold_percent}%`) : '关闭' }}
            </span>
          </div>
          <div class="config-row">
            <span class="config-label">数量追踪</span>
            <span class="config-value">
              {{ item.quantity_track_enabled ? (item.quantity_change_mode === 'any' ? '任何变动' : `超 ${item.quantity_threshold_percent}%`) : '关闭' }}
            </span>
          </div>
        </div>

        <!-- 实时数据 -->
        <div v-if="snapshots[rowKey(item)]" class="track-card__realtime">
          <div class="realtime-label">最新数据</div>
          <div class="realtime-row">
            <span class="realtime-price">
              ¥{{ snapshots[rowKey(item)]?.price?.toFixed(2) || '—' }}
            </span>
            <span class="realtime-quantity">
              {{ snapshots[rowKey(item)]?.quantity ?? '—' }} 个
            </span>
          </div>
          <div class="realtime-time">
            {{ formatTime(snapshots[rowKey(item)]?.recorded_at) }}
          </div>
        </div>

        <!-- 操作 -->
        <div class="track-card__actions">
          <n-button
            text
            size="small"
            :type="item.enabled ? 'warning' : 'success'"
            @click="handleToggle(item)"
          >
            {{ item.enabled ? '停止' : '启动' }}
          </n-button>
          <n-button text size="small" type="primary" @click="openEditModal(item)">
            编辑
          </n-button>
          <n-button text size="small" type="error" @click="openDeleteModal(item)">
            删除
          </n-button>
        </div>
      </div>
    </div>

    <!-- 分步骤添加/编辑弹窗 -->
    <n-modal
      v-model:show="modalVisible"
      :title="isEditing ? '编辑追踪配置' : '添加追踪配置'"
      preset="card"
      style="width: 560px"
      :mask-closable="false"
    >
      <n-steps :current="stepCurrent" size="small" class="mb-6">
        <n-step title="选饰品" />
        <n-step title="选平台" />
        <n-step title="设定类型" />
        <n-step title="阈值与高级" />
      </n-steps>

      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="120"
      >
        <!-- Step 1: 选饰品 -->
        <div v-if="stepCurrent === 0">
          <n-form-item label="饰品名称" path="market_hash_name">
            <n-input
              v-model:value="formData.market_hash_name"
              placeholder="请输入饰品市场名称，如 AK-47 | 红线 (久经沙场)"
              :disabled="isEditing"
            />
          </n-form-item>
        </div>

        <!-- Step 2: 选平台 -->
        <div v-if="stepCurrent === 1">
          <n-form-item label="平台" path="platform">
            <n-select
              v-model:value="formData.platform"
              placeholder="选择交易平台"
              :disabled="isEditing"
              :options="platformOptions"
            />
          </n-form-item>
          <n-form-item label="轮询间隔">
            <n-input-number
              v-model:value="formData.interval_seconds"
              :min="5"
              :step="5"
              style="width: 100%"
            >
              <template #suffix>秒</template>
            </n-input-number>
          </n-form-item>
        </div>

        <!-- Step 3: 设定类型 -->
        <div v-if="stepCurrent === 2">
          <n-form-item label="价格追踪">
            <n-space align="center">
              <n-switch v-model:value="formData.price_track_enabled" />
              <n-select
                v-model:value="formData.price_change_mode"
                :options="modeOptions"
                style="width: 120px"
                :disabled="!formData.price_track_enabled"
              />
              <n-input-number
                v-model:value="formData.price_threshold_percent"
                :min="0"
                :precision="2"
                placeholder="阈值%"
                style="width: 120px"
                :disabled="!formData.price_track_enabled || formData.price_change_mode === 'any'"
              >
                <template #suffix>%</template>
              </n-input-number>
            </n-space>
          </n-form-item>
          <n-form-item label="数量追踪">
            <n-space align="center">
              <n-switch v-model:value="formData.quantity_track_enabled" />
              <n-select
                v-model:value="formData.quantity_change_mode"
                :options="modeOptions"
                style="width: 120px"
                :disabled="!formData.quantity_track_enabled"
              />
              <n-input-number
                v-model:value="formData.quantity_threshold_percent"
                :min="0"
                :precision="2"
                placeholder="阈值%"
                style="width: 120px"
                :disabled="!formData.quantity_track_enabled || formData.quantity_change_mode === 'any'"
              >
                <template #suffix>%</template>
              </n-input-number>
            </n-space>
          </n-form-item>
        </div>

        <!-- Step 4: 阈值与高级 -->
        <div v-if="stepCurrent === 3">
          <n-form-item label="冷却时间">
            <n-input-number
              v-model:value="formData.alert_cooldown_seconds"
              :min="0"
              style="width: 100%"
            >
              <template #suffix>秒</template>
            </n-input-number>
          </n-form-item>
          <n-form-item label="免打扰时段">
            <n-space align="center">
              <n-time-picker
                v-model:formatted-value="formData.quiet_hours_start"
                value-format="HH:mm"
                placeholder="开始"
                clearable
              />
              <span>至</span>
              <n-time-picker
                v-model:formatted-value="formData.quiet_hours_end"
                value-format="HH:mm"
                placeholder="结束"
                clearable
              />
            </n-space>
          </n-form-item>
          <n-form-item label="启用">
            <n-switch v-model:value="formData.enabled" />
          </n-form-item>
        </div>
      </n-form>

      <template #footer>
        <n-space justify="space-between">
          <n-space>
            <n-button v-if="stepCurrent > 0" @click="stepCurrent--">上一步</n-button>
          </n-space>
          <n-space>
            <n-button @click="modalVisible = false">取消</n-button>
            <n-button v-if="stepCurrent < 3" type="primary" @click="nextStep">下一步</n-button>
            <n-button v-else type="primary" :loading="submitting" @click="handleSubmit">确认</n-button>
          </n-space>
        </n-space>
      </template>
    </n-modal>

    <!-- 删除确认 -->
    <n-modal
      v-model:show="deleteModalVisible"
      preset="dialog"
      title="删除确认"
      type="warning"
      positive-text="确认删除"
      negative-text="取消"
      :positive-loading="deleting"
      @positive-click="handleDeleteConfirm"
    >
      确定要删除追踪项 "{{ itemToDelete?.display_name || itemToDelete?.market_hash_name }}@{{ itemToDelete?.platform }}" 吗？此操作不可恢复。
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import {
  NButton,
  NSpace,
  NTag,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NSelect,
  NSteps,
  NStep,
  NProgress,
  NTimePicker,
  NEmpty,
  useMessage,
} from 'naive-ui'
import type { FormRules, FormInst } from 'naive-ui'
import { AddOutline, TrailSignOutline } from '@vicons/ionicons5'
import api from '@/api'
import { useExtremeTrackStore } from '@/stores/extremeTrack'
import type { ExtremeTrackConfig } from '@/api'
import { useTheme } from '@/composables/useTheme'
import PageHeader from '@/components/layout/PageHeader.vue'
import SkeletonCard from '@/components/base/SkeletonCard.vue'

const store = useExtremeTrackStore()
const message = useMessage()
const { colorUp, colorDown } = useTheme()

// 实时快照数据 { "marketHashName@platform": { price, quantity, recorded_at } }
const snapshots = ref<Record<string, { price: number; quantity: number; recorded_at: string }>>({})
let pollTimer: ReturnType<typeof setInterval> | null = null

function rowKey(row: ExtremeTrackConfig) {
  return `${row.market_hash_name}@${row.platform}`
}

async function fetchSnapshots() {
  try {
    const { data } = await api.extremeTrackSnapshots()
    const map: Record<string, { price: number; quantity: number; recorded_at: string }> = {}
    for (const s of data) {
      const key = `${s.market_hash_name}@${s.platform}`
      map[key] = { price: s.price, quantity: s.quantity, recorded_at: s.recorded_at }
    }
    snapshots.value = map
  } catch (e) {
    console.error('Failed to fetch snapshots:', e)
  }
}

function startPolling() {
  fetchSnapshots()
  pollTimer = setInterval(fetchSnapshots, 10000) // 每 10 秒轮询
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 追踪强度 = 基于开启的追踪项和阈值计算
function intensityPercent(item: ExtremeTrackConfig): number {
  let score = 0
  if (item.enabled) score += 30
  if (item.price_track_enabled) {
    score += 25
    if (item.price_change_mode === 'percent' && item.price_threshold_percent > 0) score += 10
  }
  if (item.quantity_track_enabled) {
    score += 25
    if (item.quantity_change_mode === 'percent' && item.quantity_threshold_percent > 0) score += 10
  }
  return score
}

function formatTime(recordedAt?: string): string {
  if (!recordedAt) return '—'
  const date = new Date(recordedAt)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} 小时前`
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

const modalVisible = ref(false)
const deleteModalVisible = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInst | null>(null)
const itemToDelete = ref<ExtremeTrackConfig | null>(null)
const stepCurrent = ref(0)

const platformOptions = [
  { label: 'BUFF', value: 'buff' },
  { label: '悠悠有品', value: 'youpin' },
  { label: 'IGXE', value: 'igxe' },
  { label: 'C5GAME', value: 'c5game' },
]

const modeOptions = [
  { label: '任何变动', value: 'any' },
  { label: '超百分比', value: 'percent' },
]

const formData = ref({
  market_hash_name: '',
  platform: '',
  interval_seconds: 60,
  enabled: true,
  price_track_enabled: true,
  price_change_mode: 'any',
  price_threshold_percent: 0,
  quantity_track_enabled: true,
  quantity_change_mode: 'any',
  quantity_threshold_percent: 0,
  alert_cooldown_seconds: 0,
  quiet_hours_start: null as string | null,
  quiet_hours_end: null as string | null,
})

const formRules: FormRules = {
  market_hash_name: [
    { required: true, message: '请输入饰品名称', trigger: 'blur' },
  ],
  platform: [
    { required: true, message: '请选择平台', trigger: 'blur' },
  ],
}

function resetForm() {
  formData.value = {
    market_hash_name: '',
    platform: '',
    interval_seconds: 60,
    enabled: true,
    price_track_enabled: true,
    price_change_mode: 'any',
    price_threshold_percent: 0,
    quantity_track_enabled: true,
    quantity_change_mode: 'any',
    quantity_threshold_percent: 0,
    alert_cooldown_seconds: 0,
    quiet_hours_start: null,
    quiet_hours_end: null,
  }
  stepCurrent.value = 0
}

function openCreateModal() {
  isEditing.value = false
  resetForm()
  modalVisible.value = true
}

function openEditModal(item: ExtremeTrackConfig) {
  isEditing.value = true
  formData.value = {
    market_hash_name: item.market_hash_name,
    platform: item.platform,
    interval_seconds: item.interval_seconds,
    enabled: !!item.enabled,
    price_track_enabled: !!item.price_track_enabled,
    price_change_mode: item.price_change_mode,
    price_threshold_percent: item.price_threshold_percent,
    quantity_track_enabled: !!item.quantity_track_enabled,
    quantity_change_mode: item.quantity_change_mode,
    quantity_threshold_percent: item.quantity_threshold_percent,
    alert_cooldown_seconds: item.alert_cooldown_seconds,
    quiet_hours_start: item.quiet_hours_start,
    quiet_hours_end: item.quiet_hours_end,
  }
  stepCurrent.value = 0
  modalVisible.value = true
}

function openDeleteModal(item: ExtremeTrackConfig) {
  itemToDelete.value = item
  deleteModalVisible.value = true
}

function nextStep() {
  if (stepCurrent.value === 0 && !formData.value.market_hash_name.trim()) {
    message.warning('请输入饰品名称')
    return
  }
  if (stepCurrent.value === 1 && !formData.value.platform) {
    message.warning('请选择平台')
    return
  }
  if (stepCurrent.value < 3) {
    stepCurrent.value++
  }
}

async function handleSubmit() {
  await formRef.value?.validate(async (errors) => {
    if (errors) return
    submitting.value = true
    try {
      if (isEditing.value) {
        await store.updateItem(formData.value.market_hash_name, formData.value.platform, {
          interval_seconds: formData.value.interval_seconds,
          enabled: formData.value.enabled,
          price_track_enabled: formData.value.price_track_enabled,
          price_change_mode: formData.value.price_change_mode,
          price_threshold_percent: formData.value.price_threshold_percent,
          quantity_track_enabled: formData.value.quantity_track_enabled,
          quantity_change_mode: formData.value.quantity_change_mode,
          quantity_threshold_percent: formData.value.quantity_threshold_percent,
          alert_cooldown_seconds: formData.value.alert_cooldown_seconds,
          quiet_hours_start: formData.value.quiet_hours_start,
          quiet_hours_end: formData.value.quiet_hours_end,
        })
        message.success('更新成功')
      } else {
        await store.addItem({
          market_hash_name: formData.value.market_hash_name,
          platform: formData.value.platform,
          interval_seconds: formData.value.interval_seconds,
          enabled: formData.value.enabled,
          price_track_enabled: formData.value.price_track_enabled,
          price_change_mode: formData.value.price_change_mode,
          price_threshold_percent: formData.value.price_threshold_percent,
          quantity_track_enabled: formData.value.quantity_track_enabled,
          quantity_change_mode: formData.value.quantity_change_mode,
          quantity_threshold_percent: formData.value.quantity_threshold_percent,
          alert_cooldown_seconds: formData.value.alert_cooldown_seconds,
          quiet_hours_start: formData.value.quiet_hours_start,
          quiet_hours_end: formData.value.quiet_hours_end,
        })
        message.success('添加成功')
      }
      modalVisible.value = false
    } catch (e: any) {
      message.error(e?.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

async function handleDeleteConfirm() {
  if (!itemToDelete.value) return
  deleting.value = true
  try {
    await store.removeItem(itemToDelete.value.market_hash_name, itemToDelete.value.platform)
    message.success('删除成功')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
    deleteModalVisible.value = false
  }
}

async function handleToggle(item: ExtremeTrackConfig) {
  try {
    await store.toggleEnabled(item)
    message.success(item.enabled ? '已停止' : '已启动')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '操作失败')
  }
}

onMounted(() => {
  store.fetchItems().then(() => {
    startPolling()
  })
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.empty-state {
  padding: 4rem 0;
  display: flex;
  justify-content: center;
}

.track-card {
  background: var(--n-card-color);
  border: 1px solid var(--n-border-color);
  border-radius: 0.75rem;
  padding: 1rem;
  transition: all 200ms ease;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.track-card:hover {
  border-color: var(--n-primary-color);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
  transform: translateY(-2px);
}

.track-card--disabled {
  opacity: 0.65;
}

.track-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.track-card__title {
  font-weight: 600;
  font-size: 0.9375rem;
  color: var(--n-text-color-1);
  line-height: 1.3;
  word-break: break-all;
}

.track-card__platform {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.platform-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background: var(--n-primary-color-suppl);
  color: var(--n-primary-color);
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
}

.interval-text {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.track-card__progress {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

.track-card__config {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.config-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8125rem;
}

.config-label {
  color: var(--n-text-color-3);
}

.config-value {
  color: var(--n-text-color-2);
  font-weight: 500;
}

.track-card__realtime {
  background: var(--n-hover-color);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
}

.realtime-label {
  font-size: 0.6875rem;
  color: var(--n-text-color-3);
  margin-bottom: 0.25rem;
}

.realtime-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.realtime-price {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--n-text-color-1);
}

.realtime-quantity {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--n-text-color-2);
}

.realtime-time {
  font-size: 0.6875rem;
  color: var(--n-text-color-3);
  margin-top: 0.25rem;
}

.track-card__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.25rem;
  margin-top: auto;
  padding-top: 0.25rem;
}

@media (max-width: 639px) {
  .track-card__actions {
    opacity: 1;
  }
}
</style>
