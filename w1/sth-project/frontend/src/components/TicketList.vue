<template>
  <div class="ticket-list">
    <div class="ticket-list-header">
      <h3>Ticket 列表</h3>
      <el-button type="primary" @click="handleCreate">新建 Ticket</el-button>
    </div>

    <div class="ticket-list-filters">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索 Ticket 标题"
        clearable
        @input="handleSearch"
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterStatus"
        placeholder="筛选状态"
        clearable
        @change="handleFilter"
        style="width: 150px"
      >
        <el-option label="全部" value="" />
        <el-option label="进行中" value="active" />
        <el-option label="已完成" value="completed" />
      </el-select>

      <el-select
        v-model="filterTag"
        placeholder="筛选标签"
        clearable
        filterable
        @change="handleFilter"
        style="width: 200px"
      >
        <el-option label="全部" value="" />
        <el-option
          v-for="tag in tags"
          :key="tag.id"
          :label="tag.name"
          :value="tag.id"
        />
      </el-select>
    </div>

    <div v-loading="loading" class="ticket-list-content">
      <el-empty v-if="!loading && filteredTickets.length === 0" description="暂无 Ticket" />

      <div v-else class="ticket-items">
        <ticket-item
          v-for="ticket in filteredTickets"
          :key="ticket.id"
          :ticket="ticket"
          @edit="handleEdit"
          @delete="handleDelete"
          @toggle-complete="handleToggleComplete"
        />
      </div>
    </div>

    <div class="ticket-list-pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <ticket-form
      v-model:visible="formVisible"
      :ticket="editingTicket"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import TicketItem from './TicketItem.vue'
import TicketForm from './TicketForm.vue'
import { useTicketStore } from '@/stores/ticket'
import { useTagStore } from '@/stores/tag'
import type { Ticket } from '@/types/ticket'

const ticketStore = useTicketStore()
const tagStore = useTagStore()

const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const filterTag = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const formVisible = ref(false)
const editingTicket = ref<Ticket | null>(null)

const tickets = computed(() => ticketStore.tickets)
const tags = computed(() => tagStore.tags)
const total = computed(() => ticketStore.total)

const filteredTickets = computed(() => {
  let result = [...tickets.value]

  if (filterStatus.value === 'active') {
    result = result.filter(t => !t.is_completed)
  } else if (filterStatus.value === 'completed') {
    result = result.filter(t => t.is_completed)
  }

  if (filterTag.value) {
    result = result.filter(t => 
      t.tags && t.tags.some(tag => tag.id === filterTag.value)
    )
  }

  return result
})

async function loadTickets() {
  loading.value = true
  try {
    await ticketStore.fetchTickets({
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value || undefined
    })
  } catch (error) {
    ElMessage.error('加载 Ticket 列表失败')
  } finally {
    loading.value = false
  }
}

async function loadTags() {
  try {
    await tagStore.fetchTags({ page: 1, page_size: 100 })
  } catch (error) {
    ElMessage.error('加载 Tag 列表失败')
  }
}

function handleSearch() {
  currentPage.value = 1
  loadTickets()
}

function handleFilter() {
  currentPage.value = 1
  loadTickets()
}

function handlePageChange(page: number) {
  currentPage.value = page
  loadTickets()
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadTickets()
}

function handleCreate() {
  editingTicket.value = null
  formVisible.value = true
}

function handleEdit(ticket: Ticket) {
  editingTicket.value = ticket
  formVisible.value = true
}

async function handleDelete(ticket: Ticket) {
  try {
    await ElMessageBox.confirm(
      `确定要删除 Ticket "${ticket.title}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await ticketStore.deleteTicket(ticket.id)
    ElMessage.success('删除成功')
    loadTickets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

async function handleToggleComplete(ticket: Ticket) {
  try {
    await ticketStore.toggleTicketComplete(ticket.id)
    ElMessage.success(ticket.is_completed ? '已标记为未完成' : '已标记为完成')
    loadTickets()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

async function handleSubmit(ticket: Partial<Ticket>) {
  try {
    if (editingTicket.value) {
      await ticketStore.updateTicket(editingTicket.value.id, ticket)
      ElMessage.success('更新成功')
    } else {
      await ticketStore.createTicket(ticket)
      ElMessage.success('创建成功')
    }
    formVisible.value = false
    loadTickets()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

onMounted(() => {
  loadTickets()
  loadTags()
})
</script>

<style scoped>
.ticket-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ticket-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ticket-list-header h3 {
  margin: 0;
}

.ticket-list-filters {
  display: flex;
  gap: 12px;
}

.ticket-list-content {
  min-height: 200px;
}

.ticket-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ticket-list-pagination {
  display: flex;
  justify-content: center;
}
</style>
