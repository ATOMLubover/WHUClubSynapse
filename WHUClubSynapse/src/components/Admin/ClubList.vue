<template>
  <div class="club-list">
    <el-card>
      <template #header>
        <span>社团列表管理</span>
      </template>

      <el-table :data="clubs" v-loading="loading">
        <el-table-column prop="name" label="社团名称" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="memberCount" label="成员数" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="primary" size="small">编辑</el-button>
            <el-button type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const clubs = ref([
  { id: 1, name: '计算机协会', category: '学术科技', memberCount: 120, status: 'active' },
  { id: 2, name: '摄影社', category: '文艺体育', memberCount: 85, status: 'active' },
])

onMounted(() => {
  console.log('社团列表管理页面初始化')
})
</script>

<style scoped>
.club-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
</style>
