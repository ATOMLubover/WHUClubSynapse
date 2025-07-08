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

    <!-- AI侧边栏对话 -->
    <AISideChat />

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
import AISideChat from '@/components/Chat/AISideChat.vue'

const clearsearch = ref(false)
const clearSearch = () => {
  console.log('clearSearch')
  clearsearch.value = true
}

const update = (value: boolean) => {
  clearsearch.value = value
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #8ec5fc 0%, #e0c3fc 100%);
  /* background: linear-gradient(135deg, #6e8efb 0%, #a777e3 30%, #9f7aea 70%, #5e60ce 100%); */
  background-attachment: fixed;
}

.app-header {
  margin-bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  position: sticky;
  top: 0;
  width: 100%;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0 0 5px 5px;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 60px - 60px);
}

.app-footer {
  background-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  text-align: center;
  line-height: 40px;
  color: #606266;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
}
</style>
