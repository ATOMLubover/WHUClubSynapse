// AI服务配置
export const AI_CONFIG = {
  // AI代理服务器地址 - 修改这里即可更新所有AI接口地址
  BASE_URL: ' https://85eb-125-220-159-5.ngrok-free.app',
  
  // 默认模型配置
  DEFAULT_MODEL: 'Qwen/Qwen3-8B-AWQ',
  DEFAULT_MAX_TOKENS: 1000,
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_TOP_P: 0.9,
  
  // 请求配置
  REQUEST_TIMEOUT: 30000, // 30秒超时
  RETRY_TIMES: 3, // 重试次数
}

// 获取AI接口完整地址
export const getAIApiUrl = (endpoint: string = '') => {
  return `${AI_CONFIG.BASE_URL}${endpoint}`
}

// 获取聊天接口地址
export const getChatApiUrl = () => {
  return getAIApiUrl('/chat')
}

// 获取状态检查接口地址
export const getStatusApiUrl = () => {
  return getAIApiUrl('/status')
} 