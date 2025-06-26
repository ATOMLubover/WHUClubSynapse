<template>
  <div class="user-center">
    <div class="user-layout">
      <!-- 侧边栏 -->
      <UserSidebar />
      <!-- 主内容区 -->
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import UserSidebar from '@/components/User/UserSidebar.vue'
</script>

<style>
.user-center {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.user-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
</style>
