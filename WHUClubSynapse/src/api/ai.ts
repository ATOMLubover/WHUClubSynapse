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
  try {
    const url = `${AI_CONFIG.BASE_URL}`
    console.log('检查AI服务状态，URL:', url)
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
      },
      signal: AbortSignal.timeout(10000) // 10秒超时
    })
    
    console.log('AI状态检查响应状态:', response.status)
    
    // 只要有任何响应就认为服务可用
    if (response.status >= 200 && response.status < 600) {
      console.log('AI服务可用')
      return true
    }
    
    console.error('AI状态检查失败:', response.status)
    return false
    
  } catch (error) {
    console.error('检查AI服务状态失败:', error)
    return false
  }
} 