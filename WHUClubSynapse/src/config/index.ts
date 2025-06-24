// 应用配置
export const config = {
  // API基础URL
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api',

  // API模式: 'mock' | 'real'
  apiMode: (import.meta.env.VITE_API_MODE || 'mock') as 'mock' | 'real',

  // 是否启用API调试日志
  apiDebug: import.meta.env.VITE_API_DEBUG === 'true',

  // 模拟API延迟时间（毫秒）
  mockDelay: Number(import.meta.env.VITE_MOCK_DELAY) || 800,

  // 应用信息
  app: {
    name: 'WHU社团联盟',
    version: '1.0.0',
    description: '武汉大学社团信息管理系统',
  },
}

// 开发环境配置
export const isDev = import.meta.env.DEV
export const isProd = import.meta.env.PROD

// API模式检查
export const isUsingMockAPI = config.apiMode === 'mock'
export const isUsingRealAPI = config.apiMode === 'real'

// 调试日志
if (config.apiDebug && isDev) {
  console.log('🚀 应用配置:', config)
  console.log(`📡 API模式: ${config.apiMode}`)
  console.log(`🔗 API地址: ${config.apiBaseUrl}`)
}
