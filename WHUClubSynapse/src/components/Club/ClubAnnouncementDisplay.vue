<template>
  <div class="announcement-display">
    <!-- 公告区域 -->
    <div class="announcements-section" v-if="announcements.length > 0">
      <div class="section-header">
        <h3>
          <i class="fas fa-bullhorn"></i>
          社团公告
        </h3>
        <button 
          v-if="showViewAll && announcements.length > displayLimit"
          @click="$emit('view-all-announcements')"
          class="view-all-btn"
        >
          查看全部
        </button>
      </div>
      
      <div class="announcement-list">
        <div 
          v-for="announcement in displayedAnnouncements" 
          :key="announcement.id"
          class="announcement-item"
          :class="{ 'high-priority': announcement.priority === 'high' }"
        >
          <div class="announcement-header">
            <h4>{{ announcement.title }}</h4>
            <div class="announcement-meta">
              <span class="priority-badge" v-if="announcement.priority === 'high'">重要</span>
              <span class="date">{{ formatDate(announcement.created_at) }}</span>
            </div>
          </div>
          <div class="announcement-content">
            {{ announcement.content }}
          </div>
          <div class="announcement-author">
            <img 
              v-if="announcement.authorAvatar" 
              :src="announcement.authorAvatar" 
              :alt="announcement.authorName"
              class="author-avatar"
            />
            <span class="author-name">{{ announcement.authorName }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 动态区域 -->
    <div class="activities-section" v-if="activities.length > 0">
      <div class="section-header">
        <h3>
          <i class="fas fa-calendar-alt"></i>
          社团动态
        </h3>
        <button 
          v-if="showViewAll && activities.length > displayLimit"
          @click="$emit('view-all-activities')"
          class="view-all-btn"
        >
          查看全部
        </button>
      </div>
      
      <div class="activity-list">
        <div 
          v-for="activity in displayedActivities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-header">
            <h4>{{ activity.title }}</h4>
            <div class="activity-meta">
              <span class="date">{{ formatDate(activity.created_at) }}</span>
            </div>
          </div>
          <div class="activity-content">
            {{ activity.content }}
          </div>
          <div class="activity-details">
            <div v-if="activity.location" class="activity-location">
              <i class="fas fa-map-marker-alt"></i>
              {{ activity.location }}
            </div>
            <div v-if="activity.activity_time" class="activity-time">
              <i class="fas fa-clock"></i>
              {{ formatDate(activity.activity_time) }}
            </div>
          </div>
          <div class="activity-author">
            <img 
              v-if="activity.authorAvatar" 
              :src="activity.authorAvatar" 
              :alt="activity.authorName"
              class="author-avatar"
            />
            <span class="author-name">{{ activity.authorName }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="announcements.length === 0 && activities.length === 0" class="empty-state">
      <i class="fas fa-info-circle"></i>
      <p>暂无公告和动态</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getClubAnnouncements, getClubActivities } from '@/api/club'
import type { ClubAnnouncement, ClubActivity } from '@/types'

const props = defineProps<{
  clubId: string
  displayLimit?: number // 显示数量限制
  showViewAll?: boolean // 是否显示"查看全部"按钮
}>()

const emit = defineEmits<{
  'view-all-announcements': []
  'view-all-activities': []
}>()

const announcements = ref<ClubAnnouncement[]>([])
const activities = ref<ClubActivity[]>([])
const loading = ref(false)

// 显示数量限制，默认3条
const displayLimit = computed(() => props.displayLimit || 3)

// 显示的公告列表
const displayedAnnouncements = computed(() => {
  return announcements.value.slice(0, displayLimit.value)
})

// 显示的动态列表
const displayedActivities = computed(() => {
  return activities.value.slice(0, displayLimit.value)
})

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return '今天'
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 加载公告列表
const loadAnnouncements = async () => {
  try {
    announcements.value = await getClubAnnouncements(props.clubId)
  } catch (error) {
    console.error('加载公告失败:', error)
  }
}

// 加载动态列表
const loadActivities = async () => {
  try {
    activities.value = await getClubActivities(props.clubId)
  } catch (error) {
    console.error('加载动态失败:', error)
  }
}

// 刷新数据
const refresh = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadAnnouncements(),
      loadActivities()
    ])
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(async () => {
  await refresh()
})

// 暴露刷新方法供父组件调用
defineExpose({
  refresh
})
</script>

<style scoped>
.announcement-display {
  max-width: 100%;
}

.announcements-section, .activities-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-header h3 i {
  color: #007bff;
}

.view-all-btn {
  background: none;
  border: 1px solid #007bff;
  color: #007bff;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.view-all-btn:hover {
  background: #007bff;
  color: white;
}

.announcement-list, .activity-list {
  display: grid;
  gap: 16px;
}

.announcement-item, .activity-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s;
}

.announcement-item:hover, .activity-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.announcement-item.high-priority {
  border-left: 4px solid #dc3545;
  background: #fff8f8;
}

.announcement-header, .activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.announcement-header h4, .activity-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  flex: 1;
  line-height: 1.4;
}

.announcement-meta, .activity-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  flex-shrink: 0;
}

.priority-badge {
  background: #dc3545;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.announcement-content, .activity-content {
  color: #555;
  line-height: 1.6;
  margin-bottom: 12px;
  font-size: 14px;
}

.activity-details {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.activity-location, .activity-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.activity-location i, .activity-time i {
  color: #007bff;
  width: 12px;
}

.announcement-author, .activity-author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

.author-name {
  font-weight: 500;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-size: 16px;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #ddd;
}

.empty-state p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .announcement-header, .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .announcement-meta, .activity-meta {
    align-self: flex-end;
  }
  
  .activity-details {
    flex-direction: column;
    gap: 8px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .view-all-btn {
    align-self: flex-end;
  }
}
</style> 