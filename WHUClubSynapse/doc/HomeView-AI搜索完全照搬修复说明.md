# HomeView AI搜索完全照搬修复说明

## 问题描述

HomeView中的AI智能搜索功能无法正常工作，需要完全照搬AISideChat的成功实现方式。

## 修复方案

### 完全照搬AISideChat的实现逻辑

将HomeView的AI搜索实现完全照搬AISideChat的 `sendMessage` 方法，使用相同的变量命名、处理逻辑和API调用方式。

## 修复内容

### 1. 变量命名照搬

```typescript
// AISideChat的变量命名
const content = message || inputMessage.value.trim()
let answer = ''
let sources: any[] = []
let aiMsgIndex = -1

// HomeView照搬后的变量命名
const content = searchKeyword.value.trim()
let answer = ''
let sources: any[] = []
let aiMsgIndex = -1
```

### 2. API调用照搬

```typescript
// AISideChat的API调用
sideChatStream(
  {
    query: content,
    history: chatHistory.value.slice(0, -1)
  },
  {
    onSource: (src) => { sources = src },
    onToken: (token) => { /* 处理逻辑 */ },
    onEnd: () => { isLoading.value = false },
    onError: (err) => { /* 错误处理 */ }
  }
)

// HomeView照搬后的API调用
sideChatStream(
  {
    query: content,
    history: [] // 主页搜索不需要历史记录
  },
  {
    onSource: (src) => { sources = src },
    onToken: (token) => { /* 处理逻辑 */ },
    onEnd: () => { searchLoading.value = false },
    onError: (err) => { /* 错误处理 */ }
  }
)
```

### 3. 处理逻辑照搬

```typescript
// 完全相同的处理逻辑
onToken: (token) => {
  answer += token
  // 实时更新AI搜索结果
  if (aiMsgIndex === -1) {
    aiMsgIndex = 0
  }
  (aiSearchResult.value as any).answer = answer
  (aiSearchResult.value as any).source = sources
}
```

## 关键差异

### 1. 端点使用
- **HomeView**：使用 `sideChatStream`（与AISideChat相同）
- **原因**：确保使用可工作的端点

### 2. 历史记录
- **HomeView**：`history: []`（不需要历史记录）
- **AISideChat**：`history: chatHistory.value.slice(0, -1)`（完整对话历史）

### 3. 状态管理
- **HomeView**：使用 `searchLoading.value` 和 `aiSearchResult.value`
- **AISideChat**：使用 `isLoading.value` 和 `chatHistory.value`

## 当前配置

### 导入
```typescript
import { smartSearchStream, checkAiServiceHealth, sideChatStream } from '@/api/ai-search'
```

### API端点
```typescript
endpoints: {
  smartSearch: '/smart-search',    // 原AI搜索端点
  sideChat: '/sider-chat',         // 侧边栏对话端点（可工作）
  healthCheck: '/',               // 健康检查端点
}
```

## 功能状态

### ✅ 已修复
1. 完全照搬AISideChat的实现逻辑
2. 使用相同的API调用方式
3. 相同的变量命名和处理流程
4. 统一的错误处理机制

### 🔧 使用方式
1. 在主页勾选"询问AI智能体"
2. 输入搜索关键词
3. 点击搜索按钮
4. 实时显示AI回答

## 注意事项

1. **端点统一**：暂时使用 `/sider-chat` 端点确保功能正常
2. **逻辑一致**：与AISideChat保持完全相同的处理逻辑
3. **状态适配**：适配HomeView的状态管理方式
4. **向后兼容**：保持原有UI和交互不变

## 测试建议

1. 测试HomeView AI搜索功能
2. 验证流式回复效果
3. 检查错误处理
4. 对比AISideChat功能确认一致性 