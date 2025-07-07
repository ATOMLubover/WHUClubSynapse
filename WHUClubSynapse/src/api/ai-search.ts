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
  return true;
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5秒超时

    // 获取JWT token
    const jwtToken = localStorage.getItem('token')
    if (!jwtToken) {
      throw new Error('未找到认证token')
    }

    const response = await fetch(getHealthCheckURL(), {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwtToken}`
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
  signal,
  onSource,
  onToken,
  onEnd,
  onError,
}: {
  url: string
  body: any
  headers: Record<string, string>
  signal?: AbortSignal
  onSource?: (sources: any[]) => void
  onToken?: (token: string) => void
  onEnd?: () => void
  onError?: (err: any) => void
}) {
  let reader: ReadableStreamDefaultReader | null = null
  let waitingMessageInterval: number | null = null
  let waitCount = 0
  
  try {
    // 获取JWT token
    const jwtToken = localStorage.getItem('token')
    if (!jwtToken) {
      throw new Error('未找到认证token')
    }

    // 合并headers，添加Authorization
    const finalHeaders = {
      ...headers,
      'Authorization': `Bearer ${jwtToken}`
    }

    const resp = await fetch(url, {
      method: 'POST',
      headers: finalHeaders,
      body: JSON.stringify(body),
      signal
    })
    
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
    }
    
    if (!resp.body) throw new Error('No response body')
    reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    let isEnded = false
    let eventType = ''
    let completeResponse = '' // 用于存储完整响应
    
    // 设置等待消息的定时器
    waitingMessageInterval = setInterval(() => {
      waitCount++
      //console.log(`等待end标签中...已等待${waitCount}秒`)
    }, 1000)
    
    while (!isEnded) {
      const { value, done } = await reader.read()
      
      if (value) {
        buffer += decoder.decode(value, { stream: true })
        let lines = buffer.split('\n')
        buffer = lines.pop() || ''
        
        // 处理每一行数据
        for (const line of lines) {
          const trimmedLine = line.trim()
          if (!trimmedLine) continue
          
          if (trimmedLine.startsWith('event:')) {
            eventType = trimmedLine.replace('event:', '').trim()
            // 检查是否是end事件
            if (eventType === 'end') {
              console.log('收到end事件')
              isEnded = true
              break
            }
          } else if (trimmedLine.startsWith('data:')) {
            const data = trimmedLine.replace('data:', '').trim()
            if (!data) continue
            
            try {
              if (eventType === 'source') {
                const parsedData = JSON.parse(data)
                await onSource?.(parsedData)
              } else if (eventType === 'token') {
                const parsedData = JSON.parse(data)
                let token = parsedData.token || parsedData.content || parsedData
                if (typeof token !== 'string') {
                  token = String(token)
                }
                console.log('Token:', token)
                completeResponse += token
                await onToken?.(token)
              } else if (eventType === 'error') {
                const parsedData = JSON.parse(data)
                throw new Error(parsedData.error || parsedData)
              }
            } catch (parseError) {
              console.error('解析数据时出错:', parseError)
              throw parseError
            }
          }
        }
      }
      
      if (done && isEnded) {
        break
      }
    }

    // 清除等待消息的定时器
    if (waitingMessageInterval) {
      clearInterval(waitingMessageInterval)
    }

    console.log('流式传输完成，完整响应：')
    console.log(completeResponse)
    onEnd?.()
  } catch (err) {
    // 清除等待消息的定时器
    if (waitingMessageInterval) {
      clearInterval(waitingMessageInterval)
    }
    
    if (reader) {
      try {
        await reader.cancel()
      } catch (cancelError) {
        // 忽略reader关闭错误
      }
    }
    onError?.(err)
  }
}

export function smartSearchStream(
  request: SmartSearchRequest,
  { signal, onSource, onToken, onEnd, onError }: { 
    signal?: AbortSignal
    onSource?: (sources: any[]) => void
    onToken?: (token: string) => void
    onEnd?: () => void
    onError?: (err: any) => void 
  }
) {
  return fetchSSE({
    url: getSmartSearchURL(),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'X-API-Key': getApiKey()
    },
    body: request,
    signal,
    onSource,
    onToken,
    onEnd,
    onError
  })
}

export function sideChatStream(
  request: SideChatRequest,
  { signal, onSource, onToken, onEnd, onError }: { 
    signal?: AbortSignal
    onSource?: (sources: any[]) => void
    onToken?: (token: string) => void
    onEnd?: () => void
    onError?: (err: any) => void 
  }
) {
  return fetchSSE({
    url: getSideChatURL(),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'X-API-Key': getApiKey()
    },
    body: request,
    signal,
    onSource,
    onToken,
    onEnd,
    onError
  })
} 