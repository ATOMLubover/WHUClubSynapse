// JWT 解析工具函数
export interface JWTPayload {
  user_id: number
  role: string
  exp?: number  // 过期时间
  iat?: number  // 签发时间
}

/**
 * 解析JWT token获取payload数据
 * @param token JWT token字符串
 * @returns 解析后的payload数据，如果解析失败返回null
 */
export function parseJWT(token: string): JWTPayload | null {
  try {
    // 移除Bearer前缀（如果存在）
    const cleanToken = token.replace(/^Bearer\s+/i, '')
    
    // JWT由三部分组成，用.分隔：header.payload.signature
    const parts = cleanToken.split('.')
    if (parts.length !== 3) {
      console.error('JWT格式错误：token应该包含3个部分')
      return null
    }

    // 解码payload部分（第二部分）
    const payload = parts[1]
    
    // JWT使用base64url编码，需要处理padding
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const paddedBase64 = base64.padEnd(base64.length + (4 - base64.length % 4) % 4, '=')
    
    // 解码并解析JSON
    const decodedPayload = JSON.parse(atob(paddedBase64))
    
    // 根据后端JWT结构，提取用户信息
    // 后端使用的是嵌套结构：{ Inner: { UserId, Role }, exp, iat }
    const userInfo = decodedPayload.Inner || decodedPayload
    
    return {
      user_id: userInfo.UserId || userInfo.user_id,
      role: userInfo.Role || userInfo.role,
      exp: decodedPayload.exp,
      iat: decodedPayload.iat
    }
  } catch (error) {
    console.error('JWT解析失败:', error)
    return null
  }
}

/**
 * 从localStorage中获取token并解析获取user_id
 * @returns user_id，如果获取失败返回null
 */
export function getUserIdFromToken(): number | null {
  const token = localStorage.getItem('token')
  if (!token) {
    console.warn('未找到token')
    return null
  }

  const payload = parseJWT(token)
  return payload?.user_id || null
}

/**
 * 从localStorage中获取token并解析获取用户角色
 * @returns 用户角色，如果获取失败返回null
 */
export function getUserRoleFromToken(): string | null {
  const token = localStorage.getItem('token')
  if (!token) {
    console.warn('未找到token')
    return null
  }

  const payload = parseJWT(token)
  return payload?.role || null
}

/**
 * 检查token是否已过期
 * @param token JWT token字符串，如果不传则使用localStorage中的token
 * @returns true表示已过期，false表示未过期
 */
export function isTokenExpired(token?: string): boolean {
  const targetToken = token || localStorage.getItem('token')
  if (!targetToken) {
    return true
  }

  const payload = parseJWT(targetToken)
  if (!payload?.exp) {
    return true
  }

  // exp是秒级时间戳，需要转换为毫秒
  const expirationTime = payload.exp * 1000
  const currentTime = Date.now()
  
  return currentTime >= expirationTime
}

/**
 * 获取token的所有用户信息
 * @returns 完整的用户信息，如果解析失败返回null
 */
export function getUserInfoFromToken(): JWTPayload | null {
  const token = localStorage.getItem('token')
  if (!token) {
    console.warn('未找到token')
    return null
  }

  return parseJWT(token)
} 