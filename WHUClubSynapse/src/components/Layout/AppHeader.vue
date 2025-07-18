<template>
  <div class="header-container">
    <!-- 左侧Logo和标题 -->
    <div class="header-left">
      <router-link to="/" class="logo-link">
        <el-icon class="logo-icon" :size="32">
          <House />
        </el-icon>
        <span class="logo-text">WHU社团联盟</span>
      </router-link>
    </div>

    <!-- 中间搜索框 -->
    <div class="header-center">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索社团名称、分类、关键词..."
        class="search-input"
        @keyup.enter="handleSearch"
        clearable
      >
        <template #append>
          <el-button type="primary" :icon="Search" @click="handleSearch" />
        </template>
      </el-input>
    </div>

    <div>
      <el-button type="primary" @click="handleAdmin">后台管理入口</el-button>
    </div>

    <!-- 右侧用户操作区 -->
    <div class="header-right">
      <!-- 未登录状态 -->
      <template v-if="!authStore.isLoggedIn || authStore.isGuest">
        <el-button @click="goToLogin">登录</el-button>
        <el-button type="primary" @click="goToRegister">注册</el-button>
      </template>

      <!-- 已登录状态 -->
      <template v-else>
        <!-- 用户菜单 -->
        <el-dropdown
          @command="handleUserMenuCommand"
          v-if="!authStore.isGuest && authStore.isLoggedIn"
        >
          <div class="user-info">
            <el-avatar :src="authStore.user?.avatar_url" :size="32">
              {{ authStore.user?.username?.charAt(0) }}
            </el-avatar>
            <span class="username">{{ authStore.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="my-applications">
                <el-icon><Document /></el-icon>
                我的申请
              </el-dropdown-item>
              <el-dropdown-item command="favorites">
                <el-icon><Star /></el-icon>
                我的收藏
              </el-dropdown-item>
              <el-dropdown-item command="my-clubs">
                <el-icon><UserFilled /></el-icon>
                我的社团
              </el-dropdown-item>
              <el-dropdown-item command="create-clubs">
                <el-icon><Plus /></el-icon>
                创建社团
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  House,
  Search,
  Bell,
  User,
  UserFilled,
  Document,
  Star,
  SwitchButton,
  ArrowDown,
  Plus,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const props = defineProps({
  clearSearch: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:clearSearch'])

// 或者监听 count.value
watch(
  () => props.clearSearch,
  (newValue, oldValue) => {
    if (newValue) {
      searchKeyword.value = ''
      emit('update:clearSearch', false)
    }
  },
)
// 搜索关键词
const searchKeyword = ref('')

// 搜索框清空
const clearSearch = () => {
  searchKeyword.value = ''
}

// 通知数量（模拟）
// TODO: 获取通知数量
const notificationCount = ref(0)

// 搜索处理
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({
      path: '/search',
      query: { keyword: searchKeyword.value.trim() },
    })
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}

// 用户菜单命令处理
const handleUserMenuCommand = (command: string) => {
  console.log(authStore.user)
  switch (command) {
    case 'profile':
      router.push('/user/center')
      break
    case 'my-clubs':
      router.push('/user/clubs')
      break
    case 'my-applications':
      router.push('/user/applications')
      break
    case 'favorites':
      router.push('/user/favorites')
      break
    case 'create-clubs':
      router.push('/user/clubs/managed?isOpen=true')
      break
    case 'logout':
      authStore.logout()
      router.push('/')
      break
  }
}

const handleAdmin = async () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    goToLogin()
    return
  }

  if (authStore.user?.role !== 'admin') {
    ElMessage.warning('您没有权限访问后台管理')
    return
  }
  router.push('/admin')
}

onMounted(() => {
  console.log(authStore.isGuest)
})
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  background-color: transparent;
}

.header-left {
  flex: 0 0 auto;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
}

.logo-icon {
  margin-right: 8px;
}

.logo-text {
  color: #2c3e50;
}

.header-center {
  flex: 1;
  max-width: 600px;
  margin: 0 40px;
}

.search-input {
  width: 100%;
}

.header-right {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-center {
    margin: 0 16px;
  }

  .logo-text {
    display: none;
  }

  .username {
    display: none;
  }
}
.notification-drawer {
  --el-drawer-width: 30%;
  --el-drawer-padding: 0;
}
.notification-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
