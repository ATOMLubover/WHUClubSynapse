# HomeView AI搜索问题修复说明

## 问题分析

用户反馈：AI检测通过，但输入"如何创建社团"无法得到回复并报错。

## 发现的问题

### 1. 端点配置错误
- **问题**：配置文件中侧边栏对话端点为 `/sider-chat`（拼写错误）
- **影响**：导致API调用失败
- **修复**：改为 `/side-chat`

### 2. API调用混乱
- **问题**：HomeView使用 `sideChatStream`，但应该使用 `smartSearchStream`
- **影响**：功能逻辑错误，可能导致请求格式不匹配
- **修复**：HomeView改为使用 `smartSearchStream`

### 3. 错误处理不完善
- **问题**：错误信息不够详细，难以调试
- **影响**：无法准确定位问题
- **修复**：添加详细的错误日志和错误信息

## 修复内容

### 1. 修复端点配置
```typescript
// 修复前
endpoints: {
  smartSearch: '/smart-search',
  sideChat: '/sider-chat',  // 拼写错误
  healthCheck: '/',
}

// 修复后
endpoints: {
  smartSearch: '/smart-search',
  sideChat: '/side-chat',   // 修复拼写
  healthCheck: '/',
}
```

### 2. 修复API调用
```typescript
// 修复前：HomeView使用sideChatStream
sideChatStream(
  {
    query: content,
    history: [] // 主页搜索不需要历史记录
  },
  { onSource, onToken, onEnd, onError }
)

// 修复后：HomeView使用smartSearchStream
smartSearchStream(
  { query: searchKeyword.value.trim() },
  { onSource, onToken, onEnd, onError }
)
```

### 3. 增强错误处理
```typescript
// 添加详细的调试日志
console.log('开始AI搜索:', searchKeyword.value.trim())
console.log('收到source事件:', src)
console.log('收到token:', token)
console.log('AI搜索完成')
console.error('AI搜索错误:', err)

// 改进错误信息
ElMessage.error(`AI搜索失败: ${err.message || '请稍后重试'}`)
```

### 4. 修复导入
```typescript
// 修复前
import { smartSearchStream, checkAiServiceHealth, sideChatStream } from '@/api/ai-search'

// 修复后
import { smartSearchStream, checkAiServiceHealth } from '@/api/ai-search'
```

## 功能分离

### HomeView AI搜索
- **API**：`smartSearchStream`
- **端点**：`/smart-search`
- **用途**：智能搜索，不需要历史记录
- **请求格式**：`{ query: string }`

### AISideChat对话
- **API**：`sideChatStream`
- **端点**：`/side-chat`
- **用途**：多轮对话，需要历史记录
- **请求格式**：`{ query: string, history: ChatMessage[] }`

## 测试建议

### 1. 功能测试
1. 在主页勾选"询问AI智能体"
2. 输入"如何创建社团"
3. 点击搜索按钮
4. 检查控制台日志
5. 验证AI回复是否正常显示

### 2. 错误测试
1. 测试网络断开情况
2. 测试AI服务不可用情况
3. 验证错误信息是否清晰

### 3. 对比测试
1. 测试HomeView AI搜索
2. 测试AISideChat对话
3. 确认两个功能都能正常工作

## 预期结果

修复后，HomeView的AI搜索功能应该能够：
1. 正常发送请求到 `/smart-search` 端点
2. 接收并显示AI回复
3. 提供详细的错误信息
4. 在控制台显示调试日志

## 注意事项

1. **端点分离**：确保HomeView和AISideChat使用不同的端点
2. **错误处理**：保持详细的错误日志便于调试
3. **用户体验**：提供清晰的错误提示
4. **功能测试**：建议在修复后进行完整的功能测试 