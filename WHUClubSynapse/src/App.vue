<script setup lang="ts">
import { RouterView } from 'vue-router'
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import PreferenceSetupDialog from '@/components/User/PreferenceSetupDialog.vue'
import type { UserPreferences } from '@/types'
import { ElNotification, ElMessage } from 'element-plus'
import { fa } from 'element-plus/es/locales.mjs'

// 认证store
const authStore = useAuthStore()
// 社团store
const clubStore = useClubStore()

// 偏好设置弹窗
const showPreferenceDialog = ref(false)

// 检查是否需要显示偏好设置弹窗
const checkPreferenceSetup = () => {
  if (authStore.user?.username == 'guest') {
    console.log('当前用户为游客，跳过偏好设置检查')
    return
  }
  if (
    authStore.isLoggedIn &&
    authStore.user &&
    !authStore.user.hasCompletedPreferences &&
    authStore.user.username != 'guest'
  ) {
    showPreferenceDialog.value = true
  }
}

// 监听登录状态变化
watch(
  () => authStore.isLoggedIn,
  (isLoggedIn, wasLoggedIn) => {
    if (isLoggedIn && !wasLoggedIn) {
      // 刚刚登录成功，刷新用户信息
      console.log('检测到用户登录，刷新用户信息')
      authStore.fetchUserInfo().then(() => {
        // 延迟检查，确保用户信息已加载
        setTimeout(checkPreferenceSetup, 500)
      })
    }
  },
)

// TODO: 监听用户信息变化
watch(
  () => authStore.user,
  (user, olduser) => {
    if (
      user &&
      !user.hasCompletedPreferences &&
      user.username != 'guest' &&
      olduser?.user_id != user.user_id
    ) {
      checkPreferenceSetup
    }
  },
)

// 初始化
onMounted(async () => {
  console.log('App开始初始化')
  try {
    // 并行初始化认证和获取社团分类
    const [authResult] = await Promise.allSettled([authStore.initialize()])

    if (authResult.status === 'rejected') {
      console.error('认证初始化失败:', authResult.reason)
    }

    if (!authStore.isLoggedIn) {
      authStore.login({ username: 'guest', password: '123456a' })
      ElMessage.warning('您还未登录，部分功能可能无法正常使用')
      authStore.isGuest = true
      //设计一个游客登录账号
      return
    }
    if (authStore.user?.username == 'guest') {
      ElMessage.warning('您还未登录，部分功能可能无法正常使用')
      authStore.isGuest = true
    } else {
      authStore.isGuest = false
    }
    const [categoriesResult] = await Promise.allSettled([clubStore.fetchCategoriesList()])

    if (categoriesResult.status === 'rejected') {
      console.error('分类数据初始化失败:', categoriesResult.reason)
    }

    checkPreferenceSetup()
    console.log('App初始化完成')

    ElNotification({
      title: '欢迎访问',
      message: 'WHU Club Synapse - 武汉大学社团管理系统',
      type: 'success',
      duration: 3000,
    })
  } catch (error) {
    console.error('应用初始化失败:', error)
    ElNotification({
      title: '初始化失败',
      message: '部分功能可能无法正常使用',
      type: 'warning',
      duration: 5000,
    })
  }
})
</script>

<template>
  <RouterView />

  <!-- 偏好设置弹窗 -->
  <PreferenceSetupDialog v-model="showPreferenceDialog" />
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
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
  background-attachment: fixed;
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
