<template>
  <div class="markdown-renderer" v-html="renderedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import katex from 'katex'
import 'katex/dist/katex.min.css'

interface Props {
  content: string
  options?: {
    breaks?: boolean
    gfm?: boolean
  }
}

const props = withDefaults(defineProps<Props>(), {
  content: '',
  options: () => ({
    breaks: true,
    gfm: true
  })
})

// 配置marked选项
marked.setOptions({
  breaks: props.options.breaks,
  gfm: props.options.gfm
})

// 预处理数学公式
const preprocessMath = (text: string): string => {
  // 处理块级数学公式 $$...$$
  let processed = text.replace(/\$\$([^\$\n]+?)\$\$/g, (match: string, formula: string) => {
    try {
      return katex.renderToString(formula, {
        throwOnError: false,
        displayMode: true
      })
    } catch (error) {
      console.warn('KaTeX渲染错误:', error)
      return match
    }
  })
  
  // 处理行内数学公式 $...$
  processed = processed.replace(/\$([^\$\n]+?)\$/g, (match: string, formula: string) => {
    try {
      return katex.renderToString(formula, {
        throwOnError: false,
        displayMode: false
      })
    } catch (error) {
      console.warn('KaTeX渲染错误:', error)
      return match
    }
  })
  
  return processed
}

// 计算渲染后的内容
const renderedContent = computed(() => {
  if (!props.content) return ''
  
  try {
    // 先预处理数学公式
    const processedContent = preprocessMath(props.content)
    // 然后渲染Markdown
    return marked(processedContent)
  } catch (error) {
    console.error('Markdown渲染错误:', error)
    return props.content
  }
})
</script>

<style scoped>
.markdown-renderer {
  line-height: 1.6;
  color: #333;
}

.markdown-renderer :deep(h1) {
  font-size: 2em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #eaecef;
  color: #24292e;
}

.markdown-renderer :deep(h2) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #eaecef;
  color: #24292e;
}

.markdown-renderer :deep(h3) {
  font-size: 1.25em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #24292e;
}

.markdown-renderer :deep(h4) {
  font-size: 1em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #24292e;
}

.markdown-renderer :deep(h5) {
  font-size: 0.875em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #24292e;
}

.markdown-renderer :deep(h6) {
  font-size: 0.85em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
  color: #6a737d;
}

.markdown-renderer :deep(p) {
  margin: 0.5em 0;
}

.markdown-renderer :deep(strong) {
  font-weight: bold;
}

.markdown-renderer :deep(em) {
  font-style: italic;
}

.markdown-renderer :deep(code) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.9em;
}

.markdown-renderer :deep(pre) {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}

.markdown-renderer :deep(pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.markdown-renderer :deep(blockquote) {
  margin: 1em 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  margin: 1em 0;
  padding-left: 2em;
}

.markdown-renderer :deep(li) {
  margin: 0.25em 0;
}

.markdown-renderer :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.markdown-renderer :deep(th),
.markdown-renderer :deep(td) {
  border: 1px solid #dfe2e5;
  padding: 6px 13px;
  text-align: left;
}

.markdown-renderer :deep(th) {
  background-color: #f6f8fa;
  font-weight: bold;
}

.markdown-renderer :deep(hr) {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #e1e4e8;
  border: 0;
}

.markdown-renderer :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-renderer :deep(a:hover) {
  text-decoration: underline;
}

.markdown-renderer :deep(img) {
  max-width: 100%;
  height: auto;
}

/* KaTeX样式优化 */
.markdown-renderer :deep(.katex) {
  font-size: 1.1em;
}

.markdown-renderer :deep(.katex-display) {
  margin: 1em 0;
  text-align: center;
}
</style> 