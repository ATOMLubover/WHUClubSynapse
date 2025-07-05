<template>
  <div class="announcement-manager">
    <div v-if="isClubLeader" class="add-announcement">
      <el-button type="primary" @click="showAddDialog">
        新增公告/动态
      </el-button>
    </div>

    <!-- 显示现有的公告和动态列表 -->
    <div class="announcements-list">
      <el-timeline>
        <el-timeline-item
          v-for="item in announcements"
          :key="item.id"
          :timestamp="item.created_at"
          :type="item.type === 'announcement' ? 'primary' : 'success'"
        >
          <div class="announcement-item">
            <h4>{{ item.type === 'announcement' ? '公告' : '动态' }}</h4>
            <div class="content">{{ JSON.parse(item.content).content }}</div>
            <div v-if="item.content" class="metadata">
              <template v-if="JSON.parse(item.content).type === 'activity'">
                <p v-if="JSON.parse(item.content).metadata.activity_type">活动类型: {{ JSON.parse(item.content).metadata.activity_type }}</p>
                <p v-if="JSON.parse(item.content).metadata.location">地点: {{ JSON.parse(item.content).metadata.location }}</p>
                <p v-if="JSON.parse(item.content).metadata.participants">参与人数: {{ JSON.parse(item.content).metadata.participants }}</p>
              </template>
              <div v-if="JSON.parse(item.content).metadata.tags && JSON.parse(item.content).metadata.tags.length">
                标签:
                <el-tag
                  v-for="tag in JSON.parse(item.content).metadata.tags"
                  :key="tag"
                  size="small"
                  style="margin-right: 5px"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 添加公告/动态的对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="'新增' + (isActivity ? '动态' : '公告')"
      width="50%"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="类型">
          <el-radio-group v-model="isActivity">
            <el-radio :label="false">公告</el-radio>
            <el-radio :label="true">动态</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="详细内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入详细内容"
          />
        </el-form-item>

        <!-- 动态特有字段 -->
        <template v-if="isActivity">
          <el-form-item label="活动类型">
            <el-select v-model="form.metadata.activity_type" placeholder="请选择活动类型">
              <el-option label="会议" value="meeting" />
              <el-option label="培训" value="training" />
              <el-option label="比赛" value="competition" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="活动地点">
            <el-input v-model="form.metadata.location" placeholder="请输入活动地点" />
          </el-form-item>
          <el-form-item label="预计参与人数">
            <el-input-number v-model="form.metadata.participants" :min="0" />
          </el-form-item>
        </template>

        <!-- 标签（公告和动态都可以添加） -->
        <el-form-item :label="isActivity ? '活动标签' : '公告标签'">
          <el-tag
            v-for="tag in form.metadata.tags"
            :key="tag"
            closable
            @close="handleTagClose(tag)"
            style="margin-right: 5px"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="tagInputVisible"
            ref="tagInput"
            v-model="tagInputValue"
            size="small"
            @keyup.enter="handleTagConfirm"
            @blur="handleTagConfirm"
            style="width: 100px"
          />
          <el-button v-else size="small" @click="showTagInput">
            + 新标签
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import type { CommentData } from '@/types'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

interface PinnedPost {
  post_id: number;
  club_id: number;
  author_id: number;
  title: string;
  is_pinned: boolean;
  comment_count: number;
  created_at: string;
}

interface Comment {
  id: number;
  post_id: number;
  author_id: number;
  content: string;
  type: 'activity' | 'announcement';
  created_at: string;
}

const props = defineProps<{
  clubId: number
  leaderId: number
}>()

const authStore = useAuthStore()
const isClubLeader = computed(() => {
  const user = authStore.user
  return user && props.leaderId === user.user_id
})

const announcements = ref<Comment[]>([])
const dialogVisible = ref(false)
const tagInputVisible = ref(false)
const tagInputValue = ref('')
const isActivity = ref(false)

const form = ref({
  content: '',
  metadata: {
    activity_type: '',
    location: '',
    participants: 0,
    tags: [] as string[]
  }
})

// 获取置顶帖子的评论列表（作为公告和动态显示）
const fetchAnnouncements = async () => {
  try {
    // 先获取置顶帖子
    const { data: pinnedPost } = await request.get<PinnedPost>(`/api/club/post/pinned/${props.clubId}`)
    if (pinnedPost && pinnedPost.post_id) {
      // 获取置顶帖子的评论
      const { data: comments } = await request.get<Comment[]>(`/api/club/post/${pinnedPost.post_id}/comments`)
      announcements.value = comments
    }
  } catch (error) {
    console.error('获取公告/动态失败:', error)
    ElMessage.error('获取公告/动态失败')
  }
}

const showAddDialog = () => {
  form.value = {
    content: '',
    metadata: {
      activity_type: '',
      location: '',
      participants: 0,
      tags: []
    }
  }
  isActivity.value = false
  dialogVisible.value = true
}

const handleTagClose = (tag: string) => {
  form.value.metadata.tags = form.value.metadata.tags.filter(t => t !== tag)
}

const showTagInput = () => {
  tagInputVisible.value = true
  nextTick(() => {
    const input = document.querySelector('.el-input__inner') as HTMLInputElement
    if (input) {
      input.focus()
    }
  })
}

const handleTagConfirm = () => {
  if (tagInputValue.value) {
    form.value.metadata.tags.push(tagInputValue.value)
  }
  tagInputVisible.value = false
  tagInputValue.value = ''
}

const handleSubmit = async () => {
  try {
    if (!form.value.content) {
      ElMessage.warning('请输入内容')
      return
    }

    // 获取置顶帖子
    const { data: pinnedPost } = await request.get<PinnedPost>(`/api/club/post/pinned/${props.clubId}`)
    if (!pinnedPost || !pinnedPost.post_id) {
      ElMessage.error('未找到置顶帖子')
      return
    }

    // 构造评论内容
    const commentContent = {
      type: isActivity.value ? 'activity' : 'announcement',
      content: form.value.content,
      metadata: isActivity.value ? {
        activity_type: form.value.metadata.activity_type,
        location: form.value.metadata.location,
        participants: form.value.metadata.participants,
        tags: form.value.metadata.tags
      } : {
        tags: form.value.metadata.tags
      }
    }

    // 打印请求数据
    const requestData = {
      post_id: pinnedPost.post_id,
      author_id: 1,
      user_id: 1,
      content: JSON.stringify(commentContent),
      type: isActivity.value ? 'activity' : 'announcement'
    }
    console.log('发送的请求数据:', JSON.stringify(requestData, null, 2))

    // 创建评论（作为公告/动态）
    const response = await request.post('/api/club/post/comment', requestData)
    console.log('服务器响应数据:', response)

    ElMessage.success('添加成功')
    dialogVisible.value = false
    fetchAnnouncements() // 刷新列表
  } catch (error: any) {
    console.error('添加公告/动态失败:', error)
    if (error.response) {
      console.error('服务器响应:', error.response.data)
      console.error('服务器响应状态:', error.response.status)
      console.error('服务器响应头:', error.response.headers)
    }
    ElMessage.error(`添加失败: ${error.response?.data || error.message}`)
  }
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.announcement-manager {
  padding: 20px;
}

.add-announcement {
  margin-bottom: 20px;
}

.announcement-item {
  padding: 10px;
  border-radius: 4px;
  background-color: #f5f7fa;
}

.content {
  margin: 10px 0;
  font-size: 1.1em;
}

.metadata {
  margin-top: 10px;
  font-size: 0.9em;
  color: #666;
}

.dialog-footer {
  margin-top: 20px;
}
</style> 