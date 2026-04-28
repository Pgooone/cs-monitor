<template>
  <div class="item-search" ref="rootRef">
    <!-- 搜索输入框 -->
    <n-input
      v-model:value="query"
      placeholder="输入饰品名称搜索，如 AK-47、Asiimov、红线..."
      clearable
      :loading="searching"
      @update:value="onInput"
      @focus="showDropdown = candidates.length > 0"
      @keydown.enter="onEnter"
      @keydown.escape="showDropdown = false"
      @keydown.down.prevent="moveSelection(1)"
      @keydown.up.prevent="moveSelection(-1)"
    >
      <template #prefix>
        <n-icon :size="16" :component="SearchOutline" />
      </template>
    </n-input>

    <!-- 搜索候选下拉 -->
    <div
      v-if="showDropdown && candidates.length > 0"
      class="item-search__dropdown"
    >
      <div
        v-for="(item, idx) in candidates"
        :key="item.market_hash_name"
        class="item-search__candidate"
        :class="{ 'item-search__candidate--active': idx === selectedIndex }"
        @click="selectCandidate(item)"
        @mouseenter="selectedIndex = idx"
      >
        <span class="item-search__candidate-name">{{ item.name || item.market_hash_name }}</span>
        <span v-if="item.name && item.name !== item.market_hash_name" class="item-search__candidate-alias">
          {{ item.market_hash_name }}
        </span>
      </div>
    </div>

    <!-- 价格查询结果 -->
    <n-card v-if="priceResult" class="item-search__result" size="small">
      <template #header>
        <div class="item-search__header">
          <span class="item-search__name">{{ priceResult.display_name || priceResult.market_hash_name }}</span>
          <n-tag v-if="priceResult.in_watchlist" type="success" size="small">已在监控</n-tag>
        </div>
      </template>
      <div class="item-search__prices">
        <div
          v-for="p in sortedPrices"
          :key="p.platform"
          class="item-search__price-row"
        >
          <span class="item-search__platform">{{ p.platform }}</span>
          <span class="item-search__price font-mono-num">¥{{ p.price.toFixed(2) }}</span>
        </div>
      </div>
      <template v-if="!priceResult.in_watchlist" #action>
        <n-button
          type="primary"
          size="small"
          :loading="addingWatchlist"
          @click="handleAddToWatchlist(priceResult.market_hash_name)"
        >
          + 添加到监控清单
        </n-button>
      </template>
    </n-card>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="item-search__error">
      {{ errorMsg }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { NInput, NButton, NCard, NTag, NIcon } from 'naive-ui'
import { SearchOutline } from '@vicons/ionicons5'
import api from '@/api'
import type { SearchItemResult, ItemPriceResult } from '@/api'

const query = ref('')
const searching = ref(false)
const addingWatchlist = ref(false)
const candidates = ref<SearchItemResult[]>([])
const showDropdown = ref(false)
const selectedIndex = ref(-1)
const priceResult = ref<ItemPriceResult | null>(null)
const errorMsg = ref('')
const rootRef = ref<HTMLElement | null>(null)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const emit = defineEmits<{
  addToWatchlist: [name: string]
}>()

const sortedPrices = computed(() => {
  if (!priceResult.value) return []
  return priceResult.value.dataList
    .filter((p: any) => p.sellPrice > 0)
    .map((p: any) => ({ platform: p.platform, price: p.sellPrice }))
    .sort((a: any, b: any) => a.price - b.price)
})

function onInput(val: string) {
  errorMsg.value = ''
  priceResult.value = null
  selectedIndex.value = -1

  if (debounceTimer) clearTimeout(debounceTimer)

  const q = val.trim()
  if (!q) {
    candidates.value = []
    showDropdown.value = false
    return
  }

  debounceTimer = setTimeout(() => doSearch(q), 300)
}

async function doSearch(q: string) {
  searching.value = true
  try {
    const res = await api.searchItems(q)
    candidates.value = res.data || []
    showDropdown.value = candidates.value.length > 0
    selectedIndex.value = candidates.value.length > 0 ? 0 : -1
  } catch (e: any) {
    candidates.value = []
    showDropdown.value = false
  } finally {
    searching.value = false
  }
}

function moveSelection(delta: number) {
  if (!showDropdown.value || candidates.value.length === 0) return
  const total = candidates.value.length
  selectedIndex.value = ((selectedIndex.value + delta) % total + total) % total
}

async function selectCandidate(item: SearchItemResult) {
  query.value = item.market_hash_name
  showDropdown.value = false
  candidates.value = []
  await lookupPrice(item.market_hash_name)
}

async function onEnter() {
  if (showDropdown.value && selectedIndex.value >= 0 && selectedIndex.value < candidates.value.length) {
    await selectCandidate(candidates.value[selectedIndex.value])
    return
  }
  const q = query.value.trim()
  if (!q) return
  showDropdown.value = false
  // 如果候选列表有结果，选第一个
  if (candidates.value.length > 0) {
    await selectCandidate(candidates.value[0])
  } else {
    // 直接按输入查价格
    await lookupPrice(q)
  }
}

async function lookupPrice(marketHashName: string) {
  searching.value = true
  errorMsg.value = ''
  priceResult.value = null
  try {
    const res = await api.lookupItemPrice(marketHashName)
    const data = res.data
    if (data && data.dataList && data.dataList.length > 0) {
      priceResult.value = data
    } else {
      errorMsg.value = `未找到 "${marketHashName}" 的价格数据，该饰品可能未被 SteamDT 收录`
    }
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误'
    errorMsg.value = `查询失败: ${detail}`
  } finally {
    searching.value = false
  }
}

async function handleAddToWatchlist(name: string) {
  addingWatchlist.value = true
  try {
    await api.createWatchlistItem({ market_hash_name: name, threshold_percent: 5 })
    if (priceResult.value) {
      priceResult.value.in_watchlist = true
    }
    emit('addToWatchlist', name)
  } catch (e: any) {
    errorMsg.value = `添加失败: ${e.response?.data?.detail || e.message}`
  } finally {
    addingWatchlist.value = false
  }
}

// 点击外部关闭下拉
function onClickOutside(e: MouseEvent) {
  if (rootRef.value && !rootRef.value.contains(e.target as Node)) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.item-search {
  position: relative;
  margin-bottom: 1.25rem;
}

.item-search__dropdown {
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
  max-height: 320px;
  overflow-y: auto;
}

.item-search__candidate {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.15s;
  overflow: hidden;
}

.item-search__candidate:hover,
.item-search__candidate--active {
  background: rgba(99, 102, 241, 0.08);
}

.item-search__candidate-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--cs-text-primary, #333);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.item-search__candidate-alias {
  font-size: 0.75rem;
  color: var(--cs-text-secondary, #999);
  white-space: nowrap;
  flex-shrink: 0;
  max-width: 40%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-search__result {
  margin-top: 0.75rem;
  border-radius: 0.875rem;
}

.item-search__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.item-search__name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--cs-text-primary);
}

.item-search__prices {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 0.5rem;
}

.item-search__price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0.625rem;
  border-radius: 0.5rem;
  background: var(--cs-bg-card);
  border: 1px solid var(--cs-border-light);
}

.item-search__platform {
  font-size: 0.8125rem;
  color: var(--cs-text-secondary);
  font-weight: 500;
}

.item-search__price {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--cs-text-primary);
}

.item-search__error {
  margin-top: 0.5rem;
  padding: 0.625rem 0.875rem;
  border-radius: 0.625rem;
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  font-size: 0.8125rem;
}
</style>
