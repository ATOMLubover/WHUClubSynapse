<template>
  <div class="home-container">
    <!-- 轮播横幅 -->
    <el-carousel
      height="240px"
      :interval="5000"
      indicator-position="outside"
      class="banner-carousel"
    >
      <el-carousel-item v-for="(banner, index) in banners" :key="index" class="banner-item">
        <div class="banner-content">
          <h2>{{ banner.title }}</h2>
          <p>{{ banner.description }}</p>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧内容区 -->
      <div class="content-left">
        <!-- 搜索区域 -->
        <div class="search-section">
          <el-card class="search-card">
            <div class="search-input-group">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索社团名称、分类、关键词..."
                size="large"
                @keyup.enter="handleSearch"
                clearable
              >
                <template #prepend>
                  <el-icon><Search /></el-icon>
                </template>
                <template #append>
                  <el-button type="primary" @click="handleSearch" :loading="searchLoading">
                    搜索
                  </el-button>
                </template>
              </el-input>
              
              <!-- AI智能搜索选项 -->
              <div class="ai-search-option">
                <el-checkbox 
                  v-model="useAiSearch" 
                  :disabled="!isAiSearchEnabled"
                  @change="handleAiSearchChange"
                >
                  <el-icon><ChatDotRound /></el-icon>
                  询问AI智能体
                  <el-tooltip 
                    content="启用AI智能搜索，获得更精准的搜索结果和建议" 
                    placement="top"
                  >
                    <el-icon class="help-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </el-checkbox>
              </div>
            </div>
          </el-card>
        </div>

        <!-- AI搜索结果 -->
        <div v-if="showAiResult && aiSearchResult" class="ai-search-result">
          <el-card class="ai-result-card">
            <template #header>
              <div class="ai-result-header">
                <el-icon class="ai-icon"><ChatDotRound /></el-icon>
                <span>AI智能回答</span>
                <el-button 
                  type="text" 
                  size="small" 
                  @click="hideAiResult"
                  class="close-btn"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="ai-result-content">
              <div class="ai-answer" v-html="formatAiAnswer(aiSearchResult.answer)"></div>
              <div v-if="aiSearchResult.source && aiSearchResult.source.length > 0" class="ai-sources">
                <div class="sources-title">参考来源：</div>
                <div class="sources-list">
                  <div 
                    v-for="source in aiSearchResult.source" 
                    :key="source.id" 
                    class="source-item"
                  >
                    <el-icon><Document /></el-icon>
                    <span>{{ source.metadata.source }} (第{{ source.metadata.page }}页)</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 分类导航 -->
        <div class="category-nav">
          <el-tabs
            v-model="clubStore.activeCategory"
            @tab-change="handleCategoryChange"
            class="category-tabs"
          >
            <el-tab-pane label="全部" name="">
              <template #label>
                全部
                <el-badge :value="getTotalCount()" class="category-badge" />
              </template>
            </el-tab-pane>
            <el-tab-pane
              v-for="category in clubStore.categoriesList"
              :key="category.category_id"
              :label="category.name"
              :name="category.category_id"
            >
              <template #label>
                {{ category.name }}
                <el-badge
                  :value="
                    clubStore.categoriesList.find((c) => c.category_id === category.category_id)
                      ?.count || 0
                  "
                  class="category-badge"
                />
              </template>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 筛选和排序 -->
        <div class="filter-bar">
          <div class="filter-left">
            <el-select
              v-model="sortBy"
              placeholder="排序方式"
              @change="handleSortChange"
              style="width: 120px"
            >
              <el-option label="按热度" value="hot" />
              <el-option label="按时间" value="time" />
              <el-option label="按成员数" value="members" />
            </el-select>
          </div>
          <div class="filter-right">
            <span class="result-count"> 共找到 {{ clubStore.globalPageData.total }} 个社团 </span>
          </div>
        </div>

        <!-- 社团列表 -->
        <div v-loading="clubStore.loading" class="club-grid">
          <div v-for="club in clubStore.clubs" :key="club.club_id" class="club-item">
            <ClubCard :club="club" />
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-if="!clubStore.loading && clubStore.clubs.length === 0"
          description="暂无社团数据"
          :image-size="120"
        />

        <!-- 分页 -->
        <div v-if="clubStore.globalPageData.total > 0" class="pagination-container">
          <el-pagination
            v-model:current-page="clubStore.globalPageData.currentPage"
            :page-size="clubStore.globalPageData.pageSize"
            :total="clubStore.globalPageData.total"
            layout="prev, pager, next, jumper, total"
            @current-change="handlePageChange"
          />
        </div>
      </div>

      <!-- 右侧功能区 -->
      <div class="content-right">
        <!-- 热门排行 -->
        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>热门排行</span>
            </div>
          </template>
          <div class="hot-list">
            <div
              v-for="(club, index) in clubStore.hotClubs"
              :key="club.club_id"
              class="hot-item"
              @click="goToClub(club.club_id)"
            >
              <div class="hot-rank">{{ index + 1 }}</div>
              <div class="hot-info">
                <div class="hot-name">{{ club.club_name }}</div>
                <div class="hot-members">{{ club.member_count }}人</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 最新发布 -->
        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>最新发布</span>
            </div>
          </template>
          <div class="latest-list">
            <div
              v-for="club in clubStore.latestClubs"
              :key="club.club_id"
              class="latest-item"
              @click="goToClub(club.club_id)"
            >
              <div class="latest-info">
                <div class="latest-name">{{ club.club_name }}</div>
                <div class="latest-time">{{ formatDate(club.created_at) }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 推荐给你 -->
        <el-card v-if="authStore.isLoggedIn" class="sidebar-card">
          <template #header>
            <div class="card-header">
              <el-icon><Star /></el-icon>
              <span>推荐给你</span>
            </div>
          </template>
          <div class="recommend-list">
            <div
              v-for="club in clubStore.recommendedClubs"
              :key="club.club_id"
              class="recommend-item"
              @click="goToClub(club.club_id)"
            >
              <el-image :src="club.logo_url" fit="cover" class="recommend-image" />
              <div class="recommend-info">
                <div class="recommend-name">{{ club.club_name }}</div>
                <el-tag :type="getCategoryType(club.category)" size="small">
                  {{ club.category }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 快速入口 -->
        <el-card v-if="authStore.isLoggedIn" class="sidebar-card">
          <template #header>
            <div class="card-header">
              <el-icon><Menu /></el-icon>
              <span>快速入口</span>
            </div>
          </template>
          <div class="quick-links">
            <el-button
              v-for="link in quickLinks"
              :key="link.path"
              :icon="link.icon"
              @click="$router.push(link.path)"
              class="quick-link"
              text
            >
              {{ link.label }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  TrendCharts,
  Clock,
  Star,
  Menu,
  Document,
  UserFilled,
  Collection,
  Search,
  ChatDotRound,
  QuestionFilled,
  Close,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import ClubCard from '@/components/Club/ClubCard.vue'
import type { ClubCategory, SmartSearchResponse } from '@/types'
import { resetMockData } from '@/utils/mockData'
import { ElMessage } from 'element-plus'
import { smartSearch } from '@/api/ai-search'
import { isAiSearchEnabled as checkAiSearchEnabled } from '@/config/ai-search'

const router = useRouter()
const clubStore = useClubStore()
const authStore = useAuthStore()

// 开发模式标识
const isDev = import.meta.env.DEV

// 轮播横幅数据
const banners = ref([
  {
    title: '欢迎来到WHU社团联盟',
    description: '发现你的兴趣，找到志同道合的伙伴',
  },
  {
    title: '精彩社团活动等你参与',
    description: '丰富的社团活动，让大学生活更充实',
  },
  {
    title: '展示才华的舞台',
    description: '加入社团，展现你的独特才能',
  },
])

// TODO:分类数据
const categories = ref<ClubCategory[]>([])

// 排序方式
const sortBy = ref<string>('hot')

// 快速链接
const quickLinks = ref([
  { label: '我的申请', path: '/user/applications', icon: Document },
  { label: '我的社团', path: '/user/clubs', icon: UserFilled },
  { label: '我的收藏', path: '/user/favorites', icon: Collection },
])

// 搜索相关
const searchKeyword = ref('')
const searchLoading = ref(false)
const showAiResult = ref(false)
const aiSearchResult = ref<SmartSearchResponse | null>(null)
const useAiSearch = ref(false)
const isAiSearchEnabled = computed(() => checkAiSearchEnabled())

// 计算总数
const getTotalCount = () => {
  if (!clubStore.categoriesList || clubStore.categoriesList.length === 0) {
    return 0
  }
  return clubStore.categoriesList.reduce((sum, category) => sum + (category.count || 0), 0)
}

// 获取分类标签类型
const getCategoryType = (category: number) => {
  const typeMap: Record<number, string> = {
    0: 'primary',
    1: 'success',
    2: 'warning',
    3: 'danger',
    4: 'info',
  }
  return typeMap[category] || 'info'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

// 处理分类切换
const handleCategoryChange = (category: string) => {
  clubStore.setActiveCategory(category)
  clubStore.setSearchParams({ category: category as number | '' }) // 类型断言
  clubStore.fetchClubs()
}

// 处理排序切换
const handleSortChange = (sort: string) => {
  sortBy.value = sort
  clubStore.setSearchParams({ sortBy: sort as 'hot' | 'time' | 'members' })
  clubStore.fetchClubs()
}

// 处理分页切换
const handlePageChange = (page: number) => {
  clubStore.setGlobalPage(page)
  clubStore.fetchClubs()
}

// 跳转到社团详情
const goToClub = (clubId: string) => {
  console.log('点击热门/最新社团，准备跳转到详情页:', clubId)
  console.log('当前路由:', router.currentRoute.value.path)
  try {
    router.push(`/club/${clubId}`)
    console.log('路由跳转成功')
  } catch (error) {
    console.error('路由跳转失败:', error)
  }
}

// 处理搜索
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.error('请输入搜索关键词')
    return
  }

  searchLoading.value = true
  try {
    if (useAiSearch.value) {
      // 调用AI搜索
      const result = await smartSearch({ query: searchKeyword.value })
      aiSearchResult.value = result
      showAiResult.value = true
    } else {
      // 普通搜索，跳转到搜索页面
      router.push({
        path: '/search',
        query: { keyword: searchKeyword.value.trim() }
      })
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请稍后再试')
  } finally {
    searchLoading.value = false
  }
}

// 处理AI搜索选项变化
const handleAiSearchChange = () => {
  // AI搜索选项变化的处理逻辑
  console.log('AI搜索选项变化:', useAiSearch.value)
}

// 隐藏AI搜索结果
const hideAiResult = () => {
  showAiResult.value = false
  aiSearchResult.value = null
}

// 格式化AI回答
const formatAiAnswer = (answer: string) => {
  // 简单的Markdown格式化
  return answer
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

// 初始化数据
onMounted(async () => {
  try {
    console.log('HomeView开始初始化')

    // 等待分类数据加载完成（App.vue中已开始加载）
    if (clubStore.categoriesLoading) {
      console.log('等待分类数据加载完成...')
      // 等待分类加载完成
      let retries = 0
      while (clubStore.categoriesLoading && retries < 50) {
        await new Promise((resolve) => setTimeout(resolve, 100))
        retries++
      }
    }

    // 先获取社团列表
    await clubStore.fetchClubs()
    console.log('社团列表加载完成')

    if (authStore.isLoggedIn) {
      await clubStore.fetchFavoriteClubs()
    }

    // 并行获取侧边栏数据（不阻塞主列表显示）
    Promise.all([
      clubStore.fetchHotClubs(5),
      clubStore.fetchLatestClubs(5),
      // authStore.isLoggedIn ? clubStore.fetchRecommendedClubs(3) : Promise.resolve(),
    ]).catch((error) => {
      console.error('侧边栏数据加载失败:', error)
      // 不影响主界面显示
    })
  } catch (error) {
    console.error('HomeView初始化失败:', error)
    ElMessage.error('页面初始化失败，请刷新重试')
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
}

/* 轮播横幅 */
.banner-carousel {
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
}

.banner-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-content {
  text-align: center;
}

.banner-content h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.banner-content p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

/* 主要内容区域 */
.main-content {
  display: flex;
  gap: 24px;
}

.content-left {
  flex: 1;
}

.content-right {
  width: 280px;
  flex-shrink: 0;
}

/* 搜索区域 */
.search-section {
  margin-bottom: 16px;
}

.search-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.search-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-input-group .el-input {
  flex: 1;
}

.ai-search-option {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.ai-search-option .el-checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ai-search-option .el-icon {
  color: #409eff;
}

.help-icon {
  color: #909399;
  margin-left: 4px;
  cursor: help;
  font-size: 14px;
}

/* AI搜索结果 */
.ai-search-result {
  margin-bottom: 16px;
}

.ai-result-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
}

.ai-result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid #e4e7ed;
}

.ai-result-header .ai-icon {
  color: #409eff;
  margin-right: 8px;
  font-size: 18px;
}

.ai-result-header span {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
}

.close-btn {
  color: #909399;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s;
}

.close-btn:hover {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

.ai-result-content {
  padding: 20px;
  background: white;
}

.ai-answer {
  margin-bottom: 16px;
  line-height: 1.6;
  color: #303133;
  font-size: 14px;
}

.ai-answer strong {
  color: #409eff;
  font-weight: 600;
}

.ai-answer em {
  color: #67c23a;
  font-style: italic;
}

.ai-sources {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.sources-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.source-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  border: 1px solid #e4e7ed;
}

.source-item .el-icon {
  margin-right: 6px;
  color: #909399;
}

/* 分类导航 */
.category-nav {
  margin-bottom: 16px;
}

.category-tabs :deep(.el-tabs__nav-wrap) {
  background-color: #fff;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-badge {
  margin-left: 8px;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-count {
  color: #909399;
  font-size: 14px;
}

/* 社团网格 */
.club-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.club-item {
  height: 100%;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

/* 侧边栏卡片 */
.sidebar-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  font-weight: 600;
}

.card-header .el-icon {
  margin-right: 8px;
}

/* 热门排行 */
.hot-list {
  max-height: 300px;
  overflow-y: auto;
}

.hot-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s;
}

.hot-item:hover {
  background-color: #f8f9fa;
}

.hot-item:last-child {
  border-bottom: none;
}

.hot-rank {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.hot-rank:nth-child(1) {
  background-color: #f56c6c;
}

.hot-rank:nth-child(2) {
  background-color: #e6a23c;
}

.hot-rank:nth-child(3) {
  background-color: #67c23a;
}

.hot-info {
  flex: 1;
}

.hot-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hot-members {
  font-size: 12px;
  color: #909399;
}

/* 最新发布 */
.latest-item {
  padding: 8px 0;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s;
}

.latest-item:hover {
  background-color: #f8f9fa;
}

.latest-item:last-child {
  border-bottom: none;
}

.latest-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.latest-time {
  font-size: 12px;
  color: #909399;
}

/* 推荐列表 */
.recommend-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.3s;
}

.recommend-item:hover {
  background-color: #f8f9fa;
}

.recommend-item:last-child {
  border-bottom: none;
}

.recommend-image {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  margin-right: 12px;
  flex-shrink: 0;
}

.recommend-info {
  flex: 1;
}

.recommend-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 快速链接 */
.quick-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-link {
  justify-content: flex-start;
  padding: 8px 12px;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }

  .content-right {
    width: 100%;
  }

  .club-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  .filter-bar {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .search-input-group {
    gap: 8px;
  }
  
  .ai-result-header {
    padding: 12px 16px;
  }
  
  .ai-result-content {
    padding: 16px;
  }
  
  .sources-list {
    gap: 6px;
  }
  
  .source-item {
    padding: 6px 10px;
    font-size: 11px;
  }
}
</style>
