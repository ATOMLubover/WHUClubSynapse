// AI智能搜索配置
export const aiSearchConfig = {
  // AI智能搜索API基础URL
  baseURL: 'http://5c3f836f.cpolar.io', // 根据实际部署情况修改
  
  // API端点
  endpoints: {
    smartSearch: '/api/v1/smart-search',
    sideChat: '/api/v1/sider-chat',
    healthCheck: '/', // 新增健康检查端点
  },
  
  // API Key配置
  apiKey: 'super_plus_api_key', // 需要替换为实际的API Key
  
  // 请求配置
  requestConfig: {
    timeout: 30000, // 30秒超时
    retryTimes: 3, // 重试次数
    healthCheckTimeout: 5000, // 健康检查超时时间
  },
  
  // 响应配置
  responseConfig: {
    maxAnswerLength: 500, // 最大回答长度
    showSource: true, // 是否显示来源
  },
  
  // 功能开关
  features: {
    enabled: true, // 是否启用AI搜索功能
    showInSearch: true, // 是否在搜索页面显示AI回答
    sideChat: true, // 是否启用侧边栏对话功能
    healthCheck: true, // 是否启用健康检查
  },

  // 侧边栏对话配置
  sideChat: {
    maxHistory: 10, // 最大历史记录数
    autoScroll: true, // 自动滚动到最新消息
    showSource: true, // 是否显示来源信息
  }
}

// 获取完整的API URL
export const getSmartSearchURL = () => {
  return `${aiSearchConfig.baseURL}${aiSearchConfig.endpoints.smartSearch}`
}

// 获取侧边栏对话API URL
export const getSideChatURL = () => {
  return `${aiSearchConfig.baseURL}${aiSearchConfig.endpoints.sideChat}`
}

// 获取健康检查API URL
export const getHealthCheckURL = () => {
  return `${aiSearchConfig.baseURL}${aiSearchConfig.endpoints.healthCheck}`
}

// 获取API Key
export const getApiKey = () => {
  return aiSearchConfig.apiKey
}

// 检查功能是否启用
export const isAiSearchEnabled = () => {
  return aiSearchConfig.features.enabled
}

// 检查侧边栏对话是否启用
export const isSideChatEnabled = () => {
  return aiSearchConfig.features.sideChat
}

// 检查健康检查是否启用
export const isHealthCheckEnabled = () => {
  return aiSearchConfig.features.healthCheck
} 