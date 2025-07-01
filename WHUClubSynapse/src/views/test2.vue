<template>
  <el-button @click="test">测试创建社团的申请列表连接</el-button>
</template>

<script setup lang="ts">
import request from '@/utils/request'
const test = async () => {
  const response = await request.get('/api/club/my_createapplis')
  console.log(response)
}
</script>
<style scoped></style>
