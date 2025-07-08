<template>
  <div class="user-center">
    <UserSidebar style="position: fixed; width: 250px; top: 90px" />

    <div class="user-layout">
      <!-- 侧边栏 -->
      <div class="user-sidebar"></div>
      <!-- 主内容区 -->
      <router-view class="user-view" />
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
  padding: 10px;
}

.user-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.user-sidebar {
  width: 300px;
  min-height: calc(100vh - 60px);
}

.user-view {
  background: rgba(255, 255, 255, 0.9);
  margin: 0;
  border-radius: 16px;
}
</style>
