<template>
  <div class="watchlist">
    <!-- 标题区 -->
    <div class="watchlist__header">
      <div>
        <h2 class="watchlist__title">监控清单</h2>
        <p class="watchlist__desc">当前正在进行价格追踪的 {{ store.items.length }} 个饰品项。</p>
      </div>
      <div class="watchlist__header-actions">
        <button
          class="watchlist__refresh-btn"
          :disabled="refreshing || cooldownSec > 0"
          @click="handleRefresh()"
          aria-label="刷新价格"
        >
          <Zap class="w-4 h-4" />
          {{ refreshButtonText }}
        </button>
        <button class="watchlist__add-btn" @click="openCreateModal" aria-label="添加饰品">
          + 添加饰品
        </button>
      </div>
    </div>

    <!-- 空态 -->
    <div v-if="!store.loading && !store.items.length" class="watchlist__empty">
      <div class="watchlist__empty-icon">📋</div>
      <h3 class="watchlist__empty-title">{{ t('watchlist.emptyTitle') }}</h3>
      <p class="watchlist__empty-desc">{{ t('watchlist.emptyDesc') }}</p>
      <button class="watchlist__add-btn" @click="openCreateModal">
        + {{ t('watchlist.addFirstItem') }}
      </button>
    </div>

    <!-- 骨架屏 -->
    <div v-else-if="store.loading" class="watchlist__grid">
      <div v-for="n in 6" :key="n" class="glass-card watchlist-card skeleton-card">
        <div class="watchlist-card__top">
          <div class="skeleton-line" style="width: 2rem; height: 2rem; border-radius: 0.5rem;" />
          <div class="skeleton-line" style="width: 1.5rem; height: 1.5rem; border-radius: 0.25rem;" />
        </div>
        <div class="skeleton-line" style="width: 100%; height: 10rem; border-radius: 1rem; margin-bottom: 1.5rem;" />
        <div class="skeleton-line" style="width: 60%; height: 1.25rem;" />
        <div class="skeleton-line" style="width: 40%; height: 0.625rem; margin-top: 0.375rem;" />
        <div class="skeleton-line" style="width: 100%; height: 2.5rem; margin-top: 1.5rem; margin-bottom: 1.5rem;" />
        <div class="skeleton-line" style="width: 100%; height: 0.25rem; margin-bottom: 0.75rem;" />
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
          <div>
            <div class="skeleton-line" style="width: 4rem; height: 0.625rem; margin-bottom: 0.375rem;" />
            <div class="skeleton-line" style="width: 6rem; height: 1.5rem;" />
          </div>
          <div class="skeleton-line" style="width: 4rem; height: 1.5rem; border-radius: 0.25rem;" />
        </div>
      </div>
    </div>

    <!-- 卡片网格 -->
    <div v-else class="watchlist__grid">
      <div
        v-for="item in store.items"
        :key="item.market_hash_name"
        class="glass-card watchlist-card"
        :class="{ 'watchlist-card--disabled': !item.enabled }"
        @click="goToDetail(item)"
      >
        <!-- 头部 -->
        <div class="watchlist-card__top">
          <div class="watchlist-card__scan-icon">
            <Scan class="w-4 h-4" />
          </div>
          <button class="watchlist-card__more" @click.stop aria-label="更多操作">
            <MoreHorizontal class="w-5 h-5" />
          </button>
        </div>

        <!-- 图片区 -->
        <div class="watchlist-card__image">
          <span class="watchlist-card__weapon-icon">{{ getWeaponEmoji(item.market_hash_name) }}</span>
          <div v-if="!item.enabled" class="watchlist-card__paused-overlay">
            <span class="watchlist-card__paused-badge">已暂停</span>
          </div>
        </div>

        <!-- 名称区 -->
        <div class="watchlist-card__name-area">
          <h3 class="watchlist-card__display-name">{{ item.display_name || item.market_hash_name }}</h3>
          <span class="watchlist-card__hash-name">{{ item.market_hash_name }}</span>
        </div>

        <!-- 多平台价格 -->
        <div v-if="item.platform_prices?.length" class="watchlist-card__platforms">
          <span
            v-for="p in item.platform_prices.filter((pp: any) => pp.price > 0).slice(0, 4)"
            :key="p.platform"
            class="watchlist-card__platform-tag"
          >
            <span class="watchlist-card__platform-name">{{ p.platform }}</span>
            <span class="watchlist-card__platform-price font-mono-num">¥{{ p.price.toFixed(0) }}</span>
          </span>
        </div>

        <!-- Sparkline -->
        <div class="watchlist-card__sparkline">
          <MiniSparkline
            v-if="item.sparkline?.length >= 2"
            :data="item.sparkline"
            :color="sparklineColor(item)"
            :width="200"
            :height="40"
          />
          <div v-else class="watchlist-card__no-sparkline">暂无历史走势</div>
        </div>

        <!-- 价格行 -->
        <div class="watchlist-card__price-row">
          <div>
            <div class="watchlist-card__price-label">最后一次捕获</div>
            <div class="watchlist-card__price-value font-mono-num">
              ¥{{ item.latest_price?.toFixed(2) || '0.00' }}
            </div>
          </div>
          <div
            v-if="item.change_24h != null"
            class="watchlist-card__change"
            :class="item.change_24h >= 0 ? 'watchlist-card__change--up' : 'watchlist-card__change--down'"
          >
            <component :is="item.change_24h >= 0 ? ArrowUpRight : ArrowDownRight" class="w-3 h-3" />
            {{ Math.abs(item.change_24h).toFixed(2) }}%
          </div>
        </div>

        <!-- 操作栏 -->
        <div class="watchlist-card__actions" @click.stop>
          <button class="watchlist-card__action-btn" @click="handleToggle(item)">
            {{ item.enabled ? '禁用' : '启用' }}
          </button>
          <button class="watchlist-card__action-btn watchlist-card__action-btn--primary" @click="openEditModal(item)">
            编辑
          </button>
          <button class="watchlist-card__action-btn watchlist-card__action-btn--danger" @click="openDeleteModal(item)">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <n-modal
      v-model:show="modalVisible"
      :title="isEditing ? '编辑监控项' : '添加监控项'"
      preset="card"
      style="width: 480px"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="饰品名称" path="market_hash_name">
          <n-input
            v-model:value="formData.market_hash_name"
            placeholder="请输入饰品市场名称"
            :disabled="isEditing"
          />
        </n-form-item>
        <n-form-item label="显示名称" path="display_name">
          <n-input
            v-model:value="formData.display_name"
            placeholder="可选，自定义显示名称"
          />
        </n-form-item>
        <n-form-item label="阈值(%)" path="threshold_percent">
          <n-input-number
            v-model:value="formData.threshold_percent"
            :min="0.1"
            :precision="1"
            placeholder="价格变动阈值百分比"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="启用监控" path="enabled">
          <n-switch v-model:value="formData.enabled" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="modalVisible = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">
            确认
          </n-button>
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
      确定要删除监控项 "{{ itemToDelete?.display_name || itemToDelete?.market_hash_name }}" 吗？此操作不可恢复。
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NSpace,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  useMessage,
} from 'naive-ui'
import type { FormRules, FormInst } from 'naive-ui'
import { Scan, MoreHorizontal, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-vue-next'
import { useWatchlistStore } from '@/stores/watchlist'
import type { WatchlistItemWithPrice } from '@/api'
import MiniSparkline from '@/components/business/MiniSparkline.vue'
import { useTheme } from '@/composables/useTheme'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const store = useWatchlistStore()
const message = useMessage()
const { colorUp, colorDown } = useTheme()
const { t } = useI18n()

// 将 hex 颜色转为 RGB 字符串，用于 CSS rgba() 背景
function hexToRgb(hex: string): string {
  const h = hex.replace('#', '')
  const r = parseInt(h.substring(0, 2), 16)
  const g = parseInt(h.substring(2, 4), 16)
  const b = parseInt(h.substring(4, 6), 16)
  return `${r}, ${g}, ${b}`
}
const colorUpRgb = computed(() => hexToRgb(colorUp.value))
const colorDownRgb = computed(() => hexToRgb(colorDown.value))

const modalVisible = ref(false)
const deleteModalVisible = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInst | null>(null)
const itemToDelete = ref<WatchlistItemWithPrice | null>(null)

const formData = ref({
  market_hash_name: '',
  display_name: '',
  threshold_percent: 5.0,
  enabled: true,
})

// ─── 刷新状态 ───
const refreshing = ref(false)
const cooldownUntil = ref<number>(0)
const cooldownSec = ref(0)
let cooldownTimer: ReturnType<typeof setInterval> | null = null

function startCooldown(seconds: number) {
  cooldownUntil.value = Date.now() + seconds * 1000
  cooldownSec.value = seconds
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    const left = Math.ceil((cooldownUntil.value - Date.now()) / 1000)
    if (left <= 0) {
      cooldownSec.value = 0
      if (cooldownTimer) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    } else {
      cooldownSec.value = left
    }
  }, 1000)
}

async function handleRefresh(names?: string[]) {
  if (refreshing.value || cooldownSec.value > 0) return
  const targets = names ?? []
  if (targets.length === 0) {
    const all = store.items.filter((i) => i.enabled).map((i) => i.market_hash_name)
    if (all.length === 0) {
      message.warning('监控清单为空')
      return
    }
    if (all.length > 100) {
      message.warning(`监控清单有 ${all.length} 个物品，单次最多刷新 100 个`)
      return
    }
    return handleRefresh(all)
  }
  if (targets.length > 100) {
    message.warning(`选中 ${targets.length} 个超过单次上限 100，请减少选中`)
    return
  }

  refreshing.value = true
  try {
    const res = await store.refreshPrices(targets)
    if (res.failed === 0) {
      message.success(`已刷新 ${res.success} 个物品`)
    } else {
      message.warning(`刷新完成：成功 ${res.success} / 失败 ${res.failed}`)
    }
    startCooldown(60)
  } catch (e: any) {
    if (e?.response?.status === 429) {
      const retryAfter = e.response.data?.detail?.retry_after ?? 60
      message.error(`刷新过于频繁，${retryAfter}s 后再试`)
      startCooldown(retryAfter)
    } else {
      message.error(e?.response?.data?.detail || '刷新失败')
    }
  } finally {
    refreshing.value = false
  }
}

const refreshButtonText = computed(() => {
  if (cooldownSec.value > 0) return `${cooldownSec.value}s`
  if (refreshing.value) return '刷新中...'
  return '刷新全部'
})

const formRules: FormRules = {
  market_hash_name: [
    { required: true, message: '请输入饰品名称', trigger: 'blur' },
  ],
  threshold_percent: [
    { required: true, message: '请输入阈值', type: 'number', trigger: 'blur' },
  ],
}

function resetForm() {
  formData.value = {
    market_hash_name: '',
    display_name: '',
    threshold_percent: 5.0,
    enabled: true,
  }
}

function openCreateModal() {
  isEditing.value = false
  resetForm()
  modalVisible.value = true
}

function openEditModal(item: WatchlistItemWithPrice) {
  isEditing.value = true
  formData.value = {
    market_hash_name: item.market_hash_name,
    display_name: item.display_name || '',
    threshold_percent: item.threshold_percent,
    enabled: !!item.enabled,
  }
  modalVisible.value = true
}

function openDeleteModal(item: WatchlistItemWithPrice) {
  itemToDelete.value = item
  deleteModalVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate(async (errors) => {
    if (errors) return
    submitting.value = true
    try {
      if (isEditing.value) {
        await store.updateItem(formData.value.market_hash_name, {
          display_name: formData.value.display_name || null,
          threshold_percent: formData.value.threshold_percent,
          enabled: formData.value.enabled,
        })
        message.success('更新成功')
      } else {
        await store.addItem({
          market_hash_name: formData.value.market_hash_name,
          display_name: formData.value.display_name || null,
          threshold_percent: formData.value.threshold_percent,
          enabled: formData.value.enabled,
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
    await store.removeItem(itemToDelete.value.market_hash_name)
    message.success('删除成功')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
    deleteModalVisible.value = false
  }
}

async function handleToggle(item: WatchlistItemWithPrice) {
  try {
    await store.toggleEnabled(item)
    message.success(item.enabled ? '已禁用' : '已启用')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '操作失败')
  }
}

function goToDetail(item: WatchlistItemWithPrice) {
  router.push({
    name: 'ItemDetail',
    params: { name: encodeURIComponent(item.market_hash_name) },
  })
}

function sparklineColor(item: WatchlistItemWithPrice): string {
  if (!item.sparkline.length) return '#3b82f6'
  const first = item.sparkline[0]
  const last = item.sparkline[item.sparkline.length - 1]
  if (last > first) return colorUp.value
  if (last < first) return colorDown.value
  return '#3b82f6'
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

onMounted(() => {
  store.fetchItems()
})
</script>

<style scoped>
/* ─── 页面布局 ─── */
.watchlist {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 80rem;
  margin: 0 auto;
}

/* ─── 标题区 ─── */
.watchlist__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.watchlist__title {
  font-size: 1.75rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: #ffffff;
  margin: 0;
}

.watchlist__desc {
  color: #94a3b8;
  font-weight: 500;
  font-size: 0.875rem;
  margin: 0.25rem 0 0 0;
}

.watchlist__header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.watchlist__refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #1f1f23;
  background: rgba(15, 15, 18, 0.5);
  color: #94a3b8;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms;
}

.watchlist__refresh-btn:hover:not(:disabled) {
  border-color: rgba(99, 102, 241, 0.4);
  color: #ffffff;
}

.watchlist__refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.watchlist__add-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.1);
  color: #818cf8;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms;
}

.watchlist__add-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.5);
  color: #a5b4fc;
}

/* ─── 空态 ─── */
.watchlist__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  text-align: center;
}

.watchlist__empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}

.watchlist__empty-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
}

.watchlist__empty-desc {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0 0 1.5rem 0;
}

/* ─── 网格 ─── */
.watchlist__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .watchlist__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .watchlist__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* ─── 卡片 ─── */
.watchlist-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 300ms cubic-bezier(0.25, 1, 0.5, 1), box-shadow 300ms, border-color 300ms;
}

.watchlist-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.watchlist-card--disabled {
  opacity: 0.6;
}

/* ─── 头部 ─── */
.watchlist-card__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.watchlist-card__scan-icon {
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  opacity: 0.5;
  transition: opacity 300ms;
  color: #94a3b8;
}

.watchlist-card:hover .watchlist-card__scan-icon {
  opacity: 1;
}

.watchlist-card__more {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 200ms;
  display: flex;
  align-items: center;
}

.watchlist-card__more:hover {
  color: #ffffff;
}

/* ─── 图片区 ─── */
.watchlist-card__image {
  height: 10rem;
  background: linear-gradient(to bottom right, #16161d, #050505);
  border-radius: 1rem;
  border: 1px solid #1f1f23;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 1.5rem;
  transition: border-color 300ms;
}

.watchlist-card:hover .watchlist-card__image {
  border-color: rgba(99, 102, 241, 0.4);
}

.watchlist-card__weapon-icon {
  font-size: 2.5rem;
  font-weight: 800;
  font-family: 'JetBrains Mono', monospace;
  color: #94a3b8;
  opacity: 0.3;
  z-index: 1;
}

.watchlist-card__paused-overlay {
  position: absolute;
  inset: 0;
  background: rgba(5, 5, 5, 0.6);
  backdrop-filter: blur(2px);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.watchlist-card__paused-badge {
  padding: 0.25rem 0.75rem;
  background: #0f0f12;
  border: 1px solid #1f1f23;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
}

/* ─── 名称区 ─── */
.watchlist-card__name-area {
  margin-bottom: 1.5rem;
}

.watchlist-card__display-name {
  font-size: 1.125rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.25rem 0;
  transition: color 300ms;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.watchlist-card:hover .watchlist-card__display-name {
  color: #6366f1;
}

.watchlist-card__hash-name {
  font-size: 10px;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ─── 多平台价格 ─── */
.watchlist-card__platforms {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.watchlist-card__platform-tag {
  padding: 0.25rem 0.5rem;
  background: #16161d;
  border: 1px solid #1f1f23;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
}

.watchlist-card__platform-name {
  color: #94a3b8;
  font-weight: 700;
  font-size: 10px;
}

.watchlist-card__platform-price {
  font-weight: 500;
  color: #ffffff;
}

/* ─── Sparkline ─── */
.watchlist-card__sparkline {
  height: 2.5rem;
  margin-bottom: 0.25rem;
}

.watchlist-card__no-sparkline {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #71717a;
}

/* ─── 价格行 ─── */
.watchlist-card__price-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(31, 31, 35, 0.5);
}

.watchlist-card__price-label {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.25rem;
}

.watchlist-card__price-value {
  font-size: 1.5rem;
  font-weight: 900;
  color: #ffffff;
  font-variant-numeric: tabular-nums;
}

.watchlist-card__change {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.watchlist-card__change--up {
  background: v-bind('`rgba(${colorUpRgb}, 0.1)`');
  color: v-bind('colorUp');
}

.watchlist-card__change--down {
  background: v-bind('`rgba(${colorDownRgb}, 0.1)`');
  color: v-bind('colorDown');
}

/* ─── 操作栏 ─── */
.watchlist-card__actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  margin-top: 0.75rem;
  border-top: 1px solid rgba(31, 31, 35, 0.5);
}

.watchlist-card__action-btn {
  flex: 1;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  border: 1px solid #1f1f23;
  background: transparent;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms;
  text-align: center;
}

.watchlist-card__action-btn:hover {
  border-color: #2d2d35;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.05);
}

.watchlist-card__action-btn--primary {
  color: #818cf8;
  border-color: rgba(99, 102, 241, 0.2);
}

.watchlist-card__action-btn--primary:hover {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.4);
  color: #a5b4fc;
}

.watchlist-card__action-btn--danger {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.2);
}

.watchlist-card__action-btn--danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

/* ─── 骨架屏 ─── */
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
  animation: skeleton-shimmer 1.5s infinite;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ─── 浅色模式 ─── */
html:not(.dark) .watchlist__title {
  color: #0f172a;
}

html:not(.dark) .watchlist__desc {
  color: #64748b;
}

html:not(.dark) .watchlist__refresh-btn {
  background: rgba(255, 255, 255, 0.8);
  border-color: #e2e8f0;
  color: #64748b;
}

html:not(.dark) .watchlist__refresh-btn:hover:not(:disabled) {
  border-color: rgba(99, 102, 241, 0.4);
  color: #0f172a;
}

html:not(.dark) .watchlist__add-btn {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
  color: #6366f1;
}

html:not(.dark) .watchlist__add-btn:hover {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
}

html:not(.dark) .watchlist__empty-title {
  color: #0f172a;
}

html:not(.dark) .watchlist__empty-desc {
  color: #64748b;
}

html:not(.dark) .watchlist-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

html:not(.dark) .watchlist-card__scan-icon {
  background: rgba(0, 0, 0, 0.03);
  border-color: rgba(0, 0, 0, 0.06);
  color: #94a3b8;
}

html:not(.dark) .watchlist-card__more {
  color: #94a3b8;
}

html:not(.dark) .watchlist-card__more:hover {
  color: #0f172a;
}

html:not(.dark) .watchlist-card__image {
  background: linear-gradient(to bottom right, #f1f5f9, #e2e8f0);
  border-color: #e2e8f0;
}

html:not(.dark) .watchlist-card:hover .watchlist-card__image {
  border-color: rgba(99, 102, 241, 0.4);
}

html:not(.dark) .watchlist-card__weapon-icon {
  color: #94a3b8;
}

html:not(.dark) .watchlist-card__paused-badge {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #64748b;
}

html:not(.dark) .watchlist-card__paused-overlay {
  background: rgba(255, 255, 255, 0.6);
}

html:not(.dark) .watchlist-card__display-name {
  color: #0f172a;
}

html:not(.dark) .watchlist-card:hover .watchlist-card__display-name {
  color: #6366f1;
}

html:not(.dark) .watchlist-card__hash-name {
  color: #64748b;
}

html:not(.dark) .watchlist-card__platform-tag {
  background: #f8fafc;
  border-color: #e2e8f0;
}

html:not(.dark) .watchlist-card__platform-name {
  color: #64748b;
}

html:not(.dark) .watchlist-card__platform-price {
  color: #0f172a;
}

html:not(.dark) .watchlist-card__price-row {
  border-color: #e2e8f0;
}

html:not(.dark) .watchlist-card__price-label {
  color: #64748b;
}

html:not(.dark) .watchlist-card__price-value {
  color: #0f172a;
}

html:not(.dark) .watchlist-card__actions {
  border-color: #e2e8f0;
}

html:not(.dark) .watchlist-card__action-btn {
  border-color: #e2e8f0;
  color: #64748b;
}

html:not(.dark) .watchlist-card__action-btn:hover {
  border-color: #cbd5e1;
  color: #0f172a;
  background: rgba(0, 0, 0, 0.03);
}

html:not(.dark) .watchlist-card__action-btn--primary {
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.15);
}

html:not(.dark) .watchlist-card__action-btn--primary:hover {
  background: rgba(99, 102, 241, 0.08);
  border-color: rgba(99, 102, 241, 0.3);
}

html:not(.dark) .watchlist-card__action-btn--danger {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.15);
}

html:not(.dark) .watchlist-card__action-btn--danger:hover {
  background: rgba(239, 68, 68, 0.06);
  border-color: rgba(239, 68, 68, 0.3);
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
