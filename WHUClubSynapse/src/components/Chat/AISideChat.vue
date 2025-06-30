<template>
  <div class="ai-side-chat">
    <!-- 悬浮球 -->
    <div 
      v-if="isSideChatEnabled"
      class="chat-float-button"
      @click="toggleChat"
      :class="{ 'chat-open': isChatOpen }"
    >
      <el-icon v-if="!isChatOpen" class="chat-icon">
        <ChatDotRound />
      </el-icon>
      <el-icon v-else class="close-icon">
        <Close />
      </el-icon>
    </div>

    <!-- 对话窗口 -->
    <div v-if="isChatOpen" class="chat-window">
      <div class="chat-header">
        <div class="chat-title">
          <el-icon class="ai-icon"><ChatDotRound /></el-icon>
          <span>AI智能助手</span>
        </div>
        <div class="chat-actions">
          <el-button 
            type="text" 
            size="small" 
            @click="clearHistory"
            :disabled="chatHistory.length === 0"
          >
            <el-icon><Delete /></el-icon>
            清空对话
          </el-button>
          <el-button 
            type="text" 
            size="small" 
            @click="toggleChat"
          >
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 对话内容区域 -->
      <div class="chat-content" ref="chatContentRef">
        <div v-if="chatHistory.length === 0" class="welcome-message">
          <div class="welcome-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <h3>欢迎使用AI智能助手</h3>
          <p>我可以帮助您了解社团相关信息，支持多轮对话。</p>
          <div class="suggestions">
            <div class="suggestion-title">您可以问我：</div>
            <div class="suggestion-list">
              <el-tag 
                v-for="suggestion in suggestions" 
                :key="suggestion"
                @click="sendMessage(suggestion)"
                class="suggestion-tag"
              >
                {{ suggestion }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 对话消息列表 -->
        <div v-else class="message-list">
          <div 
            v-for="(message, index) in chatHistory" 
            :key="index"
            class="message-item"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar 
                :size="32"
                :src="message.role === 'user' ? userAvatar : aiAvatar"
              >
                <el-icon v-if="message.role === 'assistant'"><ChatDotRound /></el-icon>
                <el-icon v-else><User /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              
              <!-- 来源信息 -->
              <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                <div class="sources-title">参考来源：</div>
                <div class="sources-list">
                  <div 
                    v-for="source in message.sources" 
                    :key="source.id"
                    class="source-item"
                  >
                    <el-icon><Document /></el-icon>
                    <span>{{ source.metadata.source }} (第{{ source.metadata.page }}页)</span>
                  </div>
                </div>
              </div>
              
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="isLoading" class="message-item assistant">
            <div class="message-avatar">
              <el-avatar :size="32" :src="aiAvatar">
                <el-icon><ChatDotRound /></el-icon>
              </el-avatar>
            </div>
            <div class="message-content">
              <div class="loading-indicator">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>AI正在思考中...</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            placeholder="输入您的问题..."
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 4 }"
            @keydown.enter.prevent="handleEnter"
            @keydown.ctrl.enter="sendMessage"
            resize="none"
            class="message-input"
          />
          <el-button 
            type="primary" 
            @click="sendMessage"
            :loading="isLoading"
            :disabled="!inputMessage.trim()"
            class="send-button"
          >
            <el-icon><Position /></el-icon>
          </el-button>
        </div>
        <div class="input-tips">
          <span>按 Enter 发送，Ctrl + Enter 换行</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound,
  Close,
  Delete,
  User,
  Document,
  Loading,
  Position,
} from '@element-plus/icons-vue'
import { sideChat } from '@/api/ai-search'
import { isSideChatEnabled as checkSideChatEnabled } from '@/config/ai-search'
import type { ChatMessage, SmartSearchSource } from '@/types'

// 响应式数据
const isChatOpen = ref(false)
const inputMessage = ref('')
const isLoading = ref(false)
const chatContentRef = ref<HTMLElement>()

// 对话历史
const chatHistory = ref<(ChatMessage & { sources?: SmartSearchSource[] })[]>([])

// 用户头像
const userAvatar = ref('https://picsum.photos/32/32?random=user')
const aiAvatar = ref('https://picsum.photos/32/32?random=ai')

// 建议问题
const suggestions = [
  '如何创建社团？',
  '社团申请需要准备什么材料？',
  '审核一般需要多久？',
  '如何管理社团成员？',
  '社团活动有哪些类型？'
]

// 计算属性
const isSideChatEnabled = computed(() => checkSideChatEnabled())

// 方法
const toggleChat = () => {
  isChatOpen.value = !isChatOpen.value
  if (isChatOpen.value) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const clearHistory = () => {
  chatHistory.value = []
  ElMessage.success('对话历史已清空')
}

const sendMessage = async (message?: string) => {
  const content = message || inputMessage.value.trim()
  if (!content) return

  // 添加用户消息
  const userMessage: ChatMessage = {
    role: 'user',
    content,
    timestamp: new Date().toISOString()
  }
  chatHistory.value.push(userMessage)

  // 清空输入框
  inputMessage.value = ''

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  // 发送到AI
  isLoading.value = true
  try {
    const response = await sideChat({
      query: content,
      history: chatHistory.value.slice(0, -1) // 不包含当前消息
    })

    // 添加AI回复
    const aiMessage: ChatMessage & { sources?: SmartSearchSource[] } = {
      role: 'assistant',
      content: response.answer,
      timestamp: new Date().toISOString(),
      sources: response.source
    }
    chatHistory.value.push(aiMessage)

    // 滚动到底部
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送失败，请稍后重试')
    
    // 添加错误消息
    const errorMessage: ChatMessage = {
      role: 'assistant',
      content: '抱歉，我暂时无法回答您的问题，请稍后重试。',
      timestamp: new Date().toISOString()
    }
    chatHistory.value.push(errorMessage)
  } finally {
    isLoading.value = false
  }
}

const handleEnter = (event: KeyboardEvent) => {
  if (event.ctrlKey) {
    // Ctrl + Enter 换行
    return
  }
  // Enter 发送
  sendMessage()
}

const scrollToBottom = () => {
  if (chatContentRef.value) {
    chatContentRef.value.scrollTop = chatContentRef.value.scrollHeight
  }
}

const formatMessage = (content: string) => {
  // 简单的Markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp?: string) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
  })
}

// 监听对话历史变化，自动滚动
watch(chatHistory, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.ai-side-chat {
  position: relative;
  z-index: 1000;
}

/* 悬浮球 */
.chat-float-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  z-index: 1001;
}

.chat-float-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.chat-float-button.chat-open {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.chat-icon, .close-icon {
  font-size: 24px;
}

/* 对话窗口 */
.chat-window {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 400px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 对话头部 */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
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

.chat-actions {
  display: flex;
  gap: 8px;
}

.chat-actions .el-button {
  color: white;
  padding: 4px 8px;
}

.chat-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

/* 对话内容区域 */
.chat-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 40px 20px;
  color: #606266;
}

.welcome-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 16px;
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.welcome-message p {
  margin: 0 0 24px 0;
  font-size: 14px;
}

.suggestions {
  text-align: left;
}

.suggestion-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  justify-content: flex-start;
}

.suggestion-tag:hover {
  transform: translateX(4px);
}

/* 消息列表 */
.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  animation: messageSlideIn 0.3s ease;
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 280px;
  word-wrap: break-word;
}

.message-item.user .message-content {
  text-align: right;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-item.user .message-text {
  background: #667eea;
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.message-item.assistant .message-text {
  background: white;
  color: #303133;
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-text strong {
  font-weight: 600;
}

.message-text em {
  font-style: italic;
}

/* 来源信息 */
.message-sources {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  font-size: 12px;
}

.sources-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: #667eea;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
}

.source-item .el-icon {
  font-size: 12px;
}

/* 消息时间 */
.message-time {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.message-item.user .message-time {
  text-align: right;
}

.message-item.assistant .message-time {
  text-align: left;
}

/* 加载状态 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border-radius: 16px 16px 16px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  color: #606266;
  font-size: 14px;
}

/* 输入区域 */
.chat-input {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 20px;
  padding: 8px 16px;
  resize: none;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.message-input :deep(.el-textarea__inner:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.send-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s;
}

.send-button:hover {
  transform: scale(1.05);
}

.send-button:disabled {
  background: #c0c4cc;
  transform: none;
}

.input-tips {
  margin-top: 8px;
  font-size: 11px;
  color: #909399;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-window {
    width: calc(100vw - 40px);
    height: calc(100vh - 120px);
    bottom: 80px;
    right: 20px;
    left: 20px;
  }

  .chat-float-button {
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
  }

  .chat-icon, .close-icon {
    font-size: 20px;
  }

  .message-content {
    max-width: 200px;
  }
}

/* 滚动条样式 */
.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background: transparent;
}

.chat-content::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}
</style> 