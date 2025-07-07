# 用户信息API对接说明

## 问题修复总结

### 修复的主要问题

1. **偏好设置保存问题** ✅
   - 原问题：UserCenterView和App.vue中的偏好设置保存仍使用旧的`updatePreferences`方法
   - 解决方案：改为使用新的`updateUserInfo`方法，将偏好设置保存到extension字段

2. **专业字段映射问题** ✅
   - 原问题：前端使用`college`字段，但后端和extension中使用`major`字段
   - 解决方案：统一使用`major`字段，修正所有相关引用

3. **Extension字段处理问题** ✅
   - 原问题：`mergeUserExtension`函数没有处理preferences字段
   - 解决方案：在合并时正确处理preferences字段

### 修复的具体代码

#### 1. UserCenterView.vue 偏好设置保存
```typescript
// 修复前
await authStore.updatePreferences(preferences)

// 修复后  
await authStore.updateUserInfo({
  preferences: preferences,
  tags: preferences.tags
})
```

#### 2. App.vue 偏好设置保存
```typescript
// 修复前
await authStore.updatePreferences(preferences)

// 修复后
await authStore.updateUserInfo({
  preferences: preferences,
  tags: preferences.tags
})
```

#### 3. 字段名统一修正
```typescript
// editableUserInfo定义
const editableUserInfo = reactive({
  username: '',
  realName: '',
  studentId: '',
  major: '', // 修正：使用major而不是college
  email: '',
  phone: '',
  bio: '',
})

// 模板绑定
<el-select v-model="editableUserInfo.major" placeholder="请选择专业">

// 数据加载
Object.assign(editableUserInfo, {
  // ...
  major: userInfo.value.major || '', // 修正：使用major字段
  // ...
})
```

#### 4. Extension处理函数修复
```typescript
// mergeUserExtension函数 - 添加preferences处理
export function mergeUserExtension(user: User, extension: UserExtension): User {
  let mergedPreferences = user.preferences
  if (extension.preferences) {
    mergedPreferences = extension.preferences as any
  }

  return {
    ...user,
    realName: extension.realName,
    studentId: extension.studentId,
    major: extension.major,
    bio: extension.bio,
    tags: extension.tags,
    phone: extension.phone,
    preferences: mergedPreferences // 新增：正确合并preferences
  }
}

// extractUserExtension函数 - 改进preferences提取
export function extractUserExtension(user: User): UserExtension {
  let simplifiedPreferences = undefined
  if (user.preferences) {
    simplifiedPreferences = {
      interestedCategories: user.preferences.interestedCategories?.map(cat => 
        typeof cat === 'object' ? cat.category_id : cat
      ) || [],
      emailNotifications: user.preferences.emailNotifications,
      applicationNotifications: user.preferences.applicationNotifications,
      activityNotifications: user.preferences.activityNotifications,
      profilePublic: user.preferences.profilePublic,
      showJoinedClubs: user.preferences.showJoinedClubs
    }
  }
  
  return {
    realName: user.realName,
    studentId: user.studentId,
    major: user.major,
    bio: user.bio,
    preferences: simplifiedPreferences,
    tags: user.tags,
    phone: user.phone
  }
}
```

## 数据流程确认

### 偏好设置保存流程
1. 用户在偏好设置页面填写信息
2. 点击保存 → 调用`authStore.updateUserInfo()`
3. `updateUserInfo()` → 调用`prepareUserForBackend()` → 序列化extension字段
4. 发送PUT /api/user/update请求到后端
5. 后端保存extension字段到数据库
6. 前端重新获取用户信息，自动解析extension字段

### 专业信息保存流程  
1. 用户在个人信息页面选择专业
2. 点击保存 → 调用`authStore.updateUserInfo({ major: selectedMajor })`
3. 专业信息被包含在extension字段中发送到后端
4. 后端保存，前端重新获取并显示

## Extension字段JSON结构

### 完整示例
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

### 字段说明
- `realName`: 真实姓名
- `studentId`: 学号
- `major`: 专业（统一使用此字段名）
- `bio`: 个人简介
- `preferences`: 偏好设置（简化存储格式）
  - `interestedCategories`: 感兴趣的分类ID数组
  - 各种通知和隐私设置布尔值
- `tags`: 特质标签字符串数组
- `phone`: 手机号

## 测试验证

### 可用的测试页面
访问 `/test-user-info` 页面进行功能测试：
- 查看当前用户扩展信息
- 测试信息更新功能
- 查看extension字段原始JSON

### 测试项目
1. ✅ 个人信息编辑保存（真实姓名、学号、专业、简介、手机号）
2. ✅ 偏好设置保存（分类、通知、隐私、标签）
3. ✅ Extension字段正确序列化/反序列化
4. ✅ 社团管理页面正确显示用户完整信息
5. ✅ 注册页面已简化，只保留必要字段

## 注意事项

1. **数据一致性**: 所有用户信息修改都通过`updateUserInfo`方法，确保extension字段正确更新
2. **字段命名**: 统一使用`major`表示专业，避免前后端字段名不一致
3. **偏好设置**: preferences在extension中以简化格式存储，前端使用时需要适当转换
4. **错误处理**: JSON解析失败时返回空对象，保证系统稳定性
5. **向后兼容**: Extension字段为空时不影响现有功能

## 接口对接状态

- ✅ PUT /api/user/update - 更新用户信息
- ✅ GET /api/user/{id} - 获取用户信息（包含extension）
- ✅ GET /api/user/list - 获取用户列表（管理员专用，包含extension）

所有接口已正确对接，extension字段自动处理。 