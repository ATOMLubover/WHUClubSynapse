import { ref, computed, reactive } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import * as clubApi from '@/api/club'
import type { Club, ClubCategory, SearchParams, PaginatedData } from '@/types'

export const useClubStore = defineStore('club', () => {
  // 状态
  const clubs = ref<Club[]>([])
  const searchResult=ref<Club[]>([])
  const hotClubs = ref<Club[]>([])
  const favoriteClubs = ref<Club[]>([])
  const latestClubs = ref<Club[]>([])
  const recommendedClubs = ref<Club[]>([])
  const categories = ref<Record<string, number>>({})
  const currentClub = ref<Club | null>(null)

  // 分页和搜索状态

  const globalPageData=reactive({
    total:0,
    currentPage:1,
    pageSize:6,
  })

  const searchPageData=reactive({
    total:0,
    currentPage:1,
    pageSize:6,
  })

  const loading = ref(false)
  const searchParams = ref<SearchParams>({
    keyword: '',
    category: '',
    sortBy: 'hot',
  })
  
  // UI状态
  const activeCategory = ref<string>('')

  // 计算属性
  const totalPages = computed(() => Math.ceil(globalPageData.total / globalPageData.pageSize))
  const hasMore = computed(() => globalPageData.currentPage < totalPages.value)

  // 获取社团列表
  const fetchClubs = async (params?: Partial<SearchParams>) => {
    try {
      loading.value = true
      const queryParams = {
        // ...searchParams.value,
        // ...params,
        page: globalPageData.currentPage,
        pageSize: globalPageData.pageSize,
      }

      const response = await clubApi.getClubList(queryParams)
      const data = response.data.data

      clubs.value = data.list
      globalPageData.total = data.total
      globalPageData.currentPage = data.page

      return data
    } catch (error) {
      console.error('获取社团列表失败:', error)
      ElMessage.error('获取社团列表失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 搜索社团
  const searchClubs = async (keyword: string, params?: Partial<SearchParams>) => {
    try {
      loading.value = true
      const queryParams = {
        ...params,
        page: 1,
        pageSize: globalPageData.pageSize,
      }

      const response = await clubApi.searchClubs(keyword, queryParams)
      const data = response.data.data

      searchResult.value = data.list
      searchPageData.total = data.total
      console.log("searchPageData.total",searchPageData.total)
      searchPageData.currentPage = data.page

      return data
    } catch (error) {
      console.error('搜索社团失败:', error)
      ElMessage.error('搜索社团失败')
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取社团详情
  const fetchClubDetail = async (id: string) => {
    try {
      const response = await clubApi.getClubDetail(id)
      currentClub.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取社团详情失败:', error)
      ElMessage.error('获取社团详情失败')
      throw error
    }
  }

  // 获取热门社团
  const fetchHotClubs = async (limit = 10) => {
    try {
      const response = await clubApi.getHotClubs(limit)
      hotClubs.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取热门社团失败:', error)
      throw error
    }
  }

  // 获取最新社团
  const fetchLatestClubs = async (limit = 10) => {
    try {
      const response = await clubApi.getLatestClubs(limit)
      latestClubs.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取最新社团失败:', error)
      throw error
    }
  }

  // 获取推荐社团
  const fetchRecommendedClubs = async (limit = 10) => {
    try {
      const response = await clubApi.getRecommendedClubs(limit)
      recommendedClubs.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取推荐社团失败:', error)
      throw error
    }
  }

  // 获取社团分类统计
  const fetchCategories = async () => {
    try {
      const response = await clubApi.getClubCategories()
      categories.value = response.data.data
      return response.data.data
    } catch (error) {
      console.error('获取社团分类失败:', error)
      throw error
    }
  }

  // 设置搜索参数
  const setSearchParams = (params: Partial<SearchParams>) => {
    searchParams.value = { ...searchParams.value, ...params }
  }

  // 设置当前活跃分类
  const setActiveCategory = (category: string) => {
    activeCategory.value = category
  }

  //收藏社团
  const favoriteClub=async(clubId:string)=>{
    try{
      const response=await clubApi.favoriteClub(clubId);
      const data=response.data.data;
      ElMessage.success('收藏成功')
      return data;
    } catch (error) {
      console.error('收藏社团失败:', error)
      ElMessage.error('收藏社团失败')
      throw error
    }
  }

  //取消收藏社团
  const unfavoriteClub=async(clubId:string)=>{
    try{
      const response=await clubApi.unfavoriteClub(clubId);
      const data=response.data.data;
      ElMessage.success('取消收藏成功')
      return data;
    } catch (error) {
      console.error('取消收藏社团失败:', error)
      ElMessage.error('取消收藏社团失败')
      throw error
    }
  }

  //获取收藏列表
  const fetchFavoriteClubs=async()=>{
    try{
      await fetchClubs()
      const response=await clubApi.getFavoriteClubs();

      favoriteClubs.value = response.data.data.list
      favoriteClubs.value.forEach((club) => {
        const clubIndex = clubs.value.findIndex((c) => c.club_id === club.club_id)
        if (clubIndex !== -1) {
          clubs.value[clubIndex].isFavorite = true
        }
      })
      return response.data.data;
    }
    catch (error){
      console.error('获取收藏社团失败:', error)
      throw error
    }

  }

  // 申请加入社团
  const applyToClub = async (clubId: string, reason: string) => {
    try {
      const response = await clubApi.applyToClub({ clubId, reason })
      return response.data.data
    }
    catch (error) {
      console.error('申请加入社团失败:', error)
      ElMessage.error('申请加入社团失败')
      throw error
    }
  }

  // 撤销申请
  const cancelApplication = async (applicationId: string) => {
    try {
      const response = await clubApi.cancelApplication(applicationId)
      return response.data.data
    }
    catch (error) {
      console.error('撤销申请失败:', error)
      ElMessage.error('撤销申请失败')
      throw error
    }
  }

  // 获取用户已加入的社团
  const fetchJoinedClubs = async (params?: { page?: number; pageSize?: number }) => {
    try {
      const response = await clubApi.getJoinedClubs(params)
      return response.data.data
    } catch (error) {
      console.error('获取已加入社团失败:', error)
      ElMessage.error('获取已加入社团失败')
      throw error
    }
  }

  // 获取用户管理的社团
  const fetchManagedClubs = async (params?: { page?: number; pageSize?: number }) => {
    try {
      const response = await clubApi.getManagedClubs(params)
      return response.data.data
    } catch (error) {
      console.error('获取管理的社团失败:', error)
      ElMessage.error('获取管理的社团失败')
      throw error
    }
  }

  // 退出社团
  const quitClub = async (clubId: string) => {
    try {
      const response = await clubApi.quitClub(clubId)
      ElMessage.success('退出社团成功')
      return response.data.data
    } catch (error) {
      console.error('退出社团失败:', error)
      ElMessage.error('退出社团失败')
      throw error
    }
  }

  // 创建社团
  const createClub = async (data: {
    name: string
    description: string
    category: string
    maxMembers: number
    tags: string[]
    coverImage?: string
  }) => {
    try {
      const response = await clubApi.createClub(data)
      return response.data.data
    } catch (error) {
      console.error('创建社团失败:', error)
      ElMessage.error('创建社团失败')
      throw error
    }
  }

  // 删除社团
  const deleteClub = async (clubId: string) => {
    try {
      const response = await clubApi.deleteClub(clubId)
      return response.data.data
    } catch (error) {
      console.error('删除社团失败:', error)
      ElMessage.error('删除社团失败')
      throw error
    }
  }

  // 更新社团信息
  const updateClub = async (
    clubId: string,
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
  ) => {
    try {
      const response = await clubApi.updateClub(clubId, data)
      ElMessage.success('社团信息更新成功')
      
      // 如果当前正在查看这个社团，更新currentClub数据
      if (currentClub.value && currentClub.value.club_id === clubId) {
        // 只更新允许更新的字段
        if (data.name) currentClub.value.club_name = data.name
        if (data.description) currentClub.value.desc = data.description
        if (data.category) currentClub.value.category = data.category as any
        if (data.maxMembers) currentClub.value.maxMembers = data.maxMembers
        if (data.tags) currentClub.value.tags = data.tags
        if (data.coverImage) currentClub.value.logo_url = data.coverImage
        if (data.introduction) currentClub.value.introduction = data.introduction
        if (data.contactInfo) currentClub.value.contactInfo = data.contactInfo
        if (data.announcements) currentClub.value.announcements = data.announcements
        if (data.requirements) currentClub.value.requirements = data.requirements
        if (data.meetingTime) currentClub.value.meetingTime = data.meetingTime
        if (data.meetingLocation) currentClub.value.meetingLocation = data.meetingLocation
        if (data.activities) currentClub.value.activities = data.activities
      }
      
      return response.data.data
    } catch (error) {
      console.error('更新社团失败:', error)
      ElMessage.error('更新社团失败')
      throw error
    }
  }

  // 重置搜索
  const resetSearch = () => {
    searchParams.value = {
      keyword: '',
      category: '',
      sortBy: 'hot',
    }
    globalPageData.currentPage = 1
  }

  // 分页
  const setGlobalPage = (page: number) => {
    globalPageData.currentPage = page
  }
  const setSearchPage = (page: number) => {
    searchPageData.currentPage = page
  }

  const setSearchPageSize = (size: number) => {
    searchPageData.pageSize = size
    searchPageData.currentPage = 1
  }

  // 设置页面大小
  const setPageSize = (size: number) => {
    globalPageData.pageSize = size
    globalPageData.currentPage = 1
  }


  return {
    // 状态
    clubs,
    searchResult,
    hotClubs,
    favoriteClubs,
    latestClubs,
    recommendedClubs,
    categories,
    currentClub,
    globalPageData,
    searchPageData,
    loading,
    searchParams,
    activeCategory,
    // 计算属性
    totalPages,
    hasMore,
    // 方法
    fetchClubs,
    searchClubs,
    fetchClubDetail,
    fetchHotClubs,
    fetchLatestClubs,
    fetchRecommendedClubs,
    fetchCategories,
    setSearchParams,
    setActiveCategory,
    resetSearch,
    setGlobalPage,
    setSearchPage,
    setSearchPageSize,
    setPageSize,
    favoriteClub,
    unfavoriteClub,
    fetchFavoriteClubs,
    applyToClub,
    cancelApplication,
    fetchJoinedClubs,
    fetchManagedClubs,
    quitClub,
    createClub,
    deleteClub,
    updateClub,
  }
})
