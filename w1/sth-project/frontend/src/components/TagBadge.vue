<template>
  <el-tag
    :color="tag.color"
    effect="plain"
    size="default"
  >
    {{ tag.name }}
  </el-tag>
</template>

<script setup lang="ts">
import type { Tag } from '@/types/tag'

interface Props {
  tag: Tag
}

defineProps<Props>()
</script>

<style scoped>
:deep(.el-tag) {
  border: 1px solid v-bind('tag.color');
  color: v-bind('tag.color');
  background: v-bind('tag.color + "15"');
}
</style>
