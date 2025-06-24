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
  status: 'active' | 'inactive' | 'pending'
  createdAt: string
  updatedAt: string
}

// 社团分类
//TODO: 需要从后端获取
export type ClubCategory = '学术科技' | '文艺体育' | '志愿服务' | '创新创业' | '其他'

// 申请记录
export interface Application {
  id: string
  userId: string
  clubId: string
  clubName: string
  status: 'pending' | 'approved' | 'rejected'
  reason?: string
  applyReason: string
  createdAt: string
  reviewedAt?: string
  reviewerId?: string
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
