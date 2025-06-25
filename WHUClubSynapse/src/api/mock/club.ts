import type { Club, PaginatedData, SearchParams, ApiResponse } from '@/types'
import { mockClubs } from '@/utils/mockData'
import { config } from '@/config'

// 模拟延迟
const delay = (ms: number = config.mockDelay) => new Promise((resolve) => setTimeout(resolve, ms))

// 模拟获取社团列表
export const mockGetClubList = async (
  params: SearchParams = {},
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  await delay()

  let filteredClubs = [...mockClubs]

  // 分类筛选
  if (params.category) {
    filteredClubs = filteredClubs.filter((club) => club.category === params.category)
  }

  // 关键词搜索
  if (params.keyword) {
    const keyword = params.keyword.toLowerCase()
    filteredClubs = filteredClubs.filter(
      (club) =>
        club.name.toLowerCase().includes(keyword) ||
        club.description.toLowerCase().includes(keyword) ||
        club.tags.some((tag) => tag.toLowerCase().includes(keyword)),
    )
  }

  // 排序
  switch (params.sortBy) {
    case 'time':
      filteredClubs.sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      )
      break
    case 'members':
      filteredClubs.sort((a, b) => b.currentMembers - a.currentMembers)
      break
    case 'hot':
    default:
      filteredClubs.sort((a, b) => {
        if (a.isHot && !b.isHot) return -1
        if (!a.isHot && b.isHot) return 1
        return b.currentMembers - a.currentMembers
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
    data: {
      code: 200,
      message: 'success',
      data: {
        list,
        total: filteredClubs.length,
        page,
        pageSize,
      },
    },
  }
}

// 模拟获取社团详情
export const mockGetClubDetail = async (id: string): Promise<{ data: ApiResponse<Club> }> => {
  await delay(500)

  const club = mockClubs.find((c) => c.id === id)
  if (!club) {
    throw new Error('社团不存在')
  }

  return {
    data: {
      code: 200,
      message: 'success',
      data: club,
    },
  }
}

// 模拟获取热门社团
export const mockGetHotClubs = async (limit = 10): Promise<{ data: ApiResponse<Club[]> }> => {
  await delay(300)

  const hotClubs = mockClubs
    .filter((club) => club.isHot)
    .sort((a, b) => b.currentMembers - a.currentMembers)
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
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
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
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  return mockGetClubList({ ...params, keyword })
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

  const club = mockClubs.find((c) => c.id === data.clubId)
  if (!club) {
    throw new Error('社团不存在')
  }

  return {
    data: {
      code: 200,
      message: '申请提交成功，请等待审核',
      data: null,
    },
  }
}

// 模拟收藏社团
export const mockFavoriteClub = async (clubId: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(400)

  const club = mockClubs.find((c) => c.id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }
  club.isFavorite = true

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

  const club = mockClubs.find((c) => c.id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }
  club.isFavorite = false

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
): Promise<{ data: ApiResponse<PaginatedData<Club>> }> => {
  await delay(500)

  const favoriteClubs = mockClubs.filter((club) => club.isFavorite)
  const page = params.page || 1
  const pageSize = params.pageSize || 12
  const start = (page - 1) * pageSize
  const end = start + pageSize
  const list = favoriteClubs.slice(start, end)

  console.log(list)

  return {
    data: {
      code: 200,
      message: 'success',
      data: {
        list,
        total: favoriteClubs.length,
        page,
        pageSize,
      },
    },
  }
}

// 模拟获取用户申请记录
export const mockGetUserApplications = async (
  params: {
    page?: number
    pageSize?: number
    status?: string
  } = {},
): Promise<{ data: ApiResponse<PaginatedData<any>> }> => {
  await delay(500)

  // 模拟申请记录
  const applications = [
    {
      id: '1',
      clubId: mockClubs[0].id,
      clubName: mockClubs[0].name,
      status: 'pending',
      reason: '希望能够加入学习相关技术',
      applyReason: '对技术很感兴趣',
      createdAt: new Date().toISOString(),
      clubCategory: mockClubs[0].category,
      feedback: '欢迎加入我们，请等待审核',
    },
    {
      id: '2',
      clubId: mockClubs[1].id,
      clubName: mockClubs[1].name,
      status: 'approved',
      reason: '',
      applyReason: '想要参与文艺活动',
      createdAt: new Date(Date.now() - 86400000).toISOString(),
      reviewedAt: new Date().toISOString(),
      clubCategory: mockClubs[1].category,
      feedback: '欢迎加入我们，请等待审核',
    },
  ]

  let filteredApplications = applications
  if (params.status) {
    filteredApplications = applications.filter((app) => app.status === params.status)
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
export const mockCreateClub = async (data: {
  name: string
  description: string
  category: string
  maxMembers: number
  tags: string[]
  coverImage?: string
}): Promise<{ data: ApiResponse<Club> }> => {
  await delay(800)

  const newClub: Club = {
    id: 'club_' + Date.now(),
    name: data.name,
    description: data.description,
    coverImage: data.coverImage || 'https://via.placeholder.com/400x240',
    category: data.category as any,
    adminId: 'admin_1',
    adminName: '管理员',
    currentMembers: 1,
    maxMembers: data.maxMembers,
    tags: data.tags,
    isHot: false,
    status: 'pending',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    activities: [],
    location: '',
    qq: '',
    details: '',
    isFavorite: false
  }

  return {
    data: {
      code: 200,
      message: '社团创建成功，等待审核',
      data: newClub,
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

  const club = mockClubs.find((c) => c.id === id)
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

// 模拟删除社团
export const mockDeleteClub = async (id: string): Promise<{ data: ApiResponse<null> }> => {
  await delay(500)

  return {
    data: {
      code: 200,
      message: '社团删除成功',
      data: null,
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

  // 模拟已加入的社团（前3个社团）
  const joinedClubs = mockClubs.slice(0, 3).map(club => ({
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

  // 模拟管理的社团（第1个社团）
  const managedClubs = [mockClubs[0]].map(club => ({
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

  const club = mockClubs.find((c) => c.id === clubId)
  if (!club) {
    throw new Error('社团不存在')
  }

  return {
    data: {
      code: 200,
      message: '退出社团成功',
      data: null,
    },
  }
}
