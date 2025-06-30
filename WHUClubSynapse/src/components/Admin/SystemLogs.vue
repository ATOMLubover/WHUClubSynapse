<template>
  <div class="system-logs">
    <el-card>
      <template #header>
        <span>操作日志</span>
      </template>
      <p>操作日志功能</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
console.log('操作日志页面初始化')
</script>

<style scoped>
.system-logs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
