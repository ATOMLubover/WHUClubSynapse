# AI搜索POST接口修复说明

## 问题描述

HomeView中的AI智能搜索功能无法正常工作，而AISideChat（侧边栏对话）功能可以正常运行。问题在于 `smartSearchStream` 的POST请求处理有问题，导致SSE流解析失败。

## 修复内容

### 1. 修复fetchSSE函数

**主要改进：**

1. **增强错误处理**
   - 添加HTTP状态码检查
   - 改进错误日志记录

2. **改进SSE流解析**
   - 添加空行过滤
   - 增强数据解析容错性
   - 支持多种token格式

3. **容错性提升**
   - 对JSON解析失败的情况进行处理
   - 支持直接使用原始token数据

### 2. 修复后的fetchSSE逻辑

```typescript
// 新增HTTP状态检查
if (!resp.ok) {
  throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
}

// 改进的SSE解析
for (const line of lines) {
  const trimmedLine = line.trim()
  if (!trimmedLine) continue
  
  if (trimmedLine.startsWith('event:')) {
    eventType = trimmedLine.replace('event:', '').trim()
  } else if (trimmedLine.startsWith('data:')) {
    const data = trimmedLine.replace('data:', '').trim()
    if (!data) continue
    
    try {
      if (eventType === 'token') {
        const parsedData = JSON.parse(data)
        // 处理不同的token格式
        const token = parsedData.token || parsedData.content || parsedData
        onToken && onToken(token)
      }
      // ... 其他事件处理
    } catch (parseError) {
      // 容错处理：直接使用原始数据
      if (eventType === 'token') {
        onToken && onToken(data)
      }
    }
  }
}
```

### 3. 保持端点分离

- **HomeView AI搜索**：使用 `/smart-search` 端点
- **AISideChat对话**：使用 `/sider-chat` 端点

## 当前配置

### API端点
```typescript
endpoints: {
  smartSearch: '/smart-search',    // AI智能搜索
  sideChat: '/sider-chat',         // 侧边栏对话
  healthCheck: '/',               // 健康检查
}
```

### 请求格式
- **方法**: POST
- **Content-Type**: application/json
- **自定义Header**: X-API-Key
- **流式响应**: Server-Sent Events (SSE)

### 请求体格式
```typescript
// AI智能搜索
{
  query: string
}

// 侧边栏对话
{
  query: string,
  history: ChatMessage[]
}
```

## 功能状态

### ✅ 已修复
1. SSE流解析逻辑
2. 错误处理和容错性
3. 多种token格式支持
4. HTTP状态检查

### 🔧 使用方式
1. **主页AI搜索**：勾选"询问AI智能体"后搜索
2. **侧边栏AI对话**：点击右下角悬浮球进行对话

## 注意事项

1. **端点分离**：两个功能使用不同的端点
2. **容错处理**：支持多种响应格式
3. **错误日志**：详细的错误信息记录
4. **向后兼容**：保持原有API接口不变

## 测试建议

1. 测试HomeView AI搜索功能
2. 验证流式回复效果
3. 检查错误处理
4. 对比AISideChat功能确认一致性 