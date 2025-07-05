import { AI_CONFIG, getChatApiUrl, getStatusApiUrl, getAIApiUrl } from '@/config/ai'
import type { ClubRecommendRequest, ClubRecommendResponse } from '@/types'

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

export const chatWithAI = async (requestData: ChatRequest): Promise<ChatResponse> => {
  try {
    console.log('AI聊天请求URL:', getChatApiUrl())
    console.log('AI聊天请求数据:', requestData)
    
    const token = localStorage.getItem('token')
    const response = await fetch(getChatApiUrl(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`
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
    const url = getStatusApiUrl()
    console.log('检查AI服务状态，URL:', url)
    
    const token = localStorage.getItem('token')
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': '*/*',
        'Authorization': `Bearer ${token}`
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