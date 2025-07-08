<template>
  <div class="club-post-area">
    <div class="post-header">
      <h2>社团帖子区</h2>
      <el-button
        type="primary"
        @click="showCreateDialog()"
        class="post-btn"
        plain
        :disabled="!authStore.isLoggedIn || authStore.isGuest"
      >
        <el-icon><Plus /></el-icon> 发帖
      </el-button>
    </div>

    <!-- 调试信息 -->
    <div v-if="loading" style="text-align: center; padding: 20px; color: #666">正在加载帖子...</div>

    <div v-else-if="!filteredPosts.length" style="text-align: center; padding: 20px; color: #666">
      暂无帖子 (总数: {{ total - 1 }})
    </div>

    <div v-else class="post-list">
      <div
        v-for="post in filteredPosts"
        :key="post.post_id"
        class="post-card"
        @click="goToPost(post)"
      >
        <div class="post-card-main">
          <div class="post-title">{{ post.title }}</div>
          <div class="post-meta">
            <el-avatar :size="28" :src="post.authorAvatar || ''" />
            <span class="author">发布人:{{ getAuthorName(post) }}</span>
            <span class="time">{{ formatDate(post?.created_at || '') }}</span>
            <span class="reply"
              ><el-icon><ChatLineRound /></el-icon> {{ post.comment_count }}</span
            >
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

    <el-dialog v-model="showCreate" title="发新帖" width="800px">
      <el-form :model="createForm" label-width="60px">
        <el-form-item label="标题">
          <el-input v-model="createForm.title" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="内容">
          <MarkdownEditor
            v-model="createForm.content"
            :rows="8"
            placeholder="请输入帖子内容..."
            :maxlength="2000"
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
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createClubPost } from '@/api/club'
import { useAuthStore } from '@/stores/auth'
import { useClubStore } from '@/stores/club'
import type { ClubPost, Club } from '@/types'
import { Plus, ChatLineRound, ArrowRightBold } from '@element-plus/icons-vue'
import MarkdownEditor from '@/components/MarkdownEditor.vue'

const props = defineProps<{
  clubId: string
  club?: Club | null
}>()
const router = useRouter()
const authStore = useAuthStore()
const clubStore = useClubStore()

// 使用store中的状态和方法
const loading = computed(() => clubStore.postsLoading)
const total = ref(0)
const page = ref(1)
const pageSize = 500

const showCreate = ref(false)
const createForm = ref({ title: '', content: '' })
const createLoading = ref(false)

const showCreateDialog = () => {
  if (authStore.isLoggedIn && props.club?.status == 'joined') {
    showCreate.value = true
  } else if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
  } else {
    ElMessage.warning('请先加入社团')
  }
}

// 使用store中的方法
const fetchPosts = async () => {
  try {
    console.log('正在获取社团帖子，clubId:', props.clubId)
    const res = await clubStore.fetchClubPosts(props.clubId, page.value, pageSize)
    console.log('currentClubPosts:', clubStore.currentClubPosts)
    console.log('获取到的帖子数据:', res)
    total.value = res.total
  } catch (error) {
    console.error('获取帖子失败:', error)
    total.value = 0
  }
}

const goToPost = (row: ClubPost) => {
  // 对content_url进行URL编码，避免路径中的特殊字符导致路由解析错误
  const encodedContentUrl = encodeURIComponent(row?.content_url || '')
  router.push(`/club/post/${props.clubId}/${row.post_id}/${encodedContentUrl}`)
}

const handleCreate = async () => {
  if (!createForm.value.title.trim() || !createForm.value.content.trim()) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  createLoading.value = true
  try {
    await createClubPost({
      club_id: Number(props.clubId),
      title: createForm.value.title,
      content: createForm.value.content,
    })
    ElMessage.success('发帖成功')
    showCreate.value = false
    createForm.value.title = ''
    createForm.value.content = ''
    // 使用store方法刷新帖子列表
    await fetchPosts()
  } catch (error) {
    console.error('发帖失败:', error)
    ElMessage.error('发帖失败，请重试')
  } finally {
    createLoading.value = false
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const getAuthorName = (post: ClubPost) => {
  console.log('getAuthorName - post数据:', post)
  return post.authorName || `用户${post.author_id}` || '匿名'
}

const stripMarkdown = (text: string) => {
  if (!text) return ''

  return (
    text
      // 移除HTML标签
      .replace(/<[^>]+>/g, '')
      // 移除Markdown链接 [text](url) -> text
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      // 移除行内代码 `code` -> code
      .replace(/`([^`]+)`/g, '$1')
      // 移除粗体 **text** -> text
      .replace(/\*\*([^*]+)\*\*/g, '$1')
      // 移除斜体 *text* -> text
      .replace(/\*([^*]+)\*/g, '$1')
      // 移除标题标记 # ## ###
      .replace(/^#{1,6}\s+/gm, '')
      // 移除列表标记 - * 1.
      .replace(/^[-*+]\s+/gm, '')
      .replace(/^\d+\.\s+/gm, '')
      // 移除引用标记 >
      .replace(/^>\s+/gm, '')
      // 移除数学公式
      .replace(/\$[^$\n]+\$/g, '')
      .replace(/\$\$[^$\n]+\$\$/g, '')
      // 移除多余的空行和空格
      .replace(/\n\s*\n/g, '\n')
      .trim()
  )
}

// 添加计算属性来过滤掉置顶帖子
const filteredPosts = computed(() => {
  return clubStore.currentClubPosts.filter((post) => !post.is_pinned)
})

onMounted(async () => {
  await fetchPosts()
})
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
.post-btn:disabled {
  background: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
  box-shadow: none;
}
.post-btn:disabled:hover {
  box-shadow: none;
  opacity: 1;
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
