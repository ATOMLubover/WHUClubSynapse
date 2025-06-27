<template>
  <div class="ai-chat-window">
    <div class="chat-header">
      <div class="chat-title">
        <el-icon class="ai-icon"><ChatDotRound /></el-icon>
        AI 助手
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
          @click="clearChat"
          :disabled="messages.length === 0"
        >
          清空对话
        </el-button>
      </div>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <el-icon class="empty-icon"><ChatDotRound /></el-icon>
        <p>开始与AI助手对话吧！</p>
        <p class="empty-tip">可以询问关于帖子内容、社团活动等问题</p>
      </div>
      
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        class="message-item"
        :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'assistant' }"
      >
        <div class="message-avatar">
          <el-avatar 
            :size="32" 
            :src="message.role === 'user' ? userAvatar : aiAvatar"
            :icon="message.role === 'assistant' ? ChatDotRound : User"
          />
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div v-if="isLoading" class="message-item ai-message">
        <div class="message-avatar">
          <el-avatar :size="32" :src="aiAvatar" :icon="ChatDotRound" />
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        :maxlength="500"
        show-word-limit
        placeholder="输入你的问题..."
        @keydown.enter.prevent="handleSend"
        :disabled="isLoading || !aiServiceAvailable"
        class="chat-input"
      />
      <div class="input-actions">
        <el-button 
          type="primary" 
          @click="handleSend" 
          :loading="isLoading"
          :disabled="!inputMessage.trim() || !aiServiceAvailable"
          class="send-btn"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, User, Promotion, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { chatWithAI, checkAIStatus, type ChatMessage } from '@/api/ai'

interface LocalChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const props = defineProps<{
  postTitle?: string
  postContent?: string
}>()

const authStore = useAuthStore()
const messages = ref<LocalChatMessage[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement>()
const aiServiceAvailable = ref(false)
const checkingStatus = ref(false)

const userAvatar = authStore.user?.avatar_url || 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png'
const aiAvatar = 'https://cdn.jsdelivr.net/gh/whu-asset/static/ai-avatar.png'

watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatMessage = (content: string) => {
  return content.replace(/\n/g, '<br>')
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const clearChat = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}

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

const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  if (!aiServiceAvailable.value) {
    ElMessage.warning('AI服务暂时不可用，请稍后重试')
    return
  }
  
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })
  
  isLoading.value = true
  
  try {
    let systemPrompt = "你是一个友好的AI助手，专门帮助用户解答关于社团帖子的问题。请用中文回答。"
    if (props.postTitle || props.postContent) {
      systemPrompt += `\n\n当前帖子信息：`
      if (props.postTitle) {
        systemPrompt += `\n标题：${props.postTitle}`
      }
      if (props.postContent) {
        systemPrompt += `\n内容：${props.postContent}`
      }
      systemPrompt += `\n\n请基于帖子内容为用户提供相关帮助和建议。`
    }
    
    const chatMessages: ChatMessage[] = [
      { role: 'system', content: systemPrompt },
      ...messages.value.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    ]
    
    const response = await chatWithAI({
      messages: chatMessages,
      max_tokens: 1000,
      temperature: 0.7
    })
    
    messages.value.push({
      role: 'assistant',
      content: response.response || '抱歉，我现在无法回答您的问题。',
      timestamp: new Date()
    })
    
  } catch (error) {
    console.error('AI聊天请求失败:', error)
    ElMessage.error('AI助手暂时无法响应，请稍后重试')
    
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些技术问题，暂时无法回答您的问题。请稍后重试。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  checkAIService()
})
</script>

<style scoped>
.ai-chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 1px solid #e0e0e0;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.ai-icon {
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f8f9fa;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #666;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  color: #ddd;
  margin-bottom: 16px;
}

.empty-tip {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.user-message .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-left: 40px;
}

.ai-message .message-text {
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
  margin-right: 40px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.user-message .message-time {
  text-align: right;
}

.ai-message .message-time {
  text-align: left;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  margin-right: 40px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

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

.chat-input-area {
  padding: 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.chat-input {
  margin-bottom: 12px;
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

.send-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  color: white;
  font-weight: 500;
  transition: all 0.3s ease;
}

.send-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  background: #ccc;
  transform: none;
  box-shadow: none;
}
</style> 