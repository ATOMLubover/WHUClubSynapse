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
              <el-button type="primary" size="large" :disabled="isDisabled" @click="handleApply">
                {{ getApplyButtonText() }}
              </el-button>
              <el-button
                v-if="authStore.isLoggedIn"
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
            <el-col :span="18">
              <!-- 社团介绍 -->
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Document /></el-icon> 社团介绍
                  </h3>
                </template>
                <div class="club-description">
                  <p>{{ club.description }}</p>
                  <div v-if="club.introduction" class="club-introduction">
                    <h4>详细介绍</h4>
                    <p>{{ club.introduction }}</p>
                  </div>
                  <div v-if="club.requirements" class="club-requirements">
                    <h4>加入要求</h4>
                    <p>{{ club.requirements }}</p>
                  </div>
                </div>
              </el-card>

              <!-- 社团公告 -->
              <el-card v-if="club.announcements && club.announcements.length > 0" class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Bell /></el-icon> 社团公告
                  </h3>
                </template>
                <div class="announcements-list">
                  <div v-for="(announcement, index) in club.announcements" :key="index" class="announcement-item">
                    <el-icon class="announcement-icon"><InfoFilled /></el-icon>
                    <span class="announcement-text">{{ announcement }}</span>
                  </div>
                </div>
              </el-card>

              <!-- 活动动态 -->
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Calendar /></el-icon> 最新动态
                  </h3>
                </template>
                <div v-if="club.activities && club.activities.length > 0">
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
                </div>
                <div v-else class="empty-activities">
                  <el-empty description="暂无动态" :image-size="80">
                    <el-button v-if="isUserManaged" type="primary" @click="goToEdit">添加动态</el-button>
                  </el-empty>
                </div>
              </el-card>
            </el-col>

            <el-col :span="6">
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
                  <div v-if="club.contactInfo?.qq" class="contact-item">
                    <el-icon><Message /></el-icon>
                    <span>QQ群：{{ club.contactInfo.qq }}</span>
                  </div>
                  <div v-if="club.contactInfo?.wechat" class="contact-item">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>微信号：{{ club.contactInfo.wechat }}</span>
                  </div>
                  <div v-if="club.contactInfo?.email" class="contact-item">
                    <el-icon><Message /></el-icon>
                    <span>邮箱：{{ club.contactInfo.email }}</span>
                  </div>
                  <div v-if="club.contactInfo?.phone" class="contact-item">
                    <el-icon><Phone /></el-icon>
                    <span>电话：{{ club.contactInfo.phone }}</span>
                  </div>
                  <div v-if="club.contactInfo?.address" class="contact-item">
                    <el-icon><Location /></el-icon>
                    <span>地址：{{ club.contactInfo.address }}</span>
                  </div>
                  <!-- 兼容旧数据 -->
                  <div v-if="club.qq && !club.contactInfo?.qq" class="contact-item">
                    <el-icon><Message /></el-icon>
                    <span>QQ群：{{ club.qq }}</span>
                  </div>
                  <div v-if="club.location && !club.contactInfo?.address" class="contact-item">
                    <el-icon><Location /></el-icon>
                    <span>活动地点：{{ club.location }}</span>
                  </div>
                </div>
              </el-card>

              <!-- 例会信息 -->
              <el-card v-if="club.meetingTime || club.meetingLocation" class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Calendar /></el-icon> 例会信息
                  </h3>
                </template>
                <div class="meeting-info">
                  <div v-if="club.meetingTime" class="meeting-item">
                    <el-icon><Clock /></el-icon>
                    <span>例会时间：{{ club.meetingTime }}</span>
                  </div>
                  <div v-if="club.meetingLocation" class="meeting-item">
                    <el-icon><Location /></el-icon>
                    <span>例会地点：{{ club.meetingLocation }}</span>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- AI氛围透视镜 - 独立一行 -->
          <el-row :gutter="24" style="margin-top: 24px;">
            <el-col :span="24">
              <el-card class="content-card ai-atmosphere-card">
                <template #header>
                  <h3>
                    <el-icon><View /></el-icon> AI氛围透视镜
                  </h3>
                </template>
                <div class="ai-atmosphere-container">
                  <AIClubAtmosphere 
                    :communication-content="communicationContent"
                  />
                </div>
              </el-card>
            </el-col>
          </el-row>
          <el-dialog v-model="showApplyDialog" title="申请加入新社团" width="600px">
            <el-form-item label="申请理由">
              <el-input
                v-model="reason"
                type="textarea"
                :rows="3"
                placeholder="请输入申请理由"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
            <template #footer>
              <el-button @click="showApplyDialog = false">取消</el-button>
              <el-button type="primary" @click="confirmApply()" :loading="createLoading">
                提交申请
              </el-button>
            </template>
          </el-dialog>
        </div>
      </template>

      <!-- 空状态 -->
      <el-empty v-else-if="!loading" description="社团不存在或已被删除" :image-size="120">
        <el-button type="primary" @click="$router.push('/')"> 返回首页 </el-button>
      </el-empty>
    </div>
    <div class="club-detail-bottom">
      <ClubPostArea :club-id="clubId" :club="club" />
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
  InfoFilled,
  Clock,
  View,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import type { Club, ClubCategory } from '@/types'
import ClubPostArea from '@/components/Club/ClubPostArea.vue'
import AIClubAtmosphere from '@/components/Chat/AIClubAtmosphere.vue'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()
const authStore = useAuthStore()

const loading = ref(false)
const club = ref<Club | null>(null)
const reason = ref('')
const isFavorited = computed(() => club.value?.isFavorite || false)
const showApplyDialog = ref(false)
const createLoading = ref(false)
const hasApplied = ref(false) // 添加一个标记是否已申请的状态

// 生成社团交流内容用于AI分析
const communicationContent = computed(() => {
  if (!club.value) return ''
  
  // 构建社团交流内容，包括帖子、公告、动态等
  const content = []
  
  // 添加社团介绍
  if (club.value.description) {
    content.push(`社团介绍：${club.value.description}`)
  }
  
  // 添加详细介绍
  if (club.value.introduction) {
    content.push(`详细介绍：${club.value.introduction}`)
  }
  
  // 添加公告
  if (club.value.announcements && club.value.announcements.length > 0) {
    content.push(`社团公告：${club.value.announcements.join('；')}`)
  }
  
  // 添加动态
  if (club.value.activities && club.value.activities.length > 0) {
    const activities = club.value.activities.map(activity => 
      `${activity.title}：${activity.description}`
    ).join('；')
    content.push(`社团动态：${activities}`)
  }
  
  // 添加标签
  if (club.value.tags && club.value.tags.length > 0) {
    content.push(`社团标签：${club.value.tags.join('、')}`)
  }
  
  return content.join('\n\n')
})

// 检查用户是否已加入该社团
const isUserJoined = computed(() => {
  if (!authStore.isLoggedIn || !club.value) return false
  // 使用club.status来判断，而不是userJoinedClubIds
  return club.value.status === 'approved'
})

// 检查用户是否管理该社团
const isUserManaged = computed(() => {
  if (!authStore.isLoggedIn || !club.value) return false
  // 这里可以添加检查用户是否管理该社团的逻辑
  return club.value.adminId === 'user1' // 假设当前用户ID为user1
})

// 将 isDisabled 改为计算属性
const isDisabled = computed(() => {
  if (!authStore.isLoggedIn) return false
  if (!club.value) return true

  // 如果用户已加入该社团，禁用申请按钮
  if (isUserJoined.value) return true

  // 如果已经申请过了，就禁用
  if (hasApplied.value) return true

  // 如果社团已满员
  if (club.value.currentMembers >= club.value.maxMembers) return true

  return false
})

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

  showApplyDialog.value = true
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

// 跳转到编辑页面
const goToEdit = () => {
  if (club.value) {
    router.push(`/user/edit-club/${club.value.id}`)
  }
}

// 获取社团详情
const fetchClubDetail = async () => {
  const clubId = route.params.id as string
  console.log('开始获取社团详情，clubId:', clubId)
  console.log('当前路由参数:', route.params)
  
  if (!clubId) {
    console.error('clubId 为空')
    return
  }

  try {
    loading.value = true
    console.log('调用 clubStore.fetchClubDetail...')
    club.value = await clubStore.fetchClubDetail(clubId)
    console.log('获取社团详情成功:', club.value)
  } catch (error) {
    console.error('获取社团详情失败:', error)
    ElMessage.error('获取社团详情失败')
  } finally {
    loading.value = false
  }
}

const confirmApply = async () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  if (!club.value) {
    ElMessage.error('社团不存在')
    return
  }

  try {
    createLoading.value = true
    await clubStore.applyToClub(club.value!.id, reason.value)
    
    // 申请成功后，更新社团状态
    if (club.value) {
      club.value.status = 'pending'
    }
    
    ElMessage.success('申请已提交，请等待审核')
    showApplyDialog.value = false
    reason.value = ''
    hasApplied.value = true // 标记为已申请
    console.log('已申请，按钮应该被禁用')
  } catch (error) {
    console.error('申请加入社团失败:', error)
  } finally {
    createLoading.value = false
  }
}

const getApplyButtonText = () => {
  if (!authStore.isLoggedIn) return '登录后申请'
  if (!club.value) return '加载中...'

  // 根据社团状态返回对应文本
  if (club.value.status === 'approved') return '已加入'
  if (club.value.status === 'pending') return '等待审核中'
  if (hasApplied.value) return '等待审核中'

  // 如果社团已满员
  if (club.value.currentMembers >= club.value.maxMembers) return '已满员'

  return '申请加入'
}

const clubId = String(route.params.id)

onMounted(async () => {
  console.log('ClubDetailView 组件已挂载')
  console.log('路由参数:', route.params)
  console.log('当前路由:', route.path)
  
  window.scrollTo(0, 0)
  
  try {
    await fetchClubDetail()
    console.log('社团详情获取完成')
  } catch (error) {
    console.error('获取社团详情时出错:', error)
  }

  // 检查 URL 参数，如果有 isApply=true，自动打开申请弹窗
  const isApply = route.query.isApply
  if (isApply === 'true') {
    // 检查用户是否已登录
    if (!authStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    // 检查是否可以申请
    if (!isDisabled.value) {
      showApplyDialog.value = true
    }

    // 清除 URL 中的查询参数，避免刷新时重复打开
    router.replace({
      path: route.path,
      query: { ...route.query, isApply: undefined },
    })
  }
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

.club-introduction,
.club-requirements {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.club-introduction h4,
.club-requirements h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.announcement-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.announcement-icon {
  color: #409eff;
  margin-top: 2px;
  flex-shrink: 0;
}

.announcement-text {
  flex: 1;
  line-height: 1.6;
  color: #606266;
}

.empty-activities {
  text-align: center;
  padding: 40px 20px;
}

.meeting-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meeting-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #606266;
}

.meeting-item:last-child {
  margin-bottom: 0;
}

.ai-atmosphere-container {
  height: 350px;
  overflow: hidden;
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 16px;
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

.content-card.ai-atmosphere-card {
  min-height: 570px;
}
.ai-atmosphere-container {
  min-height: 550px;
}
</style>
