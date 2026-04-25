<template>
  <div class="item-search">
    <n-input-group>
      <n-input
        v-model:value="query"
        placeholder="输入饰品名称搜索，如 AK-47 | Bloodsport (Field-Tested)"
        clearable
        :loading="loading"
        @keydown.enter="search"
      />
      <n-button type="primary" :loading="loading" @click="search">
        搜索
      </n-button>
    </n-input-group>

    <!-- 搜索结果 -->
    <n-card v-if="result" class="item-search__result" size="small">
      <template #header>
        <div class="item-search__header">
          <span class="item-search__name">{{ result.market_hash_name }}</span>
          <n-tag v-if="result.in_watchlist" type="success" size="small">已在监控</n-tag>
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
      <template v-if="!result.in_watchlist" #action>
        <n-button
          type="primary"
          size="small"
          :loading="loading"
          @click="handleAddToWatchlist(result.market_hash_name)"
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
import { ref, computed } from 'vue'
import { NInput, NInputGroup, NButton, NCard, NTag } from 'naive-ui'
import api from '@/api'

const query = ref('')
const loading = ref(false)
const result = ref<{
  market_hash_name: string
  dataList: { platform: string; sellPrice: number }[]
  in_watchlist: boolean
} | null>(null)
const errorMsg = ref('')

const emit = defineEmits<{
  addToWatchlist: [name: string]
}>()

const sortedPrices = computed(() => {
  if (!result.value) return []
  const valid = result.value.dataList.filter((p: any) => p.sellPrice > 0)
  return valid
    .map((p: any) => ({ platform: p.platform, price: p.sellPrice }))
    .sort((a, b) => a.price - b.price)
})

async function search() {
  const q = query.value.trim()
  if (!q) return

  loading.value = true
  errorMsg.value = ''
  result.value = null

  try {
    const response = await api.searchItemPrice(q)
    const data = response.data
    if (data && data.dataList && data.dataList.length > 0) {
      result.value = data
    } else {
      errorMsg.value = `未找到 "${q}" 的价格数据，请检查饰品名称是否正确`
    }
  } catch (e: any) {
    const detail = e.response?.data?.detail || e.message || '未知错误'
    errorMsg.value = `搜索失败: ${detail}`
  } finally {
    loading.value = false
  }
}

async function handleAddToWatchlist(name: string) {
  try {
    await api.createWatchlistItem({ market_hash_name: name, threshold_percent: 5 })
    if (result.value) {
      result.value.in_watchlist = true
    }
    emit('addToWatchlist', name)
  } catch (e: any) {
    errorMsg.value = `添加失败: ${e.response?.data?.detail || e.message}`
  }
}
</script>

<style scoped>
.item-search {
  margin-bottom: 1.25rem;
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
