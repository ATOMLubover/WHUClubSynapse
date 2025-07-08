<template>
  <div class="footer-container">
    <div class="footer-content">
      <span>© 2024 武汉大学社团联盟</span>
      <span class="divider">|</span>
      <span>让社团生活更精彩</span>
      <span class="divider">|</span>
      <span @click="aboutUs" class="about-us">关于我们</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
const aboutUs = () => {
  router.push('/about')
}
</script>

<style scoped>
.footer-container {
  background-color: transparent;
  border-top: 1px solid #e4e7ed;
  padding: 0 20px;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  color: #909399;
  font-size: 14px;
}

.divider {
  margin: 0 12px;
}
.about-us {
  cursor: pointer;
  color: #409eff;
}
</style>
