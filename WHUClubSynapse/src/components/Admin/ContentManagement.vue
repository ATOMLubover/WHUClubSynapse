<template>
  <div class="content-management">
    <el-card>
      <template #header>
        <span>内容管理</span>
      </template>
      <p>内容管理功能</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
console.log('内容管理页面初始化')
</script>

<style scoped>
.content-management {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
