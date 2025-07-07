<template>
  <div class="admin-container">
    <!-- 侧边导航 -->
    <aside class="admin-sidebar" :class="{ 'sidebar-collapsed': isCollapse }">
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <h2 v-show="!isCollapse">管理员控制台</h2>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
        :collapse="isCollapse"
        background-color="transparent"
        text-color="#64748b"
        active-text-color="#3b82f6"
      >
        <el-menu-item index="dashboard" class="menu-item">
          <el-icon><Monitor /></el-icon>
          <template #title>
            <span class="menu-text">数据看板</span>
          </template>
        </el-menu-item>

        <el-sub-menu index="user" class="submenu">
          <template #title>
            <el-icon><User /></el-icon>
            <span class="menu-text">用户管理</span>
          </template>
          <el-menu-item index="user-list" class="submenu-item">用户列表</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="club" class="submenu">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span class="menu-text">社团管理</span>
          </template>
          <el-menu-item index="club-list" class="submenu-item">社团列表</el-menu-item>
          <el-menu-item index="club-categories" class="submenu-item">分类管理</el-menu-item>
          <el-menu-item index="club-audit" class="submenu-item">社团审核</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="settings" class="menu-item">
          <el-icon><Setting /></el-icon>
          <template #title>
            <span class="menu-text">系统设置</span>
          </template>
        </el-menu-item>
      </el-menu>

      <!-- 侧边栏折叠按钮 -->
      <div class="sidebar-footer">
        <el-button @click="toggleSidebar" class="collapse-btn" :class="{ collapsed: isCollapse }">
          <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="admin-main">
      <!-- 头部 -->
      <header class="admin-header">
        <div class="header-left">
          <div class="page-title-section">
            <h1>{{ getCurrentPageTitle() }}</h1>
            <p class="page-description">{{ getPageDescription() }}</p>
          </div>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item>管理员</el-breadcrumb-item>
            <el-breadcrumb-item>{{ getCurrentPageTitle() }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <div class="user-info">
            <el-avatar :size="32" :src="authStore.user?.avatar_url" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <span class="username">{{ authStore.user?.username }}</span>
          </div>
          <el-button type="primary" @click="$router.push('/')" class="back-btn" :icon="Back">
            返回首页
          </el-button>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="admin-content">
        <div class="content-wrapper">
          <!-- 数据看板 -->
          <Dashboard v-if="activeMenu === 'dashboard'" />

          <!-- 用户管理 -->
          <UserList v-if="activeMenu === 'user-list'" />

          <!-- 社团管理 -->
          <ClubList v-if="activeMenu === 'club-list'" />
          <ClubCategories v-if="activeMenu === 'club-categories'" />
          <ClubAudit v-if="activeMenu === 'club-audit'" />

          <!-- 申请审核 -->
          <ApplicationReview v-if="activeMenu === 'applications'" />

          <!-- 系统管理 -->
          <SystemSettings v-if="activeMenu === 'settings'" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Setting,
  Monitor,
  User,
  OfficeBuilding,
  DocumentAdd,
  Document,
  Tools,
  Fold,
  Expand,
  Back,
} from '@element-plus/icons-vue'

// 导入子组件
import Dashboard from '../../components/Admin/Dashboard.vue'
import UserList from '../../components/Admin/UserList.vue'
import ClubList from '../../components/Admin/ClubList.vue'
import ClubCategories from '../../components/Admin/ClubCategories.vue'
import ClubAudit from '../../components/Admin/ClubAudit.vue'
import ApplicationReview from '../../components/Admin/ApplicationReview.vue'
import SystemSettings from '../../components/Admin/SystemSettings.vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

// 侧边栏状态
const isCollapse = ref(false)
const activeMenu = ref('dashboard')

// 页面标题映射
const pageTitles: Record<string, string> = {
  dashboard: '数据看板',
  'user-list': '用户列表',
  'club-list': '社团列表',
  'club-categories': '分类管理',
  'club-audit': '社团审核',
  settings: '系统设置',
}

// 页面描述映射
const pageDescriptions: Record<string, string> = {
  dashboard: '查看系统整体数据统计和关键指标',
  'user-list': '管理系统用户信息、权限和状态',
  'club-list': '查看和管理所有社团信息',
  'club-categories': '管理社团分类和标签',
  'club-audit': '审核新创建的社团申请',
  settings: '配置系统参数和功能设置',
}

// 获取当前页面标题
const getCurrentPageTitle = () => {
  return pageTitles[activeMenu.value] || '管理员控制台'
}

// 获取当前页面描述
const getPageDescription = () => {
  return pageDescriptions[activeMenu.value] || '系统管理控制台'
}

// 处理菜单选择
const handleMenuSelect = (index: string) => {
  activeMenu.value = index
}

// 切换侧边栏
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

onMounted(() => {
  // 默认显示数据看板
  if (!authStore.isLoggedIn) {
    ElMessage.warning('您还未登录，部分功能可能无法正常使用')
    router.push('/login')
    return
  } else if (authStore.user?.role != 'admin') {
    ElMessage.warning('您没有权限访问此页面')
    router.push('/')
    return
  }
  activeMenu.value = 'dashboard'
})
</script>

<style scoped>
.admin-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

/* 侧边栏样式 */
.admin-sidebar {
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.admin-sidebar.sidebar-collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(100, 116, 139, 0.1);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  backdrop-filter: blur(10px);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-menu {
  flex: 1;
  border: none;
  padding: 16px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  margin: 4px 12px;
  border-radius: 12px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
}

.sidebar-menu :deep(.el-sub-menu__title) {
  margin: 4px 12px;
  border-radius: 12px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s ease;
}

.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.sidebar-menu :deep(.el-menu-item.submenu-item) {
  margin: 2px 12px 2px 36px;
  height: 40px;
  line-height: 40px;
  border-radius: 8px;
  font-size: 14px;
}

.menu-text {
  font-weight: 500;
  letter-spacing: 0.5px;
}

.sidebar-footer {
  padding: 20px;
  text-align: center;
  border-top: 1px solid rgba(100, 116, 139, 0.1);
}

.collapse-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.collapse-btn.collapsed {
  width: 40px;
  height: 40px;
}

/* 主内容区样式 */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px 0 0 0;
  margin: 16px 16px 16px 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.admin-header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  padding: 24px 32px;
  border-bottom: 1px solid rgba(100, 116, 139, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 24px 24px 0 0;
}

.header-left {
  flex: 1;
}

.page-title-section {
  margin-bottom: 8px;
}

.page-title-section h1 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.page-description {
  margin: 0;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.breadcrumb {
  font-size: 13px;
}

.breadcrumb :deep(.el-breadcrumb__item) {
  color: #94a3b8;
}

.breadcrumb :deep(.el-breadcrumb__inner) {
  color: #64748b;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.user-avatar {
  border: 2px solid rgba(102, 126, 234, 0.3);
}

.username {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.back-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.admin-content {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
  background: rgba(248, 250, 252, 0.8);
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

/* 滚动条样式 */
.admin-content::-webkit-scrollbar {
  width: 8px;
}

.admin-content::-webkit-scrollbar-track {
  background: rgba(100, 116, 139, 0.1);
  border-radius: 4px;
}

.admin-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.admin-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .admin-sidebar {
    width: 240px;
  }

  .admin-sidebar.sidebar-collapsed {
    width: 70px;
  }

  .admin-header {
    padding: 20px 24px;
  }

  .page-title-section h1 {
    font-size: 24px;
  }

  .admin-content {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
  }

  .admin-sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid rgba(100, 116, 139, 0.1);
  }

  .admin-sidebar.sidebar-collapsed {
    width: 100%;
  }

  .admin-main {
    margin: 0;
    border-radius: 0;
  }

  .admin-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    padding: 20px;
    border-radius: 0;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .page-title-section h1 {
    font-size: 20px;
  }

  .admin-content {
    padding: 20px;
  }

  .content-wrapper {
    max-width: none;
  }
}

@media (max-width: 480px) {
  .admin-header {
    padding: 16px;
  }

  .page-title-section h1 {
    font-size: 18px;
  }

  .admin-content {
    padding: 16px;
  }

  .user-info {
    padding: 6px 12px;
  }

  .username {
    font-size: 12px;
  }

  .back-btn {
    padding: 10px 16px;
    font-size: 14px;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.admin-content {
  animation: fadeInUp 0.6s ease-out;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .admin-container {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  }

  .admin-sidebar {
    background: rgba(30, 41, 59, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
  }

  .admin-main {
    background: rgba(30, 41, 59, 0.95);
  }

  .admin-header {
    background: rgba(30, 41, 59, 0.9);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .page-title-section h1 {
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .page-description {
    color: #94a3b8;
  }

  .username {
    color: #e2e8f0;
  }

  .admin-content {
    background: rgba(15, 23, 42, 0.8);
  }
}
</style>
