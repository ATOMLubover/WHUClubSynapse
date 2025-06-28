<template>
  <div class="ai-screening-window">
    <div class="screening-header">
      <div class="screening-title">
        <el-icon class="ai-icon"><ChatDotRound /></el-icon>
        AI 审核助手
        <el-tag 
          :type="aiServiceAvailable ? 'success' : 'danger'" 
          size="small" 
          style="margin-left: 8px;"
        >
          {{ aiServiceAvailable ? '在线' : '离线' }}
        </el-tag>
      </div>
      <div class="header-actions">
        <el-button 
          type="text" 
          size="small" 
          @click="checkAIService"
          :loading="checkingStatus"
        >
          <el-icon><Refresh /></el-icon>
          检查状态
        </el-button>
        <el-button 
          type="text" 
          size="small" 
          @click="clearScreening"
          :disabled="!screeningResult"
        >
          清空结果
        </el-button>
      </div>
    </div>
    
    <div class="screening-content">
      <div v-if="!screeningResult && !isLoading" class="empty-state">
        <el-icon class="empty-icon"><ChatDotRound /></el-icon>
        <p>点击下方按钮开始AI审核分析</p>
        <p class="empty-tip">AI将分析申请者信息并给出建议</p>
      </div>
      
      <div v-if="isLoading" class="loading-state">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>AI正在分析申请信息...</p>
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      
      <div v-if="screeningResult" class="screening-result">
        <div class="result-section">
          <h4>申请摘要</h4>
          <div class="result-content">
            <p>{{ screeningResult.summary }}</p>
          </div>
        </div>
        
        <el-divider />
        
        <div class="result-section">
          <h4>审核建议</h4>
          <div class="result-content">
            <p>{{ screeningResult.suggestion }}</p>
          </div>
        </div>
      </div>
      
      <div v-if="errorMessage" class="error-state">
        <el-icon class="error-icon" color="#F56C6C"><Warning /></el-icon>
        <p>{{ errorMessage }}</p>
      </div>
    </div>
    
    <div class="screening-actions">
      <el-button 
        type="primary" 
        @click="startScreening" 
        :loading="isLoading"
        :disabled="!aiServiceAvailable || !applicationData"
        class="screening-btn"
        size="large"
      >
        <el-icon><Search /></el-icon>
        开始AI审核分析
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Refresh, Loading, Warning, Search } from '@element-plus/icons-vue'
import { checkAIStatus, screenApplication, type ApplicationScreeningResponse } from '@/api/ai'
import type { ClubApplication } from '@/types'

interface Props {
  applicationData?: ClubApplication
  clubName?: string
  requiredConditions?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  requiredConditions: () => []
})

const aiServiceAvailable = ref(false)
const checkingStatus = ref(false)
const isLoading = ref(false)
const screeningResult = ref<ApplicationScreeningResponse | null>(null)
const errorMessage = ref('')

// 监听申请数据变化，清空之前的结果
watch(() => props.applicationData, () => {
  screeningResult.value = null
  errorMessage.value = ''
}, { deep: true })

const checkAIService = async () => {
  if (checkingStatus.value) return
  
  checkingStatus.value = true
  
  try {
    console.log('开始检查AI服务状态...')
    aiServiceAvailable.value = await checkAIStatus()
    console.log('AI服务状态检查结果:', aiServiceAvailable.value)
    
    if (!aiServiceAvailable.value) {
      ElMessage.warning('AI服务暂时不可用，请检查网络连接或联系管理员')
    } else {
      ElMessage.success('AI服务连接正常')
    }
  } catch (error) {
    console.error('检查AI服务失败:', error)
    aiServiceAvailable.value = false
    ElMessage.error('AI服务检查失败: ' + (error instanceof Error ? error.message : '未知错误'))
  } finally {
    checkingStatus.value = false
  }
}

const clearScreening = () => {
  screeningResult.value = null
  errorMessage.value = ''
  ElMessage.success('审核结果已清空')
}

const startScreening = async () => {
  if (!props.applicationData || !props.clubName || isLoading.value) return
  
  if (!aiServiceAvailable.value) {
    ElMessage.warning('AI服务暂时不可用，请稍后重试')
    return
  }
  
  isLoading.value = true
  errorMessage.value = ''
  screeningResult.value = null
  
  try {
    // 调试信息
    console.log('props.applicationData:', props.applicationData)
    console.log('props.clubName:', props.clubName)
    console.log('props.requiredConditions:', props.requiredConditions)
    
    // 构建申请者数据
    const applicantData = {
      name: props.applicationData.realName || props.applicationData.username,
      major: props.applicationData.major || '未填写',
      skills: [
        ...(props.applicationData.interestedCategories || []),
        ...(props.applicationData.tags || [])
      ],
      experience: props.applicationData.applyReason
    }
    
    const requestData = {
      applicant_data: applicantData,
      application_reason: props.applicationData.applyReason,
      required_conditions: props.requiredConditions || [],
      club_name: props.clubName || '未知社团'
    }
    
    console.log('开始AI审核分析，请求数据:', requestData)
    
    const result = await screenApplication(requestData)
    screeningResult.value = result
    
    ElMessage.success('AI审核分析完成')
    
  } catch (error) {
    console.error('AI审核分析失败:', error)
    errorMessage.value = 'AI审核分析失败: ' + (error instanceof Error ? error.message : '未知错误')
    ElMessage.error('AI审核分析失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时检查AI服务状态
checkAIService()
</script>

<style scoped>
.ai-screening-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.screening-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
  border-radius: 8px 8px 0 0;
}

.screening-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ai-icon {
  margin-right: 8px;
  color: #409eff;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.screening-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 300px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-tip {
  font-size: 12px;
  margin-top: 8px;
  color: #c0c4cc;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #409eff;
}

.loading-icon {
  font-size: 32px;
  margin-bottom: 16px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.typing-indicator {
  display: flex;
  gap: 4px;
  margin-top: 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #409eff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.screening-result {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.result-section {
  margin-bottom: 16px;
}

.result-section:last-child {
  margin-bottom: 0;
}

.result-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.result-content {
  background: #fff;
  padding: 12px;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.result-content p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #f56c6c;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.screening-actions {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
  border-radius: 0 0 8px 8px;
}

.screening-btn {
  width: 100%;
}
</style> 