<template>
  <div class="ai-introduction-generator">
    <div class="generator-header">
      <div class="generator-title">
        <el-icon class="ai-icon"><Star /></el-icon>
        AI 社团介绍生成器
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
          @click="clearResult"
          :disabled="!generatedText"
        >
          清空结果
        </el-button>
      </div>
    </div>
    
    <div class="generator-content">
      <!-- 输入表单 -->
      <div v-if="!generatedText" class="input-form">
        <el-form ref="formRef" :model="formData" label-width="100px">
          <el-form-item label="草稿文案" prop="content">
            <el-input
              v-model="formData.content"
              type="textarea"
              :rows="4"
              placeholder="请输入社团介绍的草稿内容（可选）"
              maxlength="500"
              show-word-limit
            />
            <div class="input-tip">
              <el-icon><InfoFilled /></el-icon>
              如果您已有草稿内容，AI将基于此进行优化和扩展
            </div>
          </el-form-item>

          <el-form-item label="文体风格" prop="style">
            <el-select 
              v-model="formData.style" 
              placeholder="请选择文体风格"
              style="width: 100%"
            >
              <el-option label="正式严谨" value="formal" />
              <el-option label="活泼幽默" value="humorous" />
              <el-option label="温馨亲切" value="warm" />
              <el-option label="专业学术" value="academic" />
              <el-option label="激情活力" value="energetic" />
              <el-option label="简洁明了" value="concise" />
            </el-select>
          </el-form-item>

          <el-form-item label="目标人群" prop="targetPeople">
            <el-input
              v-model="formData.targetPeople"
              placeholder="例如：新生、对编程感兴趣的同学、有音乐基础的学生等"
              maxlength="100"
              show-word-limit
            />
            <div class="input-tip">
              <el-icon><InfoFilled /></el-icon>
              描述您希望吸引的目标群体，AI将针对性地生成介绍
            </div>
          </el-form-item>
        </el-form>

        <div class="form-actions">
          <el-button 
            type="primary" 
            @click="generateIntroduction" 
            :loading="isLoading"
            :disabled="isLoading || !aiServiceAvailable"
            class="generate-btn"
            size="large"
          >
            <el-icon><Star /></el-icon>
            生成AI社团介绍
          </el-button>
        </div>

        <div v-if="!aiServiceAvailable" class="service-tip">
          <el-icon><Warning /></el-icon>
          <span>AI服务暂时不可用，请检查网络连接</span>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <p>AI正在生成社团介绍...</p>
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
      
      <!-- 生成结果 -->
      <div v-if="generatedText && !isLoading" class="generation-result">
        <div class="result-header">
          <h4>
            <el-icon><DocumentCopy /></el-icon>
            AI生成的社团介绍
          </h4>
          <div class="result-actions">
            <el-button 
              type="primary" 
              size="small"
              @click="applyToForm"
            >
              <el-icon><Check /></el-icon>
              应用到表单
            </el-button>
            <el-button 
              size="small"
              @click="copyToClipboard"
            >
              <el-icon><CopyDocument /></el-icon>
              复制文本
            </el-button>
            <el-button 
              size="small"
              @click="regenerate"
            >
              <el-icon><Refresh /></el-icon>
              重新生成
            </el-button>
          </div>
        </div>
        
        <div class="generated-content">
          <div class="content-text">{{ generatedText }}</div>
        </div>
        
        <div class="generation-info">
          <el-tag size="small" type="info">文体风格: {{ getStyleText(formData.style) }}</el-tag>
          <el-tag size="small" type="info" style="margin-left: 8px;">
            目标人群: {{ formData.targetPeople || '通用' }}
          </el-tag>
        </div>
      </div>
      
      <!-- 错误状态 -->
      <div v-if="errorMessage" class="error-state">
        <el-icon class="error-icon" color="#F56C6C"><Warning /></el-icon>
        <p>{{ errorMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Star, 
  Refresh, 
  Loading, 
  Warning, 
  InfoFilled, 
  DocumentCopy,
  Check,
  CopyDocument
} from '@element-plus/icons-vue'
import { checkAIStatus, generateClubIntroduction, type ContentGenerationRequest } from '@/api/ai'

interface Props {
  modelValue?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: ''
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const aiServiceAvailable = ref(false)
const checkingStatus = ref(false)
const isLoading = ref(false)
const generatedText = ref('')
const errorMessage = ref('')

const formData = reactive({
  content: '',
  style: '',
  targetPeople: ''
})

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

const clearResult = () => {
  generatedText.value = ''
  errorMessage.value = ''
  ElMessage.success('生成结果已清空')
}

const getStyleText = (style: string) => {
  const styleMap: Record<string, string> = {
    formal: '正式严谨',
    humorous: '活泼幽默',
    warm: '温馨亲切',
    academic: '专业学术',
    energetic: '激情活力',
    concise: '简洁明了'
  }
  return styleMap[style] || style
}

const generateIntroduction = async () => {
  if (isLoading.value) return
  
  if (!aiServiceAvailable.value) {
    ElMessage.warning('AI服务暂时不可用，正在尝试重新连接...')
    await checkAIService()
    if (!aiServiceAvailable.value) {
      ElMessage.error('AI服务连接失败，请检查网络连接或联系管理员')
      return
    }
  }
  
  isLoading.value = true
  errorMessage.value = ''
  generatedText.value = ''
  
  try {
    const requestData: ContentGenerationRequest = {
      content: formData.content || undefined,
      style: formData.style || undefined,
      target_people: formData.targetPeople || undefined
    }
    
    console.log('开始AI社团介绍生成，请求数据:', requestData)
    
    const result = await generateClubIntroduction(requestData)
    generatedText.value = result.generated_text
    
    ElMessage.success('AI社团介绍生成完成')
    
  } catch (error) {
    console.error('AI社团介绍生成失败:', error)
    errorMessage.value = 'AI社团介绍生成失败: ' + (error instanceof Error ? error.message : '未知错误')
    ElMessage.error('AI社团介绍生成失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

const applyToForm = () => {
  emit('update:modelValue', generatedText.value)
  ElMessage.success('AI生成的介绍已应用到表单')
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedText.value)
    ElMessage.success('文本已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

const regenerate = () => {
  generateIntroduction()
}

// 组件挂载时检查AI服务状态
checkAIService()
</script>

<style scoped>
.ai-introduction-generator {
  border: 1px solid #e0e6ed;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  overflow: hidden;
  margin-top: 16px;
}

.generator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid #e0e6ed;
}

.generator-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.ai-icon {
  font-size: 18px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions .el-button {
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.3);
}

.header-actions .el-button:hover {
  color: white;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.1);
}

.generator-content {
  padding: 20px;
}

.input-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #86909c;
}

.form-actions {
  margin-top: 20px;
  text-align: center;
}

.generate-btn {
  width: auto;
  min-width: 200px;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 22px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.service-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 14px;
  text-align: center;
  justify-content: center;
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
}

.loading-icon {
  font-size: 32px;
  color: #667eea;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-state p {
  margin: 16px 0;
  color: #4e5969;
  font-size: 16px;
}

.typing-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  margin-top: 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.generation-result {
  background: white;
  border-radius: 12px;
  border: 1px solid #e0e6ed;
  overflow: hidden;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8faff 0%, #e6f2ff 100%);
  border-bottom: 1px solid #e0e6ed;
}

.result-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1d2129;
  font-size: 16px;
  font-weight: 600;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.generated-content {
  padding: 20px;
}

.content-text {
  line-height: 1.8;
  color: #1d2129;
  font-size: 15px;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #f8faff;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.generation-info {
  padding: 12px 20px;
  background: #f8faff;
  border-top: 1px solid #e0e6ed;
}

.error-state {
  text-align: center;
  padding: 40px 20px;
  color: #f56c6c;
}

.error-icon {
  font-size: 24px;
  margin-bottom: 12px;
}

.error-state p {
  margin: 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .generator-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .result-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .result-actions {
    align-self: stretch;
    justify-content: space-between;
  }

  .result-actions .el-button {
    flex: 1;
    margin: 0 2px;
  }
}
</style> 