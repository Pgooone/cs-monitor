<template>
  <div>
    <page-header title="极致追踪">
      <template #actions>
        <n-button type="primary" @click="openCreateModal">
          <template #icon>
            <span>+</span>
          </template>
          添加追踪
        </n-button>
      </template>
    </page-header>

    <n-card>
      <n-data-table
        :columns="columns"
        :data="store.items"
        :loading="store.loading"
        :pagination="{ pageSize: 10 }"
        size="small"
        striped
        :row-key="rowKey"
      />
    </n-card>

    <!-- 添加/编辑弹窗 -->
    <n-modal
      v-model:show="modalVisible"
      :title="isEditing ? '编辑追踪配置' : '添加追踪配置'"
      preset="card"
      style="width: 560px"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="120"
      >
        <n-form-item label="饰品名称" path="market_hash_name">
          <n-input
            v-model:value="formData.market_hash_name"
            placeholder="请输入饰品市场名称"
            :disabled="isEditing"
          />
        </n-form-item>
        <n-form-item label="平台" path="platform">
          <n-input
            v-model:value="formData.platform"
            placeholder="如 buff / youpin / igxe"
            :disabled="isEditing"
          />
        </n-form-item>
        <n-form-item label="轮询间隔(秒)" path="interval_seconds">
          <n-input-number
            v-model:value="formData.interval_seconds"
            :min="5"
            style="width: 100%"
          />
        </n-form-item>
        <n-divider />
        <n-form-item label="价格追踪">
          <n-space>
            <n-switch v-model:value="formData.price_track_enabled" />
            <n-select
              v-model:value="formData.price_change_mode"
              :options="modeOptions"
              style="width: 120px"
            />
            <n-input-number
              v-model:value="formData.price_threshold_percent"
              :min="0"
              :precision="2"
              placeholder="阈值%"
              style="width: 120px"
            />
          </n-space>
        </n-form-item>
        <n-form-item label="数量追踪">
          <n-space>
            <n-switch v-model:value="formData.quantity_track_enabled" />
            <n-select
              v-model:value="formData.quantity_change_mode"
              :options="modeOptions"
              style="width: 120px"
            />
            <n-input-number
              v-model:value="formData.quantity_threshold_percent"
              :min="0"
              :precision="2"
              placeholder="阈值%"
              style="width: 120px"
            />
          </n-space>
        </n-form-item>
        <n-form-item label="冷却时间(秒)">
          <n-input-number
            v-model:value="formData.alert_cooldown_seconds"
            :min="0"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="免打扰时段">
          <n-space>
            <n-time-picker
              v-model:formatted-value="formData.quiet_hours_start"
              value-format="HH:mm"
              placeholder="开始"
            />
            <span>至</span>
            <n-time-picker
              v-model:formatted-value="formData.quiet_hours_end"
              value-format="HH:mm"
              placeholder="结束"
            />
          </n-space>
        </n-form-item>
        <n-form-item label="启用">
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
      确定要删除追踪项 "{{ itemToDelete?.market_hash_name }}@{{ itemToDelete?.platform }}" 吗？此操作不可恢复。
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, h, watch } from 'vue'
import {
  NCard,
  NButton,
  NSpace,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NSelect,
  NDivider,
  NTimePicker,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, FormRules, FormInst } from 'naive-ui'
import { useExtremeTrackStore } from '@/stores/extremeTrack'
import type { ExtremeTrackConfig } from '@/api'
import { WebSocketClient } from '@/utils/ws'
import ExtremeTrackTimeline from '@/components/ExtremeTrackTimeline.vue'
import PageHeader from '@/components/layout/PageHeader.vue'

const store = useExtremeTrackStore()
const message = useMessage()

const wsMap = new Map<string, WebSocketClient>()

function rowKey(row: ExtremeTrackConfig) {
  return `${row.market_hash_name}@${row.platform}`
}

function buildWsUrl(marketHashName: string, platform: string) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  return `${protocol}//${host}/ws/extreme-track/${encodeURIComponent(marketHashName)}/${encodeURIComponent(platform)}`
}

function connectWs(item: ExtremeTrackConfig) {
  const key = `${item.market_hash_name}@${item.platform}`
  if (wsMap.has(key)) return
  const url = buildWsUrl(item.market_hash_name, item.platform)
  const ws = new WebSocketClient({
    url,
    onMessage: (msg) => {
      if (msg.type === 'extreme_track' && msg.data) {
        store.updateRealtimeData(key, msg.data)
      }
    },
  })
  ws.connect()
  wsMap.set(key, ws)
}

function disconnectWs(item: ExtremeTrackConfig) {
  const key = `${item.market_hash_name}@${item.platform}`
  const ws = wsMap.get(key)
  if (ws) {
    ws.close()
    wsMap.delete(key)
  }
}

function syncWsConnections() {
  // 为所有启用的项建立连接，禁用的断开
  store.items.forEach((item) => {
    if (item.enabled) {
      connectWs(item)
    } else {
      disconnectWs(item)
    }
  })
}

const modalVisible = ref(false)
const deleteModalVisible = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const isEditing = ref(false)
const formRef = ref<FormInst | null>(null)
const itemToDelete = ref<ExtremeTrackConfig | null>(null)

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
    { required: true, message: '请输入平台名称', trigger: 'blur' },
  ],
  interval_seconds: [
    { required: true, message: '请输入轮询间隔', type: 'number', trigger: 'blur' },
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
  modalVisible.value = true
}

function openDeleteModal(item: ExtremeTrackConfig) {
  itemToDelete.value = item
  deleteModalVisible.value = true
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
    message.success(item.enabled ? '已禁用' : '已启用')
  } catch (e: any) {
    message.error(e?.response?.data?.detail || '操作失败')
  }
}

function formatMode(mode: string, threshold: number, trackEnabled: number) {
  if (!trackEnabled) return '关闭'
  if (mode === 'any') return '任何变动'
  return `超 ${threshold}%`
}

const columns: DataTableColumns<ExtremeTrackConfig> = [
  {
    type: 'expand',
    renderExpand(rowData) {
      return h(ExtremeTrackTimeline, { item: rowData as ExtremeTrackConfig })
    },
  },
  {
    title: '饰品名称',
    key: 'market_hash_name',
    ellipsis: { tooltip: true },
  },
  { title: '平台', key: 'platform' },
  { title: '间隔(秒)', key: 'interval_seconds' },
  {
    title: '价格追踪',
    key: 'price_track',
    render(row) {
      return h(
        NTag,
        { type: row.price_track_enabled ? 'info' : 'default', size: 'small' },
        { default: () => formatMode(row.price_change_mode, row.price_threshold_percent, row.price_track_enabled) },
      )
    },
  },
  {
    title: '数量追踪',
    key: 'quantity_track',
    render(row) {
      return h(
        NTag,
        { type: row.quantity_track_enabled ? 'info' : 'default', size: 'small' },
        { default: () => formatMode(row.quantity_change_mode, row.quantity_threshold_percent, row.quantity_track_enabled) },
      )
    },
  },
  {
    title: '状态',
    key: 'enabled',
    render(row) {
      return h(
        NTag,
        { type: row.enabled ? 'success' : 'default', size: 'small' },
        { default: () => (row.enabled ? '启用' : '禁用') },
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
            {
              size: 'small',
              onClick: () => handleToggle(row),
            },
            { default: () => (row.enabled ? '禁用' : '启用') },
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              ghost: true,
              onClick: () => openEditModal(row),
            },
            { default: () => '编辑' },
          ),
          h(
            NButton,
            {
              size: 'small',
              type: 'error',
              ghost: true,
              onClick: () => openDeleteModal(row),
            },
            { default: () => '删除' },
          ),
        ],
      })
    },
  },
]

watch(() => store.items, () => {
  syncWsConnections()
}, { deep: true })

onMounted(() => {
  store.fetchItems().then(() => {
    syncWsConnections()
  })
})

onBeforeUnmount(() => {
  wsMap.forEach((ws) => ws.close())
  wsMap.clear()
})
</script>
