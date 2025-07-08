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
                  :disabled="!isAiSearchEnabled || !aiAvailable"
                  @change="handleAiSearchChange"
                >
                  <el-icon><ChatDotRound /></el-icon>
                  询问AI智能体
                  <el-tooltip
                    :content="
                      aiAvailable
                        ? '启用AI智能搜索，获得更精准的搜索结果和建议'
                        : 'AI服务暂时不可用，请稍后重试'
                    "
                    placement="top"
                  >
                    <el-icon class="help-icon"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </el-checkbox>
                <!-- AI状态指示器 -->
                <el-tag v-if="!aiAvailable" type="warning" size="small" class="ai-status-tag">
                  AI不可用
                </el-tag>
                <!-- AI连通性测试按钮 -->
                <el-button
                  type="info"
                  size="small"
                  @click="testAiConnectivity"
                  class="ai-test-btn"
                  style="margin-left: 12px"
                >
                  AI连通性测试
                </el-button>
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
                <el-button type="text" size="small" @click="hideAiResult" class="close-btn">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
            <div class="ai-result-content">
              <div class="ai-answer">
                <SmartStreamingRenderer :content="aiSearchResult.answer" />
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
                <el-badge :value="clubStore.getTotalClubCount" class="category-badge" />
              </template>
            </el-tab-pane>
            <el-tab-pane
              v-for="category in clubStore.categoriesList"
              :key="category.category_id"
              :label="category.name"
              :name="category.category_id.toString()"
            >
              <template #label>
                {{ category.name }}
                <el-badge
                  :value="clubStore.getCategoryCount(category.category_id)"
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
        <!-- 最新发布 -->
        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>最新发布</span>
            </div>
          </template>
          <div>
            <div
              v-for="(club, index) in clubStore.latestClubs"
              :key="club.club_id"
              class="hot-item"
              @click="goToClub(club.club_id)"
            >
              <div class="hot-rank">{{ index + 1 }}</div>
              <div class="hot-info">
                <div class="hot-name">{{ club.club_name }}</div>
                <div class="hot-members">{{ club.member_count }}人</div>
                <div class="latest-time">{{ formatDate(club.created_at) }}</div>
              </div>
            </div>
          </div>
        </el-card>


        <!-- 快速入口 -->
        <el-card v-if="authStore.isLoggedIn && !authStore.isGuest" class="sidebar-card">
          <template #header>
            <div class="card-header">
              <el-icon><Menu /></el-icon>
              <span>快速入口</span>
            </div>
          </template>
          <el-row v-for="link in quickLinks" :key="link.path" class="quick-links">
            <el-col :span="8">
              <el-button :icon="link.icon" @click="$router.push(link.path)" text class="quick-link">
                {{ link.label }}
              </el-button>
            </el-col>
          </el-row>
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
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import SmartStreamingRenderer from '@/components/SmartStreamingRenderer.vue'
import type { ClubCategory, SmartSearchResponse } from '@/types'
import { ElMessage } from 'element-plus'
import { smartSearchStream, checkAiServiceHealth } from '@/api/ai-search'
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

// 定义排序类型
type SortType = 'hot' | 'time' | 'members'

// 排序方式
const sortBy = ref<SortType>('time')

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
const aiAvailable = ref(true) // AI服务可用性状态
const isAiSearchEnabled = computed(() => checkAiSearchEnabled())

// 检查AI服务可用性
const checkAiAvailability = async () => {
  try {
    aiAvailable.value = await checkAiServiceHealth()
  } catch (error) {
    console.error('检查AI服务可用性失败:', error)
    aiAvailable.value = false
  }
}

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
const handleCategoryChange = async (categoryId: string) => {
  try {
    clubStore.setActiveCategory(categoryId)
    // 重置页码
    clubStore.setGlobalPage(1)
    // 重新获取社团列表
    await clubStore.fetchClubs({ sortBy: sortBy.value as SortType })
  } catch (error) {
    console.error('切换分类失败:', error)
    ElMessage.error('切换分类失败')
  }
}

// 处理排序方式改变
const handleSortChange = async () => {
  try {
    // 重置页码
    clubStore.setGlobalPage(1)
    // 重新获取社团列表
    await clubStore.fetchClubs({ sortBy: sortBy.value as SortType })
  } catch (error) {
    console.error('更改排序方式失败:', error)
    ElMessage.error('更改排序方式失败')
  }
}

// 处理页码改变
const handlePageChange = async (page: number) => {
  try {
    await clubStore.fetchClubs({ sortBy: sortBy.value as SortType }, page)
  } catch (error) {
    console.error('切换页面失败:', error)
    ElMessage.error('切换页面失败')
  }
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
      if (!aiAvailable.value) {
        ElMessage.error('AI服务暂时不可用，请稍后重试')
        return
      }

      console.log('开始AI搜索:', searchKeyword.value.trim())

      // 初始化AI搜索结果
      aiSearchResult.value = { answer: '', source: [] } as any
      showAiResult.value = true

      let answer = ''
      let sources: any[] = []

      smartSearchStream(
        { query: searchKeyword.value.trim() },
        {
          onSource: (src) => {
            console.log('收到source事件:', src)
            sources = src
            if (aiSearchResult.value) {
              ;(aiSearchResult.value as any).source = sources
            }
          },
          onToken: (token) => {
            console.log('HomeView收到token:', token, '类型:', typeof token)
            if (typeof token === 'string') {
              answer += token
              if (aiSearchResult.value) {
                ;(aiSearchResult.value as any).answer = answer
              }
            } else {
              console.error('HomeView收到非字符串token:', token)
            }
          },
          onEnd: () => {
            console.log('AI搜索完成')
            searchLoading.value = false
          },
          onError: (err) => {
            console.error('AI搜索错误:', err)
            searchLoading.value = false
            ElMessage.error(`AI搜索失败: ${err.message || '请稍后重试'}`)
            showAiResult.value = false
            aiSearchResult.value = null
          },
        },
      )
    } else {
      router.push({
        path: '/search',
        query: { keyword: searchKeyword.value.trim() },
      })
    }
  } catch (error: any) {
    console.error('搜索异常:', error)
    searchLoading.value = false
    ElMessage.error(`搜索失败: ${error.message || '请稍后再试'}`)
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

// AI连通性测试按钮逻辑
const testAiConnectivity = async () => {
  const loading = ElMessage({ message: '正在检测AI连通性...', type: 'info', duration: 0 })
  try {
    const healthy = await checkAiServiceHealth()
    ElMessage.closeAll()
    if (healthy) {
      ElMessage.success('AI服务可用')
      aiAvailable.value = true
    } else {
      ElMessage.error('AI服务不可用')
      aiAvailable.value = false
    }
  } catch (error) {
    ElMessage.closeAll()
    ElMessage.error('AI服务检测失败')
    aiAvailable.value = false
  }
}

// 初始化数据
onMounted(async () => {
  // 检查AI服务可用性
  await checkAiAvailability()
  categories.value = clubStore.categoriesList

  // 获取社团数据
  try {
    await clubStore.fetchClubs()
    await clubStore.fetchFavoriteClubs()
    await clubStore.fetchPendingClubApplications({})
    await clubStore.fetchJoinedClubs()
    await clubStore.fetchLatestClubs(6)
  } catch (error) {
    console.error('获取社团数据失败:', error)
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: calc(100vh - 60px);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* 轮播横幅 */
.banner-carousel {
  margin-bottom: 32px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.banner-item {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  height: 280px;
}

.banner-item:hover .banner-content {
  transform: translateY(-5px);
}

.banner-content {
  text-align: center;
  padding: 24px 36px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: 16px;
  transform: translateY(0);
  transition: transform 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  max-width: 600px;
}

.banner-content h2 {
  margin: 0 0 16px 0;
  font-size: 36px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
}

.banner-content p {
  margin: 0;
  font-size: 18px;
  opacity: 0.95;
  line-height: 1.6;
  font-weight: 300;
}

/* 主要内容区域 */
.main-content {
  display: flex;
  gap: 32px;
}

.content-left {
  flex: 1;
  min-width: 0;
}

.content-right {
  width: 320px;
  flex-shrink: 0;
}

/* 搜索区域 */
.search-section {
  margin-bottom: 28px;
}

.search-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.7);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  overflow: hidden;
}

.search-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}

.search-input-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-input-group :deep(.el-input) {
  --el-input-border-radius: 12px;
}

.search-input-group :deep(.el-input__wrapper) {
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.2),
    0 2px 12px rgba(0, 0, 0, 0.05);
  padding: 0 16px;
  height: 50px;
}

.search-input-group :deep(.el-input__inner) {
  font-size: 16px;
}

.search-input-group :deep(.el-input-group__prepend) {
  background-color: transparent;
}

.search-input-group :deep(.el-input-group__append .el-button) {
  border-top-right-radius: 12px;
  border-bottom-right-radius: 12px;
  padding: 12px 24px;
  font-weight: 500;
}

.ai-search-option {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(248, 249, 250, 0.5);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  transition: background-color 0.3s ease;
}

.ai-search-option:hover {
  background: rgba(240, 242, 245, 0.7);
}

.help-icon {
  margin-left: 6px;
  font-size: 14px;
  color: #909399;
}

.ai-test-btn {
  font-size: 12px;
  padding: 6px 12px;
  height: auto;
  border-radius: 6px;
}

/* AI搜索结果 */
.ai-search-result {
  margin-bottom: 28px;
}

.ai-result-card {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.ai-result-header {
  display: flex;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.ai-result-header .ai-icon {
  color: #6366f1;
  margin-right: 12px;
  font-size: 20px;
}

.ai-result-header span {
  font-weight: 600;
  color: #303133;
  font-size: 16px;
  flex: 1;
}

.close-btn {
  color: #909399;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.close-btn:hover {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

.ai-result-content {
  padding: 24px;
  background: white;
}

.ai-answer {
  margin-bottom: 16px;
  line-height: 1.7;
  color: #303133;
  font-size: 15px;
}

/* 分类导航 */
.category-nav {
  margin-bottom: 28px;
}

.category-tabs :deep(.el-tabs__nav-wrap) {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  padding: 8px 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.category-tabs :deep(.el-tabs__item) {
  padding: 14px 24px;
  font-size: 15px;
  transition: all 0.3s ease;
  font-weight: 500;
  color: #606266;
}

.category-tabs :deep(.el-tabs__item.is-active) {
  color: #6366f1;
  font-weight: 600;
}

.category-tabs :deep(.el-tabs__active-bar) {
  background-color: #6366f1;
  height: 3px;
  border-radius: 3px;
}

.category-badge {
  margin-left: 8px;
  font-size: 12px;
  height: 18px;
  line-height: 18px;
  border-radius: 9px;
  padding: 0 6px;
  background-color: rgba(99, 102, 241, 0.1);
  color: #6366f1;
  border: none;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.filter-left {
  flex: 1;
}

.filter-right {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

/* 社团网格 */
.club-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.club-item {
  height: 100%;
  transition: transform 0.3s ease;
}

.club-item:hover {
  transform: translateY(-5px);
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.pagination-container :deep(.el-pagination) {
  background: rgba(255, 255, 255, 0.8);
  padding: 16px 20px;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.pagination-container :deep(.el-pagination .el-pagination__total) {
  font-weight: 500;
}

.pagination-container :deep(.el-pagination .btn-prev),
.pagination-container :deep(.el-pagination .btn-next) {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  margin: 0 5px;
}

.pagination-container :deep(.el-pagination .el-pager li) {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  transition: all 0.3s ease;
  margin: 0 3px;
  min-width: 32px;
}

.pagination-container :deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  font-weight: 600;
  border: none;
}

.pagination-container :deep(.el-pagination .el-pager li:hover:not(.is-active)) {
  color: #6366f1;
}

/* 侧边栏卡片 */
.sidebar-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 28px;
  transition: transform 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  overflow: hidden;
}

.sidebar-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 10px 10px;
  font-weight: 600;
  font-size: 16px;
  color: #1f2937;
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.95), rgba(250, 250, 250, 0.95));
}

.card-header .el-icon {
  margin-right: 12px;
  color: #6366f1;
  font-size: 20px;
}

.hot-item {
  display: flex;
  align-items: center;
  padding: 14px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.hot-item:hover {
  background-color: rgba(99, 102, 241, 0.05);
  transform: translateX(4px);
}

.hot-rank {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  margin-right: 16px;
  flex-shrink: 0;
}

.hot-rank:nth-child(1) {
  background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
}

.hot-rank:nth-child(2) {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.hot-rank:nth-child(3) {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.hot-info {
  flex: 1;
}

.hot-name {
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.hot-members {
  font-size: 13px;
  color: #909399;
}

/* 最新发布 */
.latest-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid rgba(240, 240, 240, 0.5);
  transition: background-color 0.3s;
}

.latest-item:hover {
  background-color: rgba(99, 102, 241, 0.05);
}

.latest-item:last-child {
  border-bottom: none;
}

.latest-name {
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.latest-time {
  font-size: 13px;
  color: #909399;
}

/* 推荐列表 */
.recommend-list {
  padding: 16px;
}

.recommend-item {
  display: flex;
  align-items: center;
  padding: 14px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.3s ease;
  margin-bottom: 8px;
}

.recommend-item:hover {
  background-color: rgba(99, 102, 241, 0.05);
  transform: translateX(4px);
}

.recommend-item:last-child {
  margin-bottom: 0;
}

.recommend-image {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  margin-right: 16px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.8);
}

.recommend-info {
  flex: 1;
}

.recommend-name {
  font-size: 15px;
  color: #303133;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.recommend-info :deep(.el-tag) {
  border-radius: 6px;
  font-size: 12px;
  padding: 0 8px;
  height: 22px;
  line-height: 22px;
  border: none;
}

/* 快速链接 */
.quick-links {
  padding: 8px;
}

.quick-link {
  padding: 14px 16px !important;
  margin-bottom: 8px !important;
  border-radius: 12px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 12px !important;
  font-size: 15px !important;
  color: #4b5563 !important;
  transition: all 0.3s ease !important;
  text-align: left !important;
  font-weight: 500 !important;
}

.quick-link :deep(.el-icon) {
  margin-right: 0 !important;
  font-size: 18px !important;
  flex-shrink: 0 !important;
  color: #6366f1 !important;
}

.quick-link :deep(.el-button__content) {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  width: 100% !important;
}

.quick-link:hover {
  background-color: rgba(99, 102, 241, 0.1) !important;
  color: #6366f1 !important;
  transform: translateX(4px) !important;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }

  .content-right {
    width: 100%;
  }

  .club-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  }
}

@media (max-width: 640px) {
  .home-container {
    padding: 16px;
  }

  .banner-content h2 {
    font-size: 24px;
  }

  .banner-content p {
    font-size: 16px;
  }

  .club-grid {
    grid-template-columns: 1fr;
  }

  .filter-bar {
    flex-direction: column;
    gap: 12px;
  }

  .category-tabs :deep(.el-tabs__item) {
    padding: 8px 16px;
    font-size: 14px;
  }
}
</style>
