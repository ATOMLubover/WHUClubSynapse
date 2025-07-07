<template>
  <div class="typewriter-streaming-renderer">
    <template v-for="(segment, index) in renderSegments" :key="`segment-${index}`">
      <div v-if="segment.type === 'thinking'" :class="segment.class">
        {{ segment.content }}
      </div>
      <div v-else :class="segment.class">
        {{ segment.content }}
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  content: string
}

const props = defineProps<Props>()

interface RenderSegment {
  content: string
  class: string
  type: 'thinking' | 'normal'
}

// 打字机效果相关
const renderSegments = ref<RenderSegment[]>([])
const tokenQueue = ref<string[]>([])
const isTyping = ref(false)
const typingSpeed = 20 // 打字速度（毫秒）

// 智能流式分段处理
const parseContent = (content: string): RenderSegment[] => {
  const segments: RenderSegment[] = []
  let currentPos = 0
  let inThinking = false
  let buffer = ''
  
  while (currentPos < content.length) {
    const remaining = content.substring(currentPos)
    
    if (!inThinking) {
      const thinkStartPattern = /<think>/i
      const thinkStartMatch = remaining.match(thinkStartPattern)
      
      if (thinkStartMatch && thinkStartMatch.index === 0) {
        if (buffer.trim()) {
          segments.push({
            content: buffer,
            class: 'normal-segment',
            type: 'normal'
          })
          buffer = ''
        }
        inThinking = true
        currentPos += thinkStartMatch[0].length
        continue
      } else {
        const partialThinkStart = remaining.match(/^<(?:t(?:h(?:i(?:n(?:k>?)?)?)?)?)?$/i)
        if (partialThinkStart && currentPos + partialThinkStart[0].length === content.length) {
          if (buffer.trim()) {
            segments.push({
              content: buffer,
              class: 'normal-segment',
              type: 'normal'
            })
          }
          return segments
        }
        
        buffer += content[currentPos]
        currentPos++
      }
    } else {
      const thinkEndPattern = /<\/think>/i
      const thinkEndMatch = remaining.match(thinkEndPattern)
      
      if (thinkEndMatch && thinkEndMatch.index === 0) {
        if (buffer.trim()) {
          segments.push({
            content: buffer,
            class: 'thinking-segment',
            type: 'thinking'
          })
          buffer = ''
        }
        inThinking = false
        currentPos += thinkEndMatch[0].length
        continue
      } else {
        const partialThinkEnd = remaining.match(/^<(?:\/(?:t(?:h(?:i(?:n(?:k>?)?)?)?)?)?)?$/i)
        if (partialThinkEnd && currentPos + partialThinkEnd[0].length === content.length) {
          if (buffer.trim()) {
            segments.push({
              content: buffer,
              class: 'thinking-segment',
              type: 'thinking'
            })
          }
          return segments
        }
        
        buffer += content[currentPos]
        currentPos++
      }
    }
  }
  
  if (buffer.trim()) {
    segments.push({
      content: buffer,
      class: inThinking ? 'thinking-segment' : 'normal-segment',
      type: inThinking ? 'thinking' : 'normal'
    })
  }
  
  return segments
}

// 打字机效果处理
const processTypewriter = async () => {
  if (isTyping.value || tokenQueue.value.length === 0) return
  
  // 在开始渲染前，输出完整的队列内容
  console.log('完整的AI回复内容:', tokenQueue.value.join(''))
  
  isTyping.value = true
  let currentContent = ''
  
  while (tokenQueue.value.length > 0) {
    const token = tokenQueue.value.shift()
    if (token) {
      currentContent += token
      renderSegments.value = parseContent(currentContent)
      await new Promise(resolve => setTimeout(resolve, typingSpeed))
    }
  }
  
  isTyping.value = false
}

// 监听内容变化
watch(() => props.content, (newContent) => {
  if (!newContent) {
    renderSegments.value = []
    tokenQueue.value = []
    return
  }
  
  // 将新内容转换为字符数组并加入队列
  tokenQueue.value = newContent.split('')
  processTypewriter()
}, { immediate: true })
</script>

<style>
.typewriter-streaming-renderer {
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.typewriter-streaming-renderer .normal-segment {
  font-size: 1rem;
  color: #212529;
  display: block;
  margin: 0;
  padding: 0;
}

.typewriter-streaming-renderer .thinking-segment {
  font-size: 0.75rem;
  color: #adb5bd;
  font-style: italic;
  display: block;
  background: linear-gradient(135deg, rgba(248, 249, 250, 0.8) 0%, rgba(241, 243, 244, 0.8) 100%);
  padding: 8px 12px;
  border-left: 3px solid #adb5bd;
  border-radius: 6px;
  margin: 8px 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}
</style> 