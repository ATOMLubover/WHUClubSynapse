import { AI_CONFIG, getChatApiUrl, getStatusApiUrl } from '@/config/ai'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  model?: string
  max_tokens?: number
  temperature?: number
  top_p?: number
  stream?: boolean
  system_prompt?: string
}

export interface ChatResponse {
  response: string
  model: string
  usage?: Record<string, any>
}

export const chatWithAI = async (requestData: ChatRequest): Promise<ChatResponse> => {
  try {
    console.log('AI聊天请求URL:', getChatApiUrl())
    console.log('AI聊天请求数据:', requestData)
    
    const response = await fetch(getChatApiUrl(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        messages: requestData.messages,
        model: requestData.model || AI_CONFIG.DEFAULT_MODEL,
        max_tokens: requestData.max_tokens || AI_CONFIG.DEFAULT_MAX_TOKENS,
        temperature: requestData.temperature || AI_CONFIG.DEFAULT_TEMPERATURE,
        top_p: requestData.top_p || AI_CONFIG.DEFAULT_TOP_P,
        stream: requestData.stream || false,
        system_prompt: requestData.system_prompt || 'You are a helpful assistant.'
      }),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('AI聊天响应状态:', response.status)
    console.log('AI聊天响应头:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      const errorText = await response.text()
      console.error('AI聊天HTTP错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('AI聊天响应数据:', data)
    return data
  } catch (error) {
    console.error('AI聊天请求失败:', error)
    throw error
  }
}

// 检查AI服务状态
export const checkAIStatus = async (): Promise<boolean> => {
  // 尝试多个可能的状态检查端点
  const statusEndpoints = ['/status', '/health', '/ping', '']
  
  for (const endpoint of statusEndpoints) {
    try {
      const url = `${AI_CONFIG.BASE_URL}${endpoint}`
      console.log(`尝试检查AI服务状态，URL: ${url}`)
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: AbortSignal.timeout(10000) // 10秒超时
      })
      
      console.log(`AI状态检查响应状态 (${endpoint}):`, response.status)
      console.log(`AI状态检查响应头 (${endpoint}):`, Object.fromEntries(response.headers.entries()))
      
      if (!response.ok) {
        console.error(`AI状态检查HTTP错误 (${endpoint}):`, response.status)
        continue // 尝试下一个端点
      }
      
      const text = await response.text()
      console.log(`AI状态检查响应内容 (${endpoint}):`, text.substring(0, 200) + '...')
      
      // 检查是否返回HTML而不是JSON
      if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
        console.error(`AI状态检查返回HTML而不是JSON (${endpoint})`)
        continue // 尝试下一个端点
      }
      
      // 尝试解析JSON
      try {
        const data = JSON.parse(text)
        console.log(`AI状态检查解析结果 (${endpoint}):`, data)
        
        // 检查不同的状态字段
        if (data.status === 'running' || data.status === 'ok' || data.status === 'healthy') {
          return true
        }
        
        // 如果没有状态字段，但有其他字段，也认为服务可用
        if (Object.keys(data).length > 0) {
          console.log(`AI服务返回有效响应 (${endpoint}):`, data)
          return true
        }
      } catch (parseError) {
        console.error(`AI状态检查JSON解析失败 (${endpoint}):`, parseError)
        // 如果不是JSON，检查是否是简单的文本响应
        if (text.trim().toLowerCase().includes('ok') || text.trim().toLowerCase().includes('running')) {
          console.log(`AI服务返回简单文本响应 (${endpoint}):`, text)
          return true
        }
      }
      
    } catch (error) {
      console.error(`检查AI服务状态失败 (${endpoint}):`, error)
      continue // 尝试下一个端点
    }
  }
  
  console.error('所有AI状态检查端点都失败')
  return false
} 