<template>
  <div class="smart-streaming-renderer">
    <template v-for="(segment, index) in renderSegments" :key="`segment-${index}`">
      <div v-if="segment.type === 'thinking'" :class="segment.class">
        {{ segment.content }}
      </div>
      <div v-else :class="segment.class" v-html="renderMarkdown(segment.content)">
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

interface Props {
  content: string
}

const props = defineProps<Props>()

interface RenderSegment {
  content: string
  class: string
  type: 'thinking' | 'normal'
}

// 配置marked选项
marked.setOptions({
  breaks: true,
  gfm: true
})

// 渲染markdown并优化样式
const renderMarkdown = (content: string): string => {
  if (!content) return ''
  try {
    const html = marked.parse(content) as string
    // 直接在HTML中添加样式
    return html
      .replace(/<p>/g, '<p style="margin: 0.1em 0; line-height: 1.3;">')
      .replace(/<h([1-6])>/g, '<h$1 style="margin: 0.5em 0 0.2em 0; line-height: 1.2;">')
      .replace(/<ul>/g, '<ul style="margin: 0.2em 0; padding-left: 1.2em;">')
      .replace(/<ol>/g, '<ol style="margin: 0.2em 0; padding-left: 1.2em;">')
      .replace(/<li>/g, '<li style="margin: 0.1em 0; line-height: 1.3;">')
      .replace(/<blockquote>/g, '<blockquote style="margin: 0.2em 0; padding: 0.3em 0.8em;">')
      .replace(/<pre>/g, '<pre style="margin: 0.2em 0;">')
      .replace(/<table>/g, '<table style="margin: 0.2em 0;">')
  } catch (error) {
    console.error('Markdown渲染错误:', error)
    return content
  }
}

// 智能流式分段处理
const renderSegments = computed((): RenderSegment[] => {
  const content = props.content
  if (!content) return []
  
  const segments: RenderSegment[] = []
  let currentPos = 0
  let inThinking = false
  let buffer = ''
  
  while (currentPos < content.length) {
    const remaining = content.substring(currentPos)
    
    if (!inThinking) {
      // 检查是否遇到 <think> 开始标签（完整或不完整）
      const thinkStartPattern = /<think>/i
      const thinkStartMatch = remaining.match(thinkStartPattern)
      
      if (thinkStartMatch && thinkStartMatch.index === 0) {
        // 完整的开始标签
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
        // 检查是否是不完整的开始标签
        const partialThinkStart = remaining.match(/^<(?:t(?:h(?:i(?:n(?:k>?)?)?)?)?)?$/i)
        if (partialThinkStart) {
          // 可能是不完整的 <think> 标签，检查是否在末尾
          if (currentPos + partialThinkStart[0].length === content.length) {
            // 在内容末尾的不完整标签，等待更多内容
            if (buffer.trim()) {
              segments.push({
                content: buffer,
                class: 'normal-segment',
                type: 'normal'
              })
            }
            return segments
          }
        }
        
        // 普通字符
        buffer += content[currentPos]
        currentPos++
      }
    } else {
      // 在思考模式中
      const thinkEndPattern = /<\/think>/i
      const thinkEndMatch = remaining.match(thinkEndPattern)
      
      if (thinkEndMatch && thinkEndMatch.index === 0) {
        // 完整的结束标签
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
        // 检查是否是不完整的结束标签
        const partialThinkEnd = remaining.match(/^<(?:\/(?:t(?:h(?:i(?:n(?:k>?)?)?)?)?)?)?$/i)
        if (partialThinkEnd) {
          // 可能是不完整的 </think> 标签，检查是否在末尾
          if (currentPos + partialThinkEnd[0].length === content.length) {
            // 在内容末尾的不完整标签，等待更多内容
            if (buffer.trim()) {
              segments.push({
                content: buffer,
                class: 'thinking-segment',
                type: 'thinking'
              })
            }
            return segments
          }
        }
        
        // 思考模式下的普通字符
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
  
  return segments
})
</script>

<style>
.smart-streaming-renderer {
  line-height: 1.2;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.smart-streaming-renderer .normal-segment {
  font-size: 1rem;
  color: #212529;
  display: block;
  margin: 0;
  padding: 0;
  line-height: 1.2;
}

.smart-streaming-renderer .thinking-segment {
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
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 