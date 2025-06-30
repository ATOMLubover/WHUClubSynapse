<template>
  <div class="system-backup">
    <el-card>
      <template #header>
        <span>数据备份</span>
      </template>
      <p>数据备份功能</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
console.log('数据备份页面初始化')
</script>

<style scoped>
.system-backup {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
