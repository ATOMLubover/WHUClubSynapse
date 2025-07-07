# 用户扩展信息Extension字段实现说明

## 概述

本功能实现了用户扩展信息的extension字段，将用户的非必须注册字段（专业、学号、真实姓名、个人简介、偏好设置、特质标签）作为JSON字符串存储在数据库的extension字段中。

## 核心设计

### 数据存储规则

1. **Extension字段格式**: JSON字符串
2. **默认状态**: 注册用户的extension字段默认为空
3. **写入时机**: 用户在个人主页填写信息后写入
4. **字段内容**: 
   - `realName`: 真实姓名
   - `studentId`: 学号  
   - `major`: 专业
   - `bio`: 个人简介
   - `preferences`: 偏好设置（简化版本）
   - `tags`: 特质标签数组
   - `phone`: 手机号

### Extension JSON结构示例
```json
{
  "realName": "张三",
  "studentId": "2021301000001", 
  "major": "计算机科学与技术",
  "bio": "热爱编程和开源项目",
  "preferences": {
    "interestedCategories": [0, 1, 2],
    "emailNotifications": true,
    "applicationNotifications": true,
    "activityNotifications": false,
    "profilePublic": true,
    "showJoinedClubs": true
  },
  "tags": ["编程", "开源", "AI"],
  "phone": "13800138000"
}
```

## 实现架构

### 1. 类型定义 (types/index.ts)

#### User接口更新
```typescript
export interface User {
  user_id: number
  username: string
  email: string
  avatar_url?: string
  role: string
  last_active?: string
  extension?: string // 🆕 扩展信息JSON字符串
  
  // 以下字段从extension中解析出来，用于前端显示
  phone?: string
  realName?: string
  studentId?: string
  major?: string
  bio?: string
  tags?: string[]
}
```

#### 新增接口
```typescript
// 用户扩展信息结构
export interface UserExtension {
  realName?: string
  studentId?: string
  major?: string
  bio?: string
  preferences?: Record<string, any>
  tags?: string[]
  phone?: string
}

// 更新用户信息请求
export interface UpdateUserRequest {
  user_id?: number
  username?: string
  password?: string
  email?: string
  extension?: string
}
```

### 2. 工具函数 (utils/userExtension.ts)

提供完整的extension字段处理工具：

- **parseUserExtension()** - 解析extension JSON字符串
- **stringifyUserExtension()** - 序列化扩展信息为JSON字符串  
- **extractUserExtension()** - 从User对象提取扩展信息
- **mergeUserExtension()** - 将扩展信息合并到User对象
- **processUserFromBackend()** - 处理后端返回的用户数据
- **prepareUserForBackend()** - 准备发送到后端的数据

### 3. API层更新 (api/auth.ts)

#### 新增接口
```typescript
// 🆕 更新用户信息
export async function updateUserInfo(updateData: UpdateUserRequest): Promise<string>

// 📝 更新现有接口以支持extension字段
export async function getUserById(userId: number): Promise<User>
export async function getUserList(params: UserListParams): Promise<User[]>
```

#### 自动处理机制
- 所有获取用户信息的API自动解析extension字段
- 发送数据时自动序列化extension字段

### 4. Store层更新 (stores/auth.ts)

#### 新增方法
```typescript
// 🆕 更新用户信息，自动处理extension字段
async updateUserInfo(userData: Partial<User>): Promise<string>
```

#### 特性
- 自动处理extension字段序列化
- 更新成功后自动重新获取用户信息
- 完整的错误处理

### 5. 组件层更新

#### UserCenterView.vue
- 个人信息编辑保存使用新的`updateUserInfo` API
- 保存成功后自动刷新用户数据

#### 社团管理相关
- **社团成员管理**: `getClubMembers()`自动获取成员详细信息
- **社团申请审核**: `getClubJoinApplications()`自动获取申请者详细信息
- **社团创建审核**: `getPendingClubApplications()`自动获取申请者详细信息

## API接口对接

### 1. 更新用户信息
```
URI: PUT /api/user/update
权限: 需要身份验证 (JWT Token)
请求体: {
  "user_id": "int",
  "username": "string", 
  "password": "string",
  "email": "string",
  "extension": "string"
}
```

### 2. 获取用户信息 (已更新)
```
URI: GET /api/user/{id}
响应: {
  "user_id": "uint",
  "username": "string",
  "email": "string", 
  "avatar_url": "string",
  "role": "string",
  "last_active": "string",
  "extension": "string"
}
```

### 3. 获取用户列表 (管理员专用，已更新)
```
URI: GET /api/user/list?offset=0&num=10
响应: [
  {
    "user_id": "uint",
    "username": "string",
    "email": "string",
    "avatar_url": "string", 
    "role": "string",
    "last_active": "string",
    "extension": "string"
  }
]
```

## 数据流程

### 写入流程
1. 用户在前端填写扩展信息
2. 调用`prepareUserForBackend()`序列化extension字段
3. 发送PUT请求到`/api/user/update`
4. 数据库存储JSON字符串到extension字段

### 读取流程
1. 后端返回包含extension字段的用户数据
2. 调用`processUserFromBackend()`解析extension字段
3. 扩展信息自动合并到User对象
4. 前端正常使用解析后的字段

## 核心特性

### 1. 向后兼容
- 现有代码无需修改
- Extension字段为空时不影响现有功能
- 自动处理JSON解析错误

### 2. 自动化处理
- API层自动处理extension字段序列化/反序列化
- Store层自动管理数据同步
- 错误处理和默认值处理

### 3. 性能优化
- 只在必要时进行JSON序列化操作
- 批量处理用户信息获取
- 缓存和延迟加载

### 4. 错误处理
- JSON解析失败时返回空对象
- 网络错误时保持现有数据
- 用户友好的错误提示

## 使用示例

### 更新用户信息
```typescript
// 在组件中使用
const authStore = useAuthStore()

// 更新用户扩展信息
await authStore.updateUserInfo({
  realName: '张三',
  studentId: '2021301000001',
  major: '计算机科学与技术',
  bio: '热爱编程',
  tags: ['编程', 'AI'],
  phone: '13800138000'
})
```

### 读取用户信息
```typescript
// 用户信息自动包含解析后的扩展字段
const user = authStore.user
console.log(user.realName) // '张三'
console.log(user.studentId) // '2021301000001'
console.log(user.tags) // ['编程', 'AI']
```

## 测试验证

创建了测试页面 `test-user-info.vue` 用于验证功能：
- 显示当前用户的所有扩展信息
- 提供表单测试更新功能
- 显示extension字段的原始JSON数据
- 实时验证数据序列化/反序列化

## 注意事项

1. **数据一致性**: 更新用户信息后自动重新获取最新数据
2. **权限控制**: 只能更新当前登录用户的信息
3. **数据验证**: 前端进行基础验证，后端进行最终验证
4. **性能考虑**: 大量用户信息获取时采用批量处理策略

## 后续优化

1. **缓存机制**: 实现用户信息本地缓存
2. **增量更新**: 支持部分字段更新
3. **版本控制**: Extension字段结构版本管理
4. **数据迁移**: 历史数据平滑迁移策略 