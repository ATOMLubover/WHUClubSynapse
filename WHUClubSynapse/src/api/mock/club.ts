import type { Club, PaginatedData, SearchParams, ApiResponse, ClubCategory, ClubApplication, ClubCreationApplication } from '@/types'
import { mockClubs, mockApplications, mockUser, mockClubPosts, mockClubPostReplies, userJoinedClubIds, userManagedClubIds, userFavoriteClubIds, categories } from '@/utils/mockData'
import { config } from '@/config'
import type { ClubPost, ClubPostComment } from '@/types'

// 模拟延迟
const delay = (ms: number = config.mockDelay) => new Promise((resolve) => setTimeout(resolve, ms))

// 模拟获取社团列表
export const mockGetClubList = async (
  params: SearchParams = {},
): Promise<PaginatedData<Club>> => {
  await delay()

  let filteredClubs = [...mockClubs]

  // 分类筛选
  if (params.category) {
    filteredClubs = filteredClubs.filter((club) => categories.find((c) => c.category_id === club.category)?.name === params.category)
  }

  // 关键词搜索
  if (params.keyword) {
    const keyword = params.keyword.toLowerCase()
    filteredClubs = filteredClubs.filter(
      (club) =>
        club.club_name.toLowerCase().includes(keyword) ||
        club.desc.toLowerCase().includes(keyword) ||
        club.tags?.some((tag) => tag.toLowerCase().includes(keyword)),
    )
  }

  // 排序
  switch (params.sortBy) {
    case 'time':
      filteredClubs.sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      )
      break
    case 'members':
      filteredClubs.sort((a, b) => b.member_count - a.member_count)
      break
    case 'hot':
    default:
      filteredClubs.sort((a, b) => {
        if (a.isHot && !b.isHot) return -1
        if (!a.isHot && b.isHot) return 1
        return b.member_count - a.member_count
      })
      break
  }

  // 分页
  const page = params.page || 1
  const pageSize = params.pageSize || 12
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = filteredClubs.slice(start, end)

  console.log(list);

  return {
    list,
    total: filteredClubs.length,
    page,
    pageSize,
  }
}

// 模拟获取社团基本信息
export const mockGetClubBasic = async (clubId: string): Promise<Club> => {
  await delay(500)
  const club = mockClubs.find((c) => c.club_id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }
  return club
}

// 模拟获取社团加入申请列表
export const mockGetClubJoinApplications = async (
  clubId: string,
  params: {
    page?: number
    pageSize?: number
    status?: string
    keyword?: string
  } = {}
): Promise<PaginatedData<ClubApplication>> => {
  await delay(500)
  
  // 模拟数据 - 申请加入列表
  const mockApplications: ClubApplication[] = [
    {
      appli_id: '1',
      applied_at: '2024-01-15T10:30:00Z',
      club_id: clubId,
      applicant_id: '456',
      reason: '我对这个社团很感兴趣，希望能加入',
      status: 'pending',
      reject_reason: '',
      reviewed_at: '',
      club: {} as Club,
      username: 'student001',
      realName: '张三',
      avatar_url: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      studentId: '2021123001',
      major: '计算机科学与技术',
      phone: '13800138001',
      email: 'zhangsan@example.com'
    },
    {
      appli_id: '2',
      applied_at: '2024-01-16T14:20:00Z',
      club_id: clubId,
      applicant_id: '789',
      reason: '希望通过社团活动提升自己',
      status: 'approved',
      reject_reason: '',
      reviewed_at: '2024-01-17T09:00:00Z',
      club: {} as Club,
      username: 'student002',
      realName: '李四',
      avatar_url: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      studentId: '2021123002',
      major: '软件工程',
      phone: '13800138002',
      email: 'lisi@example.com'
    },
    {
      appli_id: '3',
      applied_at: '2024-01-17T16:45:00Z',
      club_id: clubId,
      applicant_id: '123',
      reason: '想要参与社团组织的各项活动',
      status: 'rejected',
      reject_reason: '当前成员已满',
      reviewed_at: '2024-01-18T10:30:00Z',
      club: {} as Club,
      username: 'student003',
      realName: '王五',
      avatar_url: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
      studentId: '2021123003',
      major: '信息安全',
      phone: '13800138003',
      email: 'wangwu@example.com'
    }
  ]

  // 应用筛选
  let filteredApplications = mockApplications
  if (params.status) {
    filteredApplications = filteredApplications.filter(app => app.status === params.status)
  }
  if (params.keyword) {
    filteredApplications = filteredApplications.filter(app => 
      (app.reason && app.reason.includes(params.keyword!)) ||
      (app.realName && app.realName.includes(params.keyword!)) ||
      (app.username && app.username.includes(params.keyword!)) ||
      (app.studentId && app.studentId.includes(params.keyword!))
    )
  }

  const { page = 1, pageSize = 10 } = params
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = filteredApplications.slice(start, end)

  return {
    list,
    total: filteredApplications.length,
    page,
    pageSize,
  }
}

// 模拟获取社团详情
export const mockGetClubDetail = async (id: string): Promise<Club > => {
  await delay(500)

  const club = mockClubs.find((c) => c.club_id === id)
  if (!club) {
    throw new Error('社团不存在')
  }

  return club
}

// 模拟获取热门社团
export const mockGetHotClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  await delay(300)

  const hotClubs = mockClubs
    .filter((club) => club.isHot)
    .sort((a, b) => b.member_count - a.member_count)
    .slice(0, limit)

  return {
    data: {
      code: 200,
      message: 'success',
      data: hotClubs,
    },
  }
}

// 模拟获取最新社团
export const mockGetLatestClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  await delay(300)

  const latestClubs = [...mockClubs]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, limit)

  return {
    data: {
      code: 200,
      message: 'success',
      data: latestClubs,
    },
  }
}

// 模拟获取推荐社团
export const mockGetRecommendedClubs = async (
  limit = 10,
): Promise<{ data: ApiResponse<Club[]> }> => {
  await delay(300)

  // 模拟推荐算法：随机选择一些社团
  const shuffled = [...mockClubs].sort(() => 0.5 - Math.random())
  const recommended = shuffled.slice(0, limit)

  return {
    data: {
      code: 200,
      message: 'success',
      data: recommended,
    },
  }
}

// 模拟搜索社团
export const mockSearchClubs = async (
  keyword: string,
  params: Partial<SearchParams> = {},
): Promise<PaginatedData<Club>> => {
  return mockGetClubList({ ...params, keyword })
}

// 模拟获取社团分类列表
export const mockGetClubCategoriesList = async (): Promise<ClubCategory[]> => {
  await delay(200)
  return categories
}

// 模拟获取社团分类统计
export const mockGetClubCategories = async (): Promise<{
  data: ApiResponse<Record<string, number>>
}> => {
  await delay(200)

  // 根据实际社团数据动态计算每个分类的数量
  const categories: Record<string, number> = {}
  
  mockClubs.forEach(club => {
    if (categories[club.category]) {
      categories[club.category]++
    } else {
      categories[club.category] = 1
    }
  })

  return {
    data: {
      code: 200,
      message: 'success',
      data: categories,
    },
  }
}

// 模拟申请加入社团
export const mockApplyToClub = async (data: {
  clubId: string
  reason: string
}): Promise<{ data: ApiResponse<null> }> => {
  await delay(600)

  const club = mockClubs.find((c) => c.club_id === data.clubId)
  if (!club) {
    throw new Error('社团不存在')
  }

  // 检查用户是否已经加入该社团
  if (userJoinedClubIds.includes(data.clubId)) {
    throw new Error('您已经加入该社团')
  }

  // 检查社团是否已满员 - 更严格的检查
  const currentMemberCount = club.member_count || 0
  const maxMemberCount = club.maxMembers || 50
  
  if (currentMemberCount >= maxMemberCount) {
    throw new Error(`社团已满员（${currentMemberCount}/${maxMemberCount}）`)
  }

  // 将用户添加到已加入社团列表
  userJoinedClubIds.push(data.clubId)

  // 更新社团成员数量 - 确保不超过上限
  const newMemberCount = currentMemberCount + 1
  if (newMemberCount <= maxMemberCount) {
    club.member_count = newMemberCount
  } else {
    throw new Error('社团成员数量超出上限')
  }

  // 更新社团状态为已加入
  club.status = 'joined'

  // 添加到申请记录
  mockApplications.push({
    appli_id: (mockApplications.length + 1).toString(),
    club_id: club.club_id,
    status: 'pending', // 直接批准加入
    reason: data.reason,
    applied_at: new Date().toISOString(),
    reviewed_at: new Date().toISOString(),
    reject_reason: '',
    club: club,
  });

  // 更新用户统计信息
  mockUser.stats!.joinedClubs++

  return {
    data: {
      code: 200,
      message: '申请提交成功，已自动加入社团',
      data: null,
    },
  }
}


// 模拟收藏社团
export const mockFavoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(400)

  const club = mockClubs.find((c) => c.club_id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }
  club.isFavorite = true
  userFavoriteClubIds.push(clubId)

  mockUser.stats!.favoriteClubs++

  return {
    data: {
      code: 200,
      message: '收藏成功',
      data: null,
    },
  }
}

// 模拟取消收藏社团
export const mockUnfavoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(400)

  const club = mockClubs.find((c) => c.club_id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }
  club.isFavorite = false

  mockUser.stats!.favoriteClubs--
  const index = userFavoriteClubIds.indexOf(clubId)
  if (index > -1) {
    userFavoriteClubIds.splice(index, 1)
  }
  return {
    data: {
      code: 200,
      message: '取消收藏成功',
      data: null,
    },
  }
}

// 模拟获取用户收藏的社团
export const mockGetFavoriteClubs = async (
  params: {
    page?: number
    pageSize?: number
  } = {},
): Promise<PaginatedData<Club>> => {
  await delay(500)

  const favoriteClubs = userFavoriteClubIds.map((id) => mockClubs.find((club) => club.club_id === id))
  const list = favoriteClubs.filter((club): club is Club => club !== undefined) as Club[]
  return {
    list,
    total: list.length,
    page: params.page || 1,
    pageSize: params.pageSize || 12,
  }
}

// 模拟获取用户申请记录
export const mockGetUserApplications = async (
  params: {
    page?: number
    pageSize?: number
    status?: string
    category?: string
    keyword?: string
  } = {},
): Promise<PaginatedData<ClubApplication>> => {
  await delay(500)

  let filteredApplications = mockApplications

  if (params.status) {
    filteredApplications = filteredApplications.filter((app) => app.status === params.status)
  }

  if (params.category) {
    filteredApplications = filteredApplications.filter((app) => app.club?.category?.toString() == params.category)
  }

  if (params.keyword) {
    const keyword = params.keyword.toLowerCase()
    filteredApplications = filteredApplications.filter((app) => app.club?.club_name?.toLowerCase().includes(keyword) || app.club?.category?.toString().includes(keyword))
  }

  const page = params.page || 1
  const pageSize = params.pageSize || 10
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = filteredApplications.slice(start, end)

  return {
        list,
        total: filteredApplications.length,
        page,
        pageSize,
      }
  }

// 模拟创建社团
export const mockCreateClub = async (data:  {
  name: string
  desc: string
  requirements: string
  category?: string
  maxMembers?: number
  tags?: string[]
  coverImage?: string
}): Promise<{ data: ApiResponse<null> }> => {
  await delay(600)

  // 生成新的社团ID
  const newId = (mockClubs.length + 1).toString()

  // 创建新社团对象
  const newClub: Club = {
    club_id: newId,
    club_name: data.name,
    desc: data.desc,
    category: data.category as any,
    adminId: 'user1', // 假设当前用户ID为user1
    adminName: '测试用户',
    member_count: 1, // 创建者自动成为成员
    maxMembers: data.maxMembers,
    tags: data.tags||[],
    isHot: false,
    status_for_create: 'pending',
    created_at: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    qq: '1234567890',
    details: data.desc,
    activities: [],
    location: `武汉大学${data.name}`,
    isFavorite: false,
    logo_url: data.coverImage || `https://picsum.photos/400/240?random=${newId}`,
  }

  // 添加到社团列表
  mockClubs.push(newClub)

  // 添加到用户管理的社团列表
  userManagedClubIds.push(newId)

  // 添加到用户加入的社团列表（创建者自动加入）
  userJoinedClubIds.push(newId)

  // 更新用户统计信息
  mockUser.stats!.managedClubs++
  mockUser.stats!.joinedClubs++

  return {
    data: {
      code: 200,
      message: '社团创建成功',
      data: null,
    },
  }
}

// 模拟更新社团信息
export const mockUpdateClub = async (
  id: string,
  data: Partial<{
    name: string
    description: string
    category: string
    maxMembers: number
    tags: string[]
    coverImage: string
  }>,
): Promise<{ data: ApiResponse<Club> }> => {
  await delay(600)

  const club = mockClubs.find((c) => c.club_id === id)
  if (!club) {
    throw new Error('社团不存在')
  }

  const updatedClub: Club = {
    ...club,
    ...data,
    category: (data.category as any) || club.category,
    updatedAt: new Date().toISOString(),
  }

  return {
    data: {
      code: 200,
      message: '社团信息更新成功',
      data: updatedClub,
    },
  }
}

// 模拟获取用户已加入的社团
export const mockGetJoinedClubs = async (
  params: {
    page?: number
    pageSize?: number
  } = {},
): Promise<PaginatedData<Club>> => {
  await delay(500)

  // 根据用户加入的社团ID列表获取社团
  const joinedClubs = mockClubs
    .filter(club => userJoinedClubIds.includes(club.club_id))
    .map(club => ({
      ...club,
      // 如果这个社团是用户管理的，设置leader_id为当前用户ID
      leader_id: userManagedClubIds.includes(club.club_id) ? '2' : undefined
    }))

  const page = params.page || 1
  const pageSize = params.pageSize || 12
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = joinedClubs.slice(start, end)

  return {

      list,
      total: joinedClubs.length,
      page,
      pageSize,
    
  }
}

// 模拟获取用户管理的社团
export const mockGetManagedClubs = async (
  params: {
    page?: number
    pageSize?: number
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  await delay(500)

  // 根据用户管理的社团ID列表获取社团
  const managedClubs = mockClubs
    .filter(club => userManagedClubIds.includes(club.club_id))
    .map(club => ({
      ...club,
      isFavorite: false
    }))

  const page = params.page || 1
  const pageSize = params.pageSize || 12
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = managedClubs.slice(start, end)

  return {
    data: {
      code: 200,
      message: 'success',
      data: {
        list,
        total: managedClubs.length,
        page,
        pageSize,
      },
    },
  }
}

// 模拟退出社团
export const mockQuitClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(400)

  const club = mockClubs.find((c) => c.club_id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }

  // 检查用户是否已加入该社团
  if (!userJoinedClubIds.includes(clubId)) {
    throw new Error('您未加入该社团')
  }

  // 从用户加入的社团列表中移除
  const index = userJoinedClubIds.indexOf(clubId)
  if (index > -1) {
    userJoinedClubIds.splice(index, 1)
  }

  // 更新社团成员数量
  if (club.member_count > 0) {
    club.member_count--
  }

  // 更新用户统计信息
  mockUser.stats!.joinedClubs--

  return {
    data: {
      code: 200,
      message: '退出社团成功',
      data: null,
    },
  }
}

// 模拟删除社团
export const mockDeleteClub = async (id: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(500)

  const club = mockClubs.find((c) => c.club_id === id)
  if (!club) {
    throw new Error('社团不存在')
  }

  // 检查用户是否管理该社团
  if (!userManagedClubIds.includes(id)) {
    throw new Error('您无权删除该社团')
  }

  // 从用户管理的社团列表中移除
  const managedIndex = userManagedClubIds.indexOf(id)
  if (managedIndex > -1) {
    userManagedClubIds.splice(managedIndex, 1)
  }

  // 从用户加入的社团列表中移除（如果用户也加入了该社团）
  const joinedIndex = userJoinedClubIds.indexOf(id)
  if (joinedIndex > -1) {
    userJoinedClubIds.splice(joinedIndex, 1)
    // 更新用户统计信息
    mockUser.stats!.joinedClubs--
  }

  // 更新用户统计信息
  mockUser.stats!.managedClubs--

  // 从社团列表中移除（实际项目中应该标记为删除状态）
  const clubIndex = mockClubs.findIndex(c => c.club_id === id)
  if (clubIndex > -1) {
    mockClubs.splice(clubIndex, 1)
  }

  return {
    data: {
      code: 200,
      message: '社团删除成功',
      data: null,
    },
  }
}

// 模拟获取社团帖子列表
export const mockGetClubPosts = async (clubId: string, page: number = 1, pageSize = 500) => {
  await delay(300)
  
  console.log('mockGetClubPosts 被调用，clubId:', clubId)
  console.log('所有帖子数据:', mockClubPosts)
  
  const all = mockClubPosts.filter(p => p.club_id === clubId)
  console.log('过滤后的帖子:', all)
  
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = all.slice(start, end)
  
  console.log('返回的帖子列表:', list)
  
  return {
    list,
    total: all.length,
    page,
    pageSize
  }
}

export const mockGetClubPostDetail = async (
  postId: string,
  contentUrl: string
): Promise<string > => {
  await delay(200)
  
  const post = mockClubPosts.find(p => p.post_id === postId)
  if (!post) throw new Error('帖子不存在')
  
  return post.content || ''
}

export const mockGetClubPostReplies = async (
  postId: string,
  page = 1,
  pageSize = 10
): Promise<PaginatedData<ClubPostComment>> => {
  await delay(200)
  
  const all = mockClubPostReplies.filter(r => r.post_id === postId)
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = all.slice(start, end)
  
  return {
    list,
    total: all.length,
    page,
    pageSize
  }
}

export const mockCreateClubPost = async (
  data: {
    club_id: number
    title: string
    content: string
  }
): Promise<{ data: ApiResponse<null> }> => {
  await delay(400)
  
  const newPost: ClubPost = {
    club_id: data.club_id.toString(),
    title: data.title,
    content: data.content,
    post_id: (mockClubPosts.length + 1).toString(),
    created_at: new Date().toISOString(),
    comment_count: 0
  }
  mockClubPosts.unshift(newPost)
  
  return {
    data: {
      code: 200,
      message: '发帖成功',
      data: null
    }
  }
}

export const mockReplyClubPost = async (
  data: {
  post_id: number,
  user_id: number,
  content: string
  }
): Promise<{ data: ApiResponse<null> }> => {
  await delay(300)
  
  const newReply: ClubPostComment = {
    post_id: data.post_id.toString(),
    user_id: data.user_id,
    content: data.content,
    comment_id: 'r' + (mockClubPostReplies.length + 1),
    created_at: new Date().toISOString()
  }
  mockClubPostReplies.push(newReply)
  // 更新主贴回复数
  const post = mockClubPosts.find(p => p.post_id === reply.post_id)
  if (post) post.comment_count=post.comment_count?post.comment_count+1:1
  
  return {
    data: {
      code: 200,
      message: '回复成功',
      data: null
    }
  }
}

// 模拟申请创建社团
export const mockApplyToCreateClub = async (data: {
  name: string
  desc: string
  requirements: string
  category_id: number
  tags: string[]
}): Promise<{ data: ApiResponse<null> }> => {
  await delay(800)

  // 生成新的申请ID
  const newId = (mockClubApplications.length + 1).toString()

  //将tags转换为数组
  const tags = data.tags

  // 创建申请对象
  const newApplication: ClubCreationApplication = {
    id: newId,
    userId: 'user1', // 假设当前用户ID
    username: '测试用户',
    realName: '张三',
    avatar_url: 'https://picsum.photos/100/100?random=1',
    clubName: data.name,
    description: data.desc,
    category: data.category_id || 0,
    maxMembers: 50,
    tags: tags,
    coverImage: '',
    requirements: data.requirements,
    introduction: '',
    contactInfo: {},
    meetingTime: '',
    meetingLocation: '',
    status: 'pending',
    applyTime: new Date().toISOString(),
    studentId: '2021001001',
    major: '计算机科学与技术',
    phone: '13800138000',
    email: 'test@whu.edu.cn'
  }

  // 添加到申请列表
  mockClubApplications.push(newApplication)

  return {
    data: {
      code: 200,
      message: '社团创建申请提交成功，等待管理员审核',
      data: null,
    },
  }
}

// 模拟审核社团创建申请
export const mockReviewClubApplication = async (applicationId: string, data: {
  status: 'approved' | 'rejected'
  rejectReason?: string
}): Promise<{ data: ApiResponse<null> }> => {
  await delay(500)

  const application = mockClubApplications.find(app => app.id === applicationId)
  if (!application) {
    return {
      data: {
        code: 404,
        message: '申请不存在',
        data: null,
      },
    }
  }

  // 更新申请状态
  application.status = data.status
  application.reviewTime = new Date().toISOString()
  application.reviewerId = 'admin1'
  application.reviewerName = '管理员'
  if (data.status === 'rejected' && data.rejectReason) {
    application.rejectReason = data.rejectReason
  }

  // 如果审核通过，创建社团
  if (data.status === 'approved') {
    const newClub: Club = {
      club_id: (mockClubs.length + 1).toString(),
      club_name: application.clubName,
      desc: application.description,
      logo_url: application.coverImage || `https://picsum.photos/400/240?random=${mockClubs.length + 1}`,
      category: application.category,
      adminId: application.userId,
      adminName: application.username,
      member_count: 1,
      maxMembers: application.maxMembers,
      tags: application.tags,
      isHot: false,
      status_for_create: 'approved',
      created_at: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      qq: application.contactInfo?.qq || '',
      details: application.description,
      activities: [],
      location: `武汉大学${application.clubName}`,
      isFavorite: false,
      introduction: application.introduction,
      contactInfo: application.contactInfo,
      requirements: application.requirements,
      meetingTime: application.meetingTime,
      meetingLocation: application.meetingLocation,
    }

    mockClubs.push(newClub)
  }

  return {
    data: {
      code: 200,
      message: data.status === 'approved' ? '审核通过，社团创建成功' : '审核拒绝',
      data: null,
    },
  }
}

// 模拟社团创建申请数据
export const mockClubApplications: ClubCreationApplication[] = [
  {
    id: '1',
    userId: 'user1',
    username: '张三',
    realName: '张三',
    avatar_url: 'https://picsum.photos/100/100?random=1',
    clubName: '人工智能研究社',
    description: '致力于人工智能技术的研究和应用，组织技术分享和项目实践。',
    category: 0,
    maxMembers: 60,
    tags: ['AI', '机器学习', '深度学习'],
    coverImage: 'https://picsum.photos/400/240?random=20',
    requirements: '对人工智能技术有浓厚兴趣，具备一定的编程基础。',
    introduction: '我们是一个专注于人工智能技术研究的学术社团，定期组织技术讲座、项目实践和竞赛活动。',
    contactInfo: {
      qq: '123456789',
      wechat: 'ai_research',
      email: 'ai@whu.edu.cn',
      phone: '13800138001',
      address: '武汉大学计算机学院'
    },
    meetingTime: '每周三晚上7点',
    meetingLocation: '计算机学院A101',
    status: 'pending',
    applyTime: '2024-01-25T10:00:00Z',
    studentId: '2021001001',
    major: '计算机科学与技术',
    phone: '13800138001',
    email: 'zhangsan@whu.edu.cn'
  },
  {
    id: '2',
    userId: 'user2',
    username: '李四',
    realName: '李四',
    avatar_url: 'https://picsum.photos/100/100?random=2',
    clubName: '摄影艺术社',
    description: '用镜头记录美好瞬间，分享摄影技巧，提升艺术修养。',
    category: 1,
    maxMembers: 40,
    tags: ['摄影', '艺术', '创作'],
    coverImage: 'https://picsum.photos/400/240?random=21',
    requirements: '热爱摄影艺术，愿意分享和学习。',
    introduction: '摄影艺术社致力于培养同学们的摄影兴趣和艺术修养，定期组织外拍活动和作品分享。',
    contactInfo: {
      qq: '987654321',
      wechat: 'photo_art',
      email: 'photo@whu.edu.cn',
      phone: '13800138002',
      address: '武汉大学艺术学院'
    },
    meetingTime: '每周五下午3点',
    meetingLocation: '艺术学院B201',
    status: 'pending',
    applyTime: '2024-01-24T14:30:00Z',
    studentId: '2021002001',
    major: '艺术设计',
    phone: '13800138002',
    email: 'lisi@whu.edu.cn'
  }
]
