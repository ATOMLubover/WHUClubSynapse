# 环境配置说明

## 概述

本项目支持两种API模式：**模拟数据模式(Mock)** 和 **真实API模式(Real)**，可以通过环境变量轻松切换。

## 环境变量配置

### 1. 创建环境变量文件

在项目根目录创建 `.env.local` 文件（该文件会被Git忽略）：

```env
# API配置
VITE_API_BASE_URL=http://localhost:3000/api

# API模式切换
# 'mock' = 使用模拟数据（前端开发）
# 'real' = 使用真实API（连接后端）
VITE_API_MODE=mock

# 是否启用API请求日志
VITE_API_DEBUG=true

# 模拟API延迟时间（毫秒）
VITE_MOCK_DELAY=800
```

### 2. 环境变量说明

| 变量名              | 类型                 | 默认值                      | 说明                          |
| ------------------- | -------------------- | --------------------------- | ----------------------------- |
| `VITE_API_BASE_URL` | string               | `http://localhost:3000/api` | API服务器地址                 |
| `VITE_API_MODE`     | `'mock'` \| `'real'` | `mock`                      | API模式切换                   |
| `VITE_API_DEBUG`    | boolean              | `true`                      | 是否在控制台显示API调试信息   |
| `VITE_MOCK_DELAY`   | number               | `800`                       | 模拟API的响应延迟时间（毫秒） |

## 使用场景

### 🧪 开发阶段 - 使用模拟数据

```env
VITE_API_MODE=mock
VITE_API_DEBUG=true
VITE_MOCK_DELAY=500
```

**优势：**

- ✅ 无需后端服务即可开发前端功能
- ✅ 可控制的响应延迟，模拟网络环境
- ✅ 稳定的测试数据，便于功能验证
- ✅ 完整的功能演示和原型展示

**适用情况：**

- 前端独立开发
- 功能原型演示
- 后端API尚未就绪
- 离线开发环境

### 🚀 联调阶段 - 使用真实API

```env
VITE_API_MODE=real
VITE_API_BASE_URL=http://localhost:3000/api
VITE_API_DEBUG=true
```

**优势：**

- ✅ 真实的数据交互
- ✅ 完整的错误处理验证
- ✅ 准确的性能测试
- ✅ 生产环境一致性

**适用情况：**

- 前后端联调
- 集成测试
- 性能测试
- 生产部署

## 快速切换模式

### 方法一：修改环境变量文件

编辑 `.env.local` 文件中的 `VITE_API_MODE` 值：

```env
# 切换到模拟模式
VITE_API_MODE=mock

# 切换到真实API模式
VITE_API_MODE=real
```

### 方法二：使用不同的环境文件

创建多个环境文件：

```
.env.local.mock     # 模拟数据配置
.env.local.real     # 真实API配置
```

然后复制对应文件到 `.env.local`：

```bash
# 使用模拟数据
cp .env.local.mock .env.local

# 使用真实API
cp .env.local.real .env.local
```

## 运行命令

修改环境变量后，重启开发服务器：

```bash
# 停止当前服务
Ctrl + C

# 重新启动
npm run dev
```

## 调试信息

当 `VITE_API_DEBUG=true` 时，浏览器控制台会显示：

```
🚀 应用配置: {...}
📡 API模式: mock
🔗 API地址: http://localhost:3000/api
```

## 模拟数据功能

### 认证功能

- **演示账号**: `demo` / `123456`
- **注册功能**: 支持完整注册流程
- **权限验证**: 模拟登录状态检查

### 社团数据

- **8个示例社团**: 涵盖各个分类
- **完整功能**: 搜索、筛选、分页、收藏、申请
- **动态数据**: 支持创建、更新、删除操作

### 用户交互

- **申请记录**: 模拟申请状态和审核流程
- **收藏功能**: 模拟收藏/取消收藏操作
- **个人中心**: 模拟用户数据管理

## 注意事项

1. **重启服务**: 修改环境变量后需要重启开发服务器
2. **缓存清理**: 如有异常，可清理浏览器缓存
3. **数据持久性**: 模拟数据仅在内存中，刷新页面会重置
4. **网络状态**: 模拟模式下网络错误不会影响功能
5. **生产构建**: 确保生产环境使用正确的API配置

## 故障排除

### 配置未生效

1. 检查 `.env.local` 文件是否在项目根目录
2. 确认环境变量名称是否正确（必须以 `VITE_` 开头）
3. 重启开发服务器

### 模拟数据问题

1. 检查控制台是否有错误信息
2. 确认 `VITE_API_MODE=mock`
3. 查看网络面板，确认请求未发送到真实服务器

### 真实API连接问题

1. 确认后端服务已启动
2. 检查 `VITE_API_BASE_URL` 是否正确
3. 查看网络面板的请求状态和错误信息

## 技术实现

项目通过以下方式实现API模式切换：

```typescript
// 配置检查
import { isUsingMockAPI } from '@/config'

// API函数示例
export const login = async (data) => {
  return isUsingMockAPI
    ? await mockAuth.mockLogin(data) // 模拟API
    : await request.post('/auth/login', data) // 真实API
}
```

这种设计确保了：

- 🔄 无缝切换：改变配置即可切换模式
- 🎯 类型安全：两种模式使用相同的TypeScript接口
- 🛠 开发友好：丰富的调试信息和错误处理
- 📦 生产就绪：真实API模式完全兼容生产环境
