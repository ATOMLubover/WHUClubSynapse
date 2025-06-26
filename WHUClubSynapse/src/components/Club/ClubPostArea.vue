<template>
  <div class="club-post-area">
    <div class="post-header">
      <h2>社团帖子区</h2>
      <el-button type="primary" @click="showCreate = true">发帖</el-button>
    </div>
    <el-empty v-if="!posts.length && !loading" description="暂无帖子" />
    <el-table v-else :data="posts" style="width: 100%" @row-click="goToPost">
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="authorName" label="作者" width="100" />
      <el-table-column prop="createdAt" label="发布时间" width="160">
        <template #default="scope">{{ formatDate(scope.row.createdAt) }}</template>
      </el-table-column>
      <el-table-column prop="replyCount" label="回复数" width="80" />
    </el-table>
    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next, jumper, total"
        @current-change="fetchPosts"
      />
    </div>
    <el-dialog v-model="showCreate" title="发新帖" width="400px">
      <el-form :model="createForm" label-width="60px">
        <el-form-item label="标题">
          <el-input v-model="createForm.title" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="createForm.content" type="textarea" :rows="5" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="createLoading">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getClubPosts, createClubPost } from '@/api/club'
import { useAuthStore } from '@/stores/auth'
import type { ClubPost } from '@/types'

const props = defineProps<{ clubId: string }>()
const router = useRouter()
const authStore = useAuthStore()

const posts = ref<ClubPost[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 5
const loading = ref(false)

const showCreate = ref(false)
const createForm = ref({ title: '', content: '' })
const createLoading = ref(false)

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await getClubPosts(props.clubId, page.value, pageSize)
    posts.value = res.data.data.list
    total.value = res.data.data.total
  } finally {
    loading.value = false
  }
}

const goToPost = (row: ClubPost) => {
  router.push(`/club/${props.clubId}/post/${row.id}`)
}

const handleCreate = async () => {
  if (!createForm.value.title.trim() || !createForm.value.content.trim()) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  createLoading.value = true
  try {
    await createClubPost({
      clubId: props.clubId,
      title: createForm.value.title,
      content: createForm.value.content,
      authorId: authStore.user?.id || 'user1',
      authorName: authStore.user?.realName || '匿名',
      authorAvatar: authStore.user?.avatar || '',
    })
    ElMessage.success('发帖成功')
    showCreate.value = false
    createForm.value.title = ''
    createForm.value.content = ''
    fetchPosts()
  } finally {
    createLoading.value = false
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(fetchPosts)
</script>

<style scoped>
.club-post-area {
  margin-top: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 24px;
}
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.pagination {
  margin-top: 16px;
  text-align: right;
}
</style> 