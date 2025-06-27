<template>
  <el-button type="primary" @click="handle"> 点击测试 </el-button>
  <el-button type="primary" @click="handle2"> 获取验证码 </el-button>
  <el-button type="primary" @click="handle3"> 注册 </el-button>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import request from '@/utils/request'
const handle = async () => {
  const res = await request.post('/user/login', {
    username: 'whu',
    password: '123456',
  })
  console.log(res)
}

const handle2 = async () => {
  const res = await request.post('/user/verify', {
    email: '3246119723@qq.com',
  })
  console.log(res)
}

const handle3 = async () => {
  const res = await request.post('/user/register', {
    username: 'whu',
    password: '123456',
    vrf_code: '1234',
    email: '3246119723@qq.com',
  })
  console.log(res)
  debugger
}
</script>
