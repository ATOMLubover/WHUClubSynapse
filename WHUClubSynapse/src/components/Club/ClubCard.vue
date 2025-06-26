<template>
  <el-card class="club-card" :body-style="{ padding: '0' }" shadow="hover" @click="goToDetail">
    <!-- 社团封面 -->
    <div class="club-cover">
      <el-image :src="club.coverImage" fit="cover" class="cover-image" :alt="club.name">
        <template #error>
          <div class="image-slot">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>

      <!-- 热门标签 -->
      <el-tag v-if="club.isHot" type="danger" class="hot-tag" size="small"> 热门 </el-tag>

      <!-- 收藏按钮 - 仅登录用户显示 -->
      <el-button
        v-if="authStore.isLoggedIn"
        :icon="isFavorited ? StarFilled : Star"
        class="favorite-btn"
        circle
        size="small"
        :type="isFavorited ? 'warning' : 'default'"
        @click.stop="toggleFavorite"
      />
    </div>

    <!-- 社团信息 -->
    <div class="club-info">
      <!-- 社团名称 -->
      <h3 class="club-name">{{ club.name }}</h3>

      <!-- 社团简介 -->
      <p class="club-description">{{ club.description }}</p>

      <!-- 社团详情 -->
      <div class="club-details">
        <div class="detail-item">
          <el-icon><User /></el-icon>
          <span>负责人：{{ club.adminName }}</span>
        </div>
        <div class="detail-item">
          <el-icon><UserFilled /></el-icon>
          <span>成员：{{ club.currentMembers }}/{{ club.maxMembers }}</span>
        </div>
      </div>

      <!-- 社团标签 -->
      <div class="club-tags">
        <el-tag :type="getCategoryType(club.category)" size="small">
          {{ club.category }}
        </el-tag>
        <el-tag v-for="tag in club.tags.slice(0, 2)" :key="tag" size="small" plain>
          {{ tag }}
        </el-tag>
      </div>

      <!-- 操作按钮 -->
      <div class="club-actions">
        <!-- 登录用户显示申请按钮和加入状态 -->
        <template v-if="authStore.isLoggedIn">
          <el-button type="primary" size="small" @click.stop="handleApply" :disabled="isDisabled">
            {{ getApplyButtonText() }}
          </el-button>
        </template>
        <!-- 未登录用户显示登录提示 -->
        <template v-else>
          <el-button type="primary" size="small" @click.stop="goToLogin"> 登录后申请 </el-button>
        </template>
        <el-button size="small" @click.stop="goToDetail"> 查看详情 </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture, Star, StarFilled, User, UserFilled } from '@element-plus/icons-vue'
import type { Club, ClubCategory } from '@/types'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'

interface Props {
  club: Club
}

const props = defineProps<Props>()
const emit = defineEmits(['update:favorited'])
const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()

// 收藏状态 - 仅对登录用户有意义
const isFavorited = computed(() => {
  return authStore.isLoggedIn ? props.club.isFavorite : false
})

const isDisabled = computed(() => {
  if (!props.club) return true
  if (!authStore.isLoggedIn) return true

  // 根据社团状态判断
  if (props.club.status === 'pending') return true
  if (props.club.status === 'approved') return true

  // 如果社团已满员
  if (props.club.currentMembers >= props.club.maxMembers) return true

  return false
})

// 获取分类对应的标签类型
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

// 跳转到详情页
const goToDetail = () => {
  router.push(`/club/${props.club.id}`)
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 切换收藏状态
const toggleFavorite = () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  if (isFavorited.value) {
    clubStore.unfavoriteClub(props.club.id)
    props.club.isFavorite = false
  } else {
    clubStore.favoriteClub(props.club.id)
    props.club.isFavorite = true
  }
}

// 申请加入社团
const handleApply = () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  if (props.club.currentMembers >= props.club.maxMembers) {
    ElMessage.warning('该社团已满员')
    return
  }

  // 跳转到社团详情页并自动打开申请弹窗
  router.push(`/club/${props.club.id}?isApply=true`)
}

const getApplyButtonText = () => {
  if (!props.club) return '加载中...'
  if (!authStore.isLoggedIn) return '登录后申请'

  // 根据社团状态返回对应文本
  if (props.club.status === 'pending') return '等待审核中'
  if (props.club.status === 'approved') return '已加入'
  if (props.club.currentMembers >= props.club.maxMembers) return '已满员'

  return '立即申请'
}
</script>

<style scoped>
.club-card {
  cursor: pointer;
  transition: transform 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.club-card:hover {
  transform: translateY(-4px);
}

.club-cover {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}

.hot-tag {
  position: absolute;
  top: 8px;
  left: 8px;
}

.favorite-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgba(255, 255, 255, 0.9);
}

.club-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.club-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.club-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
  min-height: 40px;
}

.club-details {
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.detail-item .el-icon {
  margin-right: 4px;
}

.club-tags {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.club-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.club-actions .el-button {
  flex: 1;
}
</style>
