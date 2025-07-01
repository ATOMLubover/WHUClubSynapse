import type { 
  SmartSearchRequest, 
  SmartSearchResponse, 
  SmartSearchError, 
  SmartSearchSource,
  SideChatRequest,
  SideChatResponse,
  ChatMessage
} from '@/types'
import { getSmartSearchURL, getSideChatURL, getHealthCheckURL, getApiKey, isAiSearchEnabled, isSideChatEnabled, isHealthCheckEnabled } from '@/config/ai-search'
import { config } from '@/config'


// AI服务健康检查
export const checkAiServiceHealth = async (): Promise<boolean> => {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5秒超时

    const response = await fetch(getHealthCheckURL(), {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    clearTimeout(timeoutId)

    if (response.ok) {
      return true
    } else {
      console.warn('AI服务健康检查失败:', response.status, response.statusText)
      return false
    }
  } catch (error) {
    console.error('AI服务健康检查异常:', error)
    return false
  }
}

// AI智能搜索API
export const smartSearch = async (request: SmartSearchRequest): Promise<SmartSearchResponse> => {
  if (!isAiSearchEnabled()) {
    throw new Error('AI搜索功能未启用')
  }

  // 检查AI服务是否可用
  const isHealthy = await checkAiServiceHealth()
  if (!isHealthy) {
    throw new Error('AI连接失败，请稍后重试')
  }

  try {
    const response = await fetch(getSmartSearchURL(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': getApiKey(),
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData: SmartSearchError = await response.json()
      throw new Error(errorData.detail || `AI连接失败，请稍后重试`)
    }

    const data: SmartSearchResponse = await response.json()
    return data
  } catch (error) {
    console.error('AI智能搜索请求失败:', error)
    throw new Error('AI连接失败，请稍后重试')
  }
}

// 侧边栏对话API
export const sideChat = async (request: SideChatRequest): Promise<SideChatResponse> => {
  if (!isSideChatEnabled()) {
    throw new Error('侧边栏对话功能未启用')
  }

  // 检查AI服务是否可用
  const isHealthy = await checkAiServiceHealth()
  if (!isHealthy) {
    throw new Error('AI连接失败，请稍后重试')
  }

  try {
    const response = await fetch(getSideChatURL(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': getApiKey(),
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const errorData: SmartSearchError = await response.json()
      throw new Error(errorData.detail || `AI连接失败，请稍后重试`)
    }

    const data: SideChatResponse = await response.json()
    return data
  } catch (error) {
    console.error('侧边栏对话请求失败:', error)
    throw new Error('AI连接失败，请稍后重试')
  }
} 