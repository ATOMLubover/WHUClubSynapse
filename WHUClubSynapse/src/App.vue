<script setup lang="ts">
import { RouterView } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import PreferenceSetupDialog from '@/components/User/PreferenceSetupDialog.vue'
import type { UserPreferences } from '@/types'

// 认证store
const authStore = useAuthStore()

// 偏好设置弹窗
const showPreferenceDialog = ref(false)

// 检查是否需要显示偏好设置弹窗
const checkPreferenceSetup = () => {
  if (authStore.isLoggedIn && authStore.user && !authStore.user.hasCompletedPreferences) {
    showPreferenceDialog.value = true
  }
}

// 处理偏好设置保存
const handlePreferenceSave = async (preferences: UserPreferences) => {
  try {
    await authStore.updatePreferences(preferences)
    showPreferenceDialog.value = false
  } catch (error) {
    console.error('保存偏好设置失败:', error)
  }
}

// 监听登录状态变化
watch(() => authStore.isLoggedIn, (isLoggedIn) => {
  if (isLoggedIn) {
    // 延迟检查，确保用户信息已加载
    setTimeout(checkPreferenceSetup, 500)
  }
})

// 监听用户信息变化
watch(() => authStore.user, (user) => {
  if (user && !user.hasCompletedPreferences) {
    showPreferenceDialog.value = true
  }
})

// 初始化
onMounted(async () => {
  await authStore.initialize()
  checkPreferenceSetup()
})
</script>

<template>
  <RouterView />
  
  <!-- 偏好设置弹窗 -->
  <PreferenceSetupDialog
    v-model="showPreferenceDialog"
    @save="handlePreferenceSave"
  />
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  font-family:
    'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑',
    Arial, sans-serif;
  overflow-x: hidden;
}

#app {
  max-width: none !important;
  margin: 0 !important;
  padding: 0 !important;
  display: block !important;
  grid-template-columns: none !important;
  width: 100%;
  height: 100vh;
}

/* Element Plus 组件样式覆盖 */
.el-button {
  font-weight: 500;
}

.el-card {
  border-radius: 8px;
}

.el-input__wrapper {
  border-radius: 6px;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式工具类 */
.text-center {
  text-align: center;
}

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mb-16 {
  margin-bottom: 16px;
}

.mb-24 {
  margin-bottom: 24px;
}

.p-16 {
  padding: 16px;
}

.p-24 {
  padding: 24px;
}
</style>
