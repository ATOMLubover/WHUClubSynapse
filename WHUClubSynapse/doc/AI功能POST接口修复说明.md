# AI功能POST接口修复说明

## 修复内容

### 1. 移除event-source-polyfill依赖
- 已从 `ai-search.ts` 中移除 `EventSourcePolyfill` 导入
- 改用原生 `fetch` + `ReadableStream` 实现POST流式SSE

### 2. 实现fetchSSE工具函数
- 支持POST请求 + 自定义header
- 手动解析SSE流数据
- 处理 `source`、`token`、`end`、`error` 事件

### 3. 修复AI搜索流式接口
- `smartSearchStream` 函数使用 `fetchSSE`
- 支持实时token拼接和UI更新
- 错误处理和加载状态管理

### 4. 修复侧边栏对话流式接口
- `sideChatStream` 函数使用 `fetchSSE`
- 支持多轮对话历史
- 实时消息渲染和滚动

## 当前配置

### API端点配置
```typescript
endpoints: {
  smartSearch: '/smart-search',    // AI智能搜索
  sideChat: '/side-chat',         // 侧边栏对话
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

### 响应事件
- `event: source` - 溯源信息
- `event: token` - AI回复token
- `event: end` - 流结束
- `event: error` - 错误信息

## 功能状态

### ✅ 已修复
1. POST流式接口实现
2. 自定义header支持
3. SSE流解析
4. 实时UI更新
5. 错误处理
6. 健康检查

### 🔧 配置项
- **baseURL**: `http://7e6e72a.cpolar.io`
- **API Key**: `super_plus_api_key`
- **超时时间**: 30秒
- **重试次数**: 3次

## 使用方式

### 主页AI搜索
1. 勾选"询问AI智能体"
2. 输入搜索关键词
3. 点击搜索按钮
4. 实时显示AI回答

### 侧边栏AI对话
1. 点击右下角悬浮球
2. 输入问题
3. 支持多轮对话
4. 实时流式回复

## 注意事项

1. 确保AI服务地址可访问
2. 检查API Key是否正确
3. 网络连接稳定
4. 浏览器支持ReadableStream

## 测试建议

1. 测试AI连通性按钮
2. 验证流式回复效果
3. 检查错误处理
4. 测试多轮对话 