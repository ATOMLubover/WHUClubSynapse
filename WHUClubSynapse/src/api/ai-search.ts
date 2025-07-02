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

// 工具函数：fetch+SSE流式处理
export async function fetchSSE({
  url,
  body,
  headers,
  onSource,
  onToken,
  onEnd,
  onError,
}: {
  url: string
  body: any
  headers: Record<string, string>
  onSource?: (sources: any[]) => void
  onToken?: (token: string) => void
  onEnd?: () => void
  onError?: (err: any) => void
}) {
  try {
    const resp = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    })
    
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
    }
    
    if (!resp.body) throw new Error('No response body')
    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let isEnded = false
    let eventType = ''
    
    while (!isEnded) {
      const { value, done } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      let lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        const trimmedLine = line.trim()
        if (!trimmedLine) continue
        
        if (trimmedLine.startsWith('event:')) {
          eventType = trimmedLine.replace('event:', '').trim()
        } else if (trimmedLine.startsWith('data:')) {
          const data = trimmedLine.replace('data:', '').trim()
          if (!data) continue
          
          try {
            if (eventType === 'source') {
              const parsedData = JSON.parse(data)
              onSource && onSource(parsedData)
            } else if (eventType === 'token') {
              const parsedData = JSON.parse(data)
              console.log('解析的token数据:', parsedData)
              // 处理不同的token格式
              let token = parsedData.token || parsedData.content || parsedData
              console.log('提取的token:', token, '类型:', typeof token)
              // 确保token是字符串类型
              if (typeof token !== 'string') {
                console.log('token不是字符串，转换为字符串')
                token = String(token)
              }
              console.log('最终token:', token, '类型:', typeof token)
              if (typeof onToken === 'function') {
                onToken(token)
              } else {
                console.error('onToken不是函数:', onToken)
              }
            } else if (eventType === 'end') {
              isEnded = true
              onEnd && onEnd()
            } else if (eventType === 'error') {
              const parsedData = JSON.parse(data)
              onError && onError(parsedData.error || parsedData)
              isEnded = true
            }
          } catch (parseError) {
            console.error('SSE数据解析错误:', parseError, '原始数据:', data)
            // 对于token事件，尝试直接使用原始数据
            if (eventType === 'token') {
              let token = data
              console.log('catch块中的原始token数据:', token, '类型:', typeof token)
              // 确保token是字符串类型
              if (typeof token !== 'string') {
                console.log('catch块中token不是字符串，转换为字符串')
                token = String(token)
              }
              console.log('catch块中最终token:', token, '类型:', typeof token)
              if (typeof onToken === 'function') {
                onToken(token)
              } else {
                console.error('catch块中onToken不是函数:', onToken)
              }
            }
          }
        }
      }
    }
  } catch (err) {
    console.error('fetchSSE错误:', err)
    onError && onError(err)
  }
}

export function smartSearchStream(
  request: SmartSearchRequest,
  { onSource, onToken, onEnd, onError }: { onSource?: (sources: any[]) => void; onToken?: (token: string) => void; onEnd?: () => void; onError?: (err: any) => void }
) {
  return fetchSSE({
    url: getSmartSearchURL(),
    body: request,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': getApiKey(),
    },
    onSource,
    onToken,
    onEnd,
    onError,
  })
}

export function sideChatStream(
  request: SideChatRequest,
  { onSource, onToken, onEnd, onError }: { onSource?: (sources: any[]) => void; onToken?: (token: string) => void; onEnd?: () => void; onError?: (err: any) => void }
) {
  return fetchSSE({
    url: getSideChatURL(),
    body: request,
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': getApiKey(),
    },
    onSource,
    onToken,
    onEnd,
    onError,
  })
} 