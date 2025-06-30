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
              v-for="category in categories"
              :key="category"
              :label="category"
              :name="category"
            >
              <template #label>
                {{ category }}
                <el-badge :value="clubStore.categories[category] || 0" class="category-badge" />
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
            <!-- 开发模式重置按钮 -->
            <el-button
              v-if="isDev"
              type="warning"
              size="small"
              @click="resetData"
              style="margin-left: 10px"
            >
              🔄 重置数据
            </el-button>
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
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import ClubCard from '@/components/Club/ClubCard.vue'
import type { ClubCategory } from '@/types'
import { resetMockData } from '@/utils/mockData'
import { ElMessage } from 'element-plus'

const router = useRouter()
const clubStore = useClubStore()
const authStore = useAuthStore()

// 开发模式标识
const isDev = import.meta.env.DEV

// 重置数据函数
const resetData = async () => {
  try {
    resetMockData()
    await clubStore.fetchClubs()
    ElMessage.success('数据已重置')
  } catch (error) {
    console.error('重置数据失败:', error)
    ElMessage.error('重置数据失败')
  }
}

// 轮播横幅数据
//TODO: 从后端获取轮播横幅数据？
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

// 分类数据
const categories = ref<ClubCategory[]>(['学术科技', '文艺体育', '志愿服务', '创新创业', '其他'])

// 排序方式
const sortBy = ref<string>('hot')

// 快速链接
const quickLinks = ref([
  { label: '我的申请', path: '/user/applications', icon: Document },
  { label: '我的社团', path: '/user/clubs', icon: UserFilled },
  { label: '我的收藏', path: '/api/club/my_favorites', icon: Collection },
])

// 计算总数
const getTotalCount = () => {
  return Object.values(clubStore.categories).reduce((sum, count) => sum + count, 0)
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
  clubStore.setSearchParams({ category: category as ClubCategory | '' }) // 类型断言
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

// 初始化数据
onMounted(async () => {
  try {
    clubStore.fetchClubs()

    if (authStore.isLoggedIn) {
      clubStore.fetchFavoriteClubs()
    }
    // 并行获取数据
    await Promise.all([
      clubStore.fetchCategories(),
      clubStore.fetchHotClubs(5),
      clubStore.fetchLatestClubs(5),
      authStore.isLoggedIn ? clubStore.fetchRecommendedClubs(3) : Promise.resolve(),
    ])
  } catch (error) {
    console.error('初始化数据失败:', error)
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
}
</style>
