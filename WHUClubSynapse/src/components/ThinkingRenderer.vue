<template>
  <div class="thinking-container" v-if="content">
    <div class="pre-think-content" v-if="preThinkContent">
      {{ preThinkContent }}
    </div>
    <div class="thinking-section" v-if="thinkContent">
      <div class="thinking-indicator">
        <span class="thinking-dot">•</span>
        <span class="thinking-dot">•</span>
        <span class="thinking-dot">•</span>
      </div>
      <div class="thinking-content">
        {{ thinkContent }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  content: string
}>()

// 分离think标签前的内容和think标签中的内容
const preThinkContent = computed(() => {
  const thinkStart = props.content.indexOf('<think>')
  return thinkStart > 0 ? props.content.substring(0, thinkStart).trim() : ''
})

const thinkContent = computed(() => {
  const thinkMatch = props.content.match(/<think>(.*?)(?:<\/think>|$)/s)
  return thinkMatch ? thinkMatch[1].trim() : props.content
})
</script>

<style scoped>
.thinking-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pre-think-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.thinking-section {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 12px;
  margin: 4px 0;
}

.thinking-indicator {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}

.thinking-dot {
  animation: thinking 1.4s infinite;
  color: #666;
  font-size: 24px;
  line-height: 8px;
}

.thinking-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes thinking {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.thinking-content {
  color: #666;
  font-style: italic;
  white-space: pre-wrap;
  word-break: break-word;
}
</style> 