<template>
  <div class="test-page">
    <h1>AI社团介绍生成器测试</h1>
    
    <div class="test-form">
      <el-form label-width="120px">
        <el-form-item label="社团介绍">
          <el-input
            v-model="testIntroduction"
            type="textarea"
            :rows="6"
            placeholder="测试介绍文本"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <!-- AI生成器组件 -->
      <AIIntroductionGenerator v-model="testIntroduction" />
      
      <div class="result-display">
        <h3>当前介绍内容：</h3>
        <div class="content-box">
          {{ testIntroduction || '暂无内容' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AIIntroductionGenerator from '@/components/Chat/AIIntroductionGenerator.vue'

const testIntroduction = ref('')
</script>

<style scoped>
.test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.result-display {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.content-box {
  padding: 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  min-height: 60px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style> 