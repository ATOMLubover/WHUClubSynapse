# AI功能可用性检测说明

## 功能概述

AI功能可用性检测系统为WHU社团联盟的AI智能搜索和侧边栏对话功能提供了实时的服务状态监控。通过健康检查接口，系统能够自动检测AI服务的可用性，并根据检测结果动态调整用户界面的显示状态，提供更好的用户体验。

## 功能特点

### 1. 实时状态检测
- **健康检查接口**：通过GET请求检测AI服务状态
- **自动检测**：页面加载时自动检查AI可用性
- **状态缓存**：避免频繁请求，提升性能

### 2. 智能界面适配
- **动态禁用**：AI不可用时自动禁用相关功能
- **状态提示**：清晰显示AI服务状态
- **友好提示**：提供详细的错误信息和解决建议

### 3. 用户体验优化
- **视觉反馈**：通过颜色和图标显示状态
- **操作引导**：指导用户在当前状态下如何操作
- **降级处理**：AI不可用时提供替代方案

## 技术实现

### 1. 健康检查接口

#### 接口规范
```typescript
// GET /health
// 检查AI服务健康状态
export const checkAiServiceHealth = async (): Promise<boolean>
```

#### 请求配置
```typescript
{
  timeout: 5000,        // 5秒超时
  method: 'GET',        // GET请求
  headers: {
    'Content-Type': 'application/json'
  }
}
```

#### 响应处理
- **成功响应**：返回true，表示AI服务可用
- **失败响应**：返回false，表示AI服务不可用
- **超时处理**：5秒内无响应视为不可用

### 2. 配置管理

#### ai-search.ts 配置
```typescript
export const aiSearchConfig = {
  endpoints: {
    healthCheck: '/health',  // 健康检查端点
  },
  requestConfig: {
    healthCheckTimeout: 5000, // 健康检查超时时间
  },
  features: {
    healthCheck: true,        // 是否启用健康检查
  }
}
```

### 3. 状态管理

#### 响应式状态
```typescript
const aiAvailable = ref(true) // AI服务可用性状态
```

#### 状态检查方法
```typescript
const checkAiAvailability = async () => {
  try {
    aiAvailable.value = await checkAiServiceHealth()
  } catch (error) {
    console.error('检查AI服务可用性失败:', error)
    aiAvailable.value = false
  }
}
```

## 界面实现

### 1. 主页AI搜索

#### 复选框状态
```vue
<el-checkbox 
  v-model="useAiSearch" 
  :disabled="!isAiSearchEnabled || !aiAvailable"
>
  询问AI智能体
</el-checkbox>
```

#### 状态指示器
```vue
<el-tag 
  v-if="!aiAvailable" 
  type="warning" 
  size="small" 
  class="ai-status-tag"
>
  AI不可用
</el-tag>
```

#### 工具提示
```vue
<el-tooltip 
  :content="aiAvailable ? '启用AI智能搜索' : 'AI服务暂时不可用，请稍后重试'" 
  placement="top"
>
  <el-icon class="help-icon"><QuestionFilled /></el-icon>
</el-tooltip>
```

### 2. 侧边栏对话

#### 悬浮球状态
```vue
<div 
  class="chat-float-button"
  :class="{ 'ai-unavailable': !aiAvailable }"
>
  <!-- 状态指示器 -->
  <div v-if="!aiAvailable" class="ai-status-indicator">
    <el-icon><Warning /></el-icon>
  </div>
</div>
```

#### 对话窗口状态
```vue
<div class="chat-title">
  <span>AI智能助手</span>
  <el-tag 
    v-if="!aiAvailable" 
    type="warning" 
    size="small" 
    class="ai-status-tag"
  >
    AI不可用
  </el-tag>
</div>
```

#### 输入区域禁用
```vue
<el-input
  v-model="inputMessage"
  :disabled="!aiAvailable"
  placeholder="输入您的问题..."
/>
```

## 错误处理

### 1. 网络错误
- **连接超时**：5秒内无响应
- **网络异常**：网络连接失败
- **服务不可达**：AI服务地址无法访问

### 2. 服务错误
- **服务维护**：AI服务正在维护
- **负载过高**：服务负载过高
- **配置错误**：API配置错误

### 3. 用户提示
```typescript
// AI不可用时的提示信息
const unavailableMessage = {
  title: 'AI服务连接失败',
  content: [
    '当前无法连接到AI服务，可能的原因：',
    '- AI服务暂时不可用',
    '- 网络连接问题', 
    '- 服务配置错误',
    '请稍后重试或联系管理员。'
  ]
}
```

## 性能优化

### 1. 检测策略
- **按需检测**：只在需要时进行检测
- **缓存结果**：避免重复检测
- **异步处理**：不阻塞主界面加载

### 2. 用户体验
- **快速响应**：检测结果快速显示
- **平滑过渡**：状态变化时的动画效果
- **降级体验**：AI不可用时的替代功能

### 3. 资源管理
- **请求控制**：限制检测请求频率
- **内存优化**：及时清理无用状态
- **错误恢复**：自动重试机制

## 配置说明

### 1. 环境配置
```typescript
// 开发环境
baseURL: 'http://localhost:8000'
healthCheckTimeout: 5000

// 生产环境  
baseURL: 'https://your-api-server.com'
healthCheckTimeout: 3000
```

### 2. 功能开关
```typescript
features: {
  healthCheck: true,    // 启用健康检查
  enabled: true,        // 启用AI功能
  sideChat: true,       // 启用侧边栏对话
}
```

### 3. 超时配置
```typescript
requestConfig: {
  timeout: 30000,           // 主请求超时
  healthCheckTimeout: 5000, // 健康检查超时
  retryTimes: 3,            // 重试次数
}
```

## 监控和日志

### 1. 状态监控
- **可用性统计**：记录AI服务可用性
- **响应时间**：监控检测响应时间
- **错误统计**：统计各种错误类型

### 2. 日志记录
```typescript
// 成功检测
console.log('AI服务可用性检查成功:', isAvailable)

// 检测失败
console.error('AI服务可用性检查失败:', error)

// 状态变化
console.log('AI服务状态变化:', { from: previousState, to: currentState })
```

### 3. 告警机制
- **服务不可用**：AI服务长时间不可用
- **响应超时**：检测响应时间过长
- **错误率过高**：检测失败率超过阈值

## 扩展功能

### 1. 高级检测
- **多端点检测**：检测多个AI服务端点
- **负载均衡**：自动选择可用服务
- **故障转移**：自动切换到备用服务

### 2. 用户通知
- **状态推送**：实时推送服务状态
- **维护通知**：提前通知维护时间
- **恢复通知**：服务恢复时通知用户

### 3. 分析功能
- **使用统计**：统计AI功能使用情况
- **性能分析**：分析AI服务性能
- **用户反馈**：收集用户使用反馈

## 测试建议

### 1. 功能测试
- **正常检测**：测试AI服务正常时的检测
- **异常检测**：测试AI服务异常时的检测
- **网络异常**：测试网络异常时的处理

### 2. 性能测试
- **响应时间**：测试检测响应时间
- **并发检测**：测试多用户同时检测
- **资源消耗**：测试检测功能的资源消耗

### 3. 兼容性测试
- **浏览器兼容**：测试不同浏览器
- **设备兼容**：测试不同设备
- **网络环境**：测试不同网络条件

## 部署说明

### 1. 环境准备
1. 确保AI服务正常运行
2. 配置正确的健康检查端点
3. 测试健康检查接口

### 2. 前端部署
1. 更新配置文件
2. 构建生产版本
3. 部署到服务器

### 3. 监控配置
1. 设置健康检查监控
2. 配置错误告警
3. 监控服务状态

## 注意事项

1. **检测频率**：避免过于频繁的检测请求
2. **超时设置**：合理设置检测超时时间
3. **错误处理**：完善的错误处理机制
4. **用户体验**：确保状态变化不影响用户体验
5. **性能影响**：最小化检测对性能的影响
6. **安全考虑**：确保检测接口的安全性

---

该功能为AI智能搜索和侧边栏对话提供了可靠的状态监控，确保用户能够及时了解AI服务的可用性，并在服务不可用时获得清晰的提示和替代方案，提升了系统的可靠性和用户体验。 