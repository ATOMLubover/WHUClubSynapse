<template>
  <div class="club-categories">
    <el-card>
      <template #header>
        <span>分类管理</span>
      </template>
      <p>社团分类管理功能</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  console.log('分类管理页面初始化')
})
</script>

<style scoped>
.club-categories {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
