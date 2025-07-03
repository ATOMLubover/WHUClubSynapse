import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage, type MessageParamsWithType } from 'element-plus'
import * as authApi from '@/api/auth'
import { getUserIdFromToken, getUserRoleFromToken, isTokenExpired, getUserInfoFromToken } from '@/utils/jwt'
import type { User, LoginRequest, RegisterRequest, UserPreferences } from '@/types'
import { config } from '@/config'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  // 从JWT中获取用户信息的计算属性
  const currentUserId = computed(() => getUserIdFromToken())
  const currentUserRole = computed(() => getUserRoleFromToken())

  // 登录
  const login = async (loginData: LoginRequest) => {
    try {
      loading.value = true
      const response = await authApi.login(loginData)
      
      // 新的API格式：{ data: User, token: string }
      user.value = response.data
      console.log(user.value)
      token.value = response.token
      localStorage.setItem('token', response.token)

      // 登录成功后获取完整的用户信息
      await fetchUserInfo()

      return response.data
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
      
      // 注册成功后需要重新登录获取完整用户信息
      // 因为注册接口只返回 { id, username }
      return response
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
      const userInfo = await authApi.getCurrentUser()
      if (userInfo.avatar_url == '') {
        userInfo.avatar_url = `${config.apiBaseUrl}/pub/user_avatars/default.jpg`
        // userInfo.avatar_url = `${config.apiBaseUrl}/pub/user_logos/_${userInfo.user_id}`

      }
      else{
         userInfo.avatar_url=`${config.apiBaseUrl}/`+userInfo.avatar_url
      }

      console.log('userInfo.avatar_url', userInfo.avatar_url)
      user.value = userInfo
      return userInfo
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果token无效，清除登录状态
      logout()
      throw error
    }
  }
  //
  const uploadAvatar=async(file: File)=>{
    try{
      await authApi.uploadAvatar(file)
      await fetchUserInfo()

    }
    catch(error){
      console.error("上传用户头像失败",error)
    }

  }

  // 退出登录
  const logout = async () => {
    try {
      if (token.value) {
        // await authApi.logout()
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
        console.log('用户信息初始化成功:', user.value)
      } catch (error) {
        console.error('初始化失败，清除无效token:', error)
        // 自动清除无效token
        logout()
      }
    }
  }

  // TODO:更新用户偏好设置
  const updatePreferences = async (preferences: UserPreferences) => {
    try {
      loading.value = true
      const response = await authApi.updateUserPreferences(preferences)
      user.value = response.data
      return response
    } catch (error) {
      console.error('更新偏好设置失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 管理员获取用户列表
  const fetchAllUsers = async (params?: { offset?: number; num?: number }) => {
    try {
      const response = await authApi.getUserList({
        offset: params?.offset || 0,
        num: params?.num || 10
      })
      console.log('response', response)
      return response.map(user => {
        if (user.avatar_url == '') {
          user.avatar_url = `${config.apiBaseUrl}/pub/user_avatars/default.jpg`
        }
        else{
          user.avatar_url=`${config.apiBaseUrl}/`+user.avatar_url
        }
        return user
      })

    } catch (error) {
      console.error('获取用户列表失败:', error)
      ElMessage.error('获取用户列表失败')
      throw error
    }
  }

  // 更新用户信息（管理员功能）
  const updateUser = async (userId: number, userData: Partial<User>) => {
    try {
      // 这里应该调用后端API，暂时模拟成功
      ElMessage.success('用户信息更新成功')
      return { success: true }
    } catch (error) {
      console.error('更新用户信息失败:', error)
      ElMessage.error('更新用户信息失败')
      throw error
    }
  }

  // 快速获取当前用户ID（从JWT解析）
  const getCurrentUserId = (): number | null => {
    return getUserIdFromToken()
  }

  // 检查token有效性
  const checkTokenValidity = (): boolean => {
    return !!token.value && !isTokenExpired()
  }



  return {
    // 状态
    user,
    token,
    loading,
    // 计算属性
    isLoggedIn,
    isAdmin,
    currentUserId,
    currentUserRole,
    // 方法
    login,
    register,
    fetchUserInfo,
    logout,
    initialize,
    updatePreferences,
    fetchAllUsers,
    updateUser,
    getCurrentUserId,
    checkTokenValidity,
    uploadAvatar
  }
})
