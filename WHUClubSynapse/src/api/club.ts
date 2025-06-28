//TODO: 需要改为与后端交互的api
import request from '@/utils/request'
import type { Club, PaginatedData, SearchParams, ApiResponse, Application } from '@/types'
import { useConfigStore } from '@/stores/config'
import { useAuthStore } from '@/stores/auth'
import * as mockClub from './mock/club'
import { mockGetClubPosts, mockGetClubPostDetail, mockGetClubPostReplies, mockCreateClubPost, mockReplyClubPost } from './mock/club'

// 获取动态配置
const getIsUsingMockAPI = () => {
  const configStore = useConfigStore()
  return configStore.isUsingMockAPI
}

// 获取社团列表
export const getClubList = async (
  params: SearchParams = {},
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetClubList(params)
  }

  const authStore = useAuthStore()
  const queryParams = new URLSearchParams()

  if (params.keyword) {
    queryParams.append('keyword', params.keyword)
  }
  if (params.category) {
    queryParams.append('category', params.category)
  }
  if (params.sortBy) {
    queryParams.append('sortBy', params.sortBy)
  }
  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  if (params.pageSize) {
    queryParams.append('pageSize', params.pageSize.toString())
  }
  
  // 添加登录状态参数，告诉后端是否需要返回用户相关的数据
  if (authStore.isLoggedIn) {
    queryParams.append('includeUserData', 'true')
  }

  const queryString = queryParams.toString()
  const url = queryString ? `/clubs?${queryString}` : '/clubs'

  // 根据登录状态使用不同的请求头
  const config = authStore.isLoggedIn ? {
    headers: {
      'Authorization': `Bearer ${authStore.token}`,
    }
  } : {}

  return await request.get(url, config)
}

// 获取社团详情
export const getClubDetail = async (id: string): Promise<{ data: ApiResponse<Club> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockGetClubDetail(id)
    : await request.get(`/clubs/${id}`)
}

// 获取热门社团
export const getHotClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockGetHotClubs(limit)
    : await request.get(`/clubs/hot?limit=${limit}`)
}

// 获取最新社团
export const getLatestClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockGetLatestClubs(limit)
    : await request.get(`/clubs/latest?limit=${limit}`)
}

// 获取推荐社团
export const getRecommendedClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockGetRecommendedClubs(limit)
    : await request.get(`/clubs/recommended?limit=${limit}`)
}

// 搜索社团
export const searchClubs = async (
  keyword: string,
  params: Partial<SearchParams> = {},
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  return getClubList({ ...params, keyword })
}

// 获取社团分类统计
export const getClubCategories = async (): Promise<{
  data: ApiResponse<Record<string, number>>
}> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockGetClubCategories()
    : await request.get('/clubs/categories')
}

// 申请加入社团
export const applyToClub = async (data: {
  clubId: string
  reason: string
}): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockApplyToClub(data)
    : await request.post('/clubs/apply', data)
}

// 撤销申请
export const cancelApplication = async (applicationId: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockCancelApplication(applicationId)
    : await request.delete(`/clubs/applications/${applicationId}`)
}

// 收藏社团
export const favoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockFavoriteClub(clubId)
    : await request.post(`/clubs/${clubId}/favorite`)
}

// 取消收藏社团
export const unfavoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockUnfavoriteClub(clubId)
    : await request.delete(`/clubs/${clubId}/favorite`)
}

// 获取用户收藏的社团
export const getFavoriteClubs: (
  params?: {
    page?: number
    pageSize?: number
  }
) => Promise<{ data: ApiResponse<PaginatedData<Club>> }> = async (
  params = {},
) => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetFavoriteClubs(params)
  }

  const queryParams = new URLSearchParams()

  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  if (params.pageSize) {
    queryParams.append('pageSize', params.pageSize.toString())
  }

  const queryString = queryParams.toString()
  const url = queryString ? `/user/favorites?${queryString}` : '/user/favorites'

  return await request.get(url)
}

// 获取用户申请记录
export const getUserApplications = async (
  params: {
    page?: number
    pageSize?: number
    status?: string
    category?: string
    keyword?: string
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<Application>> }> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetUserApplications(params)
  }

  const queryParams = new URLSearchParams()

  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  if (params.pageSize) {
    queryParams.append('pageSize', params.pageSize.toString())
  }
  if (params.status) {
    queryParams.append('status', params.status)
  }

  const queryString = queryParams.toString()
  const url = queryString ? `/user/applications?${queryString}` : '/user/applications'

  return await request.get(url)
}

// 创建社团（管理员功能）
export const createClub = async (data: {
  name: string
  description: string
  category: string
  maxMembers: number
  tags: string[]
  coverImage?: string
}): Promise<{ data: ApiResponse<Club> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockCreateClub(data)
    : await request.post('/clubs', data)
}

// 更新社团信息（社团管理员功能）
export const updateClub = async (
  id: string,
  data: Partial<{
    name: string
    description: string
    category: string
    maxMembers: number
    tags: string[]
    coverImage: string
    introduction: string
    contactInfo: {
      qq?: string
      wechat?: string
      email?: string
      phone?: string
      address?: string
    }
    announcements: string[]
    requirements: string
    meetingTime: string
    meetingLocation: string
    activities: Array<{
      id: number
      title: string
      description: string
      time: string
    }>
  }>,
): Promise<{ data: ApiResponse<Club> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockUpdateClub(id, data)
    : await request.put(`/clubs/${id}`, data)
}

// 删除社团（管理员功能）
export const deleteClub = async (id: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockDeleteClub(id)
    : await request.delete(`/clubs/${id}`)
}

// 获取用户已加入的社团
export const getJoinedClubs = async (
  params: {
    page?: number
    pageSize?: number
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetJoinedClubs(params)
  }

  const queryParams = new URLSearchParams()

  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  if (params.pageSize) {
    queryParams.append('pageSize', params.pageSize.toString())
  }

  const queryString = queryParams.toString()
  const url = queryString ? `/user/joined-clubs?${queryString}` : '/user/joined-clubs'

  return await request.get(url)
}

// 获取用户管理的社团
export const getManagedClubs = async (
  params: {
    page?: number
    pageSize?: number
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetManagedClubs(params)
  }

  const queryParams = new URLSearchParams()

  if (params.page) {
    queryParams.append('page', params.page.toString())
  }
  if (params.pageSize) {
    queryParams.append('pageSize', params.pageSize.toString())
  }

  const queryString = queryParams.toString()
  const url = queryString ? `/user/managed-clubs?${queryString}` : '/user/managed-clubs'

  return await request.get(url)
}

// 退出社团
export const quitClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockQuitClub(clubId)
    : await request.delete(`/user/joined-clubs/${clubId}`)
}

export const getClubPosts = mockGetClubPosts
export const getClubPostDetail = mockGetClubPostDetail
export const getClubPostReplies = mockGetClubPostReplies
export const createClubPost = mockCreateClubPost
export const replyClubPost = mockReplyClubPost
