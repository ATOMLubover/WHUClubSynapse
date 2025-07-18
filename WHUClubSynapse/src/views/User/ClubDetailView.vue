<template>
  <div class="club-detail-container">
    <div v-loading="loading" class="club-detail-content">
      <template v-if="club">
        <!-- 社团头部信息 -->
        <div class="club-header">
          <div class="club-cover">
            <el-image :src="club.logo_url" fit="cover" class="cover-image" />
            <div class="club-status-badge">
              <el-tag v-if="club.isHot" type="danger" size="large"> 🔥 热门社团 </el-tag>
              <el-tag v-if="isFull" type="warning" size="large"> ⚠️ 已满员 </el-tag>
            </div>
          </div>

          <div class="club-info">
            <h1 class="club-title">{{ club.club_name }}</h1>
            <div class="club-meta">
              <div class="meta-item">
                <el-icon><User /></el-icon>
                <span>负责人：{{ club.leader?.username }}</span>
              </div>
              <div class="meta-item">
                <el-icon><UserFilled /></el-icon>
                <span>成员数：{{ club.member_count }}/{{ clubStore.MAX_MEMBER_NUM }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Calendar /></el-icon>
                <span>成立时间：{{ formatDate(club.created_at) }}</span>
              </div>
            </div>

            <div class="club-tags">
              <el-tag :type="getCategoryType(club.category)" size="large">
                {{ clubStore.categoriesList.find((c) => c.category_id === club?.category)?.name }}
              </el-tag>
              <el-tag v-for="tag in club.tags" :key="tag" size="large" plain>
                {{ tag }}
              </el-tag>
            </div>

            <div class="club-actions">
              <el-button type="primary" size="large" :disabled="isDisabled" @click="handleApply">
                {{ getApplyButtonText() }}
              </el-button>
              <el-button v-if="authStore.isLoggedIn" size="large" @click="toggleFavorite">
                <div :class="['custom-heart-icon', { favorited: isFavorited }]"></div>
                <span style="margin-left: 8px">{{ isFavorited ? '已收藏' : '收藏' }}</span>
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
                  <p>{{ club.desc }}</p>
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
              <el-card class="content-card">
                <template #header>
                  <h3>
                    <el-icon><Bell /></el-icon> 社团公告
                  </h3>
                </template>
                <div v-loading="activitiesLoading">
                  <div v-if="announcements.length > 0" class="announcements-list">
                    <div
                      v-for="announcement in announcements"
                      :key="announcement.comment_id"
                      class="announcement-item"
                    >
                      <el-icon class="announcement-icon"><InfoFilled /></el-icon>
                      <div class="announcement-content">
                        <div class="announcement-text">{{ announcement.parsed_data?.content }}</div>
                        <div
                          v-if="announcement.parsed_data?.metadata?.tags"
                          class="announcement-tags"
                        >
                          <el-tag
                            v-for="tag in announcement.parsed_data.metadata.tags"
                            :key="tag"
                            size="small"
                            :type="tag === '重要' ? 'danger' : ''"
                          >
                            {{ tag }}
                          </el-tag>
                        </div>
                        <div class="announcement-meta">
                          <span class="time">{{ formatDate(announcement.created_at) }}</span>
                          <span
                            v-if="announcement.parsed_data?.metadata?.valid_until"
                            class="valid-until"
                          >
                            有效期至: {{ announcement.parsed_data.metadata.valid_until }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="empty-announcements">
                    <el-empty description="暂无公告" :image-size="80" />
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
                <div v-loading="activitiesLoading">
                  <el-timeline v-if="activities.length > 0">
                    <el-timeline-item
                      v-for="activity in activities"
                      :key="activity.comment_id"
                      :timestamp="formatDate(activity.created_at)"
                      :type="
                        activity.parsed_data?.metadata?.activity_type === 'meeting'
                          ? 'primary'
                          : 'success'
                      "
                    >
                      <h4>{{ activity.parsed_data?.content }}</h4>
                      <div v-if="activity.parsed_data?.metadata" class="activity-meta">
                        <span v-if="activity.parsed_data.metadata.location">
                          <el-icon><Location /></el-icon>
                          {{ activity.parsed_data.metadata.location }}
                        </span>
                        <span v-if="activity.parsed_data.metadata.participants">
                          <el-icon><User /></el-icon>
                          {{ activity.parsed_data.metadata.participants }}人参与
                        </span>
                      </div>
                    </el-timeline-item>
                  </el-timeline>
                  <div v-else class="empty-activities">
                    <el-empty description="暂无动态" :image-size="80" />
                  </div>
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
                    <div class="stat-number">{{ club.member_count }}</div>
                    <div class="stat-label">当前成员</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ activities.length }}</div>
                    <div class="stat-label">累计活动</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">{{ announcements.length }}</div>
                    <div class="stat-label">公告数量</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-number">
                      {{
                        clubStore.currentClubPosts.length - 1 >= 0
                          ? clubStore.currentClubPosts.length - 1
                          : 0
                      }}
                    </div>
                    <div class="stat-label">发布帖子</div>
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
          <el-row :gutter="24" style="margin-top: 24px">
            <el-col :span="24">
              <el-card class="content-card ai-atmosphere-card">
                <template #header>
                  <h3>
                    <el-icon><View /></el-icon> AI氛围透视镜
                  </h3>
                </template>
                <div class="ai-atmosphere-container">
                  <AIClubAtmosphere :communication-content="communicationContent" />
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
      <ClubAnnouncementManager
        v-if="club"
        :club-id="Number(clubId)"
        :leader-id="Number(club.leader_id || 0)"
      />
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
import ClubAnnouncementManager from '@/components/Club/ClubAnnouncementManager.vue'
import { applyToClub } from '@/api/club'
import { getPinnedPost, getPostComments } from '@/api/club'

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

interface CommentData {
  type: 'activity' | 'announcement'
  content: string
  metadata?: {
    activity_type?: string
    location?: string
    participants?: number
    priority?: string
    valid_until?: string
    tags?: string[]
  }
}

interface Activity {
  comment_id: number
  content: string
  created_at: string
  parsed_data?: CommentData
}

interface Announcement {
  comment_id: number
  content: string
  created_at: string
  parsed_data?: CommentData
}

const activities = ref<Activity[]>([])
const announcements = ref<Announcement[]>([])
const activitiesLoading = ref(false)

// 解析评论内容
const parseComment = (comment: any): CommentData | null => {
  try {
    return JSON.parse(comment.content)
  } catch (e) {
    console.warn('评论解析失败:', e)
    return null
  }
}

// 加载社团动态和公告
const loadActivitiesAndAnnouncements = async () => {
  activitiesLoading.value = true
  try {
    const { data: pinnedPost } = await getPinnedPost(Number(clubId))
    const { data: comments } = await getPostComments(pinnedPost.post_id)

    if (comments == null) {
      return
    }

    // 分类处理评论
    const sortedComments = comments.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
    )

    activities.value = []
    announcements.value = []

    sortedComments.forEach((comment) => {
      const parsedData = parseComment(comment)
      if (parsedData) {
        const enrichedComment = {
          ...comment,
          parsed_data: parsedData,
        }

        if (parsedData.type === 'activity') {
          activities.value.push(enrichedComment)
        } else if (parsedData.type === 'announcement') {
          announcements.value.push(enrichedComment)
        }
      }
    })
  } catch (e: any) {
    if (e.response?.status === 400) {
      activities.value = []
      announcements.value = []
    } else {
      ElMessage.error('加载动态和公告失败')
      console.error('加载失败:', e)
    }
  } finally {
    activitiesLoading.value = false
  }
}

// 生成社团交流内容用于AI分析
const communicationContent = computed(() => {
  if (!club.value) return ''

  // 构建社团交流内容，包括帖子、公告、动态等
  const content = []

  // 添加社团介绍
  if (club.value.desc) {
    content.push(`社团介绍：${club.value.desc}`)
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
    const activities = club.value.activities
      .map((activity) => `${activity.title}：${activity.description}`)
      .join('；')
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
  return club.value.status === 'joined'
})

// 检查用户是否管理该社团
const isUserManaged = computed(() => {
  if (!authStore.isLoggedIn || !club.value) return false
  // 这里可以添加检查用户是否管理该社团的逻辑
  return club.value.adminId === 'user1' // 假设当前用户ID为user1
})

// 满员状态
const isFull = computed(() => {
  if (!club.value) return false
  return club.value.member_count >= clubStore.MAX_MEMBER_NUM
})

// 将 isDisabled 改为计算属性
const isDisabled = computed(() => {
  if (!authStore.isLoggedIn) return false
  if (!club.value) return true

  if (club.value.status === 'joined') return true
  if (club.value.status === 'pending') return true

  // 如果已经申请过了，就禁用
  if (hasApplied.value) return true

  // 如果社团已满员
  if (club.value.member_count >= clubStore.MAX_MEMBER_NUM) return true

  return false
})

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
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const handleApply = () => {
  if (!authStore.isLoggedIn || authStore.isGuest) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  showApplyDialog.value = true
}

// 切换收藏状态
const toggleFavorite = () => {
  if (!authStore.isLoggedIn || authStore.isGuest) {
    ElMessage.warning('请先登录')
    return
  }

  if (isFavorited.value) {
    clubStore.unfavoriteClub(club.value!.club_id)
    club.value!.isFavorite = false
  } else {
    clubStore.favoriteClub(club.value!.club_id)
    club.value!.isFavorite = true
  }
}

// 分享功能
const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: club.value?.club_name,
      text: club.value?.desc,
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
    router.push(`/user/edit-club/${club.value.club_id}`)
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
    await applyToClub({ clubId: club.value!.club_id, reason: reason.value })

    // 申请成功后，更新社团状态
    if (club.value) {
      club.value.status = 'pending'
    }

    ElMessage.success('申请已提交，请等待审核')
    showApplyDialog.value = false
    reason.value = ''
    hasApplied.value = true // 标记为已申请
    console.log('已申请，按钮应该被禁用')
    await clubStore.fetchPendingClubApplications({})
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
  if (club.value.status === 'joined') return '已加入'
  if (club.value.status === 'pending') return '等待审核中'
  if (hasApplied.value) return '等待审核中'

  // 如果社团已满员
  if (club.value.member_count >= clubStore.MAX_MEMBER_NUM) return '已满员'

  return '申请加入'
}

const clubId = String(route.params.id)

onMounted(async () => {
  try {
    await fetchClubDetail()
    console.log('社团详情获取完成')
  } catch (error) {
    console.error('获取社团详情时出错:', error)
  }

  console.log('club', club.value)

  if (clubStore.favoriteClubs.length == 0) {
    await clubStore.fetchFavoriteClubs()
    console.log('获取收藏社团完成')
  }
  if (clubStore.applications.length == 0) {
    await clubStore.fetchPendingClubApplications({})
    console.log('获取加入社团申请完成')
  }
  if (clubStore.joinedClubs.length == 0) {
    await clubStore.fetchJoinedClubs()
    console.log('获取加入社团完成')
  }

  console.log('clubStore.applications:', clubStore.applications)
  console.log('clubStore.favoriteClubs:', clubStore.favoriteClubs)

  if (
    clubStore.applications.find(
      (application) => application.club_id == clubId && application.status == 'pending',
    )
  ) {
    club.value!.status = 'pending'
  }
  if (clubStore.joinedClubs.find((club) => club.club_id == clubId)) {
    club.value!.status = 'joined'
  }
  if (clubStore.favoriteClubs.find((club) => club.club_id == clubId)) {
    club.value!.isFavorite = true
  }
  const isApply = route.query.isApply
  if (isApply === 'true') {
    if (!authStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    if (!isDisabled.value) {
      showApplyDialog.value = true
    }

    // 清除 URL 中的查询参数，避免刷新时重复打开
    router.replace({
      path: route.path,
      query: { ...route.query, isApply: undefined },
    })
  }

  // 在组件挂载时加载数据
  loadActivitiesAndAnnouncements()
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
  background: rgba(255, 255, 255, 0.7);
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
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  background: rgba(255, 255, 255, 0.9);
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

.announcement-content {
  flex: 1;
}

.announcement-text {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.announcement-tags {
  margin-bottom: 8px;
}

.announcement-tags .el-tag {
  margin-right: 8px;
}

.announcement-meta {
  font-size: 12px;
  color: #999;
}

.announcement-meta .time {
  margin-right: 16px;
}

.activity-meta {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
}

.activity-meta span {
  margin-right: 16px;
  display: inline-flex;
  align-items: center;
}

.activity-meta .el-icon {
  margin-right: 4px;
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

/* 自定义心形收藏图标 */
.custom-heart-icon {
  position: relative;
  width: 16px;
  height: 16px;
  transform: rotate(-45deg);
  transition: all 0.3s ease;
  display: inline-block;
}

.custom-heart-icon::before,
.custom-heart-icon::after {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  width: 8px;
  height: 13px;
  background: #c0c4cc;
  border-radius: 8px 8px 0 0;
  transform: rotate(-45deg);
  transform-origin: 0 100%;
  transition: all 0.3s ease;
}

.custom-heart-icon::after {
  left: 0;
  transform: rotate(45deg);
  transform-origin: 100% 100%;
}

.custom-heart-icon.favorited::before,
.custom-heart-icon.favorited::after {
  background: #f56c6c;
  animation: heartBeat 0.6s ease-in-out;
}

/* 心跳动画效果 */
@keyframes heartBeat {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* 悬停效果 */
.el-button:hover .custom-heart-icon::before,
.el-button:hover .custom-heart-icon::after {
  background: #f56c6c;
}

.main-content > * {
  margin-bottom: 20px;
}
</style>
