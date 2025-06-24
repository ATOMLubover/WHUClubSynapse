<template>
  <div class="user-sidebar">
    <el-card>
      <!-- 用户信息卡片 -->
      <div class="user-profile-card">
        <el-avatar :size="64" :src="userInfo?.avatar" class="user-avatar">
          <el-icon><User /></el-icon>
        </el-avatar>
        <h3 class="user-name">{{ userInfo?.realName || userInfo?.username }}</h3>
        <p class="user-role">
          <el-tag :type="userInfo?.role === 'admin' ? 'danger' : 'primary'" size="small">
            {{ getUserRoleText(userInfo?.role) }}
          </el-tag>
        </p>
      </div>

      <!-- 导航菜单 -->
      <el-menu :default-active="activeMenu" class="user-menu" @select="handleMenuSelect">
        <el-menu-item index="user-center">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>

        <el-menu-item index="user-applications">
          <el-icon><Document /></el-icon>
          <span>我的申请</span>
          <el-badge
            v-if="stats.pendingApplications > 0"
            :value="stats.pendingApplications"
            class="menu-badge"
          />
        </el-menu-item>

        <el-menu-item index="user-favorites">
          <el-icon><Star /></el-icon>
          <span>我的收藏</span>
          <span class="menu-count">({{ stats.favoriteClubs }})</span>
        </el-menu-item>

        <el-sub-menu index="user-clubs">
          <template #title>
            <el-icon><UserFilled /></el-icon>
            <span>我的社团</span>
          </template>
          <el-menu-item index="joined-clubs">已加入社团</el-menu-item>
          <el-menu-item index="managed-clubs">管理的社团</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="user-activities">
          <el-icon><Calendar /></el-icon>
          <span>参与活动</span>
        </el-menu-item>

        <el-divider />

        <el-menu-item index="user-settings">
          <el-icon><Setting /></el-icon>
          <span>账户设置</span>
        </el-menu-item>
      </el-menu>

      <!-- 快捷操作 -->
      <div class="quick-actions">
        <el-button type="primary" size="small" @click="goToDiscover" block>
          <el-icon><Search /></el-icon>
          发现社团
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  User,
  Document,
  Star,
  UserFilled,
  Calendar,
  Setting,
  Search,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { User as UserType } from '@/types'

// 路由和Store
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const userInfo = ref<UserType | null>(authStore.user)
const stats = ref({
  pendingApplications: 0,
  favoriteClubs: 0,
  joinedClubs: 0,
  managedClubs: 0,
})

// 当前激活的菜单项
const activeMenu = computed(() => {
  return (route.name as string) || 'user-center'
})

// 方法
const getUserRoleText = (role?: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    student: '学生',
    teacher: '教师',
  }
  return roleMap[role || 'student'] || '学生'
}

const handleMenuSelect = (index: string) => {
  const routeMap: Record<string, string> = {
    'user-center': '/user/center',
    'user-applications': '/user/applications',
    'user-favorites': '/user/favorites',
    'joined-clubs': '/user/clubs/joined',
    'managed-clubs': '/user/clubs/managed',
    'user-activities': '/user/activities',
    'user-settings': '/user/settings',
  }

  const path = routeMap[index]
  if (path) {
    router.push(path)
  }
}

const goToDiscover = () => {
  router.push('/')
}

// 加载用户统计数据
const loadUserStats = async () => {
  try {
    // TODO: 调用API获取用户统计数据
    // 这里使用模拟数据
    stats.value = {
      pendingApplications: 2,
      favoriteClubs: 8,
      joinedClubs: 3,
      managedClubs: 1,
    }
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

onMounted(() => {
  loadUserStats()
})
</script>

<style scoped>
.user-sidebar {
  width: 250px;
  min-height: calc(100vh - 60px);
}

.user-profile-card {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 16px;
}

.user-avatar {
  margin-bottom: 12px;
  border: 2px solid #e4e7ed;
}

.user-name {
  margin: 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-role {
  margin: 8px 0 0 0;
}

.user-menu {
  border: none;
  background: transparent;
}

.user-menu .el-menu-item {
  border-radius: 6px;
  margin: 2px 8px;
  position: relative;
}

.user-menu .el-menu-item:hover {
  background-color: #f0f9ff;
  color: #409eff;
}

.user-menu .el-menu-item.is-active {
  background-color: #409eff;
  color: white;
}

.user-menu .el-menu-item.is-active:hover {
  background-color: #337ecc;
}

.menu-badge {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
}

.menu-count {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.user-menu .el-menu-item.is-active .menu-count {
  color: rgba(255, 255, 255, 0.8);
}

.quick-actions {
  padding: 16px 8px 8px;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-sidebar {
    width: 100%;
    min-height: auto;
  }

  .user-profile-card {
    display: flex;
    align-items: center;
    text-align: left;
    gap: 12px;
  }

  .user-avatar {
    margin-bottom: 0;
  }

  .user-name {
    margin: 0;
    font-size: 16px;
  }

  .user-menu {
    display: flex;
    overflow-x: auto;
    padding: 8px 0;
  }

  .user-menu .el-menu-item {
    flex-shrink: 0;
    margin: 0 4px;
    padding: 0 12px;
    white-space: nowrap;
  }
}
</style>
