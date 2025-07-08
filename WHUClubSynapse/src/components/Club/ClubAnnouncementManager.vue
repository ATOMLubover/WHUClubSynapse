<template>
  <div class="announcement-manager">
    <div v-if="isClubLeader" class="add-announcement">
      <el-button type="primary" @click="showAddDialog"> 新增公告/动态 </el-button>
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
                <p v-if="JSON.parse(item.content).metadata.activity_type">
                  活动类型: {{ JSON.parse(item.content).metadata.activity_type }}
                </p>
                <p v-if="JSON.parse(item.content).metadata.location">
                  地点: {{ JSON.parse(item.content).metadata.location }}
                </p>
                <p v-if="JSON.parse(item.content).metadata.participants">
                  参与人数: {{ JSON.parse(item.content).metadata.participants }}
                </p>
              </template>
              <div
                v-if="
                  JSON.parse(item.content).metadata.tags &&
                  JSON.parse(item.content).metadata.tags.length
                "
              >
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
    <el-dialog v-model="dialogVisible" :title="'新增' + (isActivity ? '动态' : '公告')" width="50%">
      <el-form :model="form" label-width="120px">
        <el-form-item label="类型">
          <el-radio-group v-model="isActivity">
            <el-radio :label="false">公告</el-radio>
            <el-radio :label="true">动态</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- AI公告生成器 -->
        <div class="ai-announcement-section">
          <div class="ai-header">
            <el-icon><Bell /></el-icon>
            <span>AI {{ isActivity ? '动态' : '公告' }}生成器</span>
            <el-tag type="success" size="small" class="status-tag">在线</el-tag>
            <el-button type="primary" text class="check-status" @click="checkAIStatus">
              <el-icon><RefreshRight /></el-icon>
              检查状态
            </el-button>
            <el-button type="primary" text class="clear-results" @click="clearResults">
              清空结果
            </el-button>
          </div>

          <el-form-item :label="isActivity ? '动态草稿' : '公告草稿'">
            <el-input
              v-model="aiDraft"
              type="textarea"
              :rows="4"
              :placeholder="
                isActivity ? '请输入动态的草稿内容（可选）' : '请输入公告的草稿内容（可选）'
              "
            />
          </el-form-item>

          <el-form-item label="文体风格">
            <el-select v-model="aiStyle" placeholder="请选择文体风格">
              <el-option label="正式严谨" value="formal" />
              <el-option label="活泼生动" value="lively" />
              <el-option label="简洁明了" value="concise" />
              <el-option label="温和友好" value="friendly" />
            </el-select>
          </el-form-item>

          <el-form-item label="预期效果">
            <el-input
              v-model="aiExpectation"
              :placeholder="
                isActivity
                  ? '例如：展示活动亮点、吸引更多参与者、营造良好氛围等'
                  : '例如：吸引更多人参与活动、激发读者热情、提高关注度等'
              "
            />
            <div class="char-count">{{ aiExpectation.length }} / 100</div>
          </el-form-item>

          <div class="generate-button">
            <el-button type="primary" :loading="generating" @click="generateAnnouncement">
              生成AI{{ isActivity ? '动态' : '公告' }}内容
            </el-button>
          </div>

          <div v-if="aiResult" class="ai-result">
            <div class="result-header">
              <span>生成结果</span>
              <el-button type="primary" text size="small" @click="useAIResult">
                使用此结果
              </el-button>
          </div>
            <div class="result-content">{{ aiResult }}</div>
          </div>
        </div>
        
        <el-divider>手动编辑区域</el-divider>

        <el-form-item label="详细内容" required>
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            :placeholder="isActivity ? '请输入动态详细内容' : '请输入公告详细内容'"
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
          <el-button v-else size="small" @click="showTagInput"> + 新标签 </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit"> 确定 </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Bell, RefreshRight, Location, User, Plus } from '@element-plus/icons-vue'
import type { CommentData } from '@/types'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

interface PinnedPost {
  post_id: number
  club_id: number
  author_id: number
  title: string
  is_pinned: boolean
  comment_count: number
  created_at: string
}

interface Announcement {
  id: number
  title: string
  content: string
  type: 'announcement' | 'activity'
  created_at: string
  metadata: {
    activity_type?: string
    location?: string
    participants?: number
    tags: string[]
  }
}

const props = defineProps<{
  clubId: number
  leaderId: number
}>()

const authStore = useAuthStore()
const isClubLeader = computed(() => {
  const user = authStore.user
  // 检查用户是否登录
  if (!user) {
    console.log('用户未登录')
    return false
  }
  
  // 检查用户是否为超级管理员
  if (user.role === 'admin') {
    console.log('用户是超级管理员')
    return true
  }
  
  // 检查用户是否为该社团的管理员
  console.log('当前用户ID:', user.user_id)
  console.log('社团负责人ID:', props.leaderId)
  return props.leaderId === user.user_id
})

const announcements = ref<Announcement[]>([])
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
    tags: [] as string[],
  },
})

// AI公告生成相关的状态
const aiDraft = ref('')
const aiStyle = ref('formal')
const aiExpectation = ref('')
const aiResult = ref('')
const generating = ref(false)

// 获取公告列表
const fetchAnnouncements = async () => {
  try {
    const response = await request.get(`/api/club/post/posts/${props.clubId}`)
    if (response.data == null) {
      return
    }
    if (response.data) {
      announcements.value = response.data.map((item: any) => {
        try {
          // 检查content是否存在且不为空
          if (!item.content) {
            console.warn('公告内容为空:', item)
            return {
              id: item.id,
              title: '无标题',
              content: '',
              type: 'announcement',
              created_at: item.created_at,
              metadata: { tags: [] },
            }
          }
          
          const content = JSON.parse(item.content)
          return {
            id: item.id,
            title: content.title || '无标题',
            content: content.content || '',
            type: content.type || 'announcement',
            created_at: item.created_at,
            metadata: content.metadata || { tags: [] },
          }
        } catch (parseError) {
          console.error('解析公告内容失败:', parseError, item)
          return {
            id: item.id,
            title: '解析错误',
            content: '该公告内容格式有误',
            type: 'announcement',
            created_at: item.created_at,
            metadata: { tags: [] },
          }
        }
      })
    }
  } catch (error) {
    console.error('获取公告列表失败:', error)
    // ElMessage.error('获取公告列表失败')
  }
}

const showAddDialog = () => {
  form.value = {
    content: '',
    metadata: {
      activity_type: '',
      location: '',
      participants: 0,
      tags: [],
    },
  }
  isActivity.value = false
  dialogVisible.value = true
}

const handleTagClose = (tag: string) => {
  form.value.metadata.tags = form.value.metadata.tags.filter((t) => t !== tag)
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
    const { data: pinnedPost } = await request.get<PinnedPost>(
      `/api/club/post/pinned/${props.clubId}`,
    )
    if (!pinnedPost || !pinnedPost.post_id) {
      ElMessage.error('未找到置顶帖子')
    return
  }

    // 构造评论内容
    const commentContent = {
      type: isActivity.value ? 'activity' : 'announcement',
      content: form.value.content,
      metadata: isActivity.value
        ? {
            activity_type: form.value.metadata.activity_type,
            location: form.value.metadata.location,
            participants: form.value.metadata.participants,
            tags: form.value.metadata.tags,
          }
        : {
            tags: form.value.metadata.tags,
          },
    }

    // 打印请求数据
    const requestData = {
      post_id: pinnedPost.post_id,
      author_id: authStore.user?.user_id,
      user_id: authStore.user?.user_id,
      content: JSON.stringify(commentContent),
      type: isActivity.value ? 'activity' : 'announcement',
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

// 检查AI服务状态
const checkAIStatus = async () => {
  try {
    const { data } = await request.get('/api/ai/health')
    if (data.status === 'ok') {
      ElMessage.success('AI服务正常运行中')
    } else {
      ElMessage.warning('AI服务暂时不可用')
    }
  } catch (error) {
    ElMessage.error('AI服务检查失败')
  }
}

// 生成AI内容
const generateAnnouncement = async () => {
  if (!aiExpectation.value) {
    ElMessage.warning('请输入预期效果')
    return
  }

  generating.value = true
  try {
    const { data } = await request.post('/api/ai/generate/announcement', {
      draft: aiDraft.value,
      style: aiStyle.value,
      expectation: aiExpectation.value,
      type: isActivity.value ? 'activity' : 'announcement', // 添加类型参数
    })
    aiResult.value = data.content
  } catch (error) {
    ElMessage.error('生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

// 使用AI生成的结果
const useAIResult = () => {
  if (aiResult.value) {
    form.value.content = aiResult.value
  }
}

// 清空AI生成结果
const clearResults = () => {
  aiResult.value = ''
}

// 添加错误处理
const handleUnauthorizedAction = () => {
  if (!authStore.user) {
    ElMessage.warning('请先登录')
    // 可以在这里添加跳转到登录页面的逻辑
    return
  }
  ElMessage.error('您没有权限执行此操作')
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

.ai-announcement-section {
  margin: 20px 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.ai-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.status-tag {
  margin-left: auto;
}

.char-count {
  text-align: right;
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.generate-button {
  text-align: center;
  margin: 20px 0;
}

.ai-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-content {
  white-space: pre-wrap;
  line-height: 1.5;
}
</style> 
