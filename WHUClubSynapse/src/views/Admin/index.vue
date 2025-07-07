<template>
  <div class="admin-container">
    <!-- 侧边导航 -->
    <aside class="admin-sidebar">
      <div class="sidebar-header">
        <el-icon><Setting /></el-icon>
        <h2>管理员控制台</h2>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
        :collapse="isCollapse"
      >
        <el-menu-item index="dashboard">
          <el-icon><Monitor /></el-icon>
          <template #title>数据看板</template>
        </el-menu-item>

        <el-sub-menu index="user">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="user-list">用户列表</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="club">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>社团管理</span>
          </template>
          <el-menu-item index="club-list">社团列表</el-menu-item>
          <el-menu-item index="club-categories">分类管理</el-menu-item>
          <el-menu-item index="club-audit">社团审核</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="settings">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>
      </el-menu>

      <!-- 侧边栏折叠按钮 -->
      <div class="sidebar-footer">
        <el-button @click="toggleSidebar" text>
          <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
        </el-button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="admin-main">
      <!-- 头部 -->
      <header class="admin-header">
        <div class="header-left">
          <h1>{{ getCurrentPageTitle() }}</h1>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>管理员</el-breadcrumb-item>
            <el-breadcrumb-item>{{ getCurrentPageTitle() }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-button type="primary" @click="$router.push('/')">
            <el-icon><Back /></el-icon>
            返回首页
          </el-button>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="admin-content">
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

// 获取当前页面标题
const getCurrentPageTitle = () => {
  return pageTitles[activeMenu.value] || '管理员控制台'
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
  if (!useAuthStore().isLoggedIn) {
    ElMessage.warning('您还未登录，部分功能可能无法正常使用')
    router.push('/login')
    return
  } else if (useAuthStore().user?.role != 'admin') {
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
  background-color: #f5f7fa;
}

/* 侧边栏样式 */
.admin-sidebar {
  width: 250px;
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.admin-sidebar.collapse {
  width: 64px;
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;
  border: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 250px;
}

.sidebar-footer {
  padding: 16px;
  text-align: center;
  border-top: 1px solid #e4e7ed;
}

/* 主内容区样式 */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-header {
  background: #ffffff;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-sidebar {
    width: 64px;
  }

  .admin-header {
    padding: 12px 16px;
  }

  .header-left h1 {
    font-size: 20px;
  }

  .admin-content {
    padding: 16px;
  }
}
</style>
