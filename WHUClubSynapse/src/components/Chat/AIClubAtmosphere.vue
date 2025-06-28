<template>
  <div class="ai-atmosphere-window">
    <div class="atmosphere-header">
      <div class="atmosphere-title">
        <el-icon class="ai-icon"><View /></el-icon>
        AI 氛围透视镜
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
          @click="clearAnalysis"
          :disabled="!atmosphereResult"
        >
          清空结果
        </el-button>
      </div>
    </div>
    
    <div class="atmosphere-content">
      <div v-if="!atmosphereResult && !isLoading" class="empty-state">
        <el-button 
          type="primary" 
          @click="startAnalysis" 
          :loading="isLoading"
          :disabled="!communicationContent || isLoading"
          class="analysis-btn"
          size="large"
        >
          <el-icon><View /></el-icon>
          开始AI氛围分析
        </el-button>
        <div v-if="!communicationContent" class="content-tip">
          <el-icon><InfoFilled /></el-icon>
          <span>暂无社团内容可分析</span>
        </div>
        <div v-if="!aiServiceAvailable" class="service-tip">
          <el-icon><Warning /></el-icon>
          <span>AI服务暂时不可用，请检查网络连接</span>
        </div>
        <p class="empty-tip">AI将分析社团交流内容，生成氛围标签和文化摘要</p>
      </div>
      
      <div v-if="isLoading" class="loading-state">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>AI正在分析社团氛围...</p>
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      
      <div v-if="atmosphereResult" class="atmosphere-result">
        <div class="result-section">
          <h4>氛围标签</h4>
          <div class="tags-container">
            <el-tag
              v-for="tag in atmosphereResult.atmosphere_tags"
              :key="tag"
              type="primary"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
            <span v-if="!atmosphereResult.atmosphere_tags?.length" class="no-data">暂无标签</span>
          </div>
        </div>
        
        <el-divider />
        
        <div class="result-section">
          <h4>文化摘要</h4>
          <div class="summary-content">
            <p>{{ atmosphereResult.culture_summary }}</p>
          </div>
        </div>
      </div>
      
      <div v-if="errorMessage" class="error-state">
        <el-icon class="error-icon" color="#F56C6C"><Warning /></el-icon>
        <p>{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { View, Refresh, Loading, Warning, InfoFilled } from '@element-plus/icons-vue'
import { checkAIStatus, analyzeClubAtmosphere, type ClubAtmosphereResponse } from '@/api/ai'

interface Props {
  communicationContent?: string
}

const props = withDefaults(defineProps<Props>(), {
  communicationContent: ''
})

const aiServiceAvailable = ref(false)
const checkingStatus = ref(false)
const isLoading = ref(false)
const atmosphereResult = ref<ClubAtmosphereResponse | null>(null)
const errorMessage = ref('')

// 监听交流内容变化，清空之前的结果
watch(() => props.communicationContent, () => {
  atmosphereResult.value = null
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

const clearAnalysis = () => {
  atmosphereResult.value = null
  errorMessage.value = ''
  ElMessage.success('分析结果已清空')
}

const startAnalysis = async () => {
  if (!props.communicationContent || isLoading.value) return
  
  if (!aiServiceAvailable.value) {
    ElMessage.warning('AI服务暂时不可用，正在尝试重新连接...')
    // 尝试重新检查AI服务状态
    await checkAIService()
    if (!aiServiceAvailable.value) {
      ElMessage.error('AI服务连接失败，请检查网络连接或联系管理员')
      return
    }
  }
  
  isLoading.value = true
  errorMessage.value = ''
  atmosphereResult.value = null
  
  try {
    const requestData = {
      communication_content: props.communicationContent
    }
    
    console.log('开始AI氛围分析，请求数据:', requestData)
    
    const result = await analyzeClubAtmosphere(requestData)
    atmosphereResult.value = result
    
    ElMessage.success('AI氛围分析完成')
    
  } catch (error) {
    console.error('AI氛围分析失败:', error)
    errorMessage.value = 'AI氛围分析失败: ' + (error instanceof Error ? error.message : '未知错误')
    ElMessage.error('AI氛围分析失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时检查AI服务状态
checkAIService()
</script>

<style scoped>
.ai-atmosphere-window {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8eaed;
  min-height: 500px;
}

.atmosphere-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border-radius: 8px 8px 0 0;
  color: white;
}

.atmosphere-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.ai-icon {
  margin-right: 8px;
  color: white;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions .el-button {
  color: white;
  border-color: rgba(255, 255, 255, 0.3);
}

.header-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.atmosphere-content {
  height: 100%;
  min-height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
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
  color: #67c23a;
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
  background: #67c23a;
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

.atmosphere-result {
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 6px;
  border: 1px solid #e4e7ed;
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

.tags-container {
  margin-top: 12px;
  margin-bottom: 12px;
}

.tag-item {
  margin-right: 8px;
  margin-bottom: 8px;
}

.no-data {
  color: #909399;
  font-size: 12px;
}

.summary-content {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #67c23a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-content p {
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

.analysis-btn {
  width: 320px;
  height: 64px;
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
  color: white;
  font-weight: 600;
  font-size: 24px;
  transition: all 0.3s ease;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.12);
  border-radius: 8px;
}

.analysis-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(103, 194, 58, 0.18);
}

.analysis-btn:disabled {
  background: #f0f2f5 !important;
  color: #b1b3b8 !important;
  border: 1.5px dashed #c0c4cc !important;
  box-shadow: none;
  opacity: 1 !important;
}

.service-tip, .content-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0 0 0;
  color: #909399;
  font-size: 14px;
  background: none;
  border-radius: 4px;
}

.service-tip .el-icon, .content-tip .el-icon {
  margin-right: 8px;
  color: #909399;
  font-size: 18px;
}
</style> 