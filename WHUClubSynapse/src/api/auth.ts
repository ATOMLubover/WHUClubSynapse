import request from '@/utils/request'
import type { User, LoginRequest, RegisterRequest, ApiResponse } from '@/types'
import { useConfigStore } from '@/stores/config'
import * as mockAuth from './mock/auth'

// 获取动态配置
const getIsUsingMockAPI = () => {
  const configStore = useConfigStore()
  return configStore.isUsingMockAPI
}

// 用户登录
export const login = async (
  data: LoginRequest,
): Promise<{ data: ApiResponse<{ user: User; token: string }> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockLogin(data)
    : await request.post('/auth/login', data)
}

// 用户注册
export const register = async (
  data: RegisterRequest,
): Promise<{ data: ApiResponse<{ user: User; token: string }> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockRegister(data)
    : await request.post('/auth/register', data)
}

// 获取当前用户信息
export const getCurrentUser = async (): Promise<{ data: ApiResponse<User> }> => {
  return getIsUsingMockAPI() ? await mockAuth.mockGetCurrentUser() : await request.get('/auth/user')
}

// 用户退出登录
export const logout = async (): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI() ? await mockAuth.mockLogout() : await request.post('/auth/logout')
}

// 检查用户名是否可用
export const checkUsername = async (
  username: string,
): Promise<{ data: ApiResponse<{ available: boolean }> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockCheckUsername(username)
    : await request.get(`/auth/check-username?username=${encodeURIComponent(username)}`)
}

// 检查邮箱是否可用
export const checkEmail = async (
  email: string,
): Promise<{ data: ApiResponse<{ available: boolean }> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockCheckEmail(email)
    : await request.get(`/auth/check-email?email=${encodeURIComponent(email)}`)
}

// 刷新token
export const refreshToken = async (): Promise<{ data: ApiResponse<{ token: string }> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockRefreshToken()
    : await request.post('/auth/refresh')
}

// 修改密码
export const changePassword = async (data: {
  oldPassword: string
  newPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockChangePassword(data)
    : await request.post('/auth/change-password', data)
}

// 忘记密码
export const forgotPassword = async (email: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockForgotPassword(email)
    : await request.post('/auth/forgot-password', { email })
}

// 重置密码
export const resetPassword = async (data: {
  token: string
  newPassword: string
}): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockResetPassword(data)
    : await request.post('/auth/reset-password', data)
}

// 更新用户偏好设置
export const updateUserPreferences = async (preferences: {
  interestedCategories: string[]
  emailNotifications: boolean
  applicationNotifications: boolean
  activityNotifications: boolean
  profilePublic: boolean
  showJoinedClubs: boolean
  tags?: string[]
}): Promise<{ data: ApiResponse<User> }> => {
  return getIsUsingMockAPI()
    ? await mockAuth.mockUpdateUserPreferences(preferences)
    : await request.put('/auth/preferences', preferences)
}
