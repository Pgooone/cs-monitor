<template>
  <div class="extreme-track">
    <!-- 标题区 -->
    <div class="extreme-track__header">
      <div>
        <h2 class="extreme-track__title">极致追踪模式</h2>
        <p class="extreme-track__desc">高频轮询模式，针对极稀有饰品进行毫秒级价格监控。</p>
      </div>
      <button class="btn-primary text-xs h-9 px-4" @click="openCreateModal">
        <Plus class="w-4 h-4" />
        添加追踪
      </button>
    </div>

    <!-- 骨架屏 -->
    <div v-if="store.loading" class="extreme-track__grid">
      <div v-for="n in 4" :key="n" class="glass-card skeleton-card track-card">
        <div class="track-card__head">
          <div class="skeleton-line" style="width: 4rem; height: 4rem; border-radius: 0.75rem;" />
          <div style="flex: 1; display: flex; flex-direction: column; gap: 0.375rem;">
            <div class="skeleton-line" style="width: 70%; height: 1.25rem;" />
            <div class="skeleton-line" style="width: 40%; height: 0.75rem;" />
          </div>
        </div>
        <div class="skeleton-line" style="width: 100%; height: 2.5rem; margin-top: 0.75rem;" />
        <div class="skeleton-line" style="width: 100%; height: 0.5rem; margin-top: 0.75rem;" />
        <div class="skeleton-line" style="width: 100%; height: 2rem; margin-top: 0.75rem;" />
        <div class="skeleton-line" style="width: 100%; height: 3rem; margin-top: 0.75rem;" />
        <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
          <div class="skeleton-line" style="flex: 1; height: 2rem; border-radius: 0.5rem;" />
          <div class="skeleton-line" style="flex: 1; height: 2rem; border-radius: 0.5rem;" />
        </div>
      </div>
    </div>

    <!-- 卡片网格 -->
    <div v-else class="extreme-track__grid">
      <div
        v-for="item in store.items"
        :key="rowKey(item)"
        class="glass-card track-card"
        :class="item.enabled ? 'track-card--enabled' : 'track-card--disabled'"
      >
        <!-- 头部：图片 + 名称 + 状态 -->
        <div class="track-card__head">
          <div class="track-card__image">
            <span v-if="item.enabled" class="track-card__image-pulse" />
            <SteamItemImage
              :market-hash-name="item.market_hash_name"
              :icon-url="item.icon_url"
              :alt="item.display_name || item.market_hash_name"
              class-name="track-card__real-img"
              :fallback-emoji="getWeaponEmoji(item.market_hash_name)"
            />
          </div>
          <div class="track-card__info">
            <h4 class="track-card__name">{{ item.display_name || item.market_hash_name }}</h4>
            <div class="track-card__meta">
              <span class="track-card__platform-badge">{{ item.platform }}</span>
              <span v-if="item.enabled" class="track-card__status track-card__status--active">
                <span class="track-card__status-dot track-card__status-dot--active" />
                运行中
              </span>
              <span v-else class="track-card__status">
                <span class="track-card__status-dot" />
                已停止
              </span>
            </div>
          </div>
        </div>

        <!-- 轮询信息栏 -->
        <div class="track-card__poll-info">
          <div class="track-card__poll-item">
            <span class="track-card__poll-label">轮询频率</span>
            <span class="track-card__poll-value">{{ item.interval_seconds }}s / 次</span>
          </div>
          <div v-if="item.alert_cooldown_seconds > 0" class="track-card__poll-item track-card__poll-item--right">
            <span class="track-card__poll-label">冷却间隔</span>
            <span class="track-card__poll-value track-card__poll-value--orange">{{ (item.alert_cooldown_seconds / 60).toFixed(0) }}m</span>
          </div>
        </div>

        <!-- 雷达强度进度条 -->
        <div class="track-card__radar">
          <div class="track-card__radar-header">
            <span class="track-card__radar-label">雷达强度 (Radar)</span>
            <span class="track-card__radar-value" :class="item.enabled ? 'track-card__radar-value--active' : ''">{{ intensityPercent(item) }}%</span>
          </div>
          <div class="track-card__radar-bar">
            <div v-if="item.enabled" class="track-card__radar-shimmer" />
            <div
              class="track-card__radar-fill"
              :class="item.enabled ? 'track-card__radar-fill--active' : 'track-card__radar-fill--inactive'"
              :style="{ width: `${intensityPercent(item)}%` }"
            >
              <div v-if="item.enabled" class="track-card__radar-tip" />
            </div>
          </div>
        </div>

        <!-- 配置行 -->
        <div class="track-card__config">
          <div class="track-card__config-row">
            <span class="track-card__config-label">价格异常捕获</span>
            <span class="track-card__config-value">
              {{ item.price_track_enabled ? (item.price_change_mode === 'any' ? '任何波动' : `> ${item.price_threshold_percent}%`) : '已关闭' }}
            </span>
          </div>
          <div class="track-card__config-row track-card__config-row--bordered">
            <span class="track-card__config-label">成交量突增监控</span>
            <span class="track-card__config-value">
              {{ item.quantity_track_enabled ? (item.quantity_change_mode === 'any' ? '任何波动' : `> ${item.quantity_threshold_percent}%`) : '已关闭' }}
            </span>
          </div>
        </div>

        <!-- 内存快照区 -->
        <div class="track-card__snapshot">
          <div class="track-card__snapshot-header">
            <span class="track-card__snapshot-label">内存快照 (Snapshot)</span>
            <span v-if="item.enabled" class="track-card__snapshot-pulse" />
          </div>
          <div class="track-card__snapshot-content">
            <div class="track-card__snapshot-price font-mono-num">
              ¥{{ snapshots[rowKey(item)]?.price?.toLocaleString(undefined, { minimumFractionDigits: 2 }) || '—' }}
            </div>
            <div class="track-card__snapshot-qty font-mono-num">
              {{ snapshots[rowKey(item)]?.quantity ?? '—' }} <span class="track-card__snapshot-qty-label">在售</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="track-card__actions">
          <button
            class="track-card__action-btn"
            :class="item.enabled ? 'track-card__action-btn--stop' : 'track-card__action-btn--start'"
            @click="handleToggle(item)"
          >
            {{ item.enabled ? '暂停进程' : '启动追踪' }}
          </button>
          <button class="track-card__action-btn track-card__action-btn--reload" @click="openEditModal(item)">
            重载配置
          </button>
          <button
            class="track-card__action-btn track-card__action-btn--delete"
            @click="openDeleteModal(item)"
            aria-label="删除追踪"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- 底部等待区 -->
    <div v-if="!store.loading && store.items.length === 0" class="glass-card extreme-track__empty">
      <Terminal class="extreme-track__empty-icon" />
      <p class="extreme-track__empty-text">等待极致配置载入...</p>
      <button class="btn-primary text-xs h-10 px-5 mt-4" @click="openCreateModal">
        <Plus class="w-4 h-4" />
        添加追踪
      </button>
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
            <div class="search-wrapper" v-if="!isEditing">
              <n-input
                v-model:value="searchQuery"
                placeholder="输入饰品名称搜索，如 AK-47、红线、Asiimov..."
                clearable
                :loading="searching"
                @update:value="onSearchInput"
                @blur="onSearchBlur"
              />
              <div v-if="showSearchDropdown && searchResults.length > 0" class="search-dropdown">
                <div
                  v-for="item in searchResults"
                  :key="item.market_hash_name"
                  class="search-item"
                  @mousedown.prevent="selectSearchResult(item)"
                >
                  <span class="search-item-name">{{ item.name || item.market_hash_name }}</span>
                  <span v-if="item.name && item.name !== item.market_hash_name" class="search-item-alias">
                    {{ item.market_hash_name }}
                  </span>
                </div>
              </div>
            </div>
            <n-input
              v-else
              :value="formData.market_hash_name"
              disabled
            />
            <div v-if="!isEditing && formData.market_hash_name" class="selected-item-hint">
              已选: {{ formData.market_hash_name }}
            </div>
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
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NSelect,
  NSteps,
  NStep,
  NTimePicker,
  useMessage,
} from 'naive-ui'
import type { FormRules, FormInst } from 'naive-ui'
import { Terminal, Plus, Trash2 } from 'lucide-vue-next'
import api from '@/api'
import { useExtremeTrackStore } from '@/stores/extremeTrack'
import type { ExtremeTrackConfig } from '@/api'
import SteamItemImage from '@/components/business/SteamItemImage.vue'
import { useTheme } from '@/composables/useTheme'

const store = useExtremeTrackStore()
const message = useMessage()
useTheme()

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

// 雷达强度 = max(10, 100 - interval_seconds / 2)
function intensityPercent(item: ExtremeTrackConfig): number {
  return Math.max(10, 100 - (item.interval_seconds / 2))
}

// 武器类型 emoji 映射
function getWeaponEmoji(name: string): string {
  const n = name.toLowerCase()
  if (n.includes('knife') || n.includes('karambit') || n.includes('bayonet') || n.includes('butterfly')) return '🗡️'
  if (n.includes('glove')) return '🧤'
  if (n.includes('ak-47')) return 'AK'
  if (n.includes('awp')) return 'AWP'
  if (n.includes('m4a4') || n.includes('m4a1')) return 'M4'
  if (n.includes('desert eagle') || n.includes('deagle')) return 'DE'
  if (n.includes('usp')) return 'USP'
  if (n.includes('glock')) return 'G'
  if (n.includes('p250')) return 'P'
  if (n.includes('five-seven')) return '5-7'
  if (n.includes('tec-9')) return 'T9'
  if (n.includes('p90')) return 'P90'
  if (n.includes('scar')) return 'SCAR'
  if (n.includes('famas')) return 'FAMAS'
  if (n.includes('galil')) return 'GALIL'
  if (n.includes('sg')) return 'SG'
  if (n.includes('aug')) return 'AUG'
  if (n.includes('ssg')) return 'SSG'
  if (n.includes('g3sg1')) return 'G3'
  if (n.includes('mac-10')) return 'MAC'
  if (n.includes('mp9')) return 'MP9'
  if (n.includes('mp7')) return 'MP7'
  if (n.includes('ump')) return 'UMP'
  if (n.includes('pp-bizon')) return 'PP'
  if (n.includes('nova')) return 'NOVA'
  if (n.includes('xm1014')) return 'XM'
  if (n.includes('sawed-off')) return 'SAW'
  if (n.includes('mag-7')) return 'MAG'
  if (n.includes('negev')) return 'NEG'
  if (n.includes('m249')) return 'M249'
  if (n.includes('r8')) return 'R8'
  if (n.includes('cz75')) return 'CZ'
  if (n.includes('dual')) return 'D'
  if (n.includes('revolver')) return 'R'
  if (n.includes('sticker')) return '🏷️'
  if (n.includes('case') || n.includes('capsule')) return '📦'
  if (n.includes('agent')) return '👤'
  if (n.includes('patch')) return '🔖'
  if (n.includes('music')) return '🎵'
  return '🔫'
}

const modalVisible = ref(false)
const deleteModalVisible = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInst | null>(null)
const itemToDelete = ref<ExtremeTrackConfig | null>(null)
const stepCurrent = ref(0)

// 搜索相关
const searchQuery = ref('')
const searchResults = ref<{ market_hash_name: string; name: string | null }[]>([])
const searching = ref(false)
const showSearchDropdown = ref(false)
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

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
    { required: true, message: '请搜索并选择饰品', trigger: 'blur' },
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
  searchQuery.value = ''
  searchResults.value = []
  showSearchDropdown.value = false
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
  searchQuery.value = item.display_name || item.market_hash_name
  stepCurrent.value = 0
  modalVisible.value = true
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
function openDeleteModal(item: ExtremeTrackConfig) {
  itemToDelete.value = item
  deleteModalVisible.value = true
}

// 搜索饰品
function onSearchInput(val: string) {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchResults.value = []
  showSearchDropdown.value = false

  const q = val.trim()
  if (!q) return

  searchDebounceTimer = setTimeout(async () => {
    searching.value = true
    try {
      const { data } = await api.searchItems(q)
      searchResults.value = data || []
      showSearchDropdown.value = searchResults.value.length > 0
    } catch {
      searchResults.value = []
    } finally {
      searching.value = false
    }
  }, 300)
}

function selectSearchResult(item: { market_hash_name: string; name: string | null }) {
  formData.value.market_hash_name = item.market_hash_name
  searchQuery.value = item.name || item.market_hash_name
  showSearchDropdown.value = false
  searchResults.value = []
}

function onSearchBlur() {
  // 延迟关闭，让点击事件先触发
  setTimeout(() => {
    showSearchDropdown.value = false
  }, 200)
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
    if (!formData.value.market_hash_name) {
      message.warning('请搜索并选择饰品')
      return
    }
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
/* ===== 页面布局 ===== */
.extreme-track {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 80rem;
  margin: 0 auto;
}

.extreme-track__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.extreme-track__title {
  font-size: 1.75rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.extreme-track__desc {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

/* ===== 网格 ===== */
.extreme-track__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .extreme-track__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .extreme-track__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1280px) {
  .extreme-track__grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* ===== 卡片基础 ===== */
.track-card {
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  transition: all 300ms;
}

.track-card--enabled {
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.1);
}

.track-card--disabled {
  opacity: 0.7;
  filter: grayscale(0.3);
}

/* ===== 头部 ===== */
.track-card__head {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.track-card__image {
  width: 4rem;
  height: 4rem;
  border-radius: 0.75rem;
  background: #16161d;
  border: 1px solid #1f1f23;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  transition: border-color 300ms;
}

.track-card:hover .track-card__image {
  border-color: rgba(99, 102, 241, 0.4);
}

.track-card__image-pulse {
  position: absolute;
  inset: 0;
  background: rgba(99, 102, 241, 0.1);
  animation: card-pulse 2s infinite;
  z-index: 0;
}

@keyframes card-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.track-card__weapon {
  font-size: 1.5rem;
  font-weight: 800;
  font-family: 'JetBrains Mono', monospace;
  color: #94a3b8;
  opacity: 0.5;
  position: relative;
  z-index: 1;
}

.track-card__real-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3));
  position: relative;
  z-index: 1;
}

.track-card__info {
  flex: 1;
  min-width: 0;
}

.track-card__name {
  font-size: 0.875rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.375rem 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-all;
}

.track-card__meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.track-card__platform-badge {
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  border: 1px solid rgba(99, 102, 241, 0.2);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.track-card__status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
}

.track-card__status--active {
  color: #22c55e;
}

.track-card__status-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: #94a3b8;
}

.track-card__status-dot--active {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
  animation: card-pulse 2s infinite;
}

/* ===== 轮询信息栏 ===== */
.track-card__poll-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 1rem;
  background: #16161d;
  border-radius: 0.5rem;
  padding: 0.5rem;
  border: 1px solid rgba(31, 31, 35, 0.5);
}

.track-card__poll-item {
  display: flex;
  flex-direction: column;
}

.track-card__poll-item--right {
  text-align: right;
}

.track-card__poll-label {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
}

.track-card__poll-value {
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  color: #6366f1;
}

.track-card__poll-value--orange {
  color: #fb923c;
}

/* ===== 雷达强度 ===== */
.track-card__radar {
  margin-bottom: 1rem;
}

.track-card__radar-header {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  font-weight: 700;
  margin-bottom: 0.25rem;
  letter-spacing: 0.05em;
}

.track-card__radar-label {
  color: #94a3b8;
  text-transform: uppercase;
}

.track-card__radar-value {
  font-family: 'JetBrains Mono', monospace;
  color: #94a3b8;
}

.track-card__radar-value--active {
  color: #6366f1;
}

.track-card__radar-bar {
  height: 0.5rem;
  width: 100%;
  background: #16161d;
  border-radius: 9999px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(31, 31, 35, 0.5);
}

.track-card__radar-shimmer {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  animation: radar-shimmer 2s infinite linear;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
  z-index: 10;
}

@keyframes radar-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.track-card__radar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 1000ms;
  position: relative;
}

.track-card__radar-fill--active {
  background: linear-gradient(to right, rgba(99, 102, 241, 0.8), #06b6d4);
  box-shadow: 0 0 8px rgba(99, 102, 241, 0.5);
}

.track-card__radar-fill--inactive {
  background: rgba(113, 113, 122, 0.5);
}

.track-card__radar-tip {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 0.25rem;
  background: #ffffff;
  border-radius: 9999px;
  box-shadow: 0 0 5px #fff;
}

/* ===== 配置行 ===== */
.track-card__config {
  margin-bottom: 0.75rem;
  font-size: 0.6875rem;
}

.track-card__config-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.track-card__config-row--bordered {
  border-top: 1px solid rgba(31, 31, 35, 0.3);
}

.track-card__config-label {
  color: #94a3b8;
}

.track-card__config-value {
  color: #ffffff;
  font-weight: 500;
}

/* ===== 内存快照 ===== */
.track-card__snapshot {
  border-top: 1px solid rgba(31, 31, 35, 0.5);
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
  margin-bottom: 0.75rem;
}

.track-card__snapshot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.track-card__snapshot-label {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.track-card__snapshot-pulse {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: #6366f1;
  animation: snapshot-ping 1s infinite;
}

@keyframes snapshot-ping {
  0% { transform: scale(1); opacity: 1; }
  75%, 100% { transform: scale(2); opacity: 0; }
}

.track-card__snapshot-content {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.track-card__snapshot-price {
  font-size: 1.25rem;
  font-weight: 900;
  color: #22c55e;
  letter-spacing: -0.02em;
}

.track-card__snapshot-qty {
  font-size: 0.875rem;
  font-weight: 700;
  color: #ffffff;
  text-align: right;
}

.track-card__snapshot-qty-label {
  font-size: 10px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-family: inherit;
}

/* ===== 操作按钮 ===== */
.track-card__actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}

.track-card__action-btn {
  flex: 1;
  height: 2rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 200ms;
  border: 1px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.track-card__action-btn--stop {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border-color: rgba(34, 197, 94, 0.2);
}

.track-card__action-btn--stop:hover {
  background: rgba(34, 197, 94, 0.2);
}

.track-card__action-btn--start {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.2);
}

.track-card__action-btn--start:hover {
  background: rgba(239, 68, 68, 0.2);
}

.track-card__action-btn--reload {
  background: #16161d;
  color: #ffffff;
  border-color: #1f1f23;
}

.track-card__action-btn--reload:hover {
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.3);
}

.track-card__action-btn--delete {
  flex: 0 0 2rem;
  width: 2rem;
  background: transparent;
  color: #71717a;
  border-color: transparent;
}

.track-card__action-btn--delete:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.2);
}

/* ===== 空态 ===== */
.extreme-track__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  border: 2px dashed #1f1f23;
  background: rgba(15, 15, 18, 0.2);
  opacity: 0.5;
}

.extreme-track__empty-icon {
  width: 2rem;
  height: 2rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

.extreme-track__empty-text {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #94a3b8;
}

/* ===== 搜索下拉框 ===== */
.search-wrapper {
  position: relative;
  width: 100%;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 100;
  margin-top: 4px;
  background: var(--n-color, #fff);
  border: 1px solid var(--n-border-color, #e0e0e6);
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  max-height: 240px;
  overflow-y: auto;
}

.search-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.search-item:hover {
  background: rgba(46, 91, 255, 0.08);
}

.search-item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--n-text-color-1);
}

.search-item-alias {
  font-size: 0.75rem;
  color: var(--n-text-color-3);
  margin-left: 0.5rem;
}

.selected-item-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--n-text-color-3);
}

/* ===== 骨架屏 ===== */
.skeleton-card {
  cursor: default !important;
}

.skeleton-card:hover {
  transform: none !important;
  border-color: #1f1f23 !important;
  box-shadow: none !important;
}

.skeleton-line {
  height: 0.875rem;
  border-radius: 0.25rem;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 25%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0.05) 75%
  );
  background-size: 200% 100%;
  animation: cs-skeleton-shimmer 1.5s infinite ease-in-out;
}

/* ===== 浅色模式 ===== */
html:not(.dark) .extreme-track__title {
  color: #0f172a;
}

html:not(.dark) .extreme-track__desc {
  color: #64748b;
}

html:not(.dark) .track-card__name {
  color: #0f172a;
}

html:not(.dark) .track-card__image {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

html:not(.dark) .track-card__weapon {
  color: #64748b;
}

html:not(.dark) .track-card__poll-info {
  background: #f8fafc;
  border-color: #e2e8f0;
}

html:not(.dark) .track-card__poll-value {
  color: #4f46e5;
}

html:not(.dark) .track-card__radar-label {
  color: #64748b;
}

html:not(.dark) .track-card__radar-value {
  color: #64748b;
}

html:not(.dark) .track-card__radar-value--active {
  color: #4f46e5;
}

html:not(.dark) .track-card__radar-bar {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

html:not(.dark) .track-card__config-label {
  color: #64748b;
}

html:not(.dark) .track-card__config-value {
  color: #0f172a;
}

html:not(.dark) .track-card__snapshot {
  border-color: #e2e8f0;
}

html:not(.dark) .track-card__snapshot-label {
  color: #64748b;
}

html:not(.dark) .track-card__snapshot-price {
  color: #10b981;
}

html:not(.dark) .track-card__snapshot-qty {
  color: #0f172a;
}

html:not(.dark) .track-card__snapshot-qty-label {
  color: #64748b;
}

html:not(.dark) .track-card__status {
  color: #64748b;
}

html:not(.dark) .track-card__action-btn--reload {
  background: #f8fafc;
  border-color: #e2e8f0;
  color: #0f172a;
}

html:not(.dark) .track-card__action-btn--reload:hover {
  color: #4f46e5;
  border-color: rgba(79, 70, 229, 0.3);
}

html:not(.dark) .track-card__action-btn--delete {
  color: #94a3b8;
}

html:not(.dark) .track-card__action-btn--delete:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.06);
  border-color: rgba(239, 68, 68, 0.3);
}

html:not(.dark) .track-card__empty {
  border-color: #e2e8f0;
  background: rgba(248, 250, 252, 0.5);
}

html:not(.dark) .track-card__empty-icon {
  color: #64748b;
}

html:not(.dark) .track-card__empty-text {
  color: #64748b;
}

html:not(.dark) .skeleton-line {
  background: linear-gradient(
    90deg,
    rgba(0, 0, 0, 0.06) 25%,
    rgba(0, 0, 0, 0.1) 50%,
    rgba(0, 0, 0, 0.06) 75%
  );
  background-size: 200% 100%;
}

html:not(.dark) .skeleton-card:hover {
  border-color: #e2e8f0 !important;
}
</style>
