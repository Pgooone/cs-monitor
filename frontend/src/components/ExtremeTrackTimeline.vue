<template>
  <div class="px-4 py-2">
    <n-empty v-if="!hasData" description="暂无实时变动数据" />
    <n-timeline v-else>
      <n-timeline-item
        v-for="(item, idx) in realtimeData"
        :key="idx"
        :type="timelineType(item) as any"}
      >
        <template #header>
          <n-space>
            <n-tag :type="tagType(item.alert_type) as any" size="small">
              {{ alertLabel(item.alert_type) }}
            </n-tag>
            <n-text depth="3" class="text-xs">{{ formatTime(item.timestamp) }}</n-text>
          </n-space>
        </template>
        <n-space vertical size="small">
          <n-text v-if="item.prev_price != null && item.curr_price != null">
            价格: ¥{{ item.prev_price.toFixed(2) }} → ¥{{ item.curr_price.toFixed(2) }}
            <n-text
              :type="priceChangeType(item.curr_price, item.prev_price)"
              class="ml-2"
            >
              {{ priceChangeText(item.curr_price, item.prev_price) }}
            </n-text>
          </n-text>
          <n-text v-if="item.prev_quantity != null && item.curr_quantity != null">
            数量: {{ item.prev_quantity }} 件 → {{ item.curr_quantity }} 件
            <n-text
              :type="qtyChangeType(item.curr_quantity, item.prev_quantity)"
              class="ml-2"
            >
              {{ qtyChangeText(item.curr_quantity, item.prev_quantity) }}
            </n-text>
          </n-text>
        </n-space>
      </n-timeline-item>
    </n-timeline>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NEmpty, NTimeline, NTimelineItem, NTag, NSpace, NText } from 'naive-ui'
import type { ExtremeTrackConfig } from '@/api'

const props = defineProps<{
  item: ExtremeTrackConfig
}>()

const realtimeData = computed(() => {
  const raw = (props.item as any)._realtime || []
  return raw.slice(0, 10)
})

const hasData = computed(() => realtimeData.value.length > 0)

function timelineType(data: any) {
  if (data.alert_type === 'both') return 'warning'
  if (data.alert_type === 'price_change') return 'info'
  return 'default'
}

function tagType(alertType: string) {
  const map: Record<string, string> = {
    both: 'error',
    price_change: 'warning',
    quantity_change: 'info',
  }
  return map[alertType] || 'default'
}

function alertLabel(alertType: string) {
  const map: Record<string, string> = {
    both: '价格+数量变动',
    price_change: '价格变动',
    quantity_change: '数量变动',
  }
  return map[alertType] || alertType
}

function priceChangeType(curr: number, prev: number) {
  return curr > prev ? 'error' : curr < prev ? 'success' : 'default'
}

function priceChangeText(curr: number, prev: number) {
  const diff = curr - prev
  const pct = prev !== 0 ? (diff / prev) * 100 : 0
  const sign = diff >= 0 ? '+' : ''
  return `${sign}¥${diff.toFixed(2)} (${sign}${pct.toFixed(2)}%)`
}

function qtyChangeType(curr: number, prev: number) {
  return curr > prev ? 'success' : curr < prev ? 'error' : 'default'
}

function qtyChangeText(curr: number, prev: number) {
  const diff = curr - prev
  const sign = diff >= 0 ? '+' : ''
  return `${sign}${diff} 件`
}

function formatTime(ts: string) {
  if (!ts) return '-'
  return new Date(ts).toLocaleString('zh-CN')
}
</script>
