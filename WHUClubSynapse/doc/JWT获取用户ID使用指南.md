# JWT 获取用户ID 使用指南

## 🎯 快速使用

### 方法一：使用 Auth Store（推荐）

```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 获取用户ID（响应式）
const userId = authStore.currentUserId
const userRole = authStore.currentUserRole

// 或者调用方法获取
const userId = authStore.getCurrentUserId()
```

### 方法二：直接使用工具函数

```typescript
import { getUserIdFromToken, getUserRoleFromToken } from '@/utils/jwt'

// 获取用户ID
const userId = getUserIdFromToken()

// 获取用户角色  
const userRole = getUserRoleFromToken()
```

## 📚 完整API参考

### JWT工具函数

| 函数名 | 返回值 | 说明 |
|--------|--------|------|
| `getUserIdFromToken()` | `number \| null` | 从JWT获取用户ID |
| `getUserRoleFromToken()` | `string \| null` | 从JWT获取用户角色 |
| `isTokenExpired()` | `boolean` | 检查token是否过期 |
| `getUserInfoFromToken()` | `JWTPayload \| null` | 获取完整用户信息 |
| `parseJWT(token)` | `JWTPayload \| null` | 解析指定JWT token |

### Auth Store新增属性和方法

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| `currentUserId` | `ComputedRef<number \| null>` | 当前用户ID（响应式） |
| `currentUserRole` | `ComputedRef<string \| null>` | 当前用户角色（响应式） |
| `getCurrentUserId()` | `() => number \| null` | 获取当前用户ID |
| `checkTokenValidity()` | `() => boolean` | 检查token有效性 |

## 🔥 实际应用场景

### 1. 在API调用中使用

```typescript
// 获取用户专属数据
const loadUserData = async () => {
  const userId = getUserIdFromToken()
  if (!userId) {
    ElMessage.error('用户未登录')
    return
  }
  
  const data = await api.getUserData(userId)
  return data
}
```

### 2. 权限控制

```typescript
// 检查用户权限
const hasPermission = (requiredRole: string) => {
  const userRole = getUserRoleFromToken()
  return userRole === requiredRole || userRole === 'admin'
}

// 在组件中使用
const canEdit = computed(() => {
  return hasPermission('admin') || post.authorId === authStore.currentUserId
})
```

### 3. 路由守卫

```typescript
// router/index.ts
import { getUserIdFromToken } from '@/utils/jwt'

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const userId = getUserIdFromToken()
    if (!userId) {
      next('/login')
      return
    }
  }
  next()
})
```

### 4. 在Composition API中使用

```vue
<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getUserIdFromToken } from '@/utils/jwt'

const authStore = useAuthStore()

// 响应式用户ID
const userId = computed(() => authStore.currentUserId)

// 或者直接获取
const currentUserId = getUserIdFromToken()

// 监听用户ID变化
watch(userId, (newUserId) => {
  if (newUserId) {
    loadUserData(newUserId)
  }
})
</script>
```

## ⚠️ 注意事项

1. **Token有效性检查**：使用前建议检查token是否过期
2. **空值处理**：所有函数都可能返回null，需要进行空值检查
3. **错误处理**：JWT解析可能失败，建议添加try-catch
4. **安全性**：不要在客户端存储敏感信息，JWT中只包含必要的用户标识

## 🛡️ 安全最佳实践

```typescript
// 安全的用户ID获取
const safeGetUserId = (): number | null => {
  try {
    // 首先检查token是否过期
    if (isTokenExpired()) {
      console.warn('Token已过期')
      return null
    }
    
    return getUserIdFromToken()
  } catch (error) {
    console.error('获取用户ID失败:', error)
    return null
  }
}

// 在需要的地方使用
const userId = safeGetUserId()
if (userId) {
  // 安全地使用用户ID
  performUserAction(userId)
}
```

## 🎨 TypeScript类型定义

```typescript
interface JWTPayload {
  user_id: number
  role: string
  exp?: number  // 过期时间
  iat?: number  // 签发时间
}
```

这样就可以在整个项目中安全、便捷地获取用户ID了！ 🚀 