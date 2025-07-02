// 用户类型
export interface User {
  user_id: number
  username: string
  email: string
  avatar_url: string
  role: 'user' | 'admin'
  last_active: string
  // 扩展字段（前端使用）
  id?: number // 兼容现有代码
  studentId?: string
  realName?: string
  major?: string
  phone?: string
  createdAt?: string
  emailVerified?: string
  phoneVerified?: string
  bio?: string
  status?: 'active' | 'disabled'
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
  // 新增字段用于编辑
  isNew?: boolean // 标记是否为新增的动态
}

// 社团类型
export interface Club {
  club_id: string
  club_name: string
  desc: string
  logo_url: string
  category: number
  created_at: string
  member_count: number
  leader_id?: string
  //以上是必须包含的，以下是可选的
  adminId?: string
  adminName?: string
  maxMembers?: number
  tags: string[]
  isHot?: boolean
  isFavorite?: boolean
  status?: 'pending' | 'joined' |  'not_applied'
  status_for_create?: 'pending' | 'approved' | 'rejected'
  updatedAt?: string
  activities?: Activity[]
  location?: string
  qq?: string
  details?: string
  // 新增字段用于编辑功能
  introduction?: string // 社团详细介绍
  contactInfo?: {
    qq?: string
    wechat?: string
    email?: string
    phone?: string
    address?: string
  }
  announcements?: string[] // 社团公告
  requirements?: string // 加入要求
  meetingTime?: string // 例会时间
  meetingLocation?: string // 例会地点
  posts?: ClubPost[]
  members?: ClubMember[]
}

// 社团分类
export interface ClubCategory {
  category_id: number
  name: string
  count?: number
}


// 收藏记录
export interface Favorite {
  id: string
  userId: string
  clubId: string
  createdAt: string
}

// API响应类型（保持原有，但很多接口不使用这个格式）
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
  category?: number | ''
  sortBy?: 'hot' | 'time' | 'members'
  page?: number
  pageSize?: number
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求（根据接口文档）
export interface RegisterRequest {
  username: string
  email: string
  password: string  // 前端加密后的密码
  vrfcode: string  // 邮箱收到的 4 位验证码
  realName?: string
  studentId?: string
  major?: string
  phone?: string
}

// 发送验证码请求
export interface VerifyEmailRequest {
  email: string
}

// 用户列表查询参数（管理员接口）
export interface UserListParams {
  offset: number  // 分页起始位置
  num: number     // 每页数量
}

// 注册成功响应
export interface RegisterResponse {
  user_id: number
  username: string
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

// 社团帖子类型
export interface ClubPost {
  post_id?: string
  club_id?: string
  title: string
  created_at?: string
  comment_count?: number
  author_id?: number
  content_url?: string

  content?: string
  authorName?: string
  authorAvatar?: string
}

// 帖子回复类型
export interface ClubPostReply {
  id: string
  postId: string
  authorId: number
  authorName: string
  authorAvatar?: string
  content: string
  createdAt: string
}

// 社团成员类型
export interface ClubMember {
  member_id: string
  user_id: string
  club_id: string
  joined_at: string
  role_in_club: 'admin' | 'member' // 在社团中的角色
  last_active: string

  username?: string
  realName?: string
  avatar_url?: string
  status?: 'active' | 'inactive'
  studentId?: string
  major?: string
  phone?: string
  email?: string
}

// 社团申请类型
export interface ClubApplication {
  appli_id: string
  reject_reason: string
  club_id: string
  reason: string
  applied_at: string
  reviewed_at: string
  status: string
  club:Club
}

// 用户创建的社团申请记录
export interface ClubCreatedApplication {
  appli_id: number
  applied_at: string  // RFC3339格式
  reject_reason: string
  reviewed_at: string  // RFC3339格式
  club_id:number
  club?:Club
}

// 社团创建申请类型
export interface ClubCreationApplication {
  id: string
  userId: string
  username: string
  realName?: string
  avatar_url: string
  clubName: string
  description: string
  category: number
  maxMembers: number
  tags: string[]
  coverImage?: string
  requirements: string
  introduction?: string
  contactInfo?: {
    qq?: string
    wechat?: string
    email?: string
    phone?: string
    address?: string
  }
  meetingTime?: string
  meetingLocation?: string
  status: 'pending' | 'approved' | 'rejected'
  applyTime: string
  reviewTime?: string
  reviewerId?: string
  reviewerName?: string
  rejectReason?: string
  studentId?: string
  major?: string
  phone?: string
  email?: string
}

// 申请审核请求类型
export interface ApplicationReviewRequest {
  applicationId: string
  action: 'approve' | 'reject'
  reason?: string // 拒绝时需要提供原因
}

// AI智能搜索相关类型
export interface SmartSearchRequest {
  query: string
}

export interface SmartSearchSource {
  id: string
  content: string
  metadata: {
    source: string
    page: number
  }
}

export interface SmartSearchResponse {
  answer: string
  source: SmartSearchSource[]
}

export interface SmartSearchError {
  detail: string
}

// 侧边栏对话相关类型
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

export interface SideChatRequest {
  query: string
  history: ChatMessage[]
}

export interface SideChatResponse {
  answer: string
  source: SmartSearchSource[]
}

// AI智能推荐社团相关类型
export interface ClubRecommendRequest {
  User_name: string
  User_description: string
  User_tags: string[]
  User_major: string
}

export interface ClubInfo {
  club_name: string
  description: string
  tags: string[]
  recommend_reason: string
}

export interface ClubRecommendResponse {
  Summary_text: string
  Recommend_club_list: ClubInfo[]
}
