<template>
  <div class="jwt-usage-example">
    <el-card header="JWT 用户ID获取示例">
      <div class="demo-section">
        <h3>方法一：使用Auth Store（推荐）</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="当前用户ID">
            {{ authStore.currentUserId || '未登录' }}
          </el-descriptions-item>
          <el-descriptions-item label="当前用户角色">
            {{ authStore.currentUserRole || '未登录' }}
          </el-descriptions-item>
          <el-descriptions-item label="登录状态">
            {{ authStore.isLoggedIn ? '已登录' : '未登录' }}
          </el-descriptions-item>
          <el-descriptions-item label="是否管理员">
            {{ authStore.isAdmin ? '是' : '否' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="code-example">
          <pre><code>// 在组件中使用
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 获取用户ID（响应式）
const userId = authStore.currentUserId

// 或者调用方法获取
const userId = authStore.getCurrentUserId()</code></pre>
        </div>
      </div>

      <el-divider />

      <div class="demo-section">
        <h3>方法二：直接使用JWT工具函数</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="从工具函数获取用户ID">
            {{ directUserId || '未登录' }}
          </el-descriptions-item>
          <el-descriptions-item label="从工具函数获取角色">
            {{ directUserRole || '未登录' }}
          </el-descriptions-item>
          <el-descriptions-item label="Token是否过期">
            {{ tokenExpired ? '已过期' : '有效' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="code-example">
          <pre><code>// 直接使用工具函数
import { 
  getUserIdFromToken, 
  getUserRoleFromToken, 
  isTokenExpired,
  getUserInfoFromToken 
} from '@/utils/jwt'

// 获取用户ID
const userId = getUserIdFromToken()

// 获取用户角色
const role = getUserRoleFromToken()

// 检查token是否过期
const expired = isTokenExpired()

// 获取完整用户信息
const userInfo = getUserInfoFromToken()</code></pre>
        </div>
      </div>

      <el-divider />

      <div class="demo-section">
        <h3>方法三：在API调用中使用</h3>
        <el-button @click="callApiWithUserId">调用需要用户ID的API</el-button>
        <el-button @click="checkUserPermission">检查用户权限</el-button>

        <div class="code-example">
          <pre><code>// 在API调用中使用用户ID
const callApiWithUserId = () => {
  const userId = getUserIdFromToken()
  if (!userId) {
    ElMessage.error('用户未登录')
    return
  }
  
  // 调用API
  apiCall(userId)
}

// 检查权限
const checkPermission = () => {
  const role = getUserRoleFromToken()
  if (role === 'admin') {
    // 管理员操作
  } else {
    // 普通用户操作
  }
}</code></pre>
        </div>
      </div>

      <el-divider />

      <div class="demo-section">
        <h3>实际应用场景</h3>
        <div class="use-cases">
          <el-tag type="success">获取当前用户的社团列表</el-tag>
          <el-tag type="info">过滤用户专属内容</el-tag>
          <el-tag type="warning">权限控制和路由守卫</el-tag>
          <el-tag type="danger">用户操作记录</el-tag>
        </div>

        <div class="code-example">
          <pre><code>// 实际使用示例

// 1. 获取用户的社团列表
const loadUserClubs = async () => {
  const userId = getUserIdFromToken()
  if (userId) {
    const clubs = await clubApi.getUserClubs(userId)
    return clubs
  }
}

// 2. 检查是否可以编辑帖子
const canEditPost = (post) => {
  const userId = getUserIdFromToken()
  const userRole = getUserRoleFromToken()
  
  return post.authorId === userId || userRole === 'admin'
}

// 3. 路由守卫中使用
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !getUserIdFromToken()) {
    next('/login')
  } else {
    next()
  }
})</code></pre>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import {
  getUserIdFromToken,
  getUserRoleFromToken,
  isTokenExpired,
  getUserInfoFromToken,
} from '@/utils/jwt'

const authStore = useAuthStore()

// 直接从JWT获取的数据
const directUserId = ref<number | null>(null)
const directUserRole = ref<string | null>(null)
const tokenExpired = ref<boolean>(true)

// 示例API调用
const callApiWithUserId = () => {
  const userId = getUserIdFromToken()
  if (!userId) {
    ElMessage.error('用户未登录，无法调用API')
    return
  }

  ElMessage.success(`调用API，用户ID: ${userId}`)
  console.log('API调用，用户ID:', userId)
}

// 权限检查示例
const checkUserPermission = () => {
  const role = getUserRoleFromToken()
  if (!role) {
    ElMessage.warning('用户未登录')
    return
  }

  if (role === 'admin') {
    ElMessage.success('用户具有管理员权限')
  } else {
    ElMessage.info(`用户角色: ${role}`)
  }
}

// 页面加载时获取数据
onMounted(() => {
  directUserId.value = getUserIdFromToken()
  directUserRole.value = getUserRoleFromToken()
  tokenExpired.value = isTokenExpired()

  // 输出完整的JWT信息到控制台
  const fullInfo = getUserInfoFromToken()
  console.log('JWT完整信息:', fullInfo)
})
</script>

<style scoped>
.jwt-usage-example {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.demo-section {
  margin-bottom: 20px;
}

.demo-section h3 {
  color: #409eff;
  margin-bottom: 15px;
}

.code-example {
  margin-top: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #409eff;
}

.code-example pre {
  margin: 0;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #2c3e50;
}

.use-cases {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.el-descriptions {
  margin-bottom: 15px;
}
</style>
