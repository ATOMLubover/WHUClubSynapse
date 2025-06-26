<template>
  <div class="club-post-detail">
    <el-card class="post-main">
      <div class="post-title">{{ post?.title }}</div>
      <div class="post-meta">
        <el-avatar :size="40" :src="post?.authorAvatar || defaultAvatar" class="post-avatar" />
        <div class="meta-info">
          <span class="author">{{ post?.authorName }}</span>
          <span class="time">{{ formatDate(post?.createdAt) }}</span>
        </div>
      </div>
      <div class="post-content">{{ post?.content }}</div>
    </el-card>
    <el-card class="reply-area">
      <div class="reply-header">全部回复（{{ total }}）</div>
      <el-empty v-if="!replies.length && !loading" description="暂无回复" />
      <div v-else class="reply-list">
        <div v-for="(reply, idx) in replies" :key="reply.id" class="reply-item">
          <el-avatar :size="32" :src="reply.authorAvatar || defaultAvatar" class="reply-avatar" />
          <div class="reply-info">
            <div class="reply-meta">
              <span class="reply-author">{{ reply.authorName }}</span>
              <span class="reply-time">{{ formatDate(reply.createdAt) }}</span>
            </div>
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
      <div class="reply-input-area">
        <el-input
          v-model="replyContent"
          type="textarea"
          :rows="3"
          maxlength="300"
          show-word-limit
          placeholder="说点什么吧..."
          class="reply-input"
        />
        <el-button type="primary" @click="handleReply" :loading="replyLoading" class="reply-btn">回复</el-button>
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

const defaultAvatar = 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png'
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
      authorId: authStore.user?.id || 0,
      authorName: authStore.user?.realName || '匿名',
      authorAvatar: authStore.user?.avatar_url || defaultAvatar,
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
  margin-bottom: 28px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(64,158,255,0.08);
  background: linear-gradient(135deg, #f8fafc 60%, #e6f0ff 100%);
  padding: 32px 28px 24px 28px;
}
.post-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 14px;
  color: #222;
  letter-spacing: 1px;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #888;
  font-size: 15px;
  margin-bottom: 18px;
}
.post-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(64,158,255,0.08);
}
.meta-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.author {
  font-weight: 600;
  color: #409eff;
}
.time {
  font-size: 13px;
  color: #aaa;
}
.post-content {
  font-size: 18px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 8px;
  word-break: break-all;
}
.reply-area {
  margin-top: 8px;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(64,158,255,0.06);
  padding: 28px 20px 20px 20px;
}
.reply-header {
  font-weight: 600;
  margin-bottom: 18px;
  font-size: 17px;
  color: #222;
}
.reply-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.reply-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #f8fafc;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  padding: 14px 18px 14px 14px;
  position: relative;
  border: 1px solid #f0f0f0;
}
.reply-avatar {
  border: 1.5px solid #fff;
}
.reply-info {
  flex: 1;
  min-width: 0;
}
.reply-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 2px;
}
.reply-author {
  font-weight: 500;
  color: #409eff;
}
.reply-time {
  color: #aaa;
  font-size: 13px;
}
.reply-content {
  margin-top: 2px;
  font-size: 15px;
  color: #333;
  word-break: break-all;
}
.reply-floor {
  position: absolute;
  right: 18px;
  top: 14px;
  color: #bbb;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 1px;
}
.reply-input-area {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: #f4f8ff;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(64,158,255,0.04);
  padding: 16px 12px 12px 12px;
}
.reply-input {
  border-radius: 8px;
  font-size: 15px;
}
.reply-btn {
  align-self: flex-end;
  margin-top: 4px;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  color: #fff;
  border: none;
  font-weight: 500;
  border-radius: 20px;
  padding: 0 22px;
  box-shadow: 0 2px 8px rgba(64,158,255,0.08);
  transition: box-shadow 0.2s;
}
.reply-btn:hover {
  box-shadow: 0 4px 16px rgba(64,158,255,0.18);
  opacity: 0.92;
}
.pagination {
  margin-top: 16px;
  text-align: right;
}
@media (max-width: 600px) {
  .club-post-detail {
    padding: 0 2vw;
  }
  .post-main {
    padding: 16px 4vw 12px 4vw;
  }
  .reply-area {
    padding: 12px 2vw 8px 2vw;
  }
  .post-title {
    font-size: 18px;
  }
  .reply-header {
    font-size: 15px;
  }
}
</style> 