import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import * as authApi from '@/api/auth'
import type { User, LoginRequest, RegisterRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isClubAdmin = computed(() => user.value?.role === 'club_admin')

  // 登录
  const login = async (loginData: LoginRequest) => {
    try {
      loading.value = true
      const response = await authApi.login(loginData)
      const { user: userInfo, token: userToken } = response.data.data

      user.value = userInfo
      token.value = userToken
      localStorage.setItem('token', userToken)

      // ElMessage.success('登录成功')
      return userInfo
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (registerData: RegisterRequest) => {
    try {
      loading.value = true
      const response = await authApi.register(registerData)
      const { user: userInfo, token: userToken } = response.data.data

      user.value = userInfo
      token.value = userToken
      localStorage.setItem('token', userToken)

      ElMessage.success('注册成功')
      return userInfo
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!token.value) return null

    try {
      const response = await authApi.getCurrentUser()
      user.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果token无效，清除登录状态
      logout()
      throw error
    }
  }

  // 退出登录
  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      ElMessage.success('已退出登录')
    }
  }

  // 初始化（检查登录状态）
  const initialize = async () => {
    if (token.value) {
      try {
        await fetchUserInfo()
      } catch (error) {
        // 自动清除无效token
        logout()
      }
    }
  }

  return {
    // 状态
    user,
    token,
    loading,
    // 计算属性
    isLoggedIn,
    isAdmin,
    isClubAdmin,
    // 方法
    login,
    register,
    fetchUserInfo,
    logout,
    initialize,
  }
})
