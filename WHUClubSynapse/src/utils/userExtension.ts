import type { User, UserExtension, UserPreferences } from '@/types'

/**
 * 解析用户extension字段
 * @param extension - 来自后端的extension字符串
 * @returns 解析后的用户扩展信息对象
 */
export function parseUserExtension(extension?: string): UserExtension {
  if (!extension) {
    return {}
  }

  try {
    const parsed = JSON.parse(extension)
    return parsed as UserExtension
  } catch (error) {
    console.warn('解析用户扩展信息失败:', error)
    return {}
  }
}

/**
 * 序列化用户扩展信息为JSON字符串
 * @param extension - 用户扩展信息对象
 * @returns JSON字符串
 */
export function stringifyUserExtension(extension: UserExtension): string {
  try {
    return JSON.stringify(extension)
  } catch (error) {
    console.warn('序列化用户扩展信息失败:', error)
    return '{}'
  }
}

/**
 * 从User对象中提取扩展信息
 * @param user - 用户对象
 * @returns 用户扩展信息对象
 */
export function extractUserExtension(user: Partial<User>): UserExtension {
  return {
    realName: user.realName,
    studentId: user.studentId,
    major: user.major,
    bio: user.bio,
    phone: user.phone,
    preferences: user.preferences,
    tags: user.tags,
    hasCompletedPreferences: user.hasCompletedPreferences,
  }
}

/**
 * 将解析后的扩展信息合并到User对象中
 * @param user - 原始用户对象
 * @param extension - 解析后的扩展信息
 * @returns 合并后的用户对象
 */
export function mergeUserExtension(user: User, extension: UserExtension): User {
  return {
    ...user,
    realName: extension.realName,
    studentId: extension.studentId,
    major: extension.major,
    bio: extension.bio,
    phone: extension.phone,
    preferences: extension.preferences,
    tags: extension.tags,
    hasCompletedPreferences: extension.hasCompletedPreferences,
  }
}

/**
 * 处理后端返回的用户信息，解析extension字段
 * @param user - 来自后端的用户对象
 * @returns 处理后的用户对象
 */
export function processUserFromBackend(user: User): User {
  if (!user.extension) {
    return user
  }

  const extension = parseUserExtension(user.extension)
  return mergeUserExtension(user, extension)
}

/**
 * 准备发送到后端的用户信息，序列化extension字段
 * @param user - 前端用户对象
 * @returns 准备发送的对象
 */
export function prepareUserForBackend(user: Partial<User>): {
  user_id?: number
  username?: string
  email?: string
  extension?: string
} {
  const extension = extractUserExtension(user)
  
  return {
    user_id: user.user_id,
    username: user.username,
    email: user.email,
    extension: stringifyUserExtension(extension),
  }
} 