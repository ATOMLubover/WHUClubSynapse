<template>
  <div class="system-settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      <p>系统设置功能</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
console.log('系统设置页面初始化')
</script>

<style scoped>
.system-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
