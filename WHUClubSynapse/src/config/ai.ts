// AI服务配置
export const AI_CONFIG = {
  // AI代理服务器地址 - 修改这里即可更新所有AI接口地址
  BASE_URL: 'http://localhost:8080/api/trans/llm/',
  
  // 默认模型配置
  DEFAULT_MODEL: 'Qwen/Qwen3-8B-AWQ',
  DEFAULT_MAX_TOKENS: 1000,
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_TOP_P: 0.9,
  
  // 请求配置
  REQUEST_TIMEOUT: 30000, // 30秒超时
  RETRY_TIMES: 3, // 重试次数
  HEALTH_CHECK_TIMEOUT: 10000, // 健康检查超时时间
  
  // 测试配置
  TEST_REQUEST: {
    content: '测试消息',
    max_tokens: 10,
    temperature: 0.7
  }
}

// 获取AI接口完整地址
export const getAIApiUrl = (endpoint: string = '') => {
  return `${AI_CONFIG.BASE_URL}${endpoint}`
}

// 获取聊天接口地址
export const getChatApiUrl = () => {
  return getAIApiUrl('chat')
}

// 获取测试配置
export const getTestConfig = () => {
  return AI_CONFIG.TEST_REQUEST
} 