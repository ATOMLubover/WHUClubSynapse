<template>
  <div class="test-page">
    <h1>功能测试页面</h1>
    
    <el-card class="test-section">
      <template #header>
        <h3>AI审核助手测试</h3>
      </template>
      
      <div class="ai-test-layout">
        <div class="test-info-section">
          <h4>测试数据</h4>
          <div class="test-data">
            <p><strong>申请者姓名:</strong> 赵六</p>
            <p><strong>专业:</strong> 计算机科学与技术</p>
            <p><strong>学号:</strong> 2021001004</p>
            <p><strong>偏好社团:</strong> 学术科技, 创新创业</p>
            <p><strong>特质标签:</strong> 编程开发, 逻辑清晰, 团队协作, 创新冒险</p>
            <p><strong>申请理由:</strong> 我对编程很感兴趣，希望能加入社团学习更多技术知识。</p>
            <p><strong>社团名称:</strong> 计算机科学协会</p>
            <p><strong>社团要求:</strong> 有编程基础, 对算法有兴趣, 积极参与团队项目</p>
          </div>
        </div>
        
        <div class="ai-test-section">
          <AIApplicationScreening 
            :application-data="testApplicationData"
            :club-name="testClubName"
            :required-conditions="testRequiredConditions"
          />
        </div>
      </div>
      
      <!-- 调试信息 -->
      <el-card class="test-section">
        <template #header>
          <h3>调试信息</h3>
        </template>
        <div class="debug-info">
          <p><strong>测试社团名称:</strong> {{ testClubName }}</p>
          <p><strong>测试要求条件:</strong> {{ testRequiredConditions.join(', ') }}</p>
          <p><strong>申请者姓名:</strong> {{ testApplicationData.realName }}</p>
          <p><strong>申请者专业:</strong> {{ testApplicationData.major }}</p>
          <p><strong>偏好社团:</strong> {{ testApplicationData.interestedCategories?.join(', ') }}</p>
          <p><strong>特质标签:</strong> {{ testApplicationData.tags?.join(', ') }}</p>
        </div>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import AIApplicationScreening from '@/components/Chat/AIApplicationScreening.vue'
import type { ClubApplication } from '@/types'

// 测试数据
const testApplicationData: ClubApplication = {
  id: 'test1',
  userId: 'user4',
  clubId: '1',
  username: 'applicant1',
  realName: '赵六',
  avatar_url: 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png',
  applyReason: '我对编程很感兴趣，希望能加入社团学习更多技术知识。',
  status: 'pending',
  applyTime: '2024-06-25T10:00:00Z',
  studentId: '2021001004',
  major: '计算机科学与技术',
  phone: '13800138003',
  email: 'applicant1@example.com',
  interestedCategories: ['学术科技', '创新创业'],
  tags: ['编程开发', '逻辑清晰', '团队协作', '创新冒险'],
}

const testClubName = '计算机科学协会'
const testRequiredConditions = ['有编程基础', '对算法有兴趣', '积极参与团队项目']
</script>

<style scoped>
.test-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 20px;
}

.ai-test-layout {
  display: flex;
  gap: 20px;
  min-height: 600px;
}

.test-info-section {
  flex: 1;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.test-info-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.test-data p {
  margin: 8px 0;
  line-height: 1.5;
}

.test-data strong {
  color: #606266;
}

.ai-test-section {
  flex: 1;
}

.debug-info p {
  margin: 8px 0;
  line-height: 1.5;
}

.debug-info strong {
  color: #606266;
}
</style>
