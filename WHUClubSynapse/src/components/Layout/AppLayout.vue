<template>
  <el-container class="app-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <AppHeader :clearSearch="clearsearch" @update:clearSearch="update" />
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="app-main">
      <router-view @clearSearch="clearSearch" />
    </el-main>

    <!-- 底部 -->
    <el-footer class="app-footer">
      <AppFooter />
    </el-footer>

    <!-- API模式切换组件 (仅开发环境显示) -->
    <ApiModeSwitch />
  </el-container>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/Layout/AppHeader.vue'
import AppFooter from '@/components/Layout/AppFooter.vue'
import ApiModeSwitch from '@/components/Layout/ApiModeSwitch.vue'

const authStore = useAuthStore()

const clearsearch = ref(false)
const clearSearch = () => {
  console.log('clearSearch')
  clearsearch.value = true
}

const update = (value: boolean) => {
  clearsearch.value = value
}

// 初始化应用
onMounted(async () => {
  await authStore.initialize()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.app-header {
  margin-bottom: 0;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  position: sticky;
  top: 0;
  width: 100%;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 60px - 60px);
}

.app-footer {
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  text-align: center;
  line-height: 40px;
  color: #606266;
}
</style>
