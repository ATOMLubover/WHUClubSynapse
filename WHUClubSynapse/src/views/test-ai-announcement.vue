<template>
  <div class="test-ai-announcement">
    <div class="test-header">
      <h1>AI公告生成器测试</h1>
      <p>测试AI公告内容生成功能</p>
    </div>
    
    <div class="test-content">
      <div class="test-section">
        <h2>基础测试</h2>
        <div class="test-form">
          <el-form-item label="公告内容">
            <el-input
              v-model="testAnnouncement"
              type="textarea"
              :rows="4"
              placeholder="AI生成的公告内容将显示在这里"
              readonly
            />
          </el-form-item>
          
          <AIAnnouncementGenerator v-model="testAnnouncement" />
        </div>
      </div>
      
      <div class="test-section">
        <h2>多个公告测试</h2>
        <div class="announcements-test">
          <div v-for="(announcement, index) in testAnnouncements" :key="index" class="announcement-test-item">
            <div class="announcement-header">
              <span class="announcement-title">测试公告 {{ index + 1 }}</span>
              <el-button type="danger" size="small" @click="removeTestAnnouncement(index)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
            
            <el-input
              v-model="testAnnouncements[index]"
              type="textarea"
              :rows="3"
              placeholder="AI生成的公告内容"
              readonly
            />
            
            <AIAnnouncementGenerator v-model="testAnnouncements[index]" />
          </div>
          
          <el-button type="primary" @click="addTestAnnouncement">
            <el-icon><Plus /></el-icon>
            添加测试公告
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import AIAnnouncementGenerator from '@/components/Chat/AIAnnouncementGenerator.vue'

const testAnnouncement = ref('')
const testAnnouncements = ref<string[]>([''])

const addTestAnnouncement = () => {
  testAnnouncements.value.push('')
}

const removeTestAnnouncement = (index: number) => {
  testAnnouncements.value.splice(index, 1)
}
</script>

<style scoped>
.test-ai-announcement {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.test-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.test-header h1 {
  margin: 0 0 12px 0;
  font-size: 32px;
  color: #303133;
}

.test-header p {
  margin: 0;
  font-size: 16px;
  color: #606266;
}

.test-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.test-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.test-section h2 {
  margin: 0;
  padding: 20px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.test-form {
  padding: 20px;
}

.announcements-test {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.announcement-test-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
}

.announcement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.announcement-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.announcement-test-item .el-input {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .test-ai-announcement {
    padding: 10px;
  }

  .test-header h1 {
    font-size: 24px;
  }

  .test-section {
    margin: 0 -10px;
    border-radius: 0;
  }

  .announcement-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style> 