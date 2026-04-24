<template>
  <div>
    <page-header title="监控清单">
      <template #actions>
        <n-space>
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

    <!-- 卡片视图 -->
    <template v-else>
      <div class="card-grid">
        <div
          v-for="item in store.items"
          :key="item.market_hash_name"
          class="watchlist-card"
          :class="{ 'watchlist-card--disabled': !item.enabled }"
        >
          <div class="watchlist-card__header">
            <n-checkbox
              :checked="checkedKeys.includes(item.market_hash_name)"
              @update:checked="(v) => toggleCheck(item.market_hash_name, v as boolean)"
            />
            <div class="watchlist-card__badge" :class="getWearClass(item.market_hash_name)">
              {{ getWearLabel(item.market_hash_name) }}
            </div>
          </div>
          <div class="watchlist-card__name">{{ item.display_name || item.market_hash_name }}</div>
          <div class="watchlist-card__price">
            <span class="font-mono-num">
              <AnimatedNumber
                v-if="item.latest_price != null"
                :value="item.latest_price"
                :precision="2"
                prefix="¥"
              />
              <span v-else>—</span>
            </span>
            <span
              v-if="item.change_24h != null"
              class="watchlist-card__change"
              :class="item.change_24h >= 0 ? 'up' : 'down'"
            >
              {{ item.change_24h >= 0 ? '▲' : '▼' }} {{ Math.abs(item.change_24h).toFixed(2) }}%
            </span>
          </div>
          <div class="watchlist-card__platforms">
            <n-tag
              v-for="p in item.platform_prices.slice(0, 3)"
              :key="p.platform"
              size="tiny"
              :type="p.price === minPlatformPrice(item) ? 'primary' : 'default'"
            >
              {{ p.platform }} ¥{{ p.price.toFixed(0) }}
            </n-tag>
          </div>
          <div class="watchlist-card__sparkline">
            <MiniSparkline
              v-if="item.sparkline.length >= 2"
              :data="item.sparkline"
              :color="sparklineColor(item)"
              :width="200"
              :height="40"
            />
            <span v-else class="text-xs text-gray-400">暂无趋势数据</span>
          </div>
          <div class="watchlist-card__actions">
            <n-button text size="tiny" @click="goToDetail(item)">查看详情</n-button>
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
import { ref, onMounted, h } from 'vue'
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
  return item.platform_prices.length
    ? Math.min(...item.platform_prices.map((p) => p.price))
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
        row.platform_prices.length > 0
          ? h(
              'div',
              { class: 'price-cell__platforms' },
              row.platform_prices.slice(0, 3).map((p) =>
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
  background: #dcfce7;
  color: #166534;
}
.wear--mw {
  background: #dbeafe;
  color: #1e40af;
}
.wear--ft {
  background: #fef3c7;
  color: #92400e;
}
.wear--ww {
  background: #ffedd5;
  color: #9a3412;
}
.wear--bs {
  background: #fee2e2;
  color: #991b1b;
}
html.dark .wear--fn {
  background: #14532d;
  color: #86efac;
}
html.dark .wear--mw {
  background: #1e3a8a;
  color: #93c5fd;
}
html.dark .wear--ft {
  background: #78350f;
  color: #fcd34d;
}
html.dark .wear--ww {
  background: #7c2d12;
  color: #fdba74;
}
html.dark .wear--bs {
  background: #7f1d1d;
  color: #fca5a5;
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

/* 卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.watchlist-card {
  border-radius: 0.75rem;
  padding: 1rem;
  background: var(--n-card-color, #fff);
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: transform 200ms ease, box-shadow 200ms ease;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
html.dark .watchlist-card {
  border-color: rgba(255, 255, 255, 0.06);
}
.watchlist-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.watchlist-card--disabled {
  opacity: 0.6;
}
.watchlist-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.watchlist-card__badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}
.watchlist-card__name {
  font-weight: 600;
  font-size: 0.9375rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.watchlist-card__price {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.watchlist-card__change {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8125rem;
  font-weight: 600;
}
.watchlist-card__change.up {
  color: v-bind('colorUp');
}
.watchlist-card__change.down {
  color: v-bind('colorDown');
}
.watchlist-card__platforms {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}
.watchlist-card__sparkline {
  height: 40px;
  display: flex;
  align-items: center;
}
.watchlist-card__actions {
  display: flex;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}
html.dark .watchlist-card__actions {
  border-top-color: rgba(255, 255, 255, 0.06);
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
