<template>
  <div class="markdown-editor">
    <div class="editor-toolbar">
      <el-button-group>
        <el-button size="small" @click="insertText('# ', '')" title="一级标题">H1</el-button>
        <el-button size="small" @click="insertText('## ', '')" title="二级标题">H2</el-button>
        <el-button size="small" @click="insertText('### ', '')" title="三级标题">H3</el-button>
      </el-button-group>
      
      <el-button-group>
        <el-button size="small" @click="insertText('**', '**')" title="粗体">B</el-button>
        <el-button size="small" @click="insertText('*', '*')" title="斜体">I</el-button>
        <el-button size="small" @click="insertText('`', '`')" title="行内代码">Code</el-button>
      </el-button-group>
      
      <el-button-group>
        <el-button size="small" @click="insertText('- ', '')" title="无序列表">•</el-button>
        <el-button size="small" @click="insertText('1. ', '')" title="有序列表">1.</el-button>
        <el-button size="small" @click="insertText('> ', '')" title="引用">Quote</el-button>
      </el-button-group>
      
      <el-button-group>
        <el-button size="small" @click="insertText('$', '$')" title="行内数学公式">$</el-button>
        <el-button size="small" @click="insertText('$$\n', '\n$$')" title="块级数学公式">$$</el-button>
      </el-button-group>
      
      <el-button-group>
        <el-button size="small" @click="insertText('[', '](url)')" title="链接">Link</el-button>
        <el-button size="small" @click="insertText('![', '](url)')" title="图片">Image</el-button>
      </el-button-group>
    </div>
    
    <div class="editor-content">
      <div class="editor-tabs">
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="编辑" name="edit">
            <el-input
              v-model="inputValue"
              type="textarea"
              :rows="rows"
              :placeholder="placeholder"
              :maxlength="maxlength"
              show-word-limit
              @input="handleInput"
              class="markdown-textarea"
            />
          </el-tab-pane>
          <el-tab-pane label="预览" name="preview">
            <div class="preview-content">
              <MarkdownRenderer :content="modelValue" />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import MarkdownRenderer from './MarkdownRenderer.vue'

interface Props {
  modelValue: string
  rows?: number
  placeholder?: string
  maxlength?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  rows: 10,
  placeholder: '请输入Markdown内容...',
  maxlength: 5000
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const activeTab = ref('edit')

// 使用computed属性来处理双向绑定
const inputValue = computed({
  get: () => props.modelValue,
  set: (value: string) => {
    emit('update:modelValue', value)
  }
})

// 处理输入
const handleInput = (value: string) => {
  emit('update:modelValue', value)
}

// 插入文本到光标位置
const insertText = (before: string, after: string) => {
  const textarea = document.querySelector('.markdown-textarea textarea') as HTMLTextAreaElement
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = props.modelValue.substring(start, end)
  
  const newText = props.modelValue.substring(0, start) + before + selectedText + after + props.modelValue.substring(end)
  emit('update:modelValue', newText)
  
  // 设置光标位置
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + before.length, end + before.length)
  })
}
</script>

<style scoped>
.markdown-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-toolbar {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.editor-toolbar .el-button-group {
  margin-right: 8px;
}

.editor-content {
  background-color: #fff;
}

.editor-tabs {
  height: 100%;
}

.markdown-textarea {
  border: none;
  resize: vertical;
}

.markdown-textarea :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.6;
  padding: 16px;
}

.preview-content {
  padding: 16px;
  min-height: 200px;
  max-height: 600px;
  overflow-y: auto;
}

/* 自定义标签页样式 */
.editor-tabs :deep(.el-tabs__header) {
  margin: 0;
  background-color: #f5f7fa;
}

.editor-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 16px;
}

.editor-tabs :deep(.el-tabs__item) {
  padding: 8px 16px;
  font-size: 14px;
}

.editor-tabs :deep(.el-tabs__content) {
  padding: 0;
}
</style> 