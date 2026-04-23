<template>
  <div>
    <page-header title="监控清单">
      <template #actions>
        <n-button type="primary" @click="openCreateModal">
          <template #icon>
            <span>+</span>
          </template>
          添加饰品
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
      />
    </n-card>

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
  NSpace,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NTag,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, FormRules, FormInst } from 'naive-ui'
import { useWatchlistStore } from '@/stores/watchlist'
import type { WatchlistItemWithPrice } from '@/api'
import PageHeader from '@/components/layout/PageHeader.vue'

const router = useRouter()
const store = useWatchlistStore()
const message = useMessage()

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

const columns: DataTableColumns<WatchlistItemWithPrice> = [
  {
    title: '饰品名称',
    key: 'market_hash_name',
    ellipsis: { tooltip: true },
    render(row) {
      return h(
        'a',
        {
          href: 'javascript:void(0)',
          style: 'color: #1890ff; text-decoration: none;',
          onClick: () => goToDetail(row),
        },
        row.display_name || row.market_hash_name,
      )
    },
  },
  {
    title: '当前价格',
    key: 'latest_price',
    render(row) {
      if (row.latest_price == null) return h('span', '—')
      return h('span', `¥${row.latest_price.toFixed(2)}`)
    },
  },
  { title: '平台', key: 'platform', render(row) {
    return row.platform || '—'
  } },
  {
    title: '阈值(%)',
    key: 'threshold_percent',
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

onMounted(() => {
  store.fetchItems()
})
</script>
