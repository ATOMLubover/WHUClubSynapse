<template>
  <div class="ai-differential-renderer">
    <div v-for="(segment, index) in streamingSegments" :key="index" :class="segment.class">
      <MarkdownRenderer :content="segment.content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref } from 'vue'
import MarkdownRenderer from './MarkdownRenderer.vue'

interface Props {
  content: string
}

const props = defineProps<Props>()

interface StreamingSegment {
  content: string
  class: string
  type: 'thinking' | 'normal'
}

// 流式渲染状态
const isInThinkingMode = ref(false)
const currentContent = ref('')
const processedIndex = ref(0)

// 流式分段处理
const streamingSegments = computed((): StreamingSegment[] => {
  const content = props.content
  if (!content) return []
  
  const segments: StreamingSegment[] = []
  let currentPos = 0
  let inThinking = false
  let buffer = ''
  
  // 逐字符处理内容，检测标签
  while (currentPos < content.length) {
    const remaining = content.substring(currentPos)
    
    if (!inThinking) {
      // 查找 <think> 开始标签
      const thinkStartMatch = remaining.match(/^<think>/i)
      if (thinkStartMatch) {
        // 先保存之前的正常内容
        if (buffer.trim()) {
          segments.push({
            content: buffer,
            class: 'normal-segment',
            type: 'normal'
          })
        }
        buffer = ''
        inThinking = true
        currentPos += thinkStartMatch[0].length
        continue
      } else {
        // 继续添加正常内容
        buffer += content[currentPos]
        currentPos++
      }
    } else {
      // 在思考模式中，查找 </think> 结束标签
      const thinkEndMatch = remaining.match(/^<\/think>/i)
      if (thinkEndMatch) {
        // 保存思考内容
        if (buffer.trim()) {
          segments.push({
            content: buffer,
            class: 'thinking-segment',
            type: 'thinking'
          })
        }
        buffer = ''
        inThinking = false
        currentPos += thinkEndMatch[0].length
        continue
      } else {
        // 继续添加思考内容
        buffer += content[currentPos]
        currentPos++
      }
    }
  }
  
  // 处理剩余内容
  if (buffer.trim()) {
    segments.push({
      content: buffer,
      class: inThinking ? 'thinking-segment' : 'normal-segment',
      type: inThinking ? 'thinking' : 'normal'
    })
  }
  
  // 如果没有分段，整个内容作为正常内容
  if (segments.length === 0) {
    segments.push({
      content: content,
      class: 'normal-segment',
      type: 'normal'
    })
  }
  
  return segments
})

// 监听内容变化，实时更新渲染
watch(() => props.content, (newContent, oldContent) => {
  // 检测是否有新的内容追加
  if (newContent && oldContent && newContent.startsWith(oldContent)) {
    // 这是流式追加，重新计算分段
    processedIndex.value = 0
  }
}, { immediate: true })
</script>

<style scoped>
.ai-differential-renderer {
  width: 100%;
}

.normal-segment {
  font-size: 1rem;
  color: #212529;
  line-height: 1.6;
}

.normal-segment :deep(p) {
  margin: 0 0 12px 0;
}

.normal-segment :deep(p:last-child) {
  margin-bottom: 0;
}

.normal-segment :deep(code) {
  background-color: #f1f3f4;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
  color: #d73a49;
}

.normal-segment :deep(pre) {
  background-color: #f8f9fa;
  padding: 12px 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid #e9ecef;
}

.thinking-segment {
  font-size: 0.75rem;
  color: #adb5bd;
  line-height: 1.5;
  font-style: italic;
  margin: 8px 0;
  padding: 8px 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
  border-left: 3px solid #adb5bd;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.thinking-segment :deep(p) {
  margin: 0 0 6px 0;
}

.thinking-segment :deep(p:last-child) {
  margin-bottom: 0;
}

.thinking-segment :deep(code) {
  background-color: #e9ecef;
  padding: 1px 3px;
  border-radius: 2px;
  font-size: 0.7em;
  color: #6c757d;
}

.thinking-segment :deep(pre) {
  background-color: #e9ecef;
  padding: 6px 10px;
  border-radius: 3px;
  overflow-x: auto;
  margin: 6px 0;
  border: 1px solid #dee2e6;
  font-size: 0.7em;
}

.thinking-segment :deep(ul), .thinking-segment :deep(ol) {
  margin: 6px 0;
  padding-left: 16px;
}

.thinking-segment :deep(li) {
  margin: 2px 0;
}
</style> 