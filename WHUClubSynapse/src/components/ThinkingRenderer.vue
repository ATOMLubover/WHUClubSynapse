<template>
  <div class="thinking-renderer">
    <div v-if="thinkingContent" class="thinking-section">
      <div class="thinking-header">
        <el-icon class="thinking-icon"><ChatDotRound /></el-icon>
        <span class="thinking-title">深度思考</span>
      </div>
      <div class="thinking-content">
        <MarkdownRenderer :content="thinkingContent" />
      </div>
    </div>
    <div v-if="answerContent" class="answer-section">
      <MarkdownRenderer :content="answerContent" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChatDotRound } from '@element-plus/icons-vue'
import MarkdownRenderer from './MarkdownRenderer.vue'

interface Props {
  content: string
}

const props = defineProps<Props>()

// 解析内容，分离思考过程和答案
const thinkingData = computed(() => {
  const content = props.content
  console.log('ThinkingRenderer收到内容:', content)
  console.log('内容长度:', content.length)
  console.log('内容前50个字符:', content.substring(0, 50))
  
  // 查找思考过程的标签
  const thinkingPatterns = [
    /<think>(.*?)<\/think>/s,
    /<thinking>(.*?)<\/thinking>/s,
    /<思考>(.*?)<\/思考>/s,
    /<thought>(.*?)<\/thought>/s,
    /<reasoning>(.*?)<\/reasoning>/s,
    /<分析>(.*?)<\/分析>/s,
    /<推理>(.*?)<\/推理>/s
  ]
  
  let thinkingContent = ''
  let answerContent = content
  
  for (let i = 0; i < thinkingPatterns.length; i++) {
    const pattern = thinkingPatterns[i]
    console.log(`测试模式 ${i + 1}:`, pattern)
    const match = content.match(pattern)
    if (match) {
      console.log('找到思考标签:', match[0])
      console.log('匹配的完整标签:', match[0])
      thinkingContent = match[1].trim()
      // 移除思考标签，保留剩余内容作为答案
      answerContent = content.replace(pattern, '').trim()
      console.log('思考内容:', thinkingContent)
      console.log('答案内容:', answerContent)
      break
    } else {
      console.log(`模式 ${i + 1} 没有匹配`)
    }
  }
  
  if (!thinkingContent) {
    console.log('没有找到思考标签，所有内容作为答案显示')
    // 手动检查是否包含think标签
    if (content.includes('<think>')) {
      console.log('发现内容包含<think>标签，但正则表达式没有匹配到')
      console.log('尝试手动提取...')
      const startIndex = content.indexOf('<think>')
      const endIndex = content.indexOf('</think>')
      if (startIndex !== -1 && endIndex !== -1) {
        thinkingContent = content.substring(startIndex + 7, endIndex).trim()
        answerContent = content.substring(endIndex + 8).trim()
        console.log('手动提取成功:')
        console.log('思考内容:', thinkingContent)
        console.log('答案内容:', answerContent)
      }
    }
  }
  
  return { thinkingContent, answerContent }
})

const thinkingContent = computed(() => thinkingData.value.thinkingContent)
const answerContent = computed(() => thinkingData.value.answerContent)
</script>

<style scoped>
.thinking-renderer {
  width: 100%;
}

.thinking-section {
  margin-bottom: 16px;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
  border-left: 3px solid #adb5bd;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.thinking-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #e9ecef;
}

.thinking-icon {
  font-size: 14px;
  color: #adb5bd;
  margin-right: 6px;
}

.thinking-title {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.thinking-content {
  font-size: 0.75rem;
  color: #adb5bd;
  line-height: 1.5;
  font-style: italic;
}

.thinking-content :deep(p) {
  margin: 0 0 6px 0;
}

.thinking-content :deep(p:last-child) {
  margin-bottom: 0;
}

.thinking-content :deep(code) {
  background-color: #e9ecef;
  padding: 1px 3px;
  border-radius: 2px;
  font-size: 0.7em;
  color: #6c757d;
}

.thinking-content :deep(pre) {
  background-color: #e9ecef;
  padding: 6px 10px;
  border-radius: 3px;
  overflow-x: auto;
  margin: 6px 0;
  border: 1px solid #dee2e6;
  font-size: 0.7em;
}

.thinking-content :deep(ul), .thinking-content :deep(ol) {
  margin: 6px 0;
  padding-left: 16px;
}

.thinking-content :deep(li) {
  margin: 2px 0;
}

.answer-section {
  font-size: 1rem;
  color: #212529;
  line-height: 1.6;
}

.answer-section :deep(p) {
  margin: 0 0 12px 0;
}

.answer-section :deep(p:last-child) {
  margin-bottom: 0;
}

.answer-section :deep(code) {
  background-color: #f1f3f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
  color: #d73a49;
}

.answer-section :deep(pre) {
  background-color: #f8f9fa;
  padding: 12px 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid #e9ecef;
}

.answer-section :deep(ul), .answer-section :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.answer-section :deep(li) {
  margin: 6px 0;
}

.answer-section :deep(blockquote) {
  border-left: 4px solid #007bff;
  padding-left: 16px;
  margin: 12px 0;
  color: #6c757d;
  font-style: italic;
}
</style> 