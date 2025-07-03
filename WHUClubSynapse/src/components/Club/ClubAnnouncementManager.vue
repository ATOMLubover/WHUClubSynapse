<template>
  <div class="announcement-manager">
    <!-- 公告管理 -->
    <div class="section">
      <div class="section-header">
        <h3>社团公告</h3>
        <button 
          @click="showAddAnnouncementDialog = true"
          class="add-btn"
          v-if="canManage"
        >
          <i class="fas fa-plus"></i>
          发布公告
        </button>
      </div>
      
      <div class="announcement-list">
        <div 
          v-for="announcement in announcements" 
          :key="announcement.id"
          class="announcement-item"
          :class="{ 'high-priority': announcement.priority === 'high' }"
        >
          <div class="announcement-header">
            <h4>{{ announcement.title }}</h4>
            <div class="announcement-meta">
              <span class="priority-badge" v-if="announcement.priority === 'high'">重要</span>
              <span class="author">{{ announcement.authorName }}</span>
              <span class="date">{{ formatDate(announcement.created_at) }}</span>
              <button 
                v-if="canManage"
                @click="deleteAnnouncement(announcement.id)"
                class="delete-btn"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          <div class="announcement-content">
            {{ announcement.content }}
          </div>
        </div>
        
        <div v-if="announcements.length === 0" class="empty-state">
          暂无公告
        </div>
      </div>
    </div>

    <!-- 动态管理 -->
    <div class="section">
      <div class="section-header">
        <h3>社团动态</h3>
        <button 
          @click="showAddActivityDialog = true"
          class="add-btn"
          v-if="canManage"
        >
          <i class="fas fa-plus"></i>
          发布动态
        </button>
      </div>
      
      <div class="activity-list">
        <div 
          v-for="activity in activities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-header">
            <h4>{{ activity.title }}</h4>
            <div class="activity-meta">
              <span class="author">{{ activity.authorName }}</span>
              <span class="date">{{ formatDate(activity.created_at) }}</span>
              <button 
                v-if="canManage"
                @click="deleteActivity(activity.id)"
                class="delete-btn"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          <div class="activity-content">
            {{ activity.content }}
          </div>
          <div v-if="activity.location" class="activity-location">
            <i class="fas fa-map-marker-alt"></i>
            {{ activity.location }}
          </div>
          <div v-if="activity.activity_time" class="activity-time">
            <i class="fas fa-clock"></i>
            {{ formatDate(activity.activity_time) }}
          </div>
        </div>
        
        <div v-if="activities.length === 0" class="empty-state">
          暂无动态
        </div>
      </div>
    </div>

    <!-- 添加公告对话框 -->
    <div v-if="showAddAnnouncementDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>发布公告</h3>
          <button @click="closeDialog" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="dialog-content">
          <form @submit.prevent="submitAnnouncement">
            <div class="form-group">
              <label>公告标题</label>
              <input 
                v-model="newAnnouncement.title" 
                type="text" 
                placeholder="请输入公告标题"
                required
              />
            </div>
            <div class="form-group">
              <label>优先级</label>
              <select v-model="newAnnouncement.priority">
                <option value="normal">普通</option>
                <option value="high">重要</option>
              </select>
            </div>
            <div class="form-group">
              <label>公告内容</label>
              <textarea 
                v-model="newAnnouncement.content" 
                placeholder="请输入公告内容"
                rows="6"
                required
              ></textarea>
            </div>
            <div class="form-actions">
              <button type="button" @click="closeDialog" class="cancel-btn">取消</button>
              <button type="submit" class="submit-btn" :disabled="loading">
                {{ loading ? '发布中...' : '发布公告' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 添加动态对话框 -->
    <div v-if="showAddActivityDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>发布动态</h3>
          <button @click="closeDialog" class="close-btn">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="dialog-content">
          <form @submit.prevent="submitActivity">
            <div class="form-group">
              <label>动态标题</label>
              <input 
                v-model="newActivity.title" 
                type="text" 
                placeholder="请输入动态标题"
                required
              />
            </div>
            <div class="form-group">
              <label>动态内容</label>
              <textarea 
                v-model="newActivity.content" 
                placeholder="请输入动态内容"
                rows="6"
                required
              ></textarea>
            </div>
            <div class="form-group">
              <label>活动地点（可选）</label>
              <input 
                v-model="newActivity.location" 
                type="text" 
                placeholder="请输入活动地点"
              />
            </div>
            <div class="form-group">
              <label>活动时间（可选）</label>
              <input 
                v-model="newActivity.activity_time" 
                type="datetime-local"
              />
            </div>
            <div class="form-actions">
              <button type="button" @click="closeDialog" class="cancel-btn">取消</button>
              <button type="submit" class="submit-btn" :disabled="loading">
                {{ loading ? '发布中...' : '发布动态' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { 
  getClubAnnouncements, 
  getClubActivities, 
  addClubAnnouncement, 
  addClubActivity, 
  deleteClubAnnouncement, 
  deleteClubActivity 
} from '@/api/club'
import type { ClubAnnouncement, ClubActivity } from '@/types'

const props = defineProps<{
  clubId: string
  userRole?: 'leader' | 'admin' | 'member'
}>()

const authStore = useAuthStore()

const announcements = ref<ClubAnnouncement[]>([])
const activities = ref<ClubActivity[]>([])
const loading = ref(false)
const showAddAnnouncementDialog = ref(false)
const showAddActivityDialog = ref(false)

const newAnnouncement = ref({
  title: '',
  content: '',
  priority: 'normal' as 'high' | 'normal' | 'low'
})

const newActivity = ref({
  title: '',
  content: '',
  location: '',
  activity_time: ''
})

// 是否可以管理（发布、删除）
const canManage = computed(() => {
  return props.userRole === 'leader' || props.userRole === 'admin'
})

// 格式化日期
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
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

// 提交公告
const submitAnnouncement = async () => {
  if (!newAnnouncement.value.title || !newAnnouncement.value.content) {
    return
  }

  loading.value = true
  try {
    await addClubAnnouncement(props.clubId, {
      title: newAnnouncement.value.title,
      content: newAnnouncement.value.content,
      priority: newAnnouncement.value.priority,
      author_id: authStore.user?.user_id || 0,
      authorName: authStore.user?.username || '',
      authorAvatar: authStore.user?.avatar_url || '',
      type: 'announcement'
    })
    
    await loadAnnouncements()
    closeDialog()
  } catch (error) {
    console.error('发布公告失败:', error)
    alert('发布公告失败，请重试')
  } finally {
    loading.value = false
  }
}

// 提交动态
const submitActivity = async () => {
  if (!newActivity.value.title || !newActivity.value.content) {
    return
  }

  loading.value = true
  try {
    await addClubActivity(props.clubId, {
      title: newActivity.value.title,
      content: newActivity.value.content,
      location: newActivity.value.location || undefined,
      activity_time: newActivity.value.activity_time || undefined,
      author_id: authStore.user?.user_id || 0,
      authorName: authStore.user?.username || '',
      authorAvatar: authStore.user?.avatar_url || '',
      type: 'activity'
    })
    
    await loadActivities()
    closeDialog()
  } catch (error) {
    console.error('发布动态失败:', error)
    alert('发布动态失败，请重试')
  } finally {
    loading.value = false
  }
}

// 删除公告
const deleteAnnouncement = async (announcementId: string) => {
  if (!confirm('确定要删除这条公告吗？')) {
    return
  }

  try {
    await deleteClubAnnouncement(props.clubId, announcementId)
    await loadAnnouncements()
  } catch (error) {
    console.error('删除公告失败:', error)
    alert('删除公告失败，请重试')
  }
}

// 删除动态
const deleteActivity = async (activityId: string) => {
  if (!confirm('确定要删除这条动态吗？')) {
    return
  }

  try {
    await deleteClubActivity(props.clubId, activityId)
    await loadActivities()
  } catch (error) {
    console.error('删除动态失败:', error)
    alert('删除动态失败，请重试')
  }
}

// 关闭对话框
const closeDialog = () => {
  showAddAnnouncementDialog.value = false
  showAddActivityDialog.value = false
  
  // 重置表单
  newAnnouncement.value = {
    title: '',
    content: '',
    priority: 'normal'
  }
  
  newActivity.value = {
    title: '',
    content: '',
    location: '',
    activity_time: ''
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadAnnouncements(),
    loadActivities()
  ])
})
</script>

<style scoped>
.announcement-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.add-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.add-btn:hover {
  background: #0056b3;
}

.announcement-list, .activity-list {
  display: grid;
  gap: 16px;
}

.announcement-item, .activity-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: box-shadow 0.2s;
}

.announcement-item:hover, .activity-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.announcement-item.high-priority {
  border-left: 4px solid #dc3545;
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
  font-size: 18px;
  flex: 1;
}

.announcement-meta, .activity-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #666;
}

.priority-badge {
  background: #dc3545;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.delete-btn {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.delete-btn:hover {
  background: #f8f9fa;
}

.announcement-content, .activity-content {
  color: #555;
  line-height: 1.6;
  margin-bottom: 12px;
}

.activity-location, .activity-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
  margin-top: 8px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px;
  font-size: 16px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 4px;
}

.close-btn:hover {
  color: #333;
}

.dialog-content {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input, .form-group select, .form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.cancel-btn:hover {
  background: #e9ecef;
}

.submit-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.submit-btn:hover:not(:disabled) {
  background: #0056b3;
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style> 