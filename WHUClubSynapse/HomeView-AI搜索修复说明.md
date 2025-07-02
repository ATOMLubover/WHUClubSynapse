# HomeView AI搜索修复说明

## 问题描述

HomeView中的AI智能搜索功能无法正常工作，而AISideChat（侧边栏对话）功能可以正常运行。

## 问题分析

1. **端点差异**：
   - HomeView使用 `/smart-search` 端点
   - AISideChat使用 `/sider-chat` 端点（可以工作）

2. **实现差异**：
   - HomeView使用 `smartSearchStream` 函数
   - AISideChat使用 `sideChatStream` 函数

## 修复方案

### 1. 统一使用侧边栏对话端点

既然 `/sider-chat` 端点可以正常工作，我们将HomeView的AI搜索也改为使用这个端点。

### 2. 修改HomeView实现

```typescript
// 修改前：使用smartSearchStream
smartSearchStream(
  { query: searchKeyword.value },
  { onSource, onToken, onEnd, onError }
)

// 修改后：使用sideChatStream
sideChatStream(
  { 
    query: searchKeyword.value,
    history: [] // 主页搜索不需要历史记录
  },
  { onSource, onToken, onEnd, onError }
)
```

### 3. 添加必要的导入

```typescript
import { smartSearchStream, checkAiServiceHealth, sideChatStream } from '@/api/ai-search'
```

## 修复内容

### ✅ 已完成的修改

1. **导入sideChatStream函数**
   - 在HomeView中添加了 `sideChatStream` 的导入

2. **修改handleSearch方法**
   - 将 `smartSearchStream` 替换为 `sideChatStream`
   - 添加了 `history: []` 参数（主页搜索不需要历史记录）
   - 保持了相同的回调函数结构

3. **保持UI和交互不变**
   - 搜索界面和交互逻辑保持不变
   - 只修改了底层API调用

## 当前配置

### API端点
```typescript
endpoints: {
  smartSearch: '/smart-search',    // 原AI搜索端点（可能有问题）
  sideChat: '/sider-chat',         // 侧边栏对话端点（可以工作）
  healthCheck: '/',               // 健康检查端点
}
```

### 请求格式
- **HomeView AI搜索**：使用 `/sider-chat` 端点
- **AISideChat对话**：使用 `/sider-chat` 端点
- **请求方法**：POST
- **Content-Type**：application/json
- **自定义Header**：X-API-Key

## 功能状态

### ✅ 已修复
1. HomeView AI搜索使用可工作的端点
2. 保持与AISideChat相同的实现逻辑
3. 流式响应处理
4. 错误处理和加载状态

### 🔧 使用方式
1. 在主页勾选"询问AI智能体"
2. 输入搜索关键词
3. 点击搜索按钮
4. 实时显示AI回答

## 注意事项

1. **端点统一**：现在两个AI功能都使用 `/sider-chat` 端点
2. **历史记录**：HomeView搜索不传递历史记录，AISideChat传递完整对话历史
3. **功能区分**：虽然使用相同端点，但功能逻辑不同
4. **向后兼容**：如果 `/smart-search` 端点修复，可以轻松切换回去

## 测试建议

1. 测试HomeView AI搜索功能
2. 验证流式回复效果
3. 检查错误处理
4. 对比AISideChat功能确认一致性 