<template>
  <div class="tags-page">
    <div class="page-header">
      <h1>标签管理</h1>
      <p class="page-description">创建和管理您的标签</p>
    </div>

    <div class="page-content">
      <el-card shadow="never">
        <tag-list />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import TagList from '@/components/TagList.vue'
</script>

<style scoped>
.tags-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.page-content {
  background: #f5f7fa;
  padding: 24px;
  border-radius: 8px;
}
</style>
