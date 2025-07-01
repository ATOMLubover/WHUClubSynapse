<template>
  <div class="ai-side-chat">
    <!-- 悬浮球 -->
    <div 
      v-if="isSideChatEnabled"
      class="chat-float-button"
      @click="toggleChat"
      :class="{ 
        'chat-open': isChatOpen,
        'ai-unavailable': !aiAvailable 
      }"
    >
      <el-icon v-if="!isChatOpen" class="chat-icon">
        <ChatDotRound />
      </el-icon>
      <el-icon v-else class="close-icon">
        <Close />
      </el-icon>
      <!-- AI状态指示器 -->
      <div v-if="!aiAvailable" class="ai-status-indicator">
        <el-icon><Warning /></el-icon>
      </div>
    </div>

    <!-- 对话窗口 -->
    <div v-if="isChatOpen" class="chat-window">
      <div class="chat-header">
        <div class="chat-title">
          <el-icon class="ai-icon"><ChatDotRound /></el-icon>
          <span>AI智能助手</span>
          <!-- AI状态标签 -->
          <el-tag 
            v-if="!aiAvailable" 
            type="warning" 
            size="small" 
            class="ai-status-tag"
          >
            AI不可用
          </el-tag>
        </div>
        <div class="chat-actions">
          <el-button 
            type="info" 
            size="small" 
            @click="testAiConnectivity"
            class="ai-test-btn"
            style="margin-right: 8px;"
          >
            AI连通性测试
          </el-button>
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
          <p v-if="aiAvailable">我可以帮助您了解社团相关信息，支持多轮对话。</p>
          <p v-else class="ai-unavailable-text">AI服务暂时不可用，请稍后重试。</p>
          
          <!-- AI不可用时的提示 -->
          <div v-if="!aiAvailable" class="ai-unavailable-notice">
            <el-alert
              title="AI服务连接失败"
              type="warning"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>当前无法连接到AI服务，可能的原因：</p>
                <ul>
                  <li>AI服务暂时不可用</li>
                  <li>网络连接问题</li>
                  <li>服务配置错误</li>
                </ul>
                <p>请稍后重试或联系管理员。</p>
              </template>
            </el-alert>
          </div>
          
          <!-- AI可用时的建议问题 -->
          <div v-else class="suggestions">
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
              <div class="message-text">
                <MarkdownRenderer :content="message.content" />
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
            :disabled="!aiAvailable"
          />
          <el-button 
            type="primary" 
            @click="sendMessage"
            :loading="isLoading"
            :disabled="!inputMessage.trim() || !aiAvailable"
            class="send-button"
          >
            <el-icon><Position /></el-icon>
          </el-button>
        </div>
        <div class="input-tips">
          <span v-if="aiAvailable">按 Enter 发送，Ctrl + Enter 换行</span>
          <span v-else class="ai-unavailable-tip">AI服务不可用，无法发送消息</span>
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
  Warning,
} from '@element-plus/icons-vue'
import { sideChat, checkAiServiceHealth } from '@/api/ai-search'
import { isSideChatEnabled as checkSideChatEnabled } from '@/config/ai-search'
import type { ChatMessage, SmartSearchSource } from '@/types'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

// 响应式数据
const isChatOpen = ref(false)
const inputMessage = ref('')
const isLoading = ref(false)
const chatContentRef = ref<HTMLElement>()
const aiAvailable = ref(true) // AI服务可用性状态

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
    // 打开对话窗口时检查AI可用性
    checkAiAvailability()
    nextTick(() => {
      scrollToBottom()
    })
  }
}

const clearHistory = () => {
  chatHistory.value = []
  ElMessage.success('对话历史已清空')
}

// 检查AI服务可用性
const checkAiAvailability = async () => {
  try {
    aiAvailable.value = await checkAiServiceHealth()
  } catch (error) {
    console.error('检查AI服务可用性失败:', error)
    aiAvailable.value = false
  }
}

const sendMessage = async (message?: string) => {
  const content = message || inputMessage.value.trim()
  if (!content || !aiAvailable.value) return

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
    
    // 检查是否是AI连接失败
    if (error instanceof Error && error.message.includes('AI连接失败')) {
      aiAvailable.value = false
      ElMessage.error('AI连接失败，请稍后重试')
    } else {
      ElMessage.error('发送失败，请稍后重试')
    }
    
    // AI连接失败时不添加任何错误消息
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
  // 初始化时检查AI可用性
  checkAiAvailability()
})

// AI连通性测试按钮逻辑
const testAiConnectivity = async () => {
  const loading = ElMessage({ message: '正在检测AI连通性...', type: 'info', duration: 0 })
  try {
    const healthy = await checkAiServiceHealth()
    ElMessage.closeAll()
    if (healthy) {
      ElMessage.success('AI服务可用')
      aiAvailable.value = true
    } else {
      ElMessage.error('AI服务不可用')
      aiAvailable.value = false
    }
  } catch (error) {
    ElMessage.closeAll()
    ElMessage.error('AI服务检测失败')
    aiAvailable.value = false
  }
}
</script>

<style scoped>
.ai-side-chat {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
}

.ai-side-chat > * {
  pointer-events: auto;
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
  z-index: 9999;
  position: fixed;
}

.chat-float-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
}

.chat-float-button.chat-open {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.chat-float-button.ai-unavailable {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  opacity: 0.8;
}

.chat-icon, .close-icon {
  font-size: 24px;
}

/* AI状态指示器 */
.ai-status-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 20px;
  height: 20px;
  background: #f56c6c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
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

.ai-status-tag {
  margin-left: 8px;
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

.ai-unavailable-text {
  color: #f56c6c;
  font-weight: 500;
}

/* AI不可用提示 */
.ai-unavailable-notice {
  margin: 20px 0;
  text-align: left;
}

.ai-unavailable-notice ul {
  margin: 8px 0;
  padding-left: 20px;
}

.ai-unavailable-notice li {
  margin: 4px 0;
  font-size: 13px;
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

.message-text :deep(.markdown-renderer) {
  font-size: 14px;
  line-height: 1.5;
}

.message-text :deep(.markdown-renderer h1) {
  font-size: 1.3em;
  margin: 0.6em 0 0.3em 0;
}

.message-text :deep(.markdown-renderer h2) {
  font-size: 1.2em;
  margin: 0.5em 0 0.2em 0;
}

.message-text :deep(.markdown-renderer h3) {
  font-size: 1.1em;
  margin: 0.4em 0 0.2em 0;
}

.message-text :deep(.markdown-renderer p) {
  margin: 0.4em 0;
}

.message-text :deep(.markdown-renderer code) {
  background-color: #f6f8fa;
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-size: 0.85em;
}

.message-text :deep(.markdown-renderer pre) {
  background-color: #f6f8fa;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0.4em 0;
  font-size: 0.85em;
}

.message-text :deep(.markdown-renderer blockquote) {
  margin: 0.4em 0;
  padding: 0 0.6em;
  color: #6a737d;
  border-left: 0.2em solid #dfe2e5;
  font-size: 0.9em;
}

.message-text :deep(.katex) {
  font-size: 1em;
}

.message-text :deep(.katex-display) {
  margin: 0.4em 0;
  text-align: center;
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

.message-input :deep(.el-textarea__inner:disabled) {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
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

.ai-unavailable-tip {
  color: #f56c6c;
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