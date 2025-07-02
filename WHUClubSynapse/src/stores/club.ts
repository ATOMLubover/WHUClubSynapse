import { ref, computed, reactive } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'
import * as clubApi from '@/api/club'
import type { Club, ClubCategory, SearchParams, PaginatedData, ClubPost, ClubApplication } from '@/types'
import { useAuthStore } from '@/stores/auth'

export const useClubStore = defineStore('club', () => {
  const MAX_MEMBER_NUM=50
  const authStore = useAuthStore()
  // 状态
  const clubs = ref<Club[]>([])
  const searchResult=ref<Club[]>([])
  const favoriteClubs = ref<Club[]>([])
  const latestClubs = ref<Club[]>([])
  const recommendedClubs = ref<Club[]>([])
  const categoriesList = ref<ClubCategory[]>([]) // 新增：分类列表
  const currentClub = ref<Club | null>(null)
  const joinedClubs = ref<Club[]>([])
  const managedClubs = ref<Club[]>([])
  const applications=ref<ClubApplication[]>([])
  
  // 新增：全局帖子数组
  const clubposts = ref<ClubPost[]>([])
  const currentClubPosts = ref<ClubPost[]>([]) // 当前社团的帖子

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

  // 分别管理不同操作的loading状态
  const loading = ref(false) // 主要用于clubs列表
  const categoriesLoading = ref(false) // 用于分类加载
  const detailLoading = ref(false) // 用于详情加载
  const postsLoading = ref(false) // 用于帖子加载
  
  const searchParams = ref<SearchParams>({
    keyword: '',
    category: '',
    sortBy: 'time',
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
      const data = response
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

  //获取社团基本信息
  const fetchClubBasic=async(clubId:string)=>{
    try{
      const response=await clubApi.getClubBasic(clubId)
      return response
    }
    catch(error){
      console.error('获取社团基本信息失败:', error)
      throw error
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
      const data = response

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
      detailLoading.value = true
      const response = await clubApi.getClubDetail(id)
      currentClub.value = response
      return response
    } catch (error) {
      console.error('获取社团详情失败:', error)
      ElMessage.error('获取社团详情失败')
      throw error
    } finally {
      detailLoading.value = false
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


  // 获取社团分类统计
  // 获取社团分类统计（保留以支持统计功能）
  const fetchCategoriesStats = async () => {
    try {
      categoriesLoading.value = true
      const response = await clubApi.getClubCategories()
      // 这里可以更新统计数据，暂时保留接口
      return response.data.data
    } catch (error) {
      console.error('获取社团分类统计失败:', error)
      throw error
    } finally {
      categoriesLoading.value = false
    }
  }

  // 获取社团分类列表
  const fetchCategoriesList = async () => {
    try {
      categoriesLoading.value = true
      const response = await clubApi.getClubCategoriesList()
      categoriesList.value = response
      console.log('社团分类列表已加载:', response)
      return response
    } catch (error) {
      console.error('获取社团分类列表失败:', error)
      ElMessage.error('获取社团分类列表失败')
      throw error
    } finally {
      categoriesLoading.value = false
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
      await fetchFavoriteClubs()
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
      await fetchFavoriteClubs()
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

      favoriteClubs.value = response.list
      favoriteClubs.value.forEach((club) => {
        const clubIndex = clubs.value.findIndex((c) => c.club_id === club.club_id)
        if (clubIndex !== -1) {
          clubs.value[clubIndex].isFavorite = true
        }
      })

      return response;
    }
    catch (error){
      console.error('获取收藏社团失败:', error)
      throw error
    }

  }

  //获取加入社团申请列表
  const fetchPendingClubApplications=async(params:{
    page?:number,
    pageSize?:number,
    status?:string,
    keyword?:string,
  })=>{
    try{
      const response=await clubApi.getClubApplications(params);
      if(clubs.value.length==0){
        await fetchClubs()
      }
      applications.value=response.list
      clubs.value.forEach((club)=>{
        if(applications.value.some((application)=>application.club_id==club.club_id && application.status=="pending")){
          club.status="pending"
        }
      })
      let list=applications.value
      if(params.page!=null&&params.pageSize!=null){
        list=list.slice((params.page-1)*params.pageSize,params.page*params.pageSize)
      }

      list.forEach(async(application)=>{
        const club=await fetchClubBasic(application.club_id)
        if(club){
          application.club=club
        }
      })

      return {
        list:list,
        total:response.total,
        page:params.page||1,
        pageSize:params.pageSize||10,
      }
    }
    catch (error){
      console.error('获取加入社团申请列表失败:', error)
      throw error
    }
  }

 
  // 申请创建社团
  const applyToCreateClub = async (data: {
    name: string
    desc: string
    requirements: string
    category_id: number
    tags: string[]
  }) => {
    try {
      const response = await clubApi.applyToCreateClub(data)
      return response.data.data
    } catch (error) {
      console.error('申请创建社团失败:', error)
      ElMessage.error('申请创建社团失败')
      throw error
    }
  }

  // 获取用户创建的社团申请列表
  const fetchUserCreatedApplications = async () => {
    try {
      const response = await clubApi.getUserCreatedApplications()
      return response
    } catch (error) {
      console.error('获取用户创建申请失败:', error)
      ElMessage.error('获取用户创建申请失败')
      throw error
    }
  }

  // 获取用户已加入的社团
  const fetchJoinedClubs = async (params?: { page?: number; pageSize?: number }) => {
    try {
      const response = await clubApi.getJoinedClubs(params)
      let list: Club[]
      if(params?.page!=null&&params.pageSize!=null){
      list=response.list.slice((params.page-1)*params.pageSize,params.page*params.pageSize)}
      else{
      list=response.list
  }
      joinedClubs.value = response.list
      return {
        list:list,
        total:response.total,
        page:params?.page||1,
        pageSize:params?.pageSize||12,
      }
    } catch (error) {
      console.error('获取已加入社团失败:', error)
      ElMessage.error('获取已加入社团失败')
      throw error
    }
  }

  // 获取用户管理的社团
  const fetchManagedClubs = async (params?: { page?: number; pageSize?: number }) => {
    try {
      if(joinedClubs.value.length==0){
        const response = await clubApi.getJoinedClubs(params)
        joinedClubs.value = response.list
      }
      managedClubs.value=joinedClubs.value.filter((club)=>club.leader_id==authStore.user?.user_id)
      return {
        list:managedClubs.value,
        total:managedClubs.value.length,
        page:params?.page||1,
        pageSize:params?.pageSize||12,
      }
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
      sortBy: 'time',
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

  // 帖子相关操作方法

  // 获取特定社团的帖子
  const fetchClubPosts = async (clubId: string, page: number = 1, pageSize: number = 10) => {
    try {
      postsLoading.value = true
      const response = await clubApi.getClubPosts(clubId, page, pageSize)
      currentClubPosts.value = response.list
      return response
    } catch (error) {
      console.error('获取社团帖子失败:', error)
      ElMessage.error('获取社团帖子失败')
      throw error
    } finally {
      postsLoading.value = false
    }
  }


  // 根据ID查找帖子
  const getPostById = (postId: string): ClubPost | undefined => {
    return clubposts.value.find(post => post.post_id === postId)
  }

  return {
    // 状态
    MAX_MEMBER_NUM,
    clubs,
    searchResult,
    favoriteClubs,
    latestClubs,
    recommendedClubs,
    joinedClubs,
    managedClubs,
    applications,
    // categories,
    categoriesList, // 新增：分类列表
    currentClub,
    globalPageData,
    searchPageData,
    loading,
    categoriesLoading, // 新增：分类加载状态
    detailLoading, // 新增：详情加载状态
    postsLoading, // 新增：帖子加载状态
    searchParams,
    activeCategory,
    // 新增：帖子相关状态
    clubposts,
    currentClubPosts,
    // 计算属性
    totalPages,
    hasMore,
    // 方法
    fetchClubs,
    searchClubs,
    fetchClubDetail,
    fetchLatestClubs,
    fetchCategoriesStats, // 获取分类统计
    fetchCategoriesList, // 获取分类列表
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
    fetchJoinedClubs,
    fetchManagedClubs,
    quitClub,
    fetchClubPosts,
    getPostById,
    updateClub,
    applyToCreateClub,
    fetchUserCreatedApplications,
    fetchPendingClubApplications,
  }
})
