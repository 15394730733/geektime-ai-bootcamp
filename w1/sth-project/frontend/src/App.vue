<template>
  <el-container class="app-container">
    <el-aside width="200px" class="app-aside">
      <div class="logo">
        <h2>Ticket Manager</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="app-menu"
      >
        <el-menu-item index="/tickets">
          <el-icon><Document /></el-icon>
          <span>Ticket 管理</span>
        </el-menu-item>
        <el-menu-item index="/tags">
          <el-icon><Collection /></el-icon>
          <span>标签管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="app-main-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1>{{ currentPageTitle }}</h1>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Collection } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  return route.meta.title as string || 'Ticket 标签管理'
})
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-aside {
  background: #001529;
  color: #fff;
}

.logo {
  padding: 24px 16px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.app-menu {
  border: none;
  background: #001529;
}

.app-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
}

.app-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.app-menu :deep(.el-menu-item.is-active) {
  background: #1890ff;
  color: #fff;
}

.app-main-container {
  background: #f0f2f5;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.app-main {
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
