<template>
  <div class="club-post-detail">
    <div class="post-layout">
      <!-- 左侧帖子内容 -->
      <div class="post-content-area">
        <el-card class="post-main" v-loading="postLoading">
          <div v-if="!postLoading && post">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-meta">
              <el-avatar :size="40" :src="post.authorAvatar || defaultAvatar" class="post-avatar" />
              <div class="meta-info">
                <span class="author">{{ post.authorName }}</span>
                <span class="time">{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
            <div class="post-content">
              <MarkdownRenderer :content="post.content || ''" />
            </div>
          </div>
          <div v-else-if="!postLoading && !post" class="error-content">
            <el-empty description="帖子不存在或已被删除" />
          </div>
        </el-card>
        <el-card class="reply-area" v-loading="repliesLoading">
          <div class="reply-header">全部回复（{{ total }}）</div>
          <el-empty v-if="!replies.length && !repliesLoading" description="暂无回复" />
          <div v-else-if="!repliesLoading" class="reply-list">
            <div v-for="(reply, idx) in replies" :key="reply.comment_id" class="reply-item">
              <el-avatar
                :size="32"
                :src="reply.authorAvatar || defaultAvatar"
                class="reply-avatar"
              />
              <div class="reply-info">
                <div class="reply-meta">
                  <span class="reply-author">{{ reply.authorName }}</span>
                  <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                </div>
                <div class="reply-content">
                  <MarkdownRenderer :content="reply.content || ''" />
                </div>
              </div>
              <div class="reply-floor">#{{ (page - 1) * pageSize + idx + 1 }}</div>
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
            <MarkdownEditor
              v-model="replyContent"
              :rows="4"
              placeholder="说点什么吧..."
              :maxlength="500"
            />
            <el-button
              type="primary"
              @click="handleReply"
              :loading="replyLoading"
              class="reply-btn"
              :disabled="!authStore.isLoggedIn || authStore.isGuest"
              >回复</el-button
            >
          </div>
        </el-card>
      </div>

      <!-- 右侧AI聊天窗口 -->
      <div class="ai-chat-area">
        <AIChatWindow :post-title="post?.title" :post-content="post?.content" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getClubPostDetail, replyClubPost } from '@/api/club'
import { useAuthStore } from '@/stores/auth'
import AIChatWindow from '@/components/Chat/AIChatWindow.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import MarkdownEditor from '@/components/MarkdownEditor.vue'
import type { ClubPost, ClubPostComment } from '@/types'
import { useClubStore } from '@/stores/club'
const defaultAvatar = 'https://cdn.jsdelivr.net/gh/whu-asset/static/avatar-default.png'
const route = useRoute()
const authStore = useAuthStore()
const clubId = String(route.params.clubId)
const postId = String(route.params.postId)
const contentUrl = decodeURIComponent(String(route.params.content_url))
const clubStore = useClubStore()
const post = ref<ClubPost | null>(null)
const replies = ref<ClubPostComment[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const postLoading = ref(false)
const repliesLoading = ref(false)
const replyContent = ref('')
const replyLoading = ref(false)

const fetchPost = async () => {
  try {
    postLoading.value = true

    // 先从store中获取帖子基础信息
    if (clubStore.currentClubPosts.length == 0) {
      await clubStore.fetchClubPosts(clubId, 1, 10)
      console.log('currentClubPosts:', clubStore.currentClubPosts)
    }
    const storePost = clubStore.currentClubPosts.find((p) => p.post_id == postId)

    if (storePost) {
      // 如果store中有基础信息，先使用它
      post.value = { ...storePost }
    }
    console.log('Post:', post.value)

    // 获取markdown内容
    console.log('正在获取帖子详细内容，postId:', postId, 'contentUrl:', contentUrl)
    const res = await getClubPostDetail(postId, contentUrl)
    console.log('获取到的markdown内容:', res)

    // 如果没有基础信息，创建一个基本的post对象
    if (!post.value) {
      post.value = {
        post_id: postId,
        title: '加载中...',
        content: '',
        authorName: '未知作者',
        authorAvatar: defaultAvatar,
        created_at: new Date().toISOString(),
        comment_count: 0,
        club_id: '',
        author_id: 0,
        content_url: contentUrl,
      }
    }

    post.value.content = res
    console.log('post.value.content:', post.value.content)

    console.log('帖子内容已更新:', post.value)
  } catch (error) {
    console.error('获取帖子详情失败:', error)
    ElMessage.error('获取帖子详情失败')
  } finally {
    postLoading.value = false
  }
}

const fetchReplies = async () => {
  repliesLoading.value = true
  try {
    const res = await clubStore.fetchClubPostComments(postId, page.value, pageSize)
    replies.value = res.list
    total.value = res.total
  } finally {
    repliesLoading.value = false
  }
}

const handleReply = async () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  if (clubStore.clubs.find((c) => c.club_id == clubId)?.status != 'joined') {
    ElMessage.warning('请先加入社团')
    return
  }

  if (!replyContent.value.trim()) {
    ElMessage.warning('回复内容不能为空')
    return
  }
  replyLoading.value = true
  const user_id = authStore.getCurrentUserId()
  try {
    await replyClubPost({
      post_id: Number(postId),
      user_id: user_id || 0,
      content: replyContent.value,
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
  max-width: 1400px;
  margin: 32px auto;
  padding: 0 20px;
}

.post-layout {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 200px);
}

.post-content-area {
  flex: 1;
  max-width: 800px;
}

.ai-chat-area {
  width: 400px;
  flex-shrink: 0;
  position: sticky;
  top: 20px;
  height: calc(100vh - 120px);
}

.post-main {
  margin-bottom: 28px;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(64, 158, 255, 0.08);
  background: linear-gradient(135deg, #f8fafc 60%, #e6f0ff 100%);
  padding: 32px 28px 24px 28px;
}

.error-content {
  text-align: center;
  padding: 40px 20px;
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
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.08);
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
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 8px;
  word-break: break-word;
}

.post-content :deep(.markdown-renderer) {
  font-size: 16px;
  line-height: 1.8;
}

.post-content :deep(.markdown-renderer h1) {
  font-size: 1.8em;
  margin: 1.2em 0 0.6em 0;
}

.post-content :deep(.markdown-renderer h2) {
  font-size: 1.5em;
  margin: 1em 0 0.5em 0;
}

.post-content :deep(.markdown-renderer h3) {
  font-size: 1.3em;
  margin: 0.8em 0 0.4em 0;
}

.post-content :deep(.markdown-renderer p) {
  margin: 0.8em 0;
}

.post-content :deep(.markdown-renderer code) {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
}

.post-content :deep(.markdown-renderer pre) {
  background-color: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}

.post-content :deep(.markdown-renderer blockquote) {
  margin: 1em 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.post-content :deep(.markdown-renderer table) {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.post-content :deep(.markdown-renderer th),
.post-content :deep(.markdown-renderer td) {
  border: 1px solid #dfe2e5;
  padding: 6px 13px;
  text-align: left;
}

.post-content :deep(.markdown-renderer th) {
  background-color: #f6f8fa;
  font-weight: bold;
}

.post-content :deep(.katex) {
  font-size: 1.1em;
}

.post-content :deep(.katex-display) {
  margin: 1em 0;
  text-align: center;
}

.reply-area {
  margin-top: 8px;
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.06);
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
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
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
  font-size: 14px;
  color: #333;
  word-break: break-word;
}

.reply-content :deep(.markdown-renderer) {
  font-size: 14px;
  line-height: 1.6;
}

.reply-content :deep(.markdown-renderer h1) {
  font-size: 1.4em;
  margin: 0.8em 0 0.4em 0;
}

.reply-content :deep(.markdown-renderer h2) {
  font-size: 1.2em;
  margin: 0.6em 0 0.3em 0;
}

.reply-content :deep(.markdown-renderer h3) {
  font-size: 1.1em;
  margin: 0.5em 0 0.2em 0;
}

.reply-content :deep(.markdown-renderer p) {
  margin: 0.4em 0;
}

.reply-content :deep(.markdown-renderer code) {
  background-color: #f6f8fa;
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-size: 0.85em;
}

.reply-content :deep(.markdown-renderer pre) {
  background-color: #f6f8fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0.6em 0;
  font-size: 0.85em;
}

.reply-content :deep(.markdown-renderer blockquote) {
  margin: 0.6em 0;
  padding: 0 0.8em;
  color: #6a737d;
  border-left: 0.2em solid #dfe2e5;
  font-size: 0.9em;
}

.reply-content :deep(.katex) {
  font-size: 1em;
}

.reply-content :deep(.katex-display) {
  margin: 0.6em 0;
  text-align: center;
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
  box-shadow: 0 1px 4px rgba(64, 158, 255, 0.04);
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
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.08);
  transition: box-shadow 0.2s;
}

.reply-btn:hover {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.18);
  opacity: 0.92;
}

.pagination {
  margin-top: 16px;
  text-align: right;
}

@media (max-width: 1200px) {
  .post-layout {
    flex-direction: column;
  }

  .ai-chat-area {
    width: 100%;
    height: 500px;
    position: static;
  }
}

@media (max-width: 600px) {
  .club-post-detail {
    padding: 0 2vw;
  }

  .post-layout {
    gap: 16px;
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

  .ai-chat-area {
    height: 400px;
  }
}
</style>
