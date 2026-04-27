<template>
  <div>
    <page-header title="监控清单">
      <template #actions>
        <n-space>
          <n-button
            :loading="refreshing"
            :disabled="refreshButtonDisabled"
            @click="handleRefresh()"
            aria-label="刷新价格"
          >
            ⚡ {{ refreshButtonText }}
          </n-button>
          <n-button-group>
            <n-button
              :type="viewMode === 'table' ? 'primary' : 'default'"
              size="small"
              @click="viewMode = 'table'"
              aria-label="表格视图"
            >
              &#9776;
            </n-button>
            <n-button
              :type="viewMode === 'card' ? 'primary' : 'default'"
              size="small"
              @click="viewMode = 'card'"
              aria-label="卡片视图"
            >
              &#9638;
            </n-button>
          </n-button-group>
          <n-button type="primary" @click="openCreateModal">
            + 添加饰品
          </n-button>
        </n-space>
      </template>
    </page-header>

    <!-- 骨架屏 -->
    <template v-if="store.loading">
      <SkeletonTable v-if="viewMode === 'table'" :rows="6" :columns="6" />
      <SkeletonCard v-else :count="8" />
    </template>

    <!-- 空态 -->
    <template v-else-if="!store.items.length">
      <EmptyState
        :title="t('watchlist.emptyTitle')"
        :description="t('watchlist.emptyDesc')"
        emoji="📋"
      >
        <template #action>
          <n-button type="primary" @click="openCreateModal">
            + {{ t('watchlist.addFirstItem') }}
          </n-button>
        </template>
      </EmptyState>
    </template>

    <!-- 表格视图 -->
    <template v-else-if="viewMode === 'table'">
      <n-card :bordered="false" size="small">
        <n-data-table
          :columns="columns"
          :data="store.items"
          :row-key="(row) => row.market_hash_name"
          :checked-row-keys="checkedKeys"
          @update:checked-row-keys="(keys) => (checkedKeys = keys as string[])"
          size="small"
          striped
          class="watchlist-table"
        />
      </n-card>
    </template>

    <!-- 卡片视图 — BUFF 风格 -->
    <template v-else>
      <div class="card-grid">
        <div
          v-for="item in store.items"
          :key="item.market_hash_name"
          class="watchlist-card"
          :class="{ 'watchlist-card--disabled': !item.enabled }"
          @click="goToDetail(item)"
        >
          <!-- 顶部：饰品图示区 -->
          <div class="watchlist-card__image">
            <div class="watchlist-card__image-inner">
              <span class="watchlist-card__image-icon">{{ getWeaponEmoji(item.market_hash_name) }}</span>
            </div>
            <div class="watchlist-card__badge" :class="getWearClass(item.market_hash_name)">
              <span class="watchlist-card__badge-dot" />
              {{ getWearLabel(item.market_hash_name) }}
            </div>
            <n-checkbox
              class="watchlist-card__check"
              :checked="checkedKeys.includes(item.market_hash_name)"
              @update:checked="(v) => toggleCheck(item.market_hash_name, v as boolean)"
              @click.stop
            />
          </div>

          <!-- 中部：名称 + 价格 -->
          <div class="watchlist-card__body">
            <div class="watchlist-card__name">{{ item.display_name || item.market_hash_name }}</div>
            <div class="watchlist-card__price">
              <span class="watchlist-card__price-symbol">¥</span>
              <AnimatedNumber
                v-if="item.latest_price != null"
                :value="item.latest_price"
                :precision="2"
                class="watchlist-card__price-value"
              />
              <span v-else class="watchlist-card__price-value">—</span>
              <span
                v-if="item.change_24h != null"
                class="watchlist-card__change"
                :class="item.change_24h >= 0 ? 'up' : 'down'"
              >
                {{ item.change_24h >= 0 ? '▲' : '▼' }}{{ Math.abs(item.change_24h).toFixed(2) }}%
              </span>
            </div>
          </div>

          <!-- 底部：平台价格 + 趋势 -->
          <div class="watchlist-card__footer">
            <div class="watchlist-card__platforms">
              <span
                v-for="p in item.platform_prices.filter((pp: any) => pp.price > 0).slice(0, 4)"
                :key="p.platform"
                class="watchlist-card__platform-tag"
                :class="{ 'watchlist-card__platform-tag--best': p.price === minPlatformPrice(item) }"
              >
                {{ p.platform }}<span class="watchlist-card__platform-price">¥{{ p.price.toFixed(0) }}</span>
              </span>
            </div>
            <div class="watchlist-card__sparkline">
              <MiniSparkline
                v-if="item.sparkline.length >= 2"
                :data="item.sparkline"
                :color="sparklineColor(item)"
                :width="120"
                :height="28"
              />
            </div>
          </div>

          <!-- 操作栏 -->
          <div class="watchlist-card__actions" @click.stop>
            <n-button text size="tiny" @click="handleToggle(item)">
              {{ item.enabled ? '禁用' : '启用' }}
            </n-button>
            <n-button text size="tiny" type="primary" @click="openEditModal(item)">编辑</n-button>
            <n-button text size="tiny" type="error" @click="openDeleteModal(item)">删除</n-button>
          </div>
        </div>
      </div>
    </template>

    <!-- 批量操作浮栏 -->
    <transition name="slide-up">
      <div v-if="checkedKeys.length > 0" class="batch-bar">
        <span class="batch-bar__count">已选 {{ checkedKeys.length }} 项</span>
        <n-space>
          <n-button
            size="small"
            :loading="refreshing"
            :disabled="refreshButtonDisabled"
            @click="handleRefresh(checkedKeys)"
          >
            ⚡ 立即刷新 ({{ checkedKeys.length }})
          </n-button>
          <n-button size="small" @click="batchToggle(true)">批量启用</n-button>
          <n-button size="small" @click="batchToggle(false)">批量禁用</n-button>
          <n-button size="small" type="error" @click="batchDelete">批量删除</n-button>
          <n-button size="small" text @click="checkedKeys = []">取消</n-button>
        </n-space>
      </div>
    </transition>

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
      确定要删除监控项 "{{ itemToDelete?.market_hash_name }}" 吗？此操作不可恢复。
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import {
  NCard,
  NButton,
  NButtonGroup,
  NSpace,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NTag,
  NCheckbox,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, FormRules, FormInst } from 'naive-ui'
import { useWatchlistStore } from '@/stores/watchlist'
import type { WatchlistItemWithPrice } from '@/api'
import PageHeader from '@/components/layout/PageHeader.vue'
import MiniSparkline from '@/components/business/MiniSparkline.vue'
import SkeletonTable from '@/components/base/SkeletonTable.vue'
import SkeletonCard from '@/components/base/SkeletonCard.vue'
import EmptyState from '@/components/base/EmptyState.vue'
import AnimatedNumber from '@/components/base/AnimatedNumber.vue'
import { useTheme } from '@/composables/useTheme'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const store = useWatchlistStore()
const message = useMessage()
const { colorUp, colorDown } = useTheme()
const { t } = useI18n()

const viewMode = ref<'table' | 'card'>('table')
const checkedKeys = ref<string[]>([])

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
  const targets = names ?? checkedKeys.value
  if (targets.length === 0) {
    const all = store.items.filter((i) => i.enabled).map((i) => i.market_hash_name)
    if (all.length === 0) {
      message.warning('监控清单为空')
      return
    }
    if (all.length > 100) {
      message.warning(`监控清单有 ${all.length} 个物品，单次最多刷新 100 个，请使用多选`)
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
  if (cooldownSec.value > 0) return `${cooldownSec.value}s 后可刷新`
  if (checkedKeys.value.length > 0) return `刷新选中 ${checkedKeys.value.length} 项`
  return '刷新全部'
})

const refreshButtonDisabled = computed(
  () => refreshing.value || cooldownSec.value > 0 || checkedKeys.value.length > 100,
)

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
    checkedKeys.value = checkedKeys.value.filter(
      (k) => k !== itemToDelete.value?.market_hash_name,
    )
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

async function batchToggle(enabled: boolean) {
  try {
    await Promise.all(
      checkedKeys.value.map((key) =>
        store.updateItem(key, { enabled }),
      ),
    )
    message.success(`已${enabled ? '启用' : '禁用'} ${checkedKeys.value.length} 项`)
    checkedKeys.value = []
    await store.fetchItems()
  } catch (e: any) {
    message.error('批量操作失败')
  }
}

async function batchDelete() {
  try {
    await Promise.all(
      checkedKeys.value.map((key) => store.removeItem(key)),
    )
    message.success(`已删除 ${checkedKeys.value.length} 项`)
    checkedKeys.value = []
    await store.fetchItems()
  } catch (e: any) {
    message.error('批量删除失败')
  }
}

function toggleCheck(name: string, checked: boolean) {
  if (checked) {
    checkedKeys.value.push(name)
  } else {
    checkedKeys.value = checkedKeys.value.filter((k) => k !== name)
  }
}

function goToDetail(item: WatchlistItemWithPrice) {
  router.push({
    name: 'ItemDetail',
    params: { name: encodeURIComponent(item.market_hash_name) },
  })
}

function minPlatformPrice(item: WatchlistItemWithPrice): number | undefined {
  const nonzero = item.platform_prices.filter((p) => p.price > 0)
  return nonzero.length
    ? Math.min(...nonzero.map((p) => p.price))
    : undefined
}

function sparklineColor(item: WatchlistItemWithPrice): string {
  if (!item.sparkline.length) return '#3b82f6'
  const first = item.sparkline[0]
  const last = item.sparkline[item.sparkline.length - 1]
  if (last > first) return colorUp.value
  if (last < first) return colorDown.value
  return '#3b82f6'
}

// 品相解析
const wearMap: Record<string, string> = {
  'Factory New': '崭新出厂',
  'Minimal Wear': '略有磨损',
  'Field-Tested': '久经沙场',
  'Well-Worn': '破损不堪',
  'Battle-Scarred': '战痕累累',
}

function getWearLabel(name: string): string {
  const match = name.match(/\(([^)]+)\)/)
  if (!match) return ''
  return wearMap[match[1]] || match[1]
}

function getWearClass(name: string): string {
  const match = name.match(/\(([^)]+)\)/)
  if (!match) return ''
  const key = match[1]
  const map: Record<string, string> = {
    'Factory New': 'wear--fn',
    'Minimal Wear': 'wear--mw',
    'Field-Tested': 'wear--ft',
    'Well-Worn': 'wear--ww',
    'Battle-Scarred': 'wear--bs',
  }
  return map[key] || ''
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
  if (n.includes('ak-47')) return 'AK'
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

const columns: DataTableColumns<WatchlistItemWithPrice> = [
  {
    type: 'selection',
    options: ['all', 'none'],
  },
  {
    title: '饰品',
    key: 'market_hash_name',
    ellipsis: { tooltip: true },
    render(row) {
      const wear = getWearLabel(row.market_hash_name)
      return h('div', { class: 'item-cell' }, [
        h('div', { class: 'item-cell__icon' }, '🔫'),
        h('div', { class: 'item-cell__info' }, [
          h(
            'a',
            {
              href: 'javascript:void(0)',
              class: 'item-cell__name',
              onClick: () => goToDetail(row),
            },
            row.display_name || row.market_hash_name,
          ),
          wear
            ? h('span', { class: ['item-cell__wear', getWearClass(row.market_hash_name)] }, wear)
            : null,
        ]),
      ])
    },
  },
  {
    title: '当前价',
    key: 'latest_price',
    width: 160,
    render(row) {
      if (row.latest_price == null) return h('span', '—')
      const minPrice = minPlatformPrice(row)
      return h('div', { class: 'price-cell' }, [
        h('div', { class: 'price-cell__main font-mono-num' }, `¥${row.latest_price.toFixed(2)}`),
        row.platform_prices.filter((p: any) => p.price > 0).length > 0
          ? h(
              'div',
              { class: 'price-cell__platforms' },
              row.platform_prices.filter((p: any) => p.price > 0).slice(0, 3).map((p) =>
                h(
                  NTag,
                  {
                    size: 'tiny',
                    type: p.price === minPrice ? 'primary' : 'default',
                    bordered: false,
                  },
                  { default: () => `${p.platform} ¥${p.price.toFixed(0)}` },
                ),
              ),
            )
          : null,
      ])
    },
  },
  {
    title: '24h 变化',
    key: 'change_24h',
    width: 120,
    align: 'right',
    sorter: (a, b) => (a.change_24h ?? -Infinity) - (b.change_24h ?? -Infinity),
    render(row) {
      if (row.change_24h == null) return h('span', { class: 'text-gray-400' }, '—')
      const isUp = row.change_24h >= 0
      return h(
        'span',
        {
          class: ['change-badge', isUp ? 'change-badge--up' : 'change-badge--down'],
          style: {
            color: isUp ? colorUp.value : colorDown.value,
          },
        },
        `${isUp ? '▲' : '▼'} ${Math.abs(row.change_24h).toFixed(2)}%`,
      )
    },
  },
  {
    title: '7天走势',
    key: 'sparkline',
    width: 140,
    render(row) {
      if (row.sparkline.length < 2) {
        return h('span', { class: 'text-xs text-gray-400' }, '暂无数据')
      }
      return h(MiniSparkline, {
        data: row.sparkline,
        color: sparklineColor(row),
        width: 120,
        height: 32,
      })
    },
  },
  {
    title: '状态',
    key: 'enabled',
    width: 90,
    render(row) {
      return h(
        NTag,
        { type: row.enabled ? 'success' : 'default', size: 'small', bordered: false },
        { default: () => (row.enabled ? '监控中' : '已禁用') },
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render(row) {
      return h(NSpace, { size: 'small' }, {
        default: () => [
          h(
            NButton,
            { size: 'tiny', text: true, onClick: () => goToDetail(row) },
            { default: () => '详情' },
          ),
          h(
            NButton,
            { size: 'tiny', text: true, onClick: () => handleToggle(row) },
            { default: () => (row.enabled ? '禁用' : '启用') },
          ),
          h(
            NButton,
            { size: 'tiny', text: true, type: 'primary', onClick: () => openEditModal(row) },
            { default: () => '编辑' },
          ),
          h(
            NButton,
            { size: 'tiny', text: true, type: 'error', onClick: () => openDeleteModal(row) },
            { default: () => '删除' },
          ),
        ],
      })
    },
  },
]

onMounted(() => {
  store.fetchItems()
})
</script>

<style scoped>
/* 空态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 1rem;
  text-align: center;
}
.empty-state__icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.6;
}
.empty-state__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--n-text-color-1);
}
.empty-state__desc {
  font-size: 0.875rem;
  color: var(--n-text-color-3);
  margin-bottom: 1.5rem;
}

/* 表格样式 */
.watchlist-table :deep(.n-data-table-tbody .n-data-table-tr:hover) {
  background: var(--n-td-color-hover);
}

.item-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.item-cell__icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}
.item-cell__info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}
.item-cell__name {
  color: var(--n-text-color-1);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-cell__name:hover {
  color: #3b82f6;
}
.item-cell__wear {
  font-size: 0.75rem;
  padding: 0 0.375rem;
  border-radius: 0.25rem;
  width: fit-content;
}
.wear--fn {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}
.wear--fn .watchlist-card__badge-dot { background: #10b981; }
.wear--mw {
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}
.wear--mw .watchlist-card__badge-dot { background: #3b82f6; }
.wear--ft {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}
.wear--ft .watchlist-card__badge-dot { background: #f59e0b; }
.wear--ww {
  background: rgba(249, 115, 22, 0.12);
  color: #f97316;
}
.wear--ww .watchlist-card__badge-dot { background: #f97316; }
.wear--bs {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
.wear--bs .watchlist-card__badge-dot { background: #ef4444; }

html.dark .wear--fn {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
}
html.dark .wear--mw {
  background: rgba(96, 165, 250, 0.12);
  color: #60a5fa;
}
html.dark .wear--ft {
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
}
html.dark .wear--ww {
  background: rgba(251, 146, 60, 0.12);
  color: #fb923c;
}
html.dark .wear--bs {
  background: rgba(248, 113, 113, 0.12);
  color: #f87171;
}

.price-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.price-cell__main {
  font-weight: 600;
  font-size: 0.9375rem;
}
.price-cell__platforms {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.change-badge {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: 0.875rem;
}

/* 卡片网格 — BUFF 风格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}

.watchlist-card {
  border-radius: 10px;
  background: var(--n-card-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  cursor: pointer;
}
html.dark .watchlist-card {
  border-color: rgba(255, 255, 255, 0.05);
}
.watchlist-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: rgba(107, 127, 248, 0.15);
}
html.dark .watchlist-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border-color: rgba(107, 127, 248, 0.2);
}
.watchlist-card--disabled {
  opacity: 0.5;
}

/* 顶部图示区 */
.watchlist-card__image {
  position: relative;
  height: 120px;
  background: linear-gradient(135deg, rgba(107, 127, 248, 0.04) 0%, rgba(251, 146, 60, 0.04) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}
html.dark .watchlist-card__image {
  background: linear-gradient(135deg, rgba(107, 127, 248, 0.06) 0%, rgba(251, 146, 60, 0.03) 100%);
  border-bottom-color: rgba(255, 255, 255, 0.03);
}
.watchlist-card__image-inner {
  font-size: 2.5rem;
  font-weight: 800;
  font-family: 'JetBrains Mono', monospace;
  color: var(--cs-text-muted);
  opacity: 0.4;
  letter-spacing: -0.03em;
  user-select: none;
}
.watchlist-card__badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 0.6875rem;
  padding: 2px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  backdrop-filter: blur(8px);
}
.watchlist-card__badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.watchlist-card__check {
  position: absolute;
  top: 8px;
  right: 8px;
}

/* 中部：名称 + 价格 */
.watchlist-card__body {
  padding: 10px 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.watchlist-card__name {
  font-weight: 500;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--cs-text-secondary);
  line-height: 1.3;
}
.watchlist-card__price {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.watchlist-card__price-symbol {
  font-size: 0.75rem;
  font-weight: 500;
  color: #fb923c;
  font-family: 'JetBrains Mono', monospace;
}
.watchlist-card__price-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.25rem;
  font-weight: 700;
  color: #fb923c;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}
.watchlist-card__change {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6875rem;
  font-weight: 600;
  margin-left: auto;
  padding: 1px 5px;
  border-radius: 3px;
}
.watchlist-card__change.up {
  color: v-bind('colorUp');
  background: rgba(239, 68, 68, 0.08);
}
.watchlist-card__change.down {
  color: v-bind('colorDown');
  background: rgba(16, 185, 129, 0.08);
}

/* 底部：平台价格 + 趋势 */
.watchlist-card__footer {
  padding: 0 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.watchlist-card__platforms {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.watchlist-card__platform-tag {
  font-size: 0.625rem;
  padding: 2px 6px;
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.04);
  color: var(--cs-text-muted);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
html.dark .watchlist-card__platform-tag {
  background: rgba(255, 255, 255, 0.04);
}
.watchlist-card__platform-tag--best {
  background: rgba(107, 127, 248, 0.1);
  color: #6b7ff8;
}
.watchlist-card__platform-price {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}
.watchlist-card__sparkline {
  height: 28px;
  display: flex;
  align-items: center;
}

/* 操作栏 */
.watchlist-card__actions {
  display: flex;
  gap: 0.5rem;
  padding: 6px 12px 10px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  margin-top: auto;
}
html.dark .watchlist-card__actions {
  border-top-color: rgba(255, 255, 255, 0.04);
}

/* 批量操作浮栏 */
.batch-bar {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.25rem;
  background: var(--n-card-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 0.75rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  z-index: 100;
}
html.dark .batch-bar {
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}
.batch-bar__count {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 240ms ease, opacity 240ms ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateX(-50%) translateY(100%);
  opacity: 0;
}
</style>
