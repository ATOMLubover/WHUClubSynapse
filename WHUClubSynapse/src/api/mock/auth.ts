import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  VerifyEmailRequest,
  UserListParams,
  RegisterResponse,
  ApiResponse,
  UserPreferences
} from '@/types'
import { config } from '@/config'
import { mockUser } from '@/utils/mockData'

// 模拟延迟
const delay = (ms: number = config.mockDelay) => new Promise((resolve) => setTimeout(resolve, ms))


// 模拟管理员用户
const mockAdmin: User = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  avatar_url: 'https://example.com/admin-avatar.jpg',
  role: 'admin',
  last_active: '2025-06-25 16:00:00'
}

// 1. 模拟用户登录
export const mockLogin = async (
  data: LoginRequest,
): Promise<{ data: User; token: string }> => {
  await delay()

  // 简单的模拟验证
  if (data.username === 'demo' && data.password === '123456') {
    return {
      data: mockUser,
      token: 'mock_jwt_token_' + Date.now(),
    }
  } else if (data.username === 'admin' && data.password === 'admin123') {
    return {
      data: mockAdmin,
      token: 'mock_jwt_token_admin_' + Date.now(),
    }
  } else {
    throw new Error('用户名或密码错误')
  }
}

// 2. 模拟发送邮箱验证码
export const mockSendVerifyEmail = async (
  data: VerifyEmailRequest,
): Promise<string> => {
  await delay(800)
  
  // 模拟已存在验证码的情况（返回202状态码的模拟）
  if (data.email === 'existing@example.com') {
    throw new Error('验证码已存在')
  }
  
  return `邮件已发送至${data.email}`
}

// 3. 模拟用户注册
export const mockRegister = async (
  data: RegisterRequest,
): Promise<RegisterResponse> => {
  await delay(1200)

  // 模拟验证码验证
  if (data.vrf_code !== '1234') {
    throw new Error('验证码错误或失效')
  }

  // 模拟用户名或邮箱已存在
  if (data.username === 'admin' || data.email === 'admin@example.com') {
    throw new Error('用户名或邮箱已存在')
  }

  return {
    id: Date.now(),
    username: data.username,
  }
}

// 4. 模拟根据ID获取用户信息
export const mockGetUserById = async (id: number): Promise<User> => {
  await delay(500)

  if (id === 1) {
    return mockAdmin
  } else if (id === 2233) {
    return mockUser
  } else {
    throw new Error('用户不存在')
  }
}

// 5. 模拟管理员获取用户列表
export const mockGetUserList = async (params: UserListParams): Promise<User[]> => {
  await delay(600)

  // 模拟权限检查
  // 在实际使用中，这个检查应该在请求拦截器中处理
  
  // 模拟分页返回
  const allUsers = [mockAdmin, mockUser]
  const start = params.offset
  const end = start + params.num
  
  return allUsers.slice(start, end)
}

// 6. 模拟ping
export const mockPing = async (): Promise<string> => {
  await delay(100)
  return 'pong'
}

// 模拟获取当前用户信息
export const mockGetCurrentUser = async (): Promise<User> => {
  await delay(500)
  return mockUser
}

// 模拟用户退出登录
export const mockLogout = async (): Promise<ApiResponse<null>> => {
  await delay(300)
  return {
    code: 200,
    message: '退出成功',
    data: null,
  }
}

//模拟更新用户偏好
export const mockUpdateUserPreferences=async(preferences: UserPreferences)=>{
  await delay(300)
  mockUser.hasCompletedPreferences=true;
  mockUser.preferences=preferences;
  return {data:mockUser}

}


