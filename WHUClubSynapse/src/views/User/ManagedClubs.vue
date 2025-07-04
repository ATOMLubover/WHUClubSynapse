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

    <!-- 申请管理区域 -->
    <div class="applications-management-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <el-tabs v-model="activeTab" type="card">
              <el-tab-pane label="创建申请" name="create">
                <template #label>
                  <span class="tab-label">
                    创建申请
                    <el-badge
                      v-if="userCreatedApplications.length > 0"
                      :value="userCreatedApplications.length"
                      class="tab-badge"
                    />
                  </span>
                </template>
              </el-tab-pane>
              <el-tab-pane label="更新申请" name="update">
                <template #label>
                  <span class="tab-label">
                    更新申请
                    <el-badge
                      v-if="userUpdateApplications.length > 0"
                      :value="userUpdateApplications.length"
                      class="tab-badge"
                    />
                  </span>
                </template>
              </el-tab-pane>
            </el-tabs>
            <el-button @click="refreshCurrentTab" :loading="applicationsLoading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <div v-loading="applicationsLoading">
          <!-- 创建申请内容 -->
          <div v-if="activeTab === 'create'">
            <!-- 空状态 -->
            <div v-if="!userCreatedApplications.length && !applicationsLoading" class="empty-state">
              <el-empty description="您还没有提交创建社团申请">
                <el-button type="primary" @click="showCreateDialog = true">
                  申请创建社团
                </el-button>
              </el-empty>
            </div>

            <!-- 创建申请列表 -->
            <div v-else class="applications-list">
              <el-table
                :data="userCreatedApplications"
                style="width: 100%"
                class="applications-table"
              >
                <el-table-column prop="appli_id" label="申请ID" width="100" />
                <el-table-column label="状态" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getApplicationStatusType(row.status)" size="small" effect="dark">
                      {{ getApplicationStatusText(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="社团信息" min-width="300">
                  <template #default="{ row }">
                    <div v-if="row.proposal && parseProposal(row.proposal)" class="club-info-cell">
                      <div class="club-name-row">
                        <strong>{{ parseProposal(row.proposal).name || '未命名社团' }}</strong>
                      </div>
                      <div class="club-desc-row">
                        {{ parseProposal(row.proposal).description || '暂无简介' }}
                      </div>
                      <div class="club-meta-row">
                        <el-tag
                          v-if="parseProposal(row.proposal).category_id"
                          size="small"
                          type="primary"
                        >
                          {{ getCategoryName(parseProposal(row.proposal).category_id) }}
                        </el-tag>
                        <div v-if="parseProposal(row.proposal).tags?.length" class="tags-display">
                          <el-tag
                            v-for="tag in parseProposal(row.proposal).tags.slice(0, 3)"
                            :key="tag"
                            size="small"
                            effect="plain"
                            class="tag-item"
                          >
                            {{ tag }}
                          </el-tag>
                          <span
                            v-if="parseProposal(row.proposal).tags.length > 3"
                            class="more-tags"
                          >
                            +{{ parseProposal(row.proposal).tags.length - 3 }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div v-else class="proposal-error">
                      <el-icon><Warning /></el-icon>
                      <span>方案数据异常</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="申请时间" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.applied_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="审核时间" width="150">
                  <template #default="{ row }">
                    {{ row.reviewed_at ? formatDate(row.reviewed_at) : '-' }}
                  </template>
                </el-table-column>
                <el-table-column label="拒绝原因" min-width="200">
                  <template #default="{ row }">
                    <div v-if="row.reject_reason" class="reject-reason">
                      <el-icon><CircleClose /></el-icon>
                      <span>{{ row.reject_reason }}</span>
                    </div>
                    <span v-else>-</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- 更新申请内容 -->
          <div v-if="activeTab === 'update'">
            <!-- 空状态 -->
            <div v-if="!userUpdateApplications.length && !applicationsLoading" class="empty-state">
              <el-empty description="您还没有提交社团信息更新申请"> </el-empty>
            </div>

            <!-- 更新申请列表 -->
            <div v-else class="applications-list">
              <el-table
                :data="userUpdateApplications"
                style="width: 100%"
                class="applications-table"
              >
                <el-table-column prop="club_id" label="社团ID" width="100" />
                <el-table-column label="状态" width="120">
                  <template #default>
                    <el-tag type="warning" size="small" effect="dark"> 更新申请 </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="社团信息" width="150">
                  <template #default="{ row }">
                    <div class="club-info-cell">
                      <div class="club-name-row">
                        <strong>{{ row.name }}</strong>
                        <el-tag size="small" type="primary">
                          {{ getCategoryName(row.category_id) }}
                        </el-tag>
                        <div v-if="row.type?.length" class="tags-display">
                          <el-tag
                            v-for="tag in row.type.slice(0, 3)"
                            :key="tag"
                            size="small"
                            effect="plain"
                            class="tag-item"
                          >
                            {{ tag }}
                          </el-tag>
                          <span v-if="row.type.length > 3" class="more-tags">
                            +{{ row.type.length - 3 }}
                          </span>
                        </div>
                      </div>

                      <div class="club-meta-row">
                        <span class="leader-info">社长ID: {{ row.leader_id }}</span>
                      </div>
                      <div v-if="row.requirements" class="requirements-display">
                        <el-icon><Document /></el-icon>
                        <span>{{ row.requirements }}</span>
                      </div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="社团简介" min-width="300">
                  <template #default="{ row }">
                    <div class="club-desc-row">
                      {{ row.description }}
                    </div></template
                  >
                </el-table-column>

                <el-table-column label="操作" width="250" fixed="right">
                  <template #default="{ row }">
                    <el-button type="primary" size="small" disabled>
                      <el-icon><Loading /></el-icon>
                      等待审核
                    </el-button>
                    <el-button type="info" size="small" @click="viewClubDetail(row.club_id)">
                      <el-icon><View /></el-icon>
                      查看社团
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
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
            <el-row :gutter="24">
              <el-col
                v-for="club in managedClubs"
                :key="club.club_id"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                :xl="4"
                class="club-card-col"
              >
                <div class="club-card">
                  <!-- 社团封面 -->
                  <div class="club-cover" @click="goToClubDetail(club.club_id)">
                    <img :src="club.logo_url" :alt="club.club_name" />
                    <div class="cover-overlay">
                      <div class="overlay-content">
                        <el-icon class="view-icon"><View /></el-icon>
                        <span>查看详情</span>
                      </div>
                    </div>
                    <div class="club-badge">
                      <el-tag size="small" type="success" effect="dark">管理中</el-tag>
                    </div>
                  </div>

                  <!-- 社团信息 -->
                  <div class="club-info">
                    <h3 class="club-name" @click="goToClubDetail(club.club_id)">
                      {{ club.club_name }}
                    </h3>

                    <div class="club-meta">
                      <div class="meta-item">
                        <el-icon class="meta-icon"><Collection /></el-icon>
                        <span class="club-category">{{ getCategoryName(club.category) }}</span>
                      </div>

                      <div class="meta-item">
                        <el-icon class="meta-icon"><User /></el-icon>
                        <span class="club-members"
                          >{{ club.member_count }}/{{ clubStore.MAX_MEMBER_NUM }} 人</span
                        >
                      </div>

                      <div class="meta-item">
                        <el-icon class="meta-icon"><Calendar /></el-icon>
                        <span class="favorite-time">{{ formatDate(club.created_at) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="club-actions">
                    <el-button
                      size="small"
                      @click="editClub(club)"
                      class="action-btn primary-action"
                    >
                      <el-icon><Edit /></el-icon>
                      编辑信息
                    </el-button>
                    <el-button size="small" @click="manageMembers(club)" class="action-btn">
                      <el-icon><User /></el-icon>
                      成员管理
                    </el-button>
                    <el-button size="small" @click="manageFinance(club)" class="action-btn">
                      <el-icon><Money /></el-icon>
                      经费管理
                    </el-button>
                    <el-button
                      size="small"
                      type="danger"
                      @click="handledelete(club)"
                      class="action-btn danger-action"
                      plain
                    >
                      <el-icon><Delete /></el-icon>
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
          <el-select v-model="createForm.category_id" placeholder="请选择社团类型">
            <el-option
              v-for="category in categoriesList"
              :key="category.category_id"
              :label="category.name"
              :value="category.category_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="最大成员数" prop="maxMembers">
          <el-input-number v-model="createForm.maxMembers" :min="1" :max="1000" />
        </el-form-item>
        <el-form-item label="社团标签" prop="tags">
          <el-select
            v-model="createForm.tags"
            multiple
            filterable
            :rules="[{ required: true, message: '请选择社团标签', trigger: 'change' }]"
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
          确定要删除社团 <strong>{{ deleteClub?.club_name }}</strong> 吗？
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
  CircleClose,
  Clock,
  Document,
  Star,
  Collection,
  PriceTag,
  View,
  Loading,
  Edit,
  Money,
  Delete,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import type { Club, ClubCategory, ClubCreatedApplication, ClubUpdateApplication } from '@/types'
import { getClubUpdateApplications } from '@/api/club'

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
const categoriesList = ref<ClubCategory[]>([])

// 用户创建申请相关数据
const userCreatedApplications = ref<ClubCreatedApplication[]>([])
const applicationsLoading = ref(false)
const userUpdateApplications = ref<ClubUpdateApplication[]>([])
const activeTab = ref('create')
// 创建表单
const createForm = ref({
  name: '',
  description: '',
  category_id: 0,
  maxMembers: 50,
  tags: [] as string[],
  requirements: '',
  coverImage: '',
})

const createRules = {
  name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入社团简介', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择社团类型', trigger: 'change' }],
  maxMembers: [{ required: true, message: '请输入最大成员数', trigger: 'blur' }],
  tags: [{ required: true, message: '请选择社团标签', trigger: 'change' }],
}

// 获取分类标签列表
const getCategoriesList = async () => {
  await clubStore.fetchCategoriesList()
  categoriesList.value = clubStore.categoriesList
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
  if (!dateStr || dateStr === '0001-01-01T00:00:00Z') {
    return '未设置'
  }

  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN')
  } catch {
    return '日期格式错误'
  }
}

// 获取申请状态类型
const getApplicationStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
}

// 获取申请状态文本
const getApplicationStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return textMap[status] || '未知状态'
}

// 解析申请方案
const parseProposal = (proposal: string | object) => {
  try {
    if (typeof proposal === 'string') {
      return JSON.parse(proposal)
    }
    return proposal
  } catch (error) {
    console.error('解析申请方案失败:', error)
    return null
  }
}

// 获取社团类型名称
const getCategoryName = (categoryId: number) => {
  const category = categoriesList.value.find((cat) => cat.category_id === categoryId)
  return category?.name || '未知类型'
}

// TODO:加载管理的社团
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
    managedClubs.value = clubStore.managedClubs
    total.value = data.total
  } catch (error) {
    console.error('加载管理的社团失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载用户创建申请
const loadUserCreatedApplications = async () => {
  if (!authStore.isLoggedIn) {
    return
  }

  try {
    applicationsLoading.value = true
    userCreatedApplications.value = await clubStore.fetchUserCreatedApplications()
  } catch (error) {
    console.error('加载用户创建申请失败:', error)
  } finally {
    applicationsLoading.value = false
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

// 查看社团详情
const viewClubDetail = (clubId: number) => {
  router.push(`/club/${clubId}`)
}

// 编辑社团
const editClub = (club: Club) => {
  router.push(`/user/edit-club/${club.club_id}`)
}

// 成员管理
const manageMembers = (club: Club) => {
  router.push(`/user/club/${club.club_id}/members`)
}

// 经费管理
const manageFinance = (club: Club) => {
  router.push(`/user/club/${club.club_id}/finance`)
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
    await clubStore.applyToCreateClub({
      name: createForm.value.name,
      desc: createForm.value.description,
      requirements: createForm.value.requirements,
      category_id: createForm.value.category_id,
      tags: createForm.value.tags,
    })
    showCreateDialog.value = false
    // 重置表单
    createForm.value = {
      name: '',
      description: '',
      category_id: 0,
      maxMembers: 50,
      tags: [] as string[],
      requirements: '',
      coverImage: '',
    }
    // 重新加载列表
    await loadManagedClubs()
  } catch (error) {
    console.error('申请创建社团失败:', error)
  } finally {
    createLoading.value = false
  }
}

// 确认删除社团
const confirmDelete = async () => {
  if (!deleteClub.value) return

  try {
    deleteLoading.value = true
    // TODO: 实现删除社团功能
    await clubStore.dismissClub(deleteClub.value.club_id)
    ElMessage.info('删除社团功能暂未实现')
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

const loadUserUpdateApplications = async () => {
  applicationsLoading.value = true

  try {
    const data = await getClubUpdateApplications()
    userUpdateApplications.value = data
    console.log('userUpdateApplications.value', userUpdateApplications.value[0].type)
  } catch (err: any) {
    console.error('加载社团更新申请失败:', err)
  } finally {
    applicationsLoading.value = false
  }
}

// 刷新当前tab的数据
const refreshCurrentTab = async () => {
  if (activeTab.value === 'create') {
    await loadUserCreatedApplications()
  } else if (activeTab.value === 'update') {
    await loadUserUpdateApplications()
  }
}

// 页面加载时获取数据
onMounted(() => {
  getCategoriesList()
  loadManagedClubs()
  loadUserCreatedApplications()
  loadUserUpdateApplications()
  const isOpen = route.query.isOpen
  if (isOpen == 'true') {
    showCreateDialog.value = true
  }
  router.replace({
    path: route.path,
    query: { ...route.query, isOpen: undefined },
  })
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
.favorites-section,
.created-applications-section {
  margin-bottom: 20px;
}

.card-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 5px;
}

.card-view {
  min-height: 400px;
}

.club-card-col {
  margin-bottom: 20px;
}

/* 社团卡片样式 */
.club-card {
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid #e8eaed;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.club-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.club-card:hover {
  transform: translateY(-6px);
  border-color: #409eff;
  box-shadow: 0 16px 48px rgba(64, 158, 255, 0.15);
}

.club-card:hover::before {
  opacity: 1;
}

/* 社团封面 */
.club-cover {
  position: relative;
  height: 160px;
  overflow: hidden;
  cursor: pointer;
}

.club-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.club-cover:hover img {
  transform: scale(1.08);
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.8) 0%, rgba(103, 194, 58, 0.8) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(4px);
}

.club-cover:hover .cover-overlay {
  opacity: 1;
}

.overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: white;
  text-align: center;
  transform: translateY(20px);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.club-cover:hover .overlay-content {
  transform: translateY(0);
}

.view-icon {
  font-size: 24px;
}

.overlay-content span {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.club-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
}

/* 社团信息 */
.club-info {
  padding: 16px;
}

.club-name {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1d2129;
  cursor: pointer;
  transition: color 0.2s;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.club-name:hover {
  color: #409eff;
}

.club-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4e5969;
  padding: 6px 10px;
  background: rgba(64, 158, 255, 0.05);
  border-radius: 6px;
  transition: all 0.2s;
}

.meta-item:hover {
  background: rgba(64, 158, 255, 0.1);
  transform: translateX(4px);
}

.meta-icon {
  color: #409eff;
  font-size: 16px;
}

.club-category {
  font-weight: 600;
  color: #409eff;
}

.club-members {
  font-weight: 500;
}

.favorite-time {
  color: #86909c;
  font-size: 12px;
}

/* 操作按钮 */
.club-actions {
  padding: 0 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: stretch;
}

.club-actions .el-button {
  width: 100% !important;
  margin: 0 !important;
  padding: 0 12px !important;
  box-sizing: border-box;
}

.action-btn {
  width: 100% !important;
  height: 38px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  letter-spacing: 0.2px;
  margin: 0 !important;
  padding: 0 12px !important;
  box-sizing: border-box;
}

.primary-action {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  width: 100%;
  margin: 0;
  padding: 0 12px;
}

.primary-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

.action-btn:not(.primary-action):not(.danger-action) {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e8eaed;
  color: #4e5969;
}

.action-btn:not(.primary-action):not(.danger-action):hover {
  background: rgba(64, 158, 255, 0.05);
  border-color: #409eff;
  color: #409eff;
  transform: translateY(-1px);
}

.danger-action {
  border-color: #f56c6c;
  color: #f56c6c;
  background: rgba(255, 255, 255, 0.8);
}

.danger-action:hover {
  background: rgba(245, 108, 108, 0.1);
  transform: translateY(-1px);
}

.pagination-section {
  margin-top: 20px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 平板响应式 */
@media (max-width: 992px) {
  .application-card-col,
  .club-card-col {
    margin-bottom: 20px;
  }

  .application-card,
  .club-card {
    border-radius: 12px;
  }

  .action-button,
  .action-btn {
    height: 40px;
    font-size: 13px;
  }
}

/* 手机端响应式 */
@media (max-width: 768px) {
  .my-favorites {
    padding: 16px;
  }

  .card-view .el-col,
  .application-card-col {
    width: 100%;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .page-header p {
    font-size: 14px;
  }

  .toolbar .el-row {
    gap: 12px;
  }

  .toolbar .el-col {
    margin-bottom: 8px;
  }

  /* 申请卡片移动端优化 */
  .application-card {
    padding: 14px 12px;
    border-radius: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin-bottom: 12px;
  }

  .status-indicator {
    align-self: stretch;
    justify-content: space-between;
  }

  .club-name {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .club-description {
    margin-top: 20px;
    font-size: 13px;
    -webkit-line-clamp: 2;
  }

  .proposal-meta {
    gap: 8px;
  }

  .meta-item {
    font-size: 12px;
    padding: 6px 10px;
  }

  .time-info {
    margin: 16px 0;
    gap: 8px;
  }

  .time-item {
    padding: 10px;
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .time-content {
    gap: 0;
  }

  .time-label {
    font-size: 11px;
  }

  .time-value {
    font-size: 13px;
  }

  .reject-reason-card {
    padding: 12px;
    margin: 16px 0;
  }

  .reject-content {
    font-size: 12px;
    padding-left: 20px;
  }

  .action-button {
    height: 42px;
    font-size: 13px;
    border-radius: 10px;
  }

  /* 社团卡片移动端优化 */
  .club-cover {
    height: 140px;
  }

  .club-info {
    padding: 16px;
  }

  .club-name {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .club-meta {
    gap: 8px;
  }

  .meta-item {
    padding: 6px 10px;
    font-size: 12px;
  }

  .meta-icon {
    font-size: 14px;
  }

  .club-actions {
    padding: 0 16px 16px;
    gap: 8px;
    align-items: stretch;
  }

  .club-actions .el-button {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 12px !important;
    box-sizing: border-box;
  }

  .action-btn {
    height: 40px;
    font-size: 12px;
    border-radius: 10px;
  }

  .overlay-content {
    transform: translateY(0);
    opacity: 1;
  }

  .club-cover .cover-overlay {
    opacity: 0.9;
  }
}

/* 申请卡片样式 */
.applications-list {
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.applications-list:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}
.application-card-col {
  margin-bottom: 24px;
}

.application-card {
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border: 1px solid #e8eaed;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  /* 固定高度和flex布局 */
  height: 480px;
  display: flex;
  flex-direction: column;
}

.application-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 50%, #e6a23c 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.application-card:hover {
  transform: translateY(-4px);
  border-color: #409eff;
  box-shadow: 0 12px 32px rgba(64, 158, 255, 0.15);
}

.application-card:hover::before {
  opacity: 1;
}

.application-card.status-approved {
  border-color: #e7f5e7;
  background: linear-gradient(135deg, #f7fff7 0%, #e7f5e7 100%);
}

.application-card.status-rejected {
  border-color: #fde2e2;
  background: linear-gradient(135deg, #fffafa 0%, #fde2e2 100%);
}

.application-card.status-pending {
  border-color: #fef3e7;
  background: linear-gradient(135deg, #fffcf7 0%, #fef3e7 100%);
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f2f5;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.status-pending {
  background: #e6a23c;
}

.status-dot.status-approved {
  background: #67c23a;
  animation: none;
}

.status-dot.status-rejected {
  background: #f56c6c;
  animation: none;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(0.8);
  }
}

.status-tag {
  font-weight: 600;
  letter-spacing: 0.5px;
}

.application-id {
  color: #8c939d;
  font-size: 12px;
  font-weight: 500;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 6px;
}

/* 申请方案预览卡片 */
.proposal-preview-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e8eaed;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  margin-bottom: 14px;
}

.proposal-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 10px;
  border-left: 3px solid #409eff;
  padding-left: 8px;
}

.proposal-main-info {
  margin-bottom: 12px;
}

.club-name {
  display: flex;
  align-items: center;
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1d2129;
  line-height: 1.3;
}

.name-icon {
  margin-right: 6px;
  color: #ffd700;
  font-size: 18px;
}

.club-description {
  margin: 0;
  color: #4e5969;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.proposal-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.meta-item .el-icon {
  color: #86909c;
  font-size: 16px;
}

.category-tag {
  font-weight: 600;
}

.tags-section {
  align-items: flex-start;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.tag-item {
  margin: 0;
  font-size: 12px;
  border-radius: 6px;
}

.more-tags {
  font-size: 12px;
  color: #86909c;
  background: #f2f3f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.proposal-error {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
  font-size: 13px;
  padding: 12px;
  background: #fef0f0;
  border-radius: 8px;
}

/* 时间信息 */
.time-info {
  margin: 14px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 6px;
  border: 1px solid #f0f2f5;
}

.time-icon {
  color: #409eff;
  font-size: 16px;
}

.time-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-label {
  font-size: 12px;
  color: #86909c;
}

.time-value {
  font-size: 14px;
  color: #1d2129;
  font-weight: 500;
}

/* 拒绝原因卡片 */
.reject-reason-card {
  margin: 14px 0;
  padding: 12px;
  background: linear-gradient(135deg, #fef5f5 0%, #fef0f0 100%);
  border: 1px solid #fbc4c4;
  border-radius: 8px;
}

.reject-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.reject-icon {
  color: #f56c6c;
  font-size: 14px;
}

.reject-title {
  font-weight: 600;
  color: #f56c6c;
  font-size: 12px;
}

.reject-content {
  margin: 0;
  color: #c53030;
  font-size: 12px;
  line-height: 1.5;
  padding-left: 20px;
}

/* 操作按钮 */
.card-actions {
  margin-top: 14px;
  text-align: center;
}

.action-button {
  width: 100%;
  height: 38px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.success-button {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

.success-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.4);
}

.pending-button {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  border: none;
  opacity: 0.8;
}

.retry-button {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.retry-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.4);
}

/* 社团信息更新申请样式 */
.update-applications-section {
  margin-bottom: 24px;
}

.update-application-card {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border: 1px solid #e1e8ff;
  position: relative;
  overflow: hidden;
}

.update-application-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #66b1ff, #409eff);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.club-preview-card {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid #e8f4ff;
}

.club-logo-section {
  flex-shrink: 0;
}

.club-logo {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid #e1e8ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.no-logo {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  border: 2px solid #e1e8ff;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f4ff 0%, #e1e8ff 100%);
  color: #409eff;
  font-size: 12px;
  font-weight: 600;
}

.club-main-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.club-name {
  margin: 0;
  color: #1d2129;
  font-size: 18px;
  font-weight: 700;
  line-height: 1.3;
}

.club-description {
  margin: 0;
  color: #4e5969;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.club-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.club-meta .meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  border: 1px solid #f0f4ff;
}

.club-meta .meta-item .el-icon {
  color: #409eff;
  font-size: 16px;
}

.member-count {
  font-weight: 600;
  color: #1d2129;
}

.leader-id {
  font-weight: 600;
  color: #1d2129;
}

.requirements-section {
  margin-top: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  border: 1px solid #e8f4ff;
}

.requirements-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.requirements-header .el-icon {
  color: #409eff;
  font-size: 14px;
}

.requirements-label {
  font-weight: 600;
  color: #1d2129;
  font-size: 12px;
}

.requirements-content {
  margin: 0;
  color: #4e5969;
  font-size: 12px;
  line-height: 1.4;
  padding-left: 20px;
}

.view-button {
  background: linear-gradient(135deg, #909399 0%, #a6a9ad 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(144, 147, 153, 0.3);
}

.view-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(144, 147, 153, 0.4);
}

/* 更新申请卡片响应式优化 */
@media (max-width: 768px) {
  .club-preview-card {
    flex-direction: column;
    gap: 12px;
    padding: 12px;
  }

  .club-logo-section {
    align-self: center;
  }

  .club-name {
    font-size: 16px;
    text-align: center;
  }

  .club-description {
    text-align: center;
  }

  .club-meta {
    gap: 6px;
  }

  .club-meta .meta-item {
    padding: 4px 8px;
    font-size: 12px;
  }

  .requirements-section {
    padding: 8px;
  }

  .requirements-content {
    font-size: 11px;
    padding-left: 16px;
  }
}

/* 申请管理区域样式 */
.applications-management-section {
  width: 100%;
  margin-bottom: 24px;
}

.applications-management-section .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.applications-management-section .el-tabs {
  flex: 1;
}

.applications-management-section .el-tabs__header {
  margin: 0;
  border-bottom: none;
}

.applications-management-section .el-tabs__nav-wrap {
  padding: 0;
}

.applications-management-section .el-tabs__item {
  height: 40px;
  line-height: 40px;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  border: 1px solid #e4e7ed;
  border-bottom: none;
  background: #fafafa;
  transition: all 0.3s ease;
}

.applications-management-section .el-tabs__item:hover {
  color: #409eff;
  background: #f0f9ff;
}

.applications-management-section .el-tabs__item.is-active {
  color: #409eff;
  background: #fff;
  border-color: #409eff;
  border-bottom-color: #fff;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-badge {
  margin-left: 4px;
}

.tab-badge .el-badge__content {
  background: #409eff;
  border: none;
  font-size: 10px;
  height: 16px;
  line-height: 16px;
  padding: 0 4px;
  min-width: 16px;
}

/* 申请列表表格样式 */
.applications-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.applications-table .el-table__header {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
}

.applications-table .el-table__header th {
  background: transparent;
  color: #1d2129;
  font-weight: 600;
  border-bottom: 2px solid #e1e8ff;
}

.applications-table .el-table__row {
  transition: all 0.3s ease;
}

.applications-table .el-table__row:hover {
  background: #f8f9ff;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.club-info-cell {
  padding: 8px 0;
}

.club-logo-name {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.club-logo-small {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #e1e8ff;
}

.no-logo-small {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #e1e8ff;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #999;
  font-size: 10px;
}

.club-name-row {
  font-size: 16px;
  color: #1d2129;
  margin-bottom: 4px;
}

.club-desc-row {
  font-size: 13px;
  color: #4e5969;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.club-meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.leader-info {
  font-size: 12px;
  color: #606266;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.tags-display {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-item {
  margin: 0;
  font-size: 11px;
  border-radius: 4px;
}

.more-tags {
  font-size: 11px;
  color: #86909c;
  background: #f2f3f5;
  padding: 1px 4px;
  border-radius: 3px;
}

.requirements-display {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #606266;
  background: #f8f9ff;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e1e8ff;
}

.requirements-display .el-icon {
  color: #409eff;
  font-size: 14px;
}

.reject-reason {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #f56c6c;
  font-size: 12px;
}

.reject-reason .el-icon {
  font-size: 14px;
}

.proposal-error {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #f56c6c;
  font-size: 12px;
  padding: 8px;
  background: #fef0f0;
  border-radius: 4px;
  border: 1px solid #fbc4c4;
}

@media (max-width: 480px) {
  .club-preview-card {
    padding: 10px;
    gap: 10px;
  }

  .club-logo,
  .no-logo {
    width: 60px;
    height: 60px;
  }

  .club-name {
    font-size: 14px;
  }

  .club-description {
    font-size: 12px;
  }

  .club-meta .meta-item {
    padding: 3px 6px;
    font-size: 11px;
  }

  .club-meta .meta-item .el-icon {
    font-size: 14px;
  }

  .requirements-section {
    padding: 6px;
  }

  .requirements-content {
    font-size: 10px;
    padding-left: 14px;
  }
}
</style>
