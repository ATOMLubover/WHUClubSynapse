// 用户类型
export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  role: 'student' | 'admin' | 'club_admin'
  studentId?: string
  realName: string
  college: string
  phone?: string
  createdAt: string
  emailVerified: string
  phoneVerified: string
  bio: string
  // 用户统计信息
  stats?: UserStats
  // 用户偏好设置
  preferences?: UserPreferences
  // 是否已完成偏好设置
  hasCompletedPreferences?: boolean
  tags?: string[] // 用户特质/爱好标签
}

// 用户统计信息类型
export interface UserStats {
  appliedClubs: number  // 申请的社团数量
  favoriteClubs: number // 收藏的社团数量
  joinedClubs: number   // 已加入的社团数量
  managedClubs: number  // 管理的社团数量
}

export interface Activity {
  id: number
  title: string
  description: string
  time: string
}

// 社团类型
export interface Club {
  id: string
  name: string
  description: string
  coverImage: string
  category: ClubCategory
  adminId: string
  adminName: string
  currentMembers: number
  maxMembers: number
  tags: string[]
  isHot: boolean
  isFavorite: boolean
  status: 'pending' | 'approved' | 'not_applied'
  createdAt: string
  updatedAt: string
  activities: Activity[]
  location: string
  qq: string
  details: string
}

// 社团分类
export type ClubCategory = '学术科技' | '文艺体育' | '志愿服务' | '创新创业' | '其他'

// 申请记录
export interface Application {
  id: string
  userId: string
  clubId: string
  clubName: string
  clubCoverImage: string
  status: 'pending' | 'approved' | 'rejected'
  reason?: string
  applyReason: string
  createdAt: string
  reviewedAt?: string
  reviewerId?: string
  clubCategory: string
  feedback?: string
}

// 收藏记录
export interface Favorite {
  id: string
  userId: string
  clubId: string
  createdAt: string
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页数据
export interface PaginatedData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// 搜索参数
export interface SearchParams {
  keyword?: string
  category?: ClubCategory | ''
  sortBy?: 'hot' | 'time' | 'members'
  page?: number
  pageSize?: number
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求
export interface RegisterRequest {
  username: string
  password: string
  email: string
  realName: string
  studentId: string
  college: string
  phone?: string
}

// 用户偏好设置类型
export interface UserPreferences {
  interestedCategories: ClubCategory[]
  emailNotifications: boolean
  applicationNotifications: boolean
  activityNotifications: boolean
  profilePublic: boolean
  showJoinedClubs: boolean
  tags?: string[] // 用户特质/爱好标签
}
