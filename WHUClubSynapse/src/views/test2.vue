<template>
  <el-button @click="test">测试创建社团的申请列表连接</el-button>
  <el-button @click="test2">测试获取用户信息连接</el-button>
</template>

<script setup lang="ts">
import { getUserById } from '@/api/auth'
import type { ClubCreatedApplication } from '@/types'
import request from '@/utils/request'
const test = async () => {
  const response = await request.get('/api/club/my_createapplis')
  const clubcreateapplication: ClubCreatedApplication[] = response.data
  console.log(clubcreateapplication)
}

const test2 = async () => {
  const response = await getUserById(4)
  console.log(response)
}
</script>
<style scoped></style>
