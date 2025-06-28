//TODO: 需要改为与后端交互的api
import request from '@/utils/request'
import type { Club, PaginatedData, SearchParams, ApiResponse, Application, ClubMember, ClubApplication, ApplicationReviewRequest } from '@/types'
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
  if (params.page && params.pageSize) {
    const offset = (params.page - 1) * params.pageSize
    queryParams.append('offset', offset.toString())
    queryParams.append('num', params.pageSize.toString())
  }

  const queryString = queryParams.toString()
  const url = queryString ? `/api/club/list?${queryString}` : '/api/club/list'

  return await request.get(url)
}

// 获取社团详情
export const getClubDetail = async (id: string,post_num:number=5): Promise<{ data: ApiResponse<Club> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockGetClubDetail(id)
    : await request.get(`/clubs/${id}?post_num=${post_num}`)
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
    : await request.post(`/api/club/${data.clubId}/join`,{reason:data.reason})
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
  requirements: string
  category?: string
  maxMembers?: number
  tags?: string[]
  coverImage?: string
}): Promise<{ data: ApiResponse<Club> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockCreateClub(data)
    : await request.post('/api/club/create', data)
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

// 获取社团成员列表
export const getClubMembers = async (
  clubId: string,
  params: {
    page?: number
    pageSize?: number
    role?: string
    status?: string
    keyword?: string
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<ClubMember>> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟数据
    const mockMembers: ClubMember[] = [
      {
        member_id: '1',
        user_id: 'user1',
        club_id: clubId,
        username: 'admin_user',
        realName: '张三',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        role_in_club: 'admin',
        joined_at: '2024-01-01T00:00:00Z',
        status: 'active',
        studentId: '2021001001',
        major: '计算机科学与技术',
        phone: '13800138000',
        email: 'admin@example.com',
        last_active: '2024-01-01T00:00:00Z',
      },
      {
        member_id: '2',
        user_id: 'user2',
        club_id: clubId,
        username: 'member1',
        realName: '李四',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        role_in_club: 'member',
        joined_at: '2024-01-15T00:00:00Z',
        status: 'active',
        studentId: '2021001002',
        major: '软件工程',
        phone: '13800138001',
        email: 'member1@example.com',
        last_active: '2024-01-15T00:00:00Z',
      },
      {
        member_id: '3',
        user_id: 'user3',
        club_id: clubId,
        username: 'member2',
        realName: '王五',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        role_in_club: 'member',
        joined_at: '2024-02-01T00:00:00Z',
        status: 'active',
        studentId: '2021001003',
        major: '信息安全',
        phone: '13800138002',
        email: 'member2@example.com',
        last_active: '2024-02-01T00:00:00Z',
      },
    ]

    const { page = 1, pageSize = 10 } = params
    const start = (page - 1) * pageSize
    const end = start + pageSize
    const list = mockMembers.slice(start, end)

    return {
      data: {
        code: 200,
        message: 'success',
        data: {
          list,
          total: mockMembers.length,
          page,
          pageSize,
        },
      },
    }
  }

  const queryParams = new URLSearchParams()
  if (params.page) queryParams.append('page', params.page.toString())
  if (params.pageSize) queryParams.append('pageSize', params.pageSize.toString())
  if (params.role) queryParams.append('role', params.role)
  if (params.status) queryParams.append('status', params.status)
  if (params.keyword) queryParams.append('keyword', params.keyword)

  const queryString = queryParams.toString()
  const url = queryString ? `/clubs/${clubId}/members?${queryString}` : `/clubs/${clubId}/members`

  return await request.get(url)
}

// 获取社团申请列表
export const getClubApplications = async (
  clubId: string,
  params: {
    page?: number
    pageSize?: number
    status?: string
    keyword?: string
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<ClubApplication>> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟数据 - 使用静态数据避免重复创建
    const mockApplications: ClubApplication[] = [
      {
        id: '1',
        userId: 'user4',
        clubId,
        username: 'applicant1',
        realName: '赵六',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        applyReason: '我对编程很感兴趣，希望能加入社团学习更多技术知识。',
        status: 'pending',
        applyTime: '2024-06-25T10:00:00Z',
        studentId: '2021001004',
        major: '计算机科学与技术',
        phone: '13800138003',
        email: 'applicant1@example.com',
        interestedCategories: ['学术科技', '创新创业'],
        tags: ['编程开发', '逻辑清晰', '团队协作', '创新冒险'],
      },
      {
        id: '2',
        userId: 'user5',
        clubId,
        username: 'applicant2',
        realName: '钱七',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        applyReason: '想参加社团活动，提升自己的实践能力。',
        status: 'pending',
        applyTime: '2024-06-26T14:30:00Z',
        studentId: '2021001005',
        major: '软件工程',
        phone: '13800138004',
        email: 'applicant2@example.com',
        interestedCategories: ['学术科技', '文艺体育'],
        tags: ['开朗外向', '善于沟通', '执行力强', '球类运动（篮球 / 足球 / 羽毛球等）'],
      },
      {
        id: '3',
        userId: 'user6',
        clubId,
        username: 'applicant3',
        realName: '孙八',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        applyReason: '希望能在社团中认识更多志同道合的朋友。',
        status: 'approved',
        applyTime: '2024-06-20T09:15:00Z',
        reviewTime: '2024-06-21T16:00:00Z',
        reviewerId: 'user1',
        reviewerName: '张三',
        studentId: '2021001006',
        major: '信息安全',
        phone: '13800138005',
        email: 'applicant3@example.com',
        interestedCategories: ['学术科技', '志愿服务'],
        tags: ['沉稳内敛', '细心周到', '同理心强', '志愿服务'],
      },
      {
        id: '4',
        userId: 'user7',
        clubId,
        username: 'applicant4',
        realName: '周九',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        applyReason: '对算法竞赛很感兴趣，希望能和志同道合的同学一起学习。',
        status: 'pending',
        applyTime: '2024-06-27T08:00:00Z',
        studentId: '2021001007',
        major: '计算机科学与技术',
        phone: '13800138006',
        email: 'applicant4@example.com',
        interestedCategories: ['学术科技'],
        tags: ['理性冷静', '追求完美', '数学建模', '学术竞赛'],
      },
      {
        id: '5',
        userId: 'user8',
        clubId,
        username: 'applicant5',
        realName: '吴十',
        avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
        applyReason: '想学习前端开发技术，希望能参与社团的项目开发。',
        status: 'pending',
        applyTime: '2024-06-27T15:20:00Z',
        studentId: '2021001008',
        major: '软件工程',
        phone: '13800138007',
        email: 'applicant5@example.com',
        interestedCategories: ['学术科技', '创新创业'],
        tags: ['编程开发', '平面设计', '创新冒险', '目标明确'],
      },
    ]

    const { page = 1, pageSize = 10, status, keyword } = params
    
    // 优化过滤逻辑
    let filteredApplications = mockApplications
    
    if (status) {
      filteredApplications = mockApplications.filter(app => app.status === status)
    }
    
    if (keyword) {
      const lowerKeyword = keyword.toLowerCase()
      filteredApplications = filteredApplications.filter(app => 
        (app.realName && app.realName.toLowerCase().includes(lowerKeyword)) ||
        (app.username && app.username.toLowerCase().includes(lowerKeyword)) ||
        (app.studentId && app.studentId.includes(keyword))
      )
    }

    const start = (page - 1) * pageSize
    const end = start + pageSize
    const list = filteredApplications.slice(start, end)

    // 立即返回，不添加延迟
    return {
      data: {
        code: 200,
        message: 'success',
        data: {
          list,
          total: filteredApplications.length,
          page,
          pageSize,
        },
      },
    }
  }

  const queryParams = new URLSearchParams()
  if (params.page) queryParams.append('page', params.page.toString())
  if (params.pageSize) queryParams.append('pageSize', params.pageSize.toString())
  if (params.status) queryParams.append('status', params.status)
  if (params.keyword) queryParams.append('keyword', params.keyword)

  const queryString = queryParams.toString()
  const url = queryString ? `/clubs/${clubId}/applications?${queryString}` : `/clubs/${clubId}/applications`

  return await request.get(url)
}

// 审核申请
export const reviewApplication = async (
  clubId: string,
  data: ApplicationReviewRequest,
): Promise<{ data: ApiResponse<null> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟审核
    return {
      data: {
        code: 200,
        message: '审核成功',
        data: null,
      },
    }
  }

  return await request.post(`/clubs/${clubId}/applications/${data.applicationId}/review`, data)
}

// 移除成员
export const removeMember = async (
  clubId: string,
  memberId: string,
  reason?: string,
): Promise<{ data: ApiResponse<null> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟移除
    return {
      data: {
        code: 200,
        message: '移除成功',
        data: null,
      },
    }
  }

  return await request.delete(`/clubs/${clubId}/members/${memberId}`, {
    data: { reason },
  })
}

// 更改成员角色
export const changeMemberRole = async (
  clubId: string,
  memberId: string,
  role: 'admin' | 'member',
): Promise<{ data: ApiResponse<null> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟更改角色
    return {
      data: {
        code: 200,
        message: '角色更改成功',
        data: null,
      },
    }
  }

  return await request.put(`/clubs/${clubId}/members/${memberId}/role`, { role })
}
