import type { Club, PaginatedData, SearchParams, ApiResponse, ClubCategory } from '@/types'
import { mockClubs, mockApplications, mockUser, mockClubPosts, mockClubPostReplies, userJoinedClubIds, userManagedClubIds, userFavoriteClubIds, categories } from '@/utils/mockData'
import { config } from '@/config'
import type { ClubPost, ClubPostReply } from '@/types'

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
    id: (mockApplications.length + 1).toString(),
    userId: 'user1',
    clubId: club.club_id,
    clubName: club.club_name,
    clubCoverImage: club.logo_url,
    status: 'approved', // 直接批准加入
    reason: data.reason,
    applyReason: data.reason,
    createdAt: new Date().toISOString(),
    clubCategory: categories.find((c) => c.category_id === club.category)?.name||' ',
    feedback: '申请已通过，欢迎加入我们！',
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

// 模拟撤销申请
export const mockCancelApplication = async (applicationId: string)
: Promise<{ data: ApiResponse<null> }> => {
  await delay(400)
  const application = mockApplications.find((app) => app.id === applicationId)
  const club = mockClubs.find((c) => c.club_id === application?.clubId)
  if (!club) {
    throw new Error('社团不存在')
  }
  
  // 如果申请状态是已批准，需要减少成员人数
  if (application?.status === 'approved') {
    if (club.member_count > 0) {
      club.member_count--
    }
    // 从用户加入的社团列表中移除
    const joinedIndex = userJoinedClubIds.indexOf(application.clubId)
    if (joinedIndex > -1) {
      userJoinedClubIds.splice(joinedIndex, 1)
      // 更新用户统计信息
      mockUser.stats!.joinedClubs--
    }
  }
  
  club.status = 'not_applied'
  if (!application) {
    throw new Error('申请不存在')
  }
  const filteredApplications = mockApplications.filter((app) => app.id !== applicationId)
  mockApplications.length = 0
  mockApplications.push(...filteredApplications)
  mockUser.stats!.appliedClubs--

  return {
    data: {
      code: 200,
      message: '撤销申请成功',
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
): Promise<{ data: ApiResponse<PaginatedData<any>> }> => {
  await delay(500)

  let filteredApplications = mockApplications

  if (params.status) {
    filteredApplications = filteredApplications.filter((app) => app.status === params.status)
  }

  if (params.category) {
    filteredApplications = filteredApplications.filter((app) => app.clubCategory == params.category)
  }

  if (params.keyword) {
    const keyword = params.keyword.toLowerCase()
    filteredApplications = filteredApplications.filter((app) => app.clubName.toLowerCase().includes(keyword) || app.clubCategory.toLowerCase().includes(keyword))
  }

  const page = params.page || 1
  const pageSize = params.pageSize || 10
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = filteredApplications.slice(start, end)

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
    tags: data.tags,
    isHot: false,
    status: 'managed', // 创建者创建的社团直接为管理中状态
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
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  await delay(500)

  // 根据用户加入的社团ID列表获取社团
  const joinedClubs = mockClubs
    .filter(club => userJoinedClubIds.includes(club.club_id))
    .map(club => ({
      ...club,
      isFavorite: false
    }))

  const page = params.page || 1
  const pageSize = params.pageSize || 12
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = joinedClubs.slice(start, end)

  return {
    data: {
      code: 200,
      message: 'success',
      data: {
        list,
        total: joinedClubs.length,
        page,
        pageSize,
      },
    },
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

export const mockGetClubPosts = async (
  clubId: string,
  page = 1,
  pageSize = 5
): Promise<PaginatedData<ClubPost>> => {
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
  postId: string
): Promise<{ data: ApiResponse<ClubPost> }> => {
  await delay(200)
  
  const post = mockClubPosts.find(p => p.post_id === postId)
  if (!post) throw new Error('帖子不存在')
  
  return {
    data: {
      code: 200,
      message: 'success',
      data: post
    }
  }
}

export const mockGetClubPostReplies = async (
  postId: string,
  page = 1,
  pageSize = 10
): Promise<{ data: ApiResponse<PaginatedData<ClubPostReply>> }> => {
  await delay(200)
  
  const all = mockClubPostReplies.filter(r => r.postId === postId)
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = all.slice(start, end)
  
  return {
    data: {
      code: 200,
      message: 'success',
      data: {
        list,
        total: all.length,
        page,
        pageSize
      }
    }
  }
}

export const mockCreateClubPost = async (
  post: Omit<ClubPost, 'id' | 'createdAt' | 'replyCount'>
): Promise<{ data: ApiResponse<ClubPost> }> => {
  await delay(400)
  
  const newPost: ClubPost = {
    ...post,
    post_id: 'p' + (mockClubPosts.length + 1),
    created_at: new Date().toISOString(),
    comment_count: 0
  }
  mockClubPosts.unshift(newPost)
  
  return {
    data: {
      code: 200,
      message: '发帖成功',
      data: newPost
    }
  }
}

export const mockReplyClubPost = async (
  reply: Omit<ClubPostReply, 'id' | 'createdAt'>
): Promise<{ data: ApiResponse<ClubPostReply> }> => {
  await delay(300)
  
  const newReply: ClubPostReply = {
    ...reply,
    id: 'r' + (mockClubPostReplies.length + 1),
    createdAt: new Date().toISOString()
  }
  mockClubPostReplies.push(newReply)
  // 更新主贴回复数
  const post = mockClubPosts.find(p => p.post_id === reply.postId)
  if (post) post.comment_count++
  
  return {
    data: {
      code: 200,
      message: '回复成功',
      data: newReply
    }
  }
}
