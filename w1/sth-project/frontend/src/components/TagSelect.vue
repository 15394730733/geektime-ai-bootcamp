<template>
  <el-select
    :model-value="modelValue"
    :multiple="multiple"
    :placeholder="placeholder"
    :filterable="filterable"
    :clearable="clearable"
    @update:model-value="handleChange"
    style="width: 100%"
  >
    <el-option
      v-for="tag in tags"
      :key="tag.id"
      :label="tag.name"
      :value="tag.id"
    >
      <div class="tag-select-option">
        <tag-badge :tag="tag" />
      </div>
    </el-option>
  </el-select>
</template>

<script setup lang="ts">
import TagBadge from './TagBadge.vue'
import type { Tag } from '@/types/tag'

interface Props {
  modelValue: string | string[] | null
  tags: Tag[]
  placeholder?: string
  multiple?: boolean
  filterable?: boolean
  clearable?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string | string[] | null): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

function handleChange(value: string | string[] | null) {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.tag-select-option {
  display: flex;
  align-items: center;
}
</style>
