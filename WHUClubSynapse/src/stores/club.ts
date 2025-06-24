import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import * as clubApi from '@/api/club'
import type { Club, ClubCategory, SearchParams, PaginatedData } from '@/types'

export const useClubStore = defineStore('club', () => {
  // 状态
  const clubs = ref<Club[]>([])
  const hotClubs = ref<Club[]>([])
  const latestClubs = ref<Club[]>([])
  const recommendedClubs = ref<Club[]>([])
  const categories = ref<Record<string, number>>({})
  const currentClub = ref<Club | null>(null)

  // 分页和搜索状态
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(12)
  const loading = ref(false)
  const searchParams = ref<SearchParams>({
    keyword: '',
    category: '',
    sortBy: 'hot',
  })

  // 计算属性
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const hasMore = computed(() => currentPage.value < totalPages.value)

  // 获取社团列表
  const fetchClubs = async (params?: Partial<SearchParams>) => {
    try {
      loading.value = true
      const queryParams = {
        ...searchParams.value,
        ...params,
        page: currentPage.value,
        pageSize: pageSize.value,
      }

      const response = await clubApi.getClubList(queryParams)
      const data = response.data.data

      clubs.value = data.list
      total.value = data.total
      currentPage.value = data.page

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
        pageSize: pageSize.value,
      }

      const response = await clubApi.searchClubs(keyword, queryParams)
      const data = response.data.data

      clubs.value = data.list
      total.value = data.total
      currentPage.value = 1
      searchParams.value.keyword = keyword

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

  // 重置搜索
  const resetSearch = () => {
    searchParams.value = {
      keyword: '',
      category: '',
      sortBy: 'hot',
    }
    currentPage.value = 1
  }

  // 分页
  const setPage = (page: number) => {
    currentPage.value = page
  }

  // 设置页面大小
  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
  }

  return {
    // 状态
    clubs,
    hotClubs,
    latestClubs,
    recommendedClubs,
    categories,
    currentClub,
    total,
    currentPage,
    pageSize,
    loading,
    searchParams,
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
    resetSearch,
    setPage,
    setPageSize,
  }
})
