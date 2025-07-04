<template>
  <div class="test-page">
    <div class="container">
      <h1>社团公告和动态功能测试</h1>
      
      <div class="test-section">
        <h2>测试说明</h2>
        <p>本页面用于测试社团公告和动态功能的完整实现</p>
        <ul>
          <li>社团公告和动态存储在置顶帖子中</li>
          <li>支持发布、查看、删除公告和动态</li>
          <li>公告支持优先级设置</li>
          <li>动态支持地点和时间信息</li>
        </ul>
      </div>

      <div class="test-section">
        <h2>选择测试社团</h2>
        <div class="club-selector">
          <input 
            v-model="testClubId" 
            type="text" 
            placeholder="输入社团ID进行测试"
            class="club-input"
          />
          <button @click="loadTestData" class="load-btn">加载测试数据</button>
        </div>
      </div>

      <div v-if="testClubId" class="test-section">
        <h2>管理界面测试</h2>
        <div class="role-selector">
          <label>
            <input 
              v-model="userRole" 
              type="radio" 
              value="leader"
            />
            社团负责人
          </label>
          <label>
            <input 
              v-model="userRole" 
              type="radio" 
              value="admin"
            />
            社团管理员
          </label>
          <label>
            <input 
              v-model="userRole" 
              type="radio" 
              value="member"
            />
            普通成员
          </label>
        </div>
        
        <ClubAnnouncementManager 
          :club-id="testClubId" 
          :user-role="userRole"
          ref="managerRef"
        />
      </div>

      <div v-if="testClubId" class="test-section">
        <h2>展示界面测试</h2>
        <ClubAnnouncementDisplay 
          :club-id="testClubId"
          :display-limit="5"
          :show-view-all="true"
          @view-all-announcements="handleViewAllAnnouncements"
          @view-all-activities="handleViewAllActivities"
          ref="displayRef"
        />
      </div>

      <div class="test-section">
        <h2>API测试</h2>
        <div class="api-test-buttons">
          <button @click="testGetPinnedPost" class="test-btn">测试获取置顶帖子</button>
          <button @click="testGetAnnouncements" class="test-btn">测试获取公告</button>
          <button @click="testGetActivities" class="test-btn">测试获取动态</button>
          <button @click="testAddAnnouncement" class="test-btn">测试添加公告</button>
          <button @click="testAddActivity" class="test-btn">测试添加动态</button>
        </div>
        
        <div v-if="apiTestResult" class="api-result">
          <h3>API测试结果</h3>
          <pre>{{ apiTestResult }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ClubAnnouncementManager from '@/components/Club/ClubAnnouncementManager.vue'
import ClubAnnouncementDisplay from '@/components/Club/ClubAnnouncementDisplay.vue'
import { 
  getClubPinnedPost, 
  getClubAnnouncements, 
  getClubActivities,
  addClubAnnouncement,
  addClubActivity
} from '@/api/club'

const authStore = useAuthStore()

const testClubId = ref('1')
const userRole = ref<'leader' | 'admin' | 'member'>('leader')
const apiTestResult = ref('')
const managerRef = ref()
const displayRef = ref()

// 加载测试数据
const loadTestData = async () => {
  if (!testClubId.value) {
    alert('请输入社团ID')
    return
  }
  
  try {
    // 刷新组件数据
    if (managerRef.value) {
      await managerRef.value.refresh?.()
    }
    if (displayRef.value) {
      await displayRef.value.refresh()
    }
    
    alert('测试数据加载完成')
  } catch (error) {
    console.error('加载测试数据失败:', error)
    alert('加载测试数据失败')
  }
}

// 处理查看全部公告
const handleViewAllAnnouncements = () => {
  alert('查看全部公告 - 这里可以跳转到公告列表页面')
}

// 处理查看全部动态
const handleViewAllActivities = () => {
  alert('查看全部动态 - 这里可以跳转到动态列表页面')
}

// 测试获取置顶帖子
const testGetPinnedPost = async () => {
  if (!testClubId.value) {
    alert('请输入社团ID')
    return
  }
  
  try {
    const result = await getClubPinnedPost(testClubId.value)
    apiTestResult.value = JSON.stringify(result, null, 2)
  } catch (error) {
    apiTestResult.value = `错误: ${error}`
  }
}

// 测试获取公告
const testGetAnnouncements = async () => {
  if (!testClubId.value) {
    alert('请输入社团ID')
    return
  }
  
  try {
    const result = await getClubAnnouncements(testClubId.value)
    apiTestResult.value = JSON.stringify(result, null, 2)
  } catch (error) {
    apiTestResult.value = `错误: ${error}`
  }
}

// 测试获取动态
const testGetActivities = async () => {
  if (!testClubId.value) {
    alert('请输入社团ID')
    return
  }
  
  try {
    const result = await getClubActivities(testClubId.value)
    apiTestResult.value = JSON.stringify(result, null, 2)
  } catch (error) {
    apiTestResult.value = `错误: ${error}`
  }
}

// 测试添加公告
const testAddAnnouncement = async () => {
  if (!testClubId.value) {
    alert('请输入社团ID')
    return
  }
  
  try {
    await addClubAnnouncement(testClubId.value, {
      title: '测试公告',
      content: '这是一条测试公告内容',
      priority: 'high',
      author_id: authStore.user?.user_id || 1,
      authorName: authStore.user?.username || '测试用户',
      authorAvatar: authStore.user?.avatar_url || '',
      type: 'announcement'
    })
    
    apiTestResult.value = '公告添加成功'
    
    // 刷新组件数据
    if (managerRef.value) {
      await managerRef.value.refresh?.()
    }
    if (displayRef.value) {
      await displayRef.value.refresh()
    }
  } catch (error) {
    apiTestResult.value = `错误: ${error}`
  }
}

// 测试添加动态
const testAddActivity = async () => {
  if (!testClubId.value) {
    alert('请输入社团ID')
    return
  }
  
  try {
    await addClubActivity(testClubId.value, {
      title: '测试动态',
      content: '这是一条测试动态内容',
      location: '测试地点',
      activity_time: new Date().toISOString(),
      author_id: authStore.user?.user_id || 1,
      authorName: authStore.user?.username || '测试用户',
      authorAvatar: authStore.user?.avatar_url || '',
      type: 'activity'
    })
    
    apiTestResult.value = '动态添加成功'
    
    // 刷新组件数据
    if (managerRef.value) {
      await managerRef.value.refresh?.()
    }
    if (displayRef.value) {
      await displayRef.value.refresh()
    }
  } catch (error) {
    apiTestResult.value = `错误: ${error}`
  }
}
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.test-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.test-section h2 {
  color: #333;
  margin-bottom: 16px;
  font-size: 20px;
}

.test-section p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.test-section ul {
  color: #666;
  margin-left: 20px;
}

.test-section li {
  margin-bottom: 8px;
}

.club-selector {
  display: flex;
  gap: 12px;
  align-items: center;
}

.club-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.load-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.load-btn:hover {
  background: #0056b3;
}

.role-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.role-selector label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.role-selector input[type="radio"] {
  margin: 0;
}

.api-test-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.test-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.test-btn:hover {
  background: #218838;
}

.api-result {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 16px;
}

.api-result h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
}

.api-result pre {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  font-size: 12px;
  color: #333;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-page {
    padding: 10px;
  }
  
  .container {
    padding: 20px;
  }
  
  .club-selector {
    flex-direction: column;
    align-items: stretch;
  }
  
  .role-selector {
    flex-direction: column;
    gap: 12px;
  }
  
  .api-test-buttons {
    flex-direction: column;
  }
  
  .test-btn {
    width: 100%;
  }
}
</style> 