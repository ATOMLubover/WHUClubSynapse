import request from '@/utils/request'
import type { Club, PaginatedData, SearchParams, ApiResponse, ClubMember, ClubApplication, ApplicationReviewRequest, ClubPost, ClubCategory, ClubCreationApplication, ClubCreatedApplication, ClubPostComment } from '@/types'
import { useConfigStore } from '@/stores/config'
import { useAuthStore } from '@/stores/auth'
import * as mockClub from './mock/club'
import { mockGetClubPosts, mockGetClubPostDetail, mockGetClubPostReplies, mockCreateClubPost, mockReplyClubPost, mockGetClubJoinApplications } from './mock/club'
import { getUserById } from './auth'
import { config } from '@/config'

// 获取动态配置
const getIsUsingMockAPI = () => {
  const configStore = useConfigStore()
  return configStore.isUsingMockAPI
}

// 获取社团列表
export const getClubList = async (
  params: SearchParams = {},
): Promise<PaginatedData<Club>> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetClubList(params)
  }

  const authStore = useAuthStore()
  const queryParams = new URLSearchParams()

  if (params.keyword) {
    queryParams.append('keyword', params.keyword)
  }
  if (params.category) {
    queryParams.append('category', params.category.toString())
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
  console.log(url)
  const response = await request.get(url)
  if(response.data==null){
    return {
      list: [],
      total: 0,
      page: params.page || 1,
      pageSize: params.pageSize || 10,
    }
  }
  const total=(await request.get('/api/club/club_num')).data.club_num
  return {
    list: response.data.map((club:Club)=>{
      if(club.tags==null){
        club.tags=[]
      }
      return club
    }),
    total: total,
    page: params.page || 1,
    pageSize: params.pageSize || 10,
  }
}

// 获取社团基本信息
export const getClubBasic = async (clubId: string): Promise<Club> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockGetClubBasic(clubId)
  }
  const response = await request.get(`/api/club/${clubId}/basic`)
  return response.data as Club
}

// 获取社团详情
export const getClubDetail = async (id: string, post_num: number = 5): Promise<Club|null> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockGetClubDetail(id)
  }
  const response = await request.get(`/api/club/${id}/info?post_num=${post_num}`)
  if(response.data==null){
    return null
  }
  if(response.data.posts==null){
    response.data.posts=[]
  }
  if(response.data.members==null){
    response.data.members=[]
  }
  return response.data as Club
}
// 获取最新社团
export const getLatestClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockGetLatestClubs(limit)
  }
  const response = await request.get(`/api/club/latest?limit=${limit}`)
  return{
    data: {
      code: response.status,
      message: ' ' ,
      data: response.data,
    },
  }
}


// 搜索社团
export const searchClubs = async (
  keyword: string,
  params: Partial<SearchParams> = {},
): Promise<PaginatedData<Club>> => {
  return getClubList({ ...params, keyword })
}

// 获取社团分类列表
export const getClubCategoriesList = async (): Promise<ClubCategory[]> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockGetClubCategoriesList()
  }
  const response = await request.get('/api/club/categories')
  if(response.data==null){
    return []
  }
  return response.data as ClubCategory[]
}



// 申请加入社团
export const applyToClub = async (data: {
  clubId: string
  reason: string
}): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockApplyToClub(data)
  }
  const response = await request.post(`/api/club/${data.clubId}/join`, { reason: data.reason })
  return{
    data: {
      code: response.status,
      message: response.data,
      data: null,
    },
  }
  
}



// 收藏社团
export const favoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockFavoriteClub(clubId)
  }
  const response = await request.post('/api/club/favorite',{club_id:clubId})
  return{
    data: {
      code: response.status,
      message: response.data,
      data: null,
    },
  }
}

// 取消收藏社团
export const unfavoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockUnfavoriteClub(clubId)
  }
  const response = await request.post('/api/club/unfavorite',{club_id:clubId})
  return{
    data: {
      code: response.status,
      message: response.data,
      data: null,
    },
  }
}

// 获取用户收藏的社团
export const getFavoriteClubs = async (
  params: {
    page?: number
    pageSize?: number
  } = {},
): Promise<PaginatedData<Club>> => {
    if (getIsUsingMockAPI()) {
      return await mockClub.mockGetFavoriteClubs(params)
    }
    const url = `/api/club/my_favorites`

    const response = await request.get(url)
    if(response.data==null){
      return {
        list: [],
        total: 0,
        page: params.page || 1,
        pageSize: params.pageSize || 12,
      }
    }
    return {
      list: response.data,
      total: response.data.length,
      page: params.page || 1,
      pageSize: params.pageSize || 12,
    }
  }
   

// 申请创建社团（需要管理员审核）
export const applyToCreateClub = async (data: {
  name: string
  desc: string
  requirements: string
  category_id: number
  tags: string[]
}): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockApplyToCreateClub(data)
  }
  const response = await request.post('/api/club/create', data)
  return{
    data: {
      code: response.status,
      message: response.data,
      data: null,
    },
  }
}

// TODO:获取待审核的社团创建申请列表（管理员功能）
export const getPendingClubApplications = async (params?: {
  page?: number
  pageSize?: number
  status?: 'pending' | 'approved' | 'rejected'
}): Promise<{ data: ApiResponse<{ list: ClubCreationApplication[], total: number }> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockGetPendingClubApplications(params)
  }
  const response = await request.get('/api/admin/club-applications', { params })
  return{
    data: {
      code: response.status,
      message: response.data,
      data: response.data,
    },
  }
}

// TODO:审核社团创建申请（管理员功能）
export const reviewClubApplication = async (applicationId: string, data: {
  status: 'approved' | 'rejected'
  rejectReason?: string
}): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockReviewClubApplication(applicationId, data)
  }
  const response = await request.post(`/api/admin/club-applications/${applicationId}/review`, data)
  return{
    data: {
      code: response.status,
      message: response.data,
      data: null,
    },
  }
}

// TODO:更新社团信息（社团管理员功能）
export const updateClub = async (
  id: string,
  data: {
    name: string
    desc: string
    category_id: number
    tags: string[]
    requirements: string
  }
): Promise<{ data: ApiResponse<Club> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockUpdateClub(id, data)
    : await request.post(`/api/club/pub/update/${id}`, data)
}

// TODO:删除社团（管理员功能）
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
): Promise<PaginatedData<Club>> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetJoinedClubs(params)
  }
  const response = (await request.get('/api/club/my_clubs')).data as Club[]
  console.log('response',response)
  if(response==null){
    return {
      list: [],
      total: 0,
      page: params.page || 1,
      pageSize: params.pageSize || 12,
    }
  }

  return {
    list: response,
    total: response.length,
    page: params.page || 1,
    pageSize: params.pageSize || 12,
  }
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

// TODO:退出社团
export const quitClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  return getIsUsingMockAPI()
    ? await mockClub.mockQuitClub(clubId)
    : await request.delete(`/user/joined-clubs/${clubId}`)
}

// 获取社团帖子列表
export const getClubPosts = async (clubId: string, page: number, pageSize: number): Promise<PaginatedData<ClubPost>> => {

    if(getIsUsingMockAPI()){
      return await mockClub.mockGetClubPosts(clubId, page, pageSize)
    }

    const queryParams = new URLSearchParams()
    if (page) queryParams.append('offset', ((page - 1) * pageSize).toString())
    if (pageSize) queryParams.append('post_num', pageSize.toString()) 

    const queryString = queryParams.toString()
    const url = queryString ? `/api/club/post/posts/${clubId}?${queryString}` : `/api/club/post/posts/${clubId}`

    const res = (await request.get(url)).data as ClubPost[]

    if(res==null){
      return{
        list:[],
        total:0,
        page:page,
        pageSize: pageSize,
      }
    }

    // 使用Promise.all等待所有用户信息获取完成
    const updatedPosts = await Promise.all(
      res.map(async (item) => {
        const user = await getUserById(item.author_id!)
        return {
          ...item,
          authorName: user.username,
          authorAvatar:`${config.apiBaseUrl}/${user.avatar_url}`
        }
      })
    )

    return {
      list: updatedPosts,
      total: updatedPosts.length,
      page: page,
      pageSize: pageSize,
    }
}

// 获取社团帖子详情
export const getClubPostDetail = async (postId: string, contentUrl: string) => {
  if(getIsUsingMockAPI()){
    const res = await mockClub.mockGetClubPostDetail(postId, contentUrl)
    return res
  }
  const res = await request.get('/'+contentUrl,{
    headers: {
      'Content-Type': '',
    },
  })
  return res.data
}

// TODO:获取社团帖子回复列表
export const getClubPostComments = async (postId: string, page: number, pageSize: number): Promise<PaginatedData<ClubPostComment>> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockGetClubPostReplies(postId, page, pageSize)
  }
  const response = await request.get(`/api/club/post/comments/${postId}`)
  if(response.data==null){
    return {
      list:[],
      total:0,
      page:page,
      pageSize:pageSize,
    }
  }
  const list = response.data as ClubPostComment[]
  const updatedList = await Promise.all(
    list.map(async (item) => {
      const user = await getUserById(item.user_id!)
      return {
        ...item,
        authorName: user.username,
        authorAvatar:`${config.apiBaseUrl}/${ user.avatar_url}`
      }
    })
  )
  return {
    list:updatedList.slice((page-1)*pageSize,page*pageSize),
    total:response.data.length,
    page:page,
    pageSize:pageSize,
  }
}

// 创建社团帖子
export const createClubPost = async (data: {
  title: string
  club_id: number
  content: string
}): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockCreateClubPost(data)
  }
  
  // 使用FormData构建multipart/form-data请求
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('club_id', data.club_id.toString())
  formData.append('content', data.content)
  
  const response = await request.post('/api/club/post/create', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  
  return {
    data: {
      code: response.status,
      message: '创建成功',
      data: null,
    },
  }
}

// TODO:回复社团帖子
export const replyClubPost = async (data: {
  post_id: number
  user_id: number
  content: string
}): Promise<{ data: ApiResponse<null> }> => {
  if(getIsUsingMockAPI()){
    return await mockClub.mockReplyClubPost(data)
  }
  const response = await request.post('/api/club/post/comment', data)
  return {
    data: {
      code: response.status,
      message: '回复成功',
      data: null,
    },
  }
}

// TODO:获取社团成员列表
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

  // 使用正确的API路径获取社团详情（包含成员列表）
  const response = await request.get(`/api/club/${clubId}/info`)
  if (!response.data || !response.data.members) {
    return {
      data: {
        code: 200,
        message: 'success',
        data: {
          list: [],
          total: 0,
          page: params.page || 1,
          pageSize: params.pageSize || 10,
        },
      },
    }
  }
  
  // 转换后端数据格式为前端需要的格式
  let members: ClubMember[] = response.data.members.map((item: any) => ({
    member_id: item.member_id?.toString() || '',
    user_id: item.member_id?.toString() || '', // 后端的member_id实际是user_id
    club_id: item.club_id?.toString() || clubId,
    joined_at: item.joined_at || '',
    role_in_club: item.role_in_club || 'member',
    last_active: item.last_active || '',
    // 这些字段需要从其他地方获取，暂时设为空
    username: '',
    realName: '',
    avatar_url: '',
    status: 'active',
    studentId: '',
    major: '',
    phone: '',
    email: ''
  }))
  
  // 前端处理筛选逻辑
  if (params.role) {
    members = members.filter(member => member.role_in_club === params.role)
  }
  if (params.status) {
    members = members.filter(member => member.status === params.status)
  }
  if (params.keyword) {
    members = members.filter(member => 
      (member.realName && member.realName.includes(params.keyword!)) ||
      (member.username && member.username.includes(params.keyword!)) ||
      (member.studentId && member.studentId.includes(params.keyword!))
    )
  }
  
  // 前端处理分页逻辑
  const { page = 1, pageSize = 10 } = params
  const total = members.length
  const startIndex = (page - 1) * pageSize
  const paginatedMembers = members.slice(startIndex, startIndex + pageSize)
  
  return {
    data: {
      code: 200,
      message: 'success',
      data: {
        list: paginatedMembers,
        total,
        page,
        pageSize,
      },
    },
  }
}

// 获取用户加入社团申请列表
export const getClubApplications = async (
  params: {
    page?: number
    pageSize?: number
    status?: string
    keyword?: string
  } = {},
): Promise<PaginatedData<ClubApplication>> => {
  if (getIsUsingMockAPI()) {
    return await mockClub.mockGetUserApplications(params)
  }

  // const queryParams = new URLSearchParams()
  // if (params.page) queryParams.append('page', params.page.toString())
  // if (params.pageSize) queryParams.append('pageSize', params.pageSize.toString())
  // if (params.status) queryParams.append('status', params.status)
  // if (params.keyword) queryParams.append('keyword', params.keyword)
  const response = await request.get('/api/club/my_joinapplis')
  console.log('response', response)
  if(response.data==null){
    return {
      list: [],
      total: 0,
      page: params.page || 1,
      pageSize: params.pageSize || 10,
    }
  }
  let list: ClubApplication[]=response.data
  return {
    list: list.map((item)=>{
      if(item.reviewed_at=="0001-01-01T00:00:00Z"){
        item.reviewed_at=""
      }
      return item
    }),
    total: response.data.length,
    page: params.page || 1,
    pageSize: params.pageSize || 10,
  }
}

// 获取社团加入申请列表 (根据社团ID)
export const getClubJoinApplications = async (
  clubId: string,
  params: {
    page?: number
    pageSize?: number
    status?: string
    keyword?: string
  } = {},
): Promise<PaginatedData<ClubApplication>> => {
  if (getIsUsingMockAPI()) {
    return await mockGetClubJoinApplications(clubId, params)
  }

  // 使用正确的API路径获取社团加入申请列表
  const response = await request.get(`/api/club/pub/join_applis/${clubId}`)
  if (response.data == null) {
    return {
      list: [],
      total: 0,
      page: params.page || 1,
      pageSize: params.pageSize || 10,
    }
  }
  
  // 保持原始数据类型，不强制转换为字符串
  let list: ClubApplication[] = response.data.map((item: any) => ({
    appli_id: item.appli_id, // 保持原始类型
    applied_at: item.applied_at,
    club_id: item.club_id?.toString(),
    applicant_id: item.applicant_id?.toString(),
    reason: item.reason || '',
    status: item.status,
    reject_reason: item.reject_reason || '',
    reviewed_at: item.reviewed_at && item.reviewed_at !== "0001-01-01T00:00:00Z" ? item.reviewed_at : '',
    club: {} as Club
  }))
  
  console.log('📋 获取的申请列表数据:', list)
  
  // 前端处理筛选逻辑
  if (params.status) {
    list = list.filter(app => app.status === params.status)
  }
  if (params.keyword) {
    list = list.filter(app => 
      (app.reason && app.reason.includes(params.keyword!)) || 
      (app.applicant_id && app.applicant_id.includes(params.keyword!))
    )
  }

  // 前端处理分页逻辑
  const { page = 1, pageSize = 10 } = params
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const paginatedList = list.slice(start, end)

  return {
    list: paginatedList,
    total: list.length,
    page,
    pageSize,
  }
}

// 审核社团加入申请
export const reviewJoinApplication = async (
  applicationId: string,
  data: {
    result: 'approve' | 'reject'
    reason?: string
  }
): Promise<{ data: ApiResponse<null> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟审核
    return {
      data: {
        code: 200,
        message: data.result === 'approve' ? '通过社团更新申请成功' : '通过社团更新申请成功',
        data: null,
      },
    }
  }

  try {
    // 使用正确的API路径审核社团加入申请
    // 处理applicationId，确保是数字类型
    let joinAppliId: number
    if (typeof applicationId === 'string') {
      joinAppliId = parseInt(applicationId)
    } else {
      joinAppliId = applicationId
    }
    
    const requestBody: any = {
      join_appli_id: joinAppliId,
      result: data.result
    }
    
    // 只有在拒绝时才添加reason字段
    if (data.result === 'reject' && data.reason) {
      requestBody.reason = data.reason
    }
    
    console.log('🔍 审核申请请求详情:')
    console.log('- 申请ID:', applicationId)
    console.log('- 解析后的申请ID:', parseInt(applicationId))
    console.log('- 审核结果:', data.result)
    console.log('- 拒绝原因:', data.reason)
    console.log('- 完整请求体:', requestBody)
    
    const response = await request.put('/api/club/pub/proc_join', requestBody)
    
    console.log('✅ 审核申请响应成功:', response)
    
    return {
      data: {
        code: response.status,
        message: typeof response.data === 'string' ? response.data : '通过社团更新申请成功',
        data: null,
      },
    }
  } catch (error: any) {
    console.error('❌ 审核申请失败详情:')
    console.error('- 错误状态码:', error.response?.status)
    console.error('- 错误消息:', error.response?.data)
    console.error('- 错误详情:', error.response)
    console.error('- 完整错误:', error)
    
    // 重新抛出错误，让上层处理
    throw error
  }
}

// 审核申请 (原有的方法，保持兼容)
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

// TODO:移除成员
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

// TODO:更改成员角色
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

//获取用户创建的社团申请列表
export const getUserCreatedApplications = async (): Promise<ClubCreatedApplication[]> => {
  if (getIsUsingMockAPI()) {
    // 模拟数据 - 按照API文档格式
    const mockApplications: ClubCreatedApplication[] = [
      {
        appli_id: 1,
        applied_at: '2024-06-25T10:00:00Z',
        proposal: JSON.stringify({ name: '计算机协会', description: '面向编程爱好者的学术社团' }),
        reject_reason: '',
        reviewed_at: '2024-06-25T10:00:00Z',
        status: 'pending',
      },
      {
        appli_id: 2,
        applied_at: '2024-06-26T14:30:00Z',
        proposal: JSON.stringify({ name: '篮球俱乐部', description: '篮球运动爱好者社团' }),
        reject_reason: '',
        reviewed_at: '2024-06-26T14:30:00Z',
        status: 'approved',
      },
      {
        appli_id: 3,
        applied_at: '2024-06-20T09:15:00Z',
        proposal: JSON.stringify({ name: '音乐社', description: '音乐爱好者交流社团' }),
        club_id: '3',
        reject_reason: '',
        reviewed_at: '2024-06-21T16:00:00Z',
        status: 'approved',
      },
      {
        appli_id: 4,
        applied_at: '2024-06-27T08:00:00Z',
        proposal: JSON.stringify({ name: '创业社', description: '创新创业社团' }),
        reject_reason: '申请材料不完整',
        reviewed_at: '2024-06-28T10:00:00Z',
        club_id: '4',
        status: 'rejected',
      },
      {
        appli_id: 5,
        applied_at: '2024-06-27T15:20:00Z',
        proposal: JSON.stringify({ name: '摄影协会', description: '摄影技术交流社团' }),
        club_id: '5',
        reject_reason: '',
        reviewed_at: '2024-06-27T15:20:00Z',
        status: 'approved',
      },
    ]

    return mockApplications
  }
 const response = await request.get('/api/club/my_createapplis')
  const clubcreateapplication: ClubCreatedApplication[] = response.data
  console.log(clubcreateapplication)

  if(clubcreateapplication==null){
    return []
  }
  
  return clubcreateapplication.map((item)=>{
    if(item.reviewed_at=="0001-01-01 00:00:00"){
      item.reviewed_at=""
    }
    return item
  })  
}


// 上传社团logo
export const uploadClubLogo = async (clubId: string, file: File): Promise<{ data: ApiResponse<string> }> => {
  if (getIsUsingMockAPI()) {
    // 模拟上传成功，返回一个假的logoURL
    return {
      data: {
        code: 200,
        message: 'logo上传成功',
        data: 'https://cdn.jsdelivr.net/gh/whu-asset/static/logo-default.png'
      }
    }
  }

  const formData = new FormData()
  formData.append('logo', file)

  const response = await request.post(`/api/club/pub/update_logo/${clubId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  console.log('response', response)
  
  return {
    data: {
      code: response.status,
      message: 'logo上传成功',
      data: response.data.path // 假设后端返回的是新的logoURL
    }
  }
}

// /api/club/pub/update_logo
