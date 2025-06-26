<template>
  <div class="club-post-detail">
    <el-card class="post-main">
      <div class="post-title">{{ post?.title }}</div>
      <div class="post-meta">
        <el-avatar :size="32" :src="post?.authorAvatar || ''" />
        <span class="author">{{ post?.authorName }}</span>
        <span class="time">{{ formatDate(post?.createdAt) }}</span>
      </div>
      <div class="post-content">{{ post?.content }}</div>
    </el-card>
    <el-card class="reply-area">
      <div class="reply-header">全部回复（{{ total }}）</div>
      <el-empty v-if="!replies.length && !loading" description="暂无回复" />
      <div v-else>
        <div v-for="(reply, idx) in replies" :key="reply.id" class="reply-item">
          <el-avatar :size="28" :src="reply.authorAvatar || ''" />
          <div class="reply-info">
            <span class="reply-author">{{ reply.authorName }}</span>
            <span class="reply-time">{{ formatDate(reply.createdAt) }}</span>
            <div class="reply-content">{{ reply.content }}</div>
          </div>
          <div class="reply-floor">#{{ (page-1)*pageSize + idx + 1 }}</div>
        </div>
        <div class="pagination" v-if="total > pageSize">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next, jumper, total"
            @current-change="fetchReplies"
          />
        </div>
      </div>
      <el-divider />
      <div class="reply-input">
        <el-input
          v-model="replyContent"
          type="textarea"
          :rows="3"
          maxlength="300"
          show-word-limit
          placeholder="说点什么吧..."
        />
        <el-button type="primary" @click="handleReply" :loading="replyLoading" style="margin-top:8px">回复</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getClubPostDetail, getClubPostReplies, replyClubPost } from '@/api/club'
import { useAuthStore } from '@/stores/auth'
import type { ClubPost, ClubPostReply } from '@/types'

const route = useRoute()
const authStore = useAuthStore()
const clubId = String(route.params.clubId)
const postId = String(route.params.postId)

const post = ref<ClubPost | null>(null)
const replies = ref<ClubPostReply[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const replyContent = ref('')
const replyLoading = ref(false)

const fetchPost = async () => {
  const res = await getClubPostDetail(postId)
  post.value = res.data.data
}
const fetchReplies = async () => {
  loading.value = true
  try {
    const res = await getClubPostReplies(postId, page.value, pageSize)
    replies.value = res.data.data.list
    total.value = res.data.data.total
  } finally {
    loading.value = false
  }
}
const handleReply = async () => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('回复内容不能为空')
    return
  }
  replyLoading.value = true
  try {
    await replyClubPost({
      postId,
      authorId: authStore.user?.id || 'user1',
      authorName: authStore.user?.realName || '匿名',
      authorAvatar: authStore.user?.avatar || '',
      content: replyContent.value
    })
    ElMessage.success('回复成功')
    replyContent.value = ''
    fetchReplies()
  } finally {
    replyLoading.value = false
  }
}
const formatDate = (date?: string) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN')
}
onMounted(() => {
  fetchPost()
  fetchReplies()
})
</script>

<style scoped>
.club-post-detail {
  max-width: 800px;
  margin: 32px auto;
}
.post-main {
  margin-bottom: 24px;
}
.post-title {
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 8px;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #888;
  font-size: 14px;
  margin-bottom: 12px;
}
.post-content {
  font-size: 16px;
  line-height: 1.7;
  margin-bottom: 8px;
}
.reply-area {
  margin-top: 8px;
}
.reply-header {
  font-weight: 500;
  margin-bottom: 12px;
}
.reply-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  border-bottom: 1px solid #f0f0f0;
  padding: 12px 0;
  position: relative;
}
.reply-info {
  flex: 1;
}
.reply-author {
  font-weight: 500;
  margin-right: 8px;
}
.reply-time {
  color: #aaa;
  font-size: 13px;
}
.reply-content {
  margin-top: 4px;
  font-size: 15px;
}
.reply-floor {
  position: absolute;
  right: 0;
  top: 12px;
  color: #bbb;
  font-size: 13px;
}
.reply-input {
  margin-top: 12px;
}
.pagination {
  margin-top: 12px;
  text-align: right;
}
</style> 