<template>
  <div class="streaming-renderer">
    <span 
      v-for="(char, index) in renderChars" 
      :key="`char-${index}`"
      :class="char.class"
    >{{ char.char }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  content: string
}

const props = defineProps<Props>()

interface CharData {
  char: string
  class: string
  type: 'thinking' | 'normal'
}

// 流式渲染状态
const currentMode = ref<'normal' | 'thinking'>('normal')
const tagBuffer = ref('')

// 逐字符处理渲染
const renderChars = computed((): CharData[] => {
  const content = props.content
  if (!content) return []
  
  const chars: CharData[] = []
  let inThinking = false
  let i = 0
  
  while (i < content.length) {
    const remaining = content.substring(i)
    
    // 检查是否是 <think> 开始标签
    if (!inThinking && remaining.toLowerCase().startsWith('<think>')) {
      inThinking = true
      i += 7 // 跳过 '<think>' 标签
      continue
    }
    
    // 检查是否是 </think> 结束标签
    if (inThinking && remaining.toLowerCase().startsWith('</think>')) {
      inThinking = false
      i += 8 // 跳过 '</think>' 标签
      continue
    }
    
    // 添加字符
    chars.push({
      char: content[i],
      class: inThinking ? 'thinking-char' : 'normal-char',
      type: inThinking ? 'thinking' : 'normal'
    })
    
    i++
  }
  
  return chars
})
</script>

<style scoped>
.streaming-renderer {
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.normal-char {
  font-size: 1rem;
  color: #212529;
}

.thinking-char {
  font-size: 0.75rem;
  color: #adb5bd;
  font-style: italic;
  background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
  padding: 0 1px;
  margin: 0;
  border-radius: 2px;
}
</style> 