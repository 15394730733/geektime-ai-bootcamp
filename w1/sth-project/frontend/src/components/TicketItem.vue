<template>
  <div class="ticket-item" :class="{ 'is-completed': ticket.is_completed }">
    <div class="ticket-item-header">
      <div class="ticket-item-title">
        <el-checkbox
          :model-value="ticket.is_completed"
          @change="handleToggleComplete"
        />
        <span class="title-text">{{ ticket.title }}</span>
      </div>
      <div class="ticket-item-actions">
        <el-button
          type="primary"
          size="small"
          text
          @click="handleEdit"
        >
          编辑
        </el-button>
        <el-button
          type="danger"
          size="small"
          text
          @click="handleDelete"
        >
          删除
        </el-button>
      </div>
    </div>

    <div v-if="ticket.description" class="ticket-item-description">
      {{ truncateText(ticket.description, 100) }}
    </div>

    <div class="ticket-item-meta">
      <div class="ticket-item-tags">
        <tag-badge
          v-for="tag in ticket.tags"
          :key="tag.id"
          :tag="tag"
        />
      </div>
      <div class="ticket-item-date">
        {{ formatDate(ticket.created_at) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDate, truncateText } from '@/utils'
import TagBadge from './TagBadge.vue'
import type { Ticket } from '@/types/ticket'

interface Props {
  ticket: Ticket
}

interface Emits {
  (e: 'edit', ticket: Ticket): void
  (e: 'delete', ticket: Ticket): void
  (e: 'toggle-complete', ticket: Ticket): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

function handleEdit() {
  emit('edit', props.ticket)
}

function handleDelete() {
  emit('delete', props.ticket)
}

function handleToggleComplete() {
  emit('toggle-complete', props.ticket)
}
</script>

<style scoped>
.ticket-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.ticket-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ticket-item.is-completed {
  opacity: 0.6;
}

.ticket-item.is-completed .title-text {
  text-decoration: line-through;
}

.ticket-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.ticket-item-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.title-text {
  font-size: 16px;
  font-weight: 500;
}

.ticket-item-actions {
  display: flex;
  gap: 8px;
}

.ticket-item-description {
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.5;
}

.ticket-item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ticket-item-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ticket-item-date {
  color: #909399;
  font-size: 12px;
}
</style>
