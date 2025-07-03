import request from '@/utils/request'
import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  VerifyEmailRequest,
  UserListParams,
  RegisterResponse,
  ApiResponse,
  UserPreferences,
  UpdateUserRequest
} from '@/types'
import { useConfigStore } from '@/stores/config'
import * as mockAuth from './mock/auth'
import { useAuthStore } from '@/stores/auth'
import { processUserFromBackend } from '@/utils/userExtension'


// 获取动态配置
const getIsUsingMockAPI = () => {
  const configStore = useConfigStore()
  return configStore.isUsingMockAPI
}

// 1. 用户登录
export const login = async (
  data: LoginRequest,
): Promise<{ data: User; token: string }> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockLogin(data)
  }
  
  const response = await request.post('/auth/login', data)
  // 后端直接返回用户对象，token在Header中
  const token = response.headers.authorization?.replace('Bearer ', '') || ''
  
  return {
    data: response.data,
    token: token
  }
}

// 2. 发送邮箱验证码
export const sendVerifyEmail = async (
  data: VerifyEmailRequest,
): Promise<string> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockSendVerifyEmail(data)
  }
  
  const response = await request.post('/auth/verify', data)
  // 返回文本消息，如："邮件已发送至{email}"
  return response.data
}

// 3. 用户注册
export const register = async (
  data: RegisterRequest,
): Promise<RegisterResponse> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockRegister(data)
  }
  
  const response = await request.post('/auth/register', data)
  // 返回 { "id": 2, "username": "new_user" }
  return response.data
}

// 4. 根据用户ID查询用户信息
export const getUserById = async (
  id: number,
): Promise<User> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockGetUserById(id)
  }
  
  const response = await request.get(`/api/user/${id}`)
  // 自动处理extension字段
  return processUserFromBackend(response.data)
}

// 5. 管理员获取用户列表
export const getUserList = async (
  params: UserListParams,
): Promise<User[]> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockGetUserList(params)
  }
  
  const response = await request.get('/api/user/list', { params })
  // 自动处理每个用户的extension字段
  return response.data.map((user: any) => processUserFromBackend(user))
}

// 6. 用户活跃状态刷新（心跳检测）
export const ping = async (): Promise<string> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockPing()
  }
  
  const response = await request.get('/api/v1/auth/ping')
  // 返回 "pong"
  return response.data
}

// 获取当前用户信息（基于token）
export const getCurrentUser = async (): Promise<User> => {
  if (getIsUsingMockAPI()) {
    return await mockAuth.mockGetCurrentUser()
  }
  const id=useAuthStore().currentUserId
  return await getUserById(id as number)
}
// TODO:用户退出登录
export const logout = async (): Promise<ApiResponse<null>> => {
  return getIsUsingMockAPI() ? await mockAuth.mockLogout() : await request.post('/auth/logout')
}

// TODO:刷新token
export const refreshToken = async (): Promise<{ token: string }> => {
  return Promise.resolve({
    token: 'mock_jwt_token_' + Date.now(),
  })
}

// TODO:修改密码
export const changePassword = async (data: {
  oldPassword: string
  newPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  return Promise.resolve({
    data: {
      code: 200,
      message: '密码修改成功',
      data: null,
    },
  })
}

// TODO:忘记密码
export const forgotPassword = async (email: string): Promise<{ data: ApiResponse<null> }> => {
  return Promise.resolve({
    data: {
      code: 200,
      message: '密码重置邮件已发送',
      data: null,
    },
  })
}

// TODO:重置密码
export const resetPassword = async (data: {
  token: string
  newPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  return Promise.resolve({
    data: {
      code: 200,
      message: '密码重置成功',
      data: null,
    },
  })
}

// TODO:更新用户偏好设置
export const updateUserPreferences = async (preferences: UserPreferences): Promise<{ data:User }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockUpdateUserPreferences(preferences)
    : (await request.put('/auth/preferences', preferences)).data
}

// 上传用户头像
export const uploadAvatar = async (file: File): Promise<{ data: ApiResponse<string> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟上传成功，返回一个假的头像URL
    return {
      data: {
        code: 200,
        message: '头像上传成功',
        data: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png'
      }
    }
  }

  const formData = new FormData()
  formData.append('avatar', file)

  const response = await request.post('/api/user/upload_avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  
  return {
    data: {
      code: response.status,
      message: '头像上传成功',
      data: response.data.path // 假设后端返回的是新的头像URL
    }
  }
}

// /api/club/pub/update_logo

/**
 * 🆕 更新用户信息
 */
export async function updateUserInfo(updateData: UpdateUserRequest): Promise<string> {
  console.log('API updateUserInfo 发送的数据:', updateData)
  const response = await request.put('/api/user/update', updateData)
  console.log('API updateUserInfo 后端响应:', response.data)
  return response.data || '更新用户信息成功'
}