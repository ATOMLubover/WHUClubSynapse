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
      <el-button type="primary" @click="adminLoginDialogVisible = true">后台管理入口</el-button>
    </div>

    <!-- 右侧用户操作区 -->
    <div class="header-right">
      <!-- 未登录状态 -->
      <template v-if="!authStore.isLoggedIn">
        <el-button @click="goToLogin">登录</el-button>
        <el-button type="primary" @click="goToRegister">注册</el-button>
      </template>

      <!-- 已登录状态 -->
      <template v-else>
        <!-- 通知 -->
        <el-badge :value="notificationCount" class="notification-badge">
          <el-button :icon="Bell" circle @click="handleNotification" />
        </el-badge>

        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserMenuCommand">
          <div class="user-info">
            <el-avatar :src="authStore.user?.avatar_url" :size="32">
              {{ authStore.user?.realName?.charAt(0) }}
            </el-avatar>
            <span class="username">{{ authStore.user?.realName }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="my-clubs">
                <el-icon><UserFilled /></el-icon>
                我的社团
              </el-dropdown-item>
              <el-dropdown-item command="my-applications">
                <el-icon><Document /></el-icon>
                申请记录
              </el-dropdown-item>
              <el-dropdown-item command="favorites">
                <el-icon><Star /></el-icon>
                我的收藏
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

  <el-drawer v-model="notificationDialogVisible" title="通知" class="notification-drawer">
    <div v-for="item in notificationList" :key="item.id" class="notification-item">
      <span>{{ item.title }}</span>
      <span>{{ item.content }}</span>
      <span>{{ item.time }}</span>
    </div>
  </el-drawer>

  <!-- 管理员登录弹窗 -->
  <el-dialog v-model="adminLoginDialogVisible" title="管理员登录" width="400px">
    <el-form :model="adminLoginForm" :rules="adminLoginRules" ref="adminLoginFormRef" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="adminLoginForm.username" autocomplete="off" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input v-model="adminLoginForm.password" type="password" autocomplete="off" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="adminLoginDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleAdminLogin" :loading="adminLoginLoading">登录</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
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

interface Notification {
  id: number | string
  title: string
  content: string
  time: string
}

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
const notificationDialogVisible = ref(false)
//TODO: 获取通知列表,美化UI
const notificationList = ref<Notification[]>([])

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

// 管理员登录弹窗相关
const adminLoginDialogVisible = ref(false)
const adminLoginLoading = ref(false)
const adminLoginForm = ref({ username: '', password: '' })
const adminLoginFormRef = ref()
const adminLoginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleAdminLogin = async () => {
  await adminLoginFormRef.value?.validate()
  adminLoginLoading.value = true
  try {
    if (
      adminLoginForm.value.username === 'admin' &&
      adminLoginForm.value.password === '123456'
    ) {
      ElMessage.success('登录成功')
      adminLoginDialogVisible.value = false
      router.push('/admin')
    } else {
      ElMessage.error('账号或密码错误')
    }
  } finally {
    adminLoginLoading.value = false
  }
}

const handleAdmin = () => {
  router.push('/admin/login')
}

const handleNotification = () => {
  notificationDialogVisible.value = true
}
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
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
