<template>
  <div class="club-detail-container">
    <div v-loading="loading" class="club-detail-content">
      <template v-if="club">
        <!-- 社团头部信息 -->
        <div class="club-header">
          <div class="club-cover">
            <el-image :src="club.coverImage" fit="cover" class="cover-image" />
            <div class="club-status-badge">
              <el-tag v-if="club.isHot" type="danger" size="large"> 🔥 热门社团 </el-tag>
            </div>
          </div>

          <div class="club-info">
            <h1 class="club-title">{{ club.name }}</h1>
            <div class="club-meta">
              <div class="meta-item">
                <el-icon><User /></el-icon>
                <span>负责人：{{ club.adminName }}</span>
              </div>
              <div class="meta-item">
                <el-icon><UserFilled /></el-icon>
                <span>成员数：{{ club.currentMembers }}/{{ club.maxMembers }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Calendar /></el-icon>
                <span>成立时间：{{ formatDate(club.createdAt) }}</span>
              </div>
            </div>

            <div class="club-tags">
              <el-tag :type="getCategoryType(club.category)" size="large">
                {{ club.category }}
              </el-tag>
              <el-tag v-for="tag in club.tags" :key="tag" size="large" plain>
                {{ tag }}
              </el-tag>
            </div>

            <div class="club-actions">
              <el-button
                type="primary"
                size="large"
                :disabled="club.currentMembers >= club.maxMembers"
                @click="handleApply"
              >
                {{ club.currentMembers >= club.maxMembers ? '已满员' : '申请加入' }}
              </el-button>
              <el-button
                :icon="isFavorited ? StarFilled : Star"
                size="large"
                @click="toggleFavorite"
              >
                {{ isFavorited ? '已收藏' : '收藏' }}
              </el-button>
              <el-button :icon="Share" size="large" @click="handleShare"> 分享 </el-button>
            </div>
          </div>
        </div>

        <!-- 社团详细信息 -->
        <div class="club-content">
          <el-row :gutter="24">
            <el-col :span="16">
              <!-- 社团介绍 -->
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Document /></el-icon> 社团介绍
                  </h3>
                </template>
                <div class="club-description">
                  <p>{{ club.description }}</p>
                  <p>{{ club.details }}</p>
                </div>
              </el-card>

              <!-- 活动动态 -->
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Bell /></el-icon> 最新动态
                  </h3>
                </template>
                <el-timeline>
                  <el-timeline-item
                    v-for="activity in club.activities"
                    :key="activity.id"
                    :timestamp="activity.time"
                  >
                    <h4>{{ activity.title }}</h4>
                    <p>{{ activity.description }}</p>
                  </el-timeline-item>
                </el-timeline>
              </el-card>
            </el-col>

            <el-col :span="8">
              <!-- 社团统计 -->
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><DataAnalysis /></el-icon> 社团数据
                  </h3>
                </template>
                <div class="stats-grid">
                  <div class="stat-item">
                    <div class="stat-number">{{ club.currentMembers }}</div>
                    <div class="stat-label">当前成员</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ Math.floor(Math.random() * 50) + 10 }}</div>
                    <div class="stat-label">累计活动</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ Math.floor(Math.random() * 20) + 5 }}</div>
                    <div class="stat-label">获得荣誉</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ Math.floor(Math.random() * 100) + 50 }}</div>
                    <div class="stat-label">影响人次</div>
                  </div>
                </div>
              </el-card>

              <!-- 联系方式 -->
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Phone /></el-icon> 联系我们
                  </h3>
                </template>
                <div class="contact-info">
                  <div class="contact-item">
                    <el-icon><Message /></el-icon>
                    <span>QQ群：{{ club.qq }}</span>
                  </div>
                  <div class="contact-item">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>微信群：扫码加入</span>
                  </div>
                  <div class="contact-item">
                    <el-icon><Location /></el-icon>
                    <span>活动地点：{{ club.location }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </template>

      <!-- 空状态 -->
      <el-empty v-else-if="!loading" description="社团不存在或已被删除" :image-size="120">
        <el-button type="primary" @click="$router.push('/')"> 返回首页 </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  UserFilled,
  Calendar,
  Star,
  StarFilled,
  Share,
  Document,
  Bell,
  DataAnalysis,
  Phone,
  Message,
  ChatDotRound,
  Location,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import type { Club, ClubCategory } from '@/types'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()
const authStore = useAuthStore()

const loading = ref(false)
const club = ref<Club | null>(null)
const isFavorited = computed(() => club.value?.isFavorite || false)

// 获取分类标签类型
const getCategoryType = (category: ClubCategory) => {
  const typeMap: Record<ClubCategory, string> = {
    学术科技: 'primary',
    文艺体育: 'success',
    志愿服务: 'warning',
    创新创业: 'danger',
    其他: 'info',
  }
  return typeMap[category] || 'info'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// TODO：申请加入社团
const handleApply = () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  // TODO：调用申请加入社团API
  clubStore.applyToClub(club.value!.id, '我想加入这个社团')

  ElMessage.success('申请已提交，请等待审核')
}

// 切换收藏状态
const toggleFavorite = () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  if (isFavorited.value) {
    clubStore.unfavoriteClub(club.value!.id)
    club.value!.isFavorite = false
  } else {
    clubStore.favoriteClub(club.value!.id)
    club.value!.isFavorite = true
  }
}

// 分享功能
const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: club.value?.name,
      text: club.value?.description,
      url: window.location.href,
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(window.location.href)
    ElMessage.success('链接已复制到剪贴板')
  }
}

// 获取社团详情
const fetchClubDetail = async () => {
  const clubId = route.params.id as string
  if (!clubId) return

  try {
    loading.value = true
    club.value = await clubStore.fetchClubDetail(clubId)
  } catch (error) {
    console.error('获取社团详情失败:', error)
    ElMessage.error('获取社团详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchClubDetail()
})
</script>

<style scoped>
.club-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.club-header {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.club-cover {
  position: relative;
  width: 300px;
  height: 200px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.club-status-badge {
  position: absolute;
  top: 12px;
  left: 12px;
}

.club-info {
  flex: 1;
}

.club-title {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}

.club-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.meta-item .el-icon {
  margin-right: 8px;
  color: #909399;
}

.club-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.club-actions {
  display: flex;
  gap: 12px;
}

.club-content {
  margin-top: 24px;
}

.content-card {
  margin-bottom: 24px;
}

.content-card :deep(.el-card__header) {
  padding: 16px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.content-card h3 {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.content-card h3 .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.club-description {
  line-height: 1.8;
  color: #606266;
}

.club-description ul {
  margin: 16px 0;
  padding-left: 20px;
}

.club-description li {
  margin: 8px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #606266;
}

.contact-item .el-icon {
  margin-right: 8px;
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .club-header {
    flex-direction: column;
    text-align: center;
  }

  .club-cover {
    width: 100%;
    height: 200px;
  }

  .club-actions {
    justify-content: center;
  }
}
</style>
