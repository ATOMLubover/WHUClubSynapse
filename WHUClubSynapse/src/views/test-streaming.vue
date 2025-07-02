<template>
  <div class="test-streaming-page">
    <h2>流式差异渲染测试</h2>
    
    <div class="test-controls">
      <el-button @click="startDemo" :disabled="isRunning">开始演示</el-button>
      <el-button @click="resetDemo">重置</el-button>
    </div>
    
    <div class="test-content">
      <h3>当前渲染内容：</h3>
      <div class="render-container">
        <SmartStreamingRenderer :content="currentContent" />
      </div>
    </div>
    
    <div class="demo-text">
      <h3>将要渲染的文本：</h3>
      <pre>{{ demoText }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SmartStreamingRenderer from '@/components/SmartStreamingRenderer.vue'

const isRunning = ref(false)
const currentContent = ref('')

const demoText = `这是一段正常的文本内容。<think>这里是AI的深度思考过程，应该用更小的字体和更淡的颜色显示。这部分内容包含了AI的推理过程和分析步骤。</think>思考完成后，这里又回到了正常的文本渲染模式。`

const startDemo = async () => {
  if (isRunning.value) return
  
  isRunning.value = true
  currentContent.value = ''
  
  // 逐字符添加内容，模拟流式输入
  for (let i = 0; i < demoText.length; i++) {
    currentContent.value += demoText[i]
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 50))
  }
  
  isRunning.value = false
}

const resetDemo = () => {
  currentContent.value = ''
  isRunning.value = false
}
</script>

<style scoped>
.test-streaming-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.test-controls {
  margin: 20px 0;
}

.test-controls .el-button {
  margin-right: 10px;
}

.render-container {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #f8f9fa;
  min-height: 100px;
  margin: 10px 0;
}

.demo-text {
  margin-top: 20px;
}

.demo-text pre {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 