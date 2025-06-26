<template>
  <div class="my-favorites">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>管理的社团</h1>
      <p>您作为管理员管理的社团，可以进行编辑和管理操作</p>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-card>
        <el-row :gutter="20" align="middle">
          <el-col :span="6">
            <el-select
              v-model="filterStatus"
              placeholder="社团状态"
              clearable
              @change="handleFilter"
            >
              <el-option label="全部状态" value="" />
              <el-option label="活跃" value="active" />
              <el-option label="暂停" value="inactive" />
              <el-option label="待审核" value="pending" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
              <el-option label="创建时间（最新）" value="createdAt_desc" />
              <el-option label="创建时间（最早）" value="createdAt_asc" />
              <el-option label="社团名称（A-Z）" value="name_asc" />
              <el-option label="成员数量（多-少）" value="members_desc" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索管理的社团"
              clearable
              @keyup.enter="handleFilter"
            >
              <template #append>
                <el-button icon="Search" @click="handleFilter" />
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="loadManagedClubs" :loading="loading">
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
            <span>管理的社团 ({{ total }})</span>
            <div class="header-actions">
              <el-button @click="showCreateDialog = true" type="primary">
                <el-icon><Plus /></el-icon>
                创建新社团
              </el-button>
            </div>
          </div>
        </template>

        <div v-loading="loading">
          <!-- 空状态 -->
          <div v-if="!managedClubs.length && !loading" class="empty-state">
            <el-empty description="您还没有管理的社团">
              <el-button type="primary" @click="showCreateDialog = true"> 创建社团 </el-button>
            </el-empty>
          </div>

          <!-- 卡片视图 -->
          <div v-else class="card-view">
            <el-row :gutter="20">
              <el-col
                v-for="club in managedClubs"
                :key="club.id"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                :xl="4"
                class="club-card-col"
              >
                <div class="club-card">
                  <!-- 社团封面 -->
                  <div class="club-cover" @click="goToClubDetail(club.id)">
                    <img :src="club.coverImage" :alt="club.name" />
                    <div class="cover-overlay">
                      <el-button type="primary" size="small">查看详情</el-button>
                    </div>
                  </div>

                  <!-- 社团信息 -->
                  <div class="club-info">
                    <h3 class="club-name" @click="goToClubDetail(club.id)">{{ club.name }}</h3>
                    <p class="club-category">{{ club.category }}</p>
                    <p class="club-members">{{ club.currentMembers }}/{{ club.maxMembers }} 人</p>
                    <p class="favorite-time">创建于 {{ formatDate(club.createdAt) }}</p>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="club-actions">
                    <el-button size="small" @click="editClub(club)">编辑信息</el-button>
                    <el-button size="small" @click="manageMembers(club)">成员管理</el-button>
                    <el-button size="small" type="danger" @click="handledelete(club)">
                      删除社团
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

    <!-- 创建社团对话框和删除社团对话框保留原有结构 -->
    <el-dialog v-model="showCreateDialog" title="创建新社团" width="600px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="社团名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入社团名称" />
        </el-form-item>
        <el-form-item label="社团简介" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入社团简介"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="社团类型" prop="category">
          <el-select v-model="createForm.category" placeholder="请选择社团类型">
            <el-option label="学术科技" value="学术科技" />
            <el-option label="文艺体育" value="文艺体育" />
            <el-option label="志愿服务" value="志愿服务" />
            <el-option label="创新创业" value="创新创业" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大成员数" prop="maxMembers">
          <el-input-number v-model="createForm.maxMembers" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="社团标签">
          <el-select
            v-model="createForm.tags"
            multiple
            filterable
            allow-create
            placeholder="请选择或输入标签"
          >
            <el-option label="编程" value="编程" />
            <el-option label="算法" value="算法" />
            <el-option label="竞赛" value="竞赛" />
            <el-option label="篮球" value="篮球" />
            <el-option label="音乐" value="音乐" />
            <el-option label="舞蹈" value="舞蹈" />
            <el-option label="志愿服务" value="志愿服务" />
            <el-option label="创业" value="创业" />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图片">
          <el-upload
            class="cover-uploader"
            action="#"
            :show-file-list="false"
            :before-upload="beforeCoverUpload"
          >
            <img v-if="createForm.coverImage" :src="createForm.coverImage" class="cover-preview" />
            <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCreate" :loading="createLoading">
          创建社团
        </el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="showDeleteDialog" title="删除社团" width="400px">
      <div class="delete-dialog-content">
        <el-icon class="warning-icon" color="#F56C6C"><Warning /></el-icon>
        <p>
          确定要删除社团 <strong>{{ deleteClub?.name }}</strong> 吗？
        </p>
        <p class="warning-text">删除后将无法恢复，所有成员将被移除</p>
      </div>

      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">
          确认删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Plus,
  User,
  UserFilled,
  Calendar,
  ArrowDown,
  Warning,
  CircleCheck,
  Clock,
  Document,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import type { Club, ClubCategory } from '@/types'

const router = useRouter()
const clubStore = useClubStore()
const authStore = useAuthStore()
const route = useRoute()

// 响应式数据
const loading = ref(false)
const createLoading = ref(false)
const deleteLoading = ref(false)
const managedClubs = ref<Club[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchKeyword = ref('')
const filterStatus = ref('')
const sortBy = ref('createdAt_desc')
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const deleteClub = ref<Club | null>(null)

// 创建表单
const createForm = ref({
  name: '',
  description: '',
  category: '',
  maxMembers: 50,
  tags: [] as string[],
  coverImage: '',
})

const createRules = {
  name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入社团简介', trigger: 'blur' }],
  category: [{ required: true, message: '请选择社团类型', trigger: 'change' }],
  maxMembers: [{ required: true, message: '请输入最大成员数', trigger: 'blur' }],
}

// 统计数据
const stats = computed(() => {
  const active = managedClubs.value.filter((club) => club.status === 'approved').length
  const pending = managedClubs.value.filter((club) => club.status === 'pending').length
  const totalMembers = managedClubs.value.reduce((sum, club) => sum + club.currentMembers, 0)
  const pendingApplications = managedClubs.value.length * 3 // 模拟数据

  return {
    active,
    pending,
    totalMembers,
    pendingApplications,
  }
})

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

// 加载管理的社团
const loadManagedClubs = async () => {
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  try {
    loading.value = true
    const data = await clubStore.fetchManagedClubs({
      page: currentPage.value,
      pageSize: pageSize.value,
    })
    managedClubs.value = data.list
    total.value = data.total
  } catch (error) {
    console.error('加载管理的社团失败:', error)
  } finally {
    loading.value = false
  }
}

// 筛选处理
const handleFilter = () => {
  currentPage.value = 1
  loadManagedClubs()
}

// 排序处理
const handleSort = () => {
  currentPage.value = 1
  loadManagedClubs()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadManagedClubs()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadManagedClubs()
}

// 跳转到社团详情
const goToClubDetail = (clubId: string) => {
  router.push(`/club/${clubId}`)
}

// 编辑社团
const editClub = (club: Club) => {
  // TODO: 跳转到编辑页面
  ElMessage.info('编辑功能开发中...')
}

// 成员管理
const manageMembers = (club: Club) => {
  // TODO: 跳转到成员管理页面
  ElMessage.info('成员管理功能开发中...')
}

// 处理删除社团
const handledelete = (club: Club) => {
  showDeleteDialog.value = true
  deleteClub.value = club
}

// 处理更多操作
const handleAction = (command: { action: string; club: Club }) => {
  switch (command.action) {
    case 'view-applications':
      ElMessage.info('查看申请功能开发中...')
      break
    case 'manage-activities':
      ElMessage.info('活动管理功能开发中...')
      break
    case 'club-settings':
      ElMessage.info('社团设置功能开发中...')
      break
    case 'delete-club':
      showDeleteDialog.value = true
      deleteClub.value = command.club
      break
  }
}

// 封面图片上传前处理
const beforeCoverUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  // 模拟上传，实际项目中应该上传到服务器
  const reader = new FileReader()
  reader.onload = (e) => {
    createForm.value.coverImage = e.target?.result as string
  }
  reader.readAsDataURL(file)

  return false // 阻止自动上传
}

// 确认创建社团
const confirmCreate = async () => {
  try {
    createLoading.value = true
    await clubStore.createClub(createForm.value)
    ElMessage.success('社团创建成功，等待审核')
    showCreateDialog.value = false
    // 重置表单
    createForm.value = {
      name: '',
      description: '',
      category: '',
      maxMembers: 50,
      tags: [],
      coverImage: '',
    }
    // 重新加载列表
    await loadManagedClubs()
  } catch (error) {
    console.error('创建社团失败:', error)
  } finally {
    createLoading.value = false
  }
}

// 确认删除社团
const confirmDelete = async () => {
  if (!deleteClub.value) return

  try {
    deleteLoading.value = true
    await clubStore.deleteClub(deleteClub.value.id)
    ElMessage.success('社团删除成功')
    showDeleteDialog.value = false
    deleteClub.value = null
    // 重新加载列表
    await loadManagedClubs()
  } catch (error) {
    console.error('删除社团失败:', error)
    ElMessage.error('删除社团失败，请重试')
  } finally {
    deleteLoading.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadManagedClubs()
  const isOpen = route.query.isOpen
  if (isOpen == 'true') {
    showCreateDialog.value = true
  }
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
  flex-direction: column;
  gap: 8px;
}

.club-actions .el-button {
  width: 100%;
  min-height: 38px;
  font-size: 15px;
  box-sizing: border-box;
  border-radius: 6px;
  margin: 0;
  text-align: center;
  justify-content: center;
  align-items: center;
  display: flex;
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
  
  .club-actions {
    padding: 0 12px 12px;
  }
  
  .club-info {
    padding: 12px;
  }
  
  .club-name {
    font-size: 14px;
  }
  
  .club-category,
  .club-members,
  .favorite-time {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .my-favorites {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .page-header p {
    font-size: 14px;
  }
  
  .club-actions .el-button {
    font-size: 12px;
    padding: 6px 12px;
  }
}
</style>
