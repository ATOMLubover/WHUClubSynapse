<template>
  <el-button @click="test">测试更新社团的申请列表连接</el-button>
  <el-button @click="test2">测试获取用户信息连接</el-button>
</template>

<script setup lang="ts">
import { getUserById } from '@/api/auth'
import type { ClubCreatedApplication, ClubUpdateApplication } from '@/types'
import request from '@/utils/request'
const test = async () => {
  const response = await request.get('/api/club/pub/my_update_applis')
  console.log(response)
}

const test2 = async () => {
  const response = await getUserById(4)
  console.log(response)
}
</script>
<style scoped></style>
