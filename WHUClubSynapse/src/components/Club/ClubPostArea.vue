<template>
  <div class="club-post-area">
    <div class="post-header">
      <h2>社团帖子区</h2>
      <el-button
        type="primary"
        @click="authStore.isLoggedIn ? (showCreate = true) : ElMessage.warning('请先登录')"
        class="post-btn"
        plain
      >
        <el-icon><Plus /></el-icon> 发帖
      </el-button>
    </div>
    <el-empty v-if="!posts.length && !loading" description="暂无帖子" />
    <div v-else class="post-list">
      <div v-for="post in posts" :key="post.id" class="post-card" @click="goToPost(post)">
        <div class="post-card-main">
          <div class="post-title">{{ post.title }}</div>
          <div class="post-meta">
            <el-avatar :size="28" :src="post.authorAvatar || ''" />
            <span class="author">{{ post.authorName }}</span>
            <span class="time">{{ formatDate(post.createdAt) }}</span>
            <span class="reply"
              ><el-icon><ChatLineRound /></el-icon> {{ post.replyCount }}</span
            >
          </div>
          <div class="post-abstract">
            {{ post.content.slice(0, 50) }}<span v-if="post.content.length > 50">...</span>
          </div>
        </div>
        <el-icon class="arrow"><ArrowRightBold /></el-icon>
      </div>
    </div>
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
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="5"
            maxlength="500"
            show-word-limit
          />
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
import { Plus, ChatLineRound, ArrowRightBold } from '@element-plus/icons-vue'

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
      authorId: authStore.user?.id || 0,
      authorName: authStore.user?.realName || '匿名',
      authorAvatar: authStore.user?.avatar_url || '',
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
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 32px 24px 24px 24px;
}
.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.post-header h2 {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 1px;
}
.post-btn {
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  color: #fff;
  border: none;
  font-weight: 500;
  border-radius: 20px;
  padding: 0 22px;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.08);
  transition: box-shadow 0.2s;
}
.post-btn:hover {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.18);
  opacity: 0.92;
}
.post-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.post-card {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  padding: 18px 20px;
  cursor: pointer;
  transition:
    box-shadow 0.2s,
    background 0.2s,
    transform 0.1s;
  position: relative;
  border: 1px solid #f0f0f0;
}
.post-card:hover {
  background: #e6f0ff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px) scale(1.01);
}
.post-card-main {
  flex: 1;
  min-width: 0;
}
.post-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #222;
  word-break: break-all;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #888;
  margin-bottom: 6px;
}
.post-meta .reply {
  display: flex;
  align-items: center;
  gap: 2px;
  color: #409eff;
  font-weight: 500;
}
.post-abstract {
  color: #666;
  font-size: 15px;
  margin-top: 2px;
  word-break: break-all;
}
.arrow {
  font-size: 20px;
  color: #bbb;
  margin-left: 12px;
  transition: color 0.2s;
}
.post-card:hover .arrow {
  color: #409eff;
}
.pagination {
  margin-top: 20px;
  text-align: right;
}
@media (max-width: 600px) {
  .club-post-area {
    padding: 12px 2vw 12px 2vw;
  }
  .post-title {
    font-size: 15px;
  }
  .post-header h2 {
    font-size: 17px;
  }
  .post-card {
    padding: 12px 8px;
  }
}
</style>
