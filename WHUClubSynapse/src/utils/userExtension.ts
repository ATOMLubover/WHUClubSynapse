import type { User, UserExtension, UserPreferences } from '@/types'

/**
 * 解析用户extension字段（JSON字符串）为UserExtension对象
 */
export function parseUserExtension(extension?: string): UserExtension {
  if (!extension) {
    return {}
  }

  try {
    return JSON.parse(extension) as UserExtension
  } catch (error) {
    console.warn('解析用户扩展信息失败:', error)
    return {}
  }
}

/**
 * 将UserExtension对象序列化为JSON字符串
 */
export function stringifyUserExtension(extension: UserExtension): string {
  if (!extension || Object.keys(extension).length === 0) {
    return ''
  }

  try {
    return JSON.stringify(extension)
  } catch (error) {
    console.warn('序列化用户扩展信息失败:', error)
    return ''
  }
}

/**
 * 从User对象中提取扩展信息
 */
export function extractUserExtension(user: User): UserExtension {
  // 处理preferences：如果是完整的UserPreferences对象，需要简化存储
  let simplifiedPreferences = undefined
  if (user.preferences) {
    simplifiedPreferences = {
      interestedCategories: user.preferences.interestedCategories?.map(cat => 
        typeof cat === 'object' ? cat.category_id : cat
      ) || [],
      emailNotifications: user.preferences.emailNotifications,
      applicationNotifications: user.preferences.applicationNotifications,
      activityNotifications: user.preferences.activityNotifications,
      profilePublic: user.preferences.profilePublic,
      showJoinedClubs: user.preferences.showJoinedClubs
    }
  }

  return {
    realName: user.realName,
    studentId: user.studentId,
    major: user.major,
    bio: user.bio,
    preferences: simplifiedPreferences,
    tags: user.tags,
    phone: user.phone
  }
}

/**
 * 将扩展信息合并到User对象中
 */
export function mergeUserExtension(user: User, extension: UserExtension): User {
  // 如果extension中有preferences，需要转换回UserPreferences格式
  let mergedPreferences = user.preferences
  if (extension.preferences) {
    // 这里需要引入分类数据来重建interestedCategories
    // 临时处理：保持简化格式，由组件层面处理转换
    mergedPreferences = extension.preferences as any
  }

  return {
    ...user,
    realName: extension.realName,
    studentId: extension.studentId,
    major: extension.major,
    bio: extension.bio,
    tags: extension.tags,
    phone: extension.phone,
    preferences: mergedPreferences
  }
}

/**
 * 处理从后端获取的用户数据，自动解析extension字段
 */
export function processUserFromBackend(userData: any): User {
  const extension = parseUserExtension(userData.extension)
  return mergeUserExtension(userData, extension)
}

/**
 * 准备发送到后端的用户数据，自动处理extension字段
 */
export function prepareUserForBackend(user: User): any {
  console.log('prepareUserForBackend 输入用户数据:', user)
  console.log('user.tags:', user.tags)
  console.log('user.preferences:', user.preferences)
  
  const extension = extractUserExtension(user)
  console.log('提取的extension:', extension)
  
  const extensionString = stringifyUserExtension(extension)
  console.log('序列化的extension:', extensionString)
  
  // 只保留必要的基础字段，明确排除密码和其他敏感字段
  const result = {
    user_id: user.user_id,
    username: user.username,
    email: user.email,
    avatar_url: user.avatar_url,
    role: user.role,
    password: "", // 🔧 修复：密码字段传空字符串，让后端知道不修改密码
    extension: extensionString
  }
  
  console.log('prepareUserForBackend 最终结果:', result)
  return result
} 