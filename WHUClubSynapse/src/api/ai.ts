import { AI_CONFIG, getChatApiUrl } from '@/config/ai'
import type { ClubRecommendRequest, ClubRecommendResponse } from '@/types'

// 基础错误类
export class AIServiceError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: string
  ) {
    super(message)
    this.name = 'AIServiceError'
  }
}

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

export interface StreamCallbacks {
  onToken?: (token: string) => void
  onError?: (error: Error) => void
  onFinish?: () => void
}

// 统一的请求处理函数
async function makeAIRequest<T>(
  url: string,
  data: any,
  options: {
    stream?: boolean
    timeout?: number
    callbacks?: StreamCallbacks
  } = {}
): Promise<T> {
  const token = localStorage.getItem('token')
  if (!token) {
    throw new AIServiceError('未找到认证token')
  }

  const { stream = false, timeout = AI_CONFIG.REQUEST_TIMEOUT, callbacks } = options

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': stream ? 'text/event-stream' : 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data),
      signal: AbortSignal.timeout(timeout)
    })

    // 处理错误响应
    if (!response.ok) {
      const errorText = await response.text()
      throw new AIServiceError(
        `请求失败: ${errorText}`,
        response.status,
        errorText
      )
    }

    // 处理流式响应
    if (stream && response.body && callbacks) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonData = line.slice(5)
              try {
                const parsed = JSON.parse(jsonData)
                if (parsed.token) {
                  callbacks.onToken?.(parsed.token)
                }
              } catch (e) {
                // 如果不是JSON，直接发送原始数据
                callbacks.onToken?.(jsonData)
              }
            }
          }
        }
        callbacks.onFinish?.()
      } catch (error) {
        callbacks.onError?.(error instanceof Error ? error : new Error(String(error)))
        reader.cancel()
      }
      return {} as T // 流式响应不返回数据
    }

    // 处理普通JSON响应
    const responseData = await response.json()
    return responseData as T
  } catch (error) {
    if (error instanceof AIServiceError) {
      throw error
    }
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new AIServiceError('请求超时')
    }
    throw new AIServiceError(
      error instanceof Error ? error.message : '未知错误'
    )
  }
}

// 修改chatWithAI函数支持流式响应
export const chatWithAI = async (
  requestData: ChatRequest,
  callbacks?: StreamCallbacks
): Promise<ChatResponse> => {
  const url = getChatApiUrl()
  console.log('AI聊天请求URL:', url)
  console.log('AI聊天请求数据:', requestData)

  const response = await makeAIRequest<ChatResponse>(
    url,
    {
      ...requestData,
      model: requestData.model || AI_CONFIG.DEFAULT_MODEL,
      max_tokens: requestData.max_tokens || AI_CONFIG.DEFAULT_MAX_TOKENS,
      temperature: requestData.temperature || AI_CONFIG.DEFAULT_TEMPERATURE,
      top_p: requestData.top_p || AI_CONFIG.DEFAULT_TOP_P,
      system_prompt: requestData.system_prompt || 'You are a helpful assistant.'
    },
    {
      stream: requestData.stream,
      callbacks
    }
  )

  console.log('AI聊天响应数据:', response)
  return response
}

// AI审核助手接口类型
export interface ApplicationScreeningRequest {
  applicant_data: {
    name: string
    major: string
    skills: string[]
    experience: string
  }
  application_reason: string
  required_conditions: string[]
  club_name: string
}

// 尝试不同的字段名格式
export interface ApplicationScreeningRequestAlt {
  applicantData: {
    name: string
    major: string
    skills: string[]
    experience: string
  }
  applicationReason: string
  requiredConditions: string[]
  clubName: string
}

export interface ApplicationScreeningResponse {
  summary: string
  suggestion: string
}

// AI审核助手API
export const screenApplication = async (requestData: ApplicationScreeningRequest): Promise<ApplicationScreeningResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}screen_application`
    console.log('申请筛选请求URL:', url)
    console.log('AI审核助手请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('AI审核助手响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('AI审核助手请求失败:', errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('AI审核助手响应数据:', data)
    return data
  } catch (error) {
    console.error('AI审核助手请求失败:', error)
    throw error
  }
}

// AI氛围透视镜接口类型
export interface ClubAtmosphereRequest {
  communication_content: string
}

export interface ClubAtmosphereResponse {
  atmosphere_tags: string[]
  culture_summary: string
}

// AI氛围透视镜API
export const analyzeClubAtmosphere = async (requestData: ClubAtmosphereRequest): Promise<ClubAtmosphereResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}club_atmosphere`
    console.log('AI氛围透视镜请求URL:', url)
    console.log('AI氛围透视镜请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('AI氛围透视镜响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('AI氛围透视镜HTTP错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('AI氛围透视镜响应数据:', data)
    return data
  } catch (error) {
    console.error('AI氛围透视镜请求失败:', error)
    throw error
  }
}

// 财务记账接口类型
export interface FinancialBookkeepingRequest {
  natural_language_input: string
  club_name: string
}

export interface FinancialEntry {
  description: string
  amount: number
  category: string
  payer: string
  type: 'income' | 'expense'
}

export interface FinancialBookkeepingResponse {
  parsed_entries: FinancialEntry[]
  confirmation_message: string
  original_input: string
}

// 财务记账API
export const financialBookkeeping = async (requestData: FinancialBookkeepingRequest): Promise<FinancialBookkeepingResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}financial_bookkeeping`
    console.log('财务记账请求URL:', url)
    console.log('财务记账请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('财务记账响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('财务记账HTTP错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('财务记账响应数据:', data)
    return data
  } catch (error) {
    console.error('财务记账请求失败:', error)
    throw error
  }
}

// 财务报表接口类型
export interface FinancialReportRequest {
  club_name: string
}

export interface FinancialReportResponse {
  report_summary: string
  expense_breakdown: Record<string, number>
  income_breakdown: Record<string, number>
}

// 生成财务报表API
export const generateFinancialReport = async (requestData: FinancialReportRequest): Promise<FinancialReportResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}generate_financial_report`
    console.log('生成财务报表请求URL:', url)
    console.log('生成财务报表请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('生成财务报表响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('生成财务报表HTTP错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('生成财务报表响应数据:', data)
    return data
  } catch (error) {
    console.error('生成财务报表请求失败:', error)
    throw error
  }
}

// AI社团介绍生成接口类型
export interface ContentGenerationRequest {
  content?: string
  style?: string
  target_people?: string
}

export interface ContentGenerationResponse {
  generated_text: string
}

// AI公告内容生成接口类型
export interface AnnouncementGenerationRequest {
  content?: string
  style?: string
  expection?: string
}

export interface AnnouncementGenerationResponse {
  generated_text: string
}

// AI社团介绍生成API
export const generateClubIntroduction = async (requestData: ContentGenerationRequest): Promise<ContentGenerationResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}introduction`
    console.log('AI社团介绍生成请求URL:', url)
    console.log('AI社团介绍生成请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('AI社团介绍生成响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('AI社团介绍生成HTTP错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('AI社团介绍生成响应数据:', data)
    return data
  } catch (error) {
    console.error('AI社团介绍生成请求失败:', error)
    throw error
  }
}

// AI公告内容生成API
export const generateAnnouncementContent = async (requestData: AnnouncementGenerationRequest): Promise<AnnouncementGenerationResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}content`
    console.log('AI公告内容生成请求URL:', url)
    console.log('AI公告内容生成请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('AI公告内容生成响应状态:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('AI公告内容生成HTTP错误:', response.status, errorText)
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
    }

    const data = await response.json()
    console.log('AI公告内容生成响应数据:', data)
    return data
  } catch (error) {
    console.error('AI公告内容生成请求失败:', error)
    throw error
  }
}

// AI智能推荐社团
export const getClubRecommendations = async (request: ClubRecommendRequest): Promise<ClubRecommendResponse> => {
  try {
    const url = `${AI_CONFIG.BASE_URL}club_recommend`
    console.log('AI智能推荐社团请求URL:', url)
    console.log('AI智能推荐社团请求数据:', request)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(request),
      signal: AbortSignal.timeout(AI_CONFIG.REQUEST_TIMEOUT)
    })

    console.log('AI智能推荐社团响应状态:', response.status)
    console.log('AI智能推荐社团响应头:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      const errorText = await response.text()
      console.error('AI智能推荐社团HTTP错误:', response.status, errorText)
      throw new Error(`HTTP ${response.status}: ${errorText}`)
    }

    const data = await response.json()
    console.log('AI智能推荐社团响应数据:', data)
    return data
  } catch (error) {
    console.error('AI智能推荐社团请求失败:', error)
    throw error
  }
}

// 修改checkAIStatus函数使用统一的请求处理
export const checkAIStatus = async (): Promise<boolean> => {
  try {
    const testRequest: ChatRequest = {
      messages: [
        {
          role: 'user',
          content: AI_CONFIG.TEST_REQUEST.content
        }
      ],
      max_tokens: AI_CONFIG.TEST_REQUEST.max_tokens,
      temperature: AI_CONFIG.TEST_REQUEST.temperature,
      stream: false
    }

    await makeAIRequest(
      getChatApiUrl(),
      testRequest,
      { timeout: AI_CONFIG.HEALTH_CHECK_TIMEOUT }
    )
    
    console.log('AI状态检查：服务正常运行')
    return true
  } catch (error) {
    console.warn('AI状态检查失败:', error instanceof Error ? error.message : error)
    return false
  }
} 