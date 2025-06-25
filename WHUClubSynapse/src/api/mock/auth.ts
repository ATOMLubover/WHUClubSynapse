import type { User, LoginRequest, RegisterRequest, ApiResponse } from '@/types'
import { mockUser } from '@/utils/mockData'
import { config } from '@/config'

// 模拟延迟
const delay = (ms: number = config.mockDelay) => new Promise((resolve) => setTimeout(resolve, ms))

// 模拟用户登录
export const mockLogin = async (
  data: LoginRequest,
): Promise<{ data: ApiResponse<{ user: User; token: string }> }> => {
  await delay()

  // 简单的模拟验证
  if (data.username === 'demo' && data.password === '123456') {
    return {
      data: {
        code: 200,
        message: '登录成功',
        data: {
          user: mockUser,
          token: 'mock_jwt_token_' + Date.now(),
        },
      },
    }
  } else {
    throw new Error('用户名或密码错误')
  }
}

// 模拟用户注册
export const mockRegister = async (
  data: RegisterRequest,
): Promise<{ data: ApiResponse<{ user: User; token: string }> }> => {
  await delay(1200)

  const newUser: User = {
    id: 'user_' + Date.now(),
    username: data.username,
    email: data.email,
    role: 'student',
    studentId: data.studentId,
    realName: data.realName,
    college: data.college,
    phone: data.phone,
    createdAt: new Date().toISOString(),
    emailVerified: 'true',
    phoneVerified: 'false',
    bio: '',
  }

  return {
    data: {
      code: 200,
      message: '注册成功',
      data: {
        user: newUser,
        token: 'mock_jwt_token_' + Date.now(),
      },
    },
  }
}

// 模拟获取当前用户信息
export const mockGetCurrentUser = async (): Promise<{ data: ApiResponse<User> }> => {
  await delay(500)

  return {
    data: {
      code: 200,
      message: 'success',
      data: mockUser,
    },
  }
}

// 模拟用户退出登录
export const mockLogout = async (): Promise<{ data: ApiResponse<null> }> => {
  await delay(300)

  return {
    data: {
      code: 200,
      message: '退出登录成功',
      data: null,
    },
  }
}

// 模拟检查用户名是否可用
export const mockCheckUsername = async (
  username: string,
): Promise<{ data: ApiResponse<{ available: boolean }> }> => {
  await delay(400)

  // 模拟已存在的用户名
  const existingUsernames = ['admin', 'test', 'user', 'demo']
  const available = !existingUsernames.includes(username.toLowerCase())

  return {
    data: {
      code: 200,
      message: 'success',
      data: { available },
    },
  }
}

// 模拟检查邮箱是否可用
export const mockCheckEmail = async (
  email: string,
): Promise<{ data: ApiResponse<{ available: boolean }> }> => {
  await delay(400)

  // 模拟已存在的邮箱
  const existingEmails = ['admin@example.com', 'test@example.com', 'user@example.com']
  const available = !existingEmails.includes(email.toLowerCase())

  return {
    data: {
      code: 200,
      message: 'success',
      data: { available },
    },
  }
}

// 模拟刷新token
export const mockRefreshToken = async (): Promise<{ data: ApiResponse<{ token: string }> }> => {
  await delay(300)

  return {
    data: {
      code: 200,
      message: 'Token刷新成功',
      data: {
        token: 'mock_jwt_token_' + Date.now(),
      },
    },
  }
}

// 模拟修改密码
export const mockChangePassword = async (data: {
  oldPassword: string
  newPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  await delay(600)

  // 简单验证
  if (data.oldPassword === '123456') {
    return {
      data: {
        code: 200,
        message: '密码修改成功',
        data: null,
      },
    }
  } else {
    throw new Error('原密码错误')
  }
}

// 模拟忘记密码
export const mockForgotPassword = async (email: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(800)

  return {
    data: {
      code: 200,
      message: '重置密码邮件已发送',
      data: null,
    },
  }
}

// 模拟重置密码
export const mockResetPassword = async (data: {
  token: string
  newPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  await delay(600)

  return {
    data: {
      code: 200,
      message: '密码重置成功',
      data: null,
    },
  }
}
