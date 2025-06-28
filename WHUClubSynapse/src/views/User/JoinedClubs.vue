<template>
  <div class="my-favorites">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>已加入社团</h1>
      <p>您当前加入的社团，可以查看详情和参与活动</p>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-card>
        <el-row :gutter="20" align="middle">
          <el-col :span="6">
            <el-select
              v-model="filterCategory"
              placeholder="筛选类型"
              clearable
              @change="handleFilter"
            >
              <el-option label="全部类型" value="" />
              <el-option label="学术科技" value="学术科技" />
              <el-option label="文艺体育" value="文艺体育" />
              <el-option label="志愿服务" value="志愿服务" />
              <el-option label="创新创业" value="创新创业" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
              <el-option label="加入时间（最新）" value="joinedAt_desc" />
              <el-option label="加入时间（最早）" value="joinedAt_asc" />
              <el-option label="社团名称（A-Z）" value="name_asc" />
              <el-option label="成员数量（多-少）" value="members_desc" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索已加入的社团"
              clearable
              @keyup.enter="handleFilter"
            >
              <template #append>
                <el-button icon="Search" @click="handleFilter" />
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="loadJoinedClubs" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 社团列表 -->
    <div class="favorites-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>已加入社团 ({{ total }})</span>
            <div class="header-actions">
              <el-button @click="loadJoinedClubs" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </template>

        <div v-loading="loading">
          <!-- 空状态 -->
          <div v-if="!joinedClubs.length && !loading" class="empty-state">
            <el-empty description="您还没有加入任何社团">
              <el-button type="primary" @click="$router.push('/')"> 去申请社团 </el-button>
            </el-empty>
          </div>

          <!-- 卡片视图 -->
          <div v-else class="card-view">
            <el-row :gutter="20">
              <el-col
                v-for="club in joinedClubs"
                :key="club.club_id"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                class="club-card-col"
              >
                <div class="club-card">
                  <!-- 社团封面 -->
                  <div class="club-cover" @click="goToClubDetail(club.club_id)">
                    <img :src="club.logo_url" :alt="club.club_name" />
                    <div class="cover-overlay">
                      <el-button type="primary" size="small">查看详情</el-button>
                    </div>
                  </div>

                  <!-- 社团信息 -->
                  <div class="club-info">
                    <h3 class="club-name" @click="goToClubDetail(club.club_id)">
                      {{ club.club_name }}
                    </h3>
                    <p class="club-category">{{ club.category }}</p>
                    <p class="club-members">{{ club.member_count }}/{{ club.maxMembers }} 人</p>
                    <p class="favorite-time">加入于 {{ formatDate(club.created_at) }}</p>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="club-actions">
                    <el-button size="small" @click="goToClubDetail(club.club_id)"> 查看 </el-button>
                    <el-button
                      size="small"
                      type="danger"
                      @click="
                        showQuitDialog = true
                        quitClub = club
                      "
                    >
                      退出社团
                    </el-button>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 退出社团确认对话框 -->
    <el-dialog v-model="showQuitDialog" title="退出社团" width="400px">
      <div class="quit-dialog-content">
        <el-icon class="warning-icon" color="#E6A23C"><Warning /></el-icon>
        <p>
          确定要退出社团 <strong>{{ quitClub?.club_name }}</strong> 吗？
        </p>
        <p class="warning-text">退出后将无法访问社团内部信息和活动</p>
      </div>
      <template #footer>
        <el-button @click="showQuitDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmQuit" :loading="quitLoading"> 确认退出 </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Plus,
  User,
  UserFilled,
  Calendar,
  Bell,
  ArrowDown,
  Warning,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import type { Club, ClubCategory } from '@/types'

const router = useRouter()
const clubStore = useClubStore()
const authStore = useAuthStore()

// 响应式数据
const loading = ref(false)
const quitLoading = ref(false)
const joinedClubs = ref<Club[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchKeyword = ref('')
const filterCategory = ref('')
const sortBy = ref('joinedAt_desc')
const showQuitDialog = ref(false)
const quitClub = ref<Club | null>(null)

// 获取分类标签类型
const getCategoryType = (category: ClubCategory) => {
  const typeMap: Record<ClubCategory, string> = {
    学术科技: 'primary',
    文艺体育: 'success',
    志愿服务: 'warning',
    创新创业: 'danger',
    其他: 'info',
  }
  return typeMap[category] || 'info'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    pending: 'warning',
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    active: '活跃',
    inactive: '暂停',
    pending: '待审核',
  }
  return textMap[status] || '未知'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 加载已加入社团
const loadJoinedClubs = async () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    loading.value = true
    const data = await clubStore.fetchJoinedClubs({
      page: currentPage.value,
      pageSize: pageSize.value,
    })
    joinedClubs.value = data.list
    total.value = data.total
  } catch (error) {
    console.error('加载已加入社团失败:', error)
  } finally {
    loading.value = false
  }
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  loadJoinedClubs()
}

// 排序处理
const handleSort = () => {
  currentPage.value = 1
  loadJoinedClubs()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadJoinedClubs()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadJoinedClubs()
}

// 跳转到社团详情
const goToClubDetail = (clubId: string) => {
  router.push(`/club/${clubId}`)
}

// 查看活动
const viewActivities = (club: Club) => {
  // TODO: 跳转到活动页面
  ElMessage.info('活动功能开发中...')
}

// 处理更多操作
const handleAction = (command: { action: string; club: Club }) => {
  switch (command.action) {
    case 'view-activities':
      viewActivities(command.club)
      break
    case 'quit-club':
      showQuitDialog.value = true
      quitClub.value = command.club
      break
  }
}

// 确认退出社团
const confirmQuit = async () => {
  if (!quitClub.value) return

  try {
    quitLoading.value = true
    await clubStore.quitClub(quitClub.value.club_id)
    ElMessage.success('退出社团成功')
    showQuitDialog.value = false
    quitClub.value = null
    // 重新加载列表
    await loadJoinedClubs()
  } catch (error) {
    console.error('退出社团失败:', error)
    ElMessage.error('退出社团失败，请重试')
  } finally {
    quitLoading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadJoinedClubs()
})
</script>

<style scoped>
.my-favorites {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.toolbar,
.favorites-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-view {
  min-height: 400px;
}

.club-card-col {
  margin-bottom: 20px;
}

.club-card {
  position: relative;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  background: #fff;
}

.club-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.club-cover:hover .cover-overlay {
  opacity: 1;
}

.club-cover {
  position: relative;
  height: 150px;
  overflow: hidden;
  cursor: pointer;
}

.club-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.club-cover:hover img {
  transform: scale(1.05);
}

.club-info {
  padding: 16px;
}

.club-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
  transition: color 0.2s;
}

.club-name:hover {
  color: #409eff;
}

.club-category,
.club-members,
.favorite-time {
  margin: 4px 0;
  color: #606266;
  font-size: 13px;
}

.club-actions {
  padding: 0 16px 16px;
  display: flex;
  gap: 8px;
}

.pagination-section {
  margin-top: 20px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

@media (max-width: 768px) {
  .card-view .el-col {
    width: 100%;
  }
}
</style>
