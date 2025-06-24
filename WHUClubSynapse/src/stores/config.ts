import { ref, computed, readonly } from 'vue'
import { defineStore } from 'pinia'
import { config as staticConfig } from '@/config'

export const useConfigStore = defineStore('config', () => {
  // 响应式的API模式状态
  const apiMode = ref<'mock' | 'real'>(staticConfig.apiMode)

  // 是否使用Mock API的计算属性
  const isUsingMockAPI = computed(() => apiMode.value === 'mock')
  const isUsingRealAPI = computed(() => apiMode.value === 'real')

  // 其他配置项
  const apiBaseUrl = ref(staticConfig.apiBaseUrl)
  const apiDebug = ref(staticConfig.apiDebug)
  const mockDelay = ref(staticConfig.mockDelay)

  // 切换API模式
  const setApiMode = (mode: 'mock' | 'real') => {
    apiMode.value = mode

    // 保存用户偏好到localStorage
    localStorage.setItem('api_mode_preference', mode)

    // 调试日志
    if (apiDebug.value) {
      console.log(`🔄 API模式已切换到: ${mode}`)
    }
  }

  // 从localStorage恢复用户偏好
  const restoreUserPreference = () => {
    const savedMode = localStorage.getItem('api_mode_preference')
    if (savedMode && (savedMode === 'mock' || savedMode === 'real')) {
      apiMode.value = savedMode as 'mock' | 'real'

      if (apiDebug.value) {
        console.log(`📱 已恢复用户偏好的API模式: ${savedMode}`)
      }
    }
  }

  // 重置为默认配置
  const resetToDefault = () => {
    apiMode.value = staticConfig.apiMode
    localStorage.removeItem('api_mode_preference')
  }

  // 获取当前配置摘要
  const getConfigSummary = () => {
    return {
      apiMode: apiMode.value,
      apiBaseUrl: apiBaseUrl.value,
      isUsingMockAPI: isUsingMockAPI.value,
      isUsingRealAPI: isUsingRealAPI.value,
      mockDelay: mockDelay.value,
      apiDebug: apiDebug.value,
    }
  }

  return {
    // 状态
    apiMode: readonly(apiMode),
    apiBaseUrl: readonly(apiBaseUrl),
    apiDebug: readonly(apiDebug),
    mockDelay: readonly(mockDelay),

    // 计算属性
    isUsingMockAPI,
    isUsingRealAPI,

    // 方法
    setApiMode,
    restoreUserPreference,
    resetToDefault,
    getConfigSummary,
  }
})
