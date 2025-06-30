<template>
  <el-button @click="test">test</el-button>
</template>

<script setup lang="ts">
import request from '@/utils/request'
import { ref } from 'vue'

const test = () => {
  request.get('/auth/my_info').then((res) => {
    console.log(res.data.data)
  })
}
</script>
