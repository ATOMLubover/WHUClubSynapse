# WHU社团联盟系统 API 文档

## 概述

本文档描述了WHU社团联盟系统的后端API接口规范。所有API都使用RESTful风格设计，支持JSON格式的请求和响应。

## 基础信息

- **Base URL**: `http://localhost:3000/api` (开发环境)
- **Content-Type**: `application/json`
- **认证方式**: Bearer Token (JWT)

## 通用响应格式

所有API响应都遵循以下格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 认证相关API

### 1. 用户登录

- **接口**: `POST /auth/login`
- **参数**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "user": {
        "id": "string",
        "username": "string",
        "email": "string",
        "realName": "string",
        "role": "student|admin|club_admin",
        "studentId": "string",
        "college": "string",
        "phone": "string",
        "avatar": "string",
        "createdAt": "string"
      },
      "token": "string"
    }
  }
  ```

### 2. 用户注册

- **接口**: `POST /auth/register`
- **参数**:
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string",
    "realName": "string",
    "studentId": "string",
    "college": "string",
    "phone": "string"
  }
  ```

### 3. 获取当前用户信息

- **接口**: `GET /auth/user`
- **Headers**: `Authorization: Bearer {token}`

### 4. 用户退出登录

- **接口**: `POST /auth/logout`
- **Headers**: `Authorization: Bearer {token}`

### 5. 检查用户名可用性

- **接口**: `GET /auth/check-username?username={username}`

### 6. 检查邮箱可用性

- **接口**: `GET /auth/check-email?email={email}`

### 7. 刷新Token

- **接口**: `POST /auth/refresh`
- **Headers**: `Authorization: Bearer {token}`

### 8. 修改密码

- **接口**: `POST /auth/change-password`
- **参数**:
  ```json
  {
    "oldPassword": "string",
    "newPassword": "string"
  }
  ```

### 9. 忘记密码

- **接口**: `POST /auth/forgot-password`
- **参数**:
  ```json
  {
    "email": "string"
  }
  ```

### 10. 重置密码

- **接口**: `POST /auth/reset-password`
- **参数**:
  ```json
  {
    "token": "string",
    "newPassword": "string"
  }
  ```

## 社团相关API

### 1. 获取社团列表

- **接口**: `GET /clubs`
- **查询参数**:
  - `keyword`: 搜索关键词
  - `category`: 社团分类 (学术科技|文艺体育|志愿服务|创新创业|其他)
  - `sortBy`: 排序方式 (hot|time|members)
  - `page`: 页码 (默认1)
  - `pageSize`: 每页数量 (默认12)

### 2. 获取社团详情

- **接口**: `GET /clubs/{id}`

### 3. 获取热门社团

- **接口**: `GET /api/club/latest?limit={limit}`

### 4. 获取最新社团

- **接口**: `GET /clubs/latest?limit={limit}`

### 5. 获取推荐社团

- **接口**: `GET /clubs/recommended?limit={limit}`
- **需要**: 用户登录状态

### 6. 获取社团分类统计

- **接口**: `GET /clubs/categories`
- **响应**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "学术科技": 25,
      "文艺体育": 18,
      "志愿服务": 12,
      "创新创业": 8,
      "其他": 6
    }
  }
  ```

### 7. 申请加入社团

- **接口**: `POST /clubs/apply`
- **Headers**: `Authorization: Bearer {token}`
- **参数**:
  ```json
  {
    "clubId": "string",
    "reason": "string"
  }
  ```

### 8. 收藏社团

- **接口**: `POST /clubs/{clubId}/favorite`
- **Headers**: `Authorization: Bearer {token}`

### 9. 取消收藏社团

- **接口**: `DELETE /clubs/{clubId}/favorite`
- **Headers**: `Authorization: Bearer {token}`

### 10. 获取用户收藏的社团

- **接口**: `GET /api/club/my_favorites`
- **Headers**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `pageSize`: 每页数量

### 11. 获取用户申请记录

- **接口**: `GET /api/club/my_joinapplis`
- **Headers**: `Authorization: Bearer {token}`
- **查询参数**:
  - `page`: 页码
  - `pageSize`: 每页数量
  - `status`: 申请状态 (pending|approved|rejected)

### 12. 创建社团 (管理员功能)

- **接口**: `POST /clubs`
- **Headers**: `Authorization: Bearer {token}`
- **参数**:
  ```json
  {
    "name": "string",
    "description": "string",
    "category": "string",
    "maxMembers": "number",
    "tags": ["string"],
    "coverImage": "string"
  }
  ```

### 13. 更新社团信息 (社团管理员功能)

- **接口**: `PUT /clubs/{id}`
- **Headers**: `Authorization: Bearer {token}`

### 14. 删除社团 (管理员功能)

- **接口**: `DELETE /clubs/{id}`
- **Headers**: `Authorization: Bearer {token}`

## 数据模型

### User (用户)

```typescript
interface User {
  id: string
  username: string
  email: string
  avatar?: string
  role: 'student' | 'admin' | 'club_admin'
  studentId?: string
  realName: string
  college: string
  phone?: string
  createdAt: string
}
```

### Club (社团)

```typescript
interface Club {
  id: string
  name: string
  description: string
  coverImage: string
  category: '学术科技' | '文艺体育' | '志愿服务' | '创新创业' | '其他'
  adminId: string
  adminName: string
  currentMembers: number
  maxMembers: number
  tags: string[]
  isHot: boolean
  status: 'active' | 'inactive' | 'pending'
  createdAt: string
  updatedAt: string
}
```

### PaginatedData (分页数据)

```typescript
interface PaginatedData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}
```

## 错误码说明

- `200`: 成功
- `400`: 请求参数错误
- `401`: 未登录或token无效
- `403`: 权限不足
- `404`: 资源不存在
- `409`: 资源冲突 (如用户名已存在)
- `500`: 服务器内部错误

## 开发注意事项

1. **环境变量**: 在 `.env` 文件中配置 `VITE_API_BASE_URL`
2. **请求拦截器**: 已在 `src/utils/request.ts` 中配置
3. **错误处理**: 统一的错误处理和消息提示
4. **Token管理**: 自动添加到请求头，支持刷新机制
5. **开发调试**: 可以使用模拟数据进行前端开发，后端就绪后切换到真实API

## Mock数据支持

在开发阶段，如果后端API尚未就绪，可以：

1. 在 `src/utils/request.ts` 中配置mock模式
2. 使用 `src/utils/mockData.ts` 中的模拟数据
3. 通过环境变量 `VITE_USE_MOCK` 控制是否使用mock数据
