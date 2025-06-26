<template>
  <div class="my-applications">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>我的申请</h1>
      <p>查看您的社团申请记录和状态</p>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <el-card>
        <el-row :gutter="20" align="middle">
          <el-col :span="6">
            <el-select
              v-model="filterStatus"
              placeholder="申请状态"
              clearable
              @change="handleFilter"
            >
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select
              v-model="filterCategory"
              placeholder="社团类型"
              clearable
              @change="handleFilter"
            >
              <el-option label="全部类型" value="" />
              <el-option
                v-for="(category, index) in categories"
                :label="categories[index]"
                :value="categories[index]"
              ></el-option>
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索社团名称"
              clearable
              @keyup.enter="handleFilter"
            >
              <template #append>
                <el-button icon="Search" @click="handleFilter" />
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button @click="resetFilter">重置</el-button>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 申请统计 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number total">{{ applicationStats.total }}</div>
              <div class="stat-label">总申请数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number pending">{{ applicationStats.pending }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number approved">{{ applicationStats.approved }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number rejected">{{ applicationStats.rejected }}</div>
              <div class="stat-label">已拒绝</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 申请列表 -->
    <div class="applications-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>申请记录</span>
            <el-button @click="loadApplications" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <div v-loading="loading">
          <!-- 空状态 -->
          <div v-if="!applications.length && !loading" class="empty-state">
            <el-empty description="暂无申请记录">
              <el-button type="primary" @click="$router.push('/')"> 去申请社团 </el-button>
            </el-empty>
          </div>

          <!-- 申请列表 -->
          <div v-else class="applications-list">
            <div v-for="application in applications" :key="application.id" class="application-item">
              <div class="application-content">
                <!-- 社团信息 -->
                <div class="club-info">
                  <el-avatar :size="50" :src="application.clubCoverImage" class="club-avatar">
                    <el-icon><UserFilled /></el-icon>
                  </el-avatar>
                  <div class="club-details">
                    <h3 class="club-name">{{ application.clubName }}</h3>
                    <p class="club-category">{{ getCategoryText(application.clubCategory) }}</p>
                    <p class="application-time">
                      申请时间：{{ formatDate(application.createdAt) }}
                    </p>
                  </div>
                </div>

                <!-- 申请信息 -->
                <div class="application-info">
                  <div class="application-reason">
                    <h4>申请理由：</h4>
                    <p>{{ application.reason || '无' }}</p>
                  </div>

                  <div v-if="application.feedback" class="application-feedback">
                    <h4>反馈信息：</h4>
                    <p>{{ application.feedback }}</p>
                  </div>
                </div>

                <!-- 状态和操作 -->
                <div class="application-actions">
                  <div class="status-section">
                    <el-tag
                      :type="getStatusType(application.status)"
                      :effect="application.status === 'pending' ? 'light' : 'plain'"
                      size="large"
                    >
                      {{ getStatusText(application.status) }}
                    </el-tag>

                    <div v-if="application.reviewedAt" class="review-time">
                      处理时间：{{ formatDate(application.reviewedAt) }}
                    </div>
                  </div>

                  <div class="action-buttons">
                    <el-button size="small" @click="viewClubDetail(application.clubId)">
                      查看社团
                    </el-button>

                    <el-button
                      v-if="application.status === 'pending'"
                      size="small"
                      type="danger"
                      @click="cancelApplication(application.id)"
                    >
                      撤销申请
                    </el-button>

                    <el-dropdown
                      v-if="application.status === 'approved'"
                      @command="(command: string) => handleApprovedAction(command, application)"
                    >
                      <el-button size="small">
                        更多操作 <el-icon><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="view-activities">查看活动</el-dropdown-item>
                          <el-dropdown-item command="quit-club">退出社团</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="applications.length" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalNum"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 重新申请对话框 -->
    <el-dialog v-model="showReapplyDialog" title="重新申请" width="600px">
      <el-form ref="reapplyFormRef" :model="reapplyForm" :rules="reapplyRules" label-width="100px">
        <el-form-item label="申请理由" prop="reason">
          <el-input
            v-model="reapplyForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请详细说明您申请加入该社团的理由..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showReapplyDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmReapply" :loading="reapplyLoading">
          提交申请
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, UserFilled, ArrowDown } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { getUserApplications, applyToClub } from '@/api/club'
import type { Application, Club, ClubCategory } from '@/types'
import { useClubStore } from '@/stores/club'

// 路由
const router = useRouter()
const clubStore = useClubStore()

// 响应式数据
const loading = ref(false)
const reapplyLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalNum = ref(0)

// 筛选条件
const filterStatus = ref('')
const filterCategory = ref('')
const searchKeyword = ref('')

// 申请数据
const applications = ref<Application[]>([])
const applicationStats = reactive({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0,
})

// 重新申请
const showReapplyDialog = ref(false)
const reapplyClubId = ref('')
const reapplyForm = reactive({
  reason: '',
})
const reapplyFormRef = ref<FormInstance>()

// 重新申请表单验证规则
const reapplyRules = {
  reason: [
    { required: true, message: '请填写申请理由', trigger: 'blur' },
    { min: 10, message: '申请理由至少10个字符', trigger: 'blur' },
  ],
}

// 计算属性
const filteredApplications = computed(() => {
  // 这里实际上应该在后端进行筛选，前端主要做展示
  return applications.value
})

// 分类数据
const categories = ref<ClubCategory[]>(['学术科技', '文艺体育', '志愿服务', '创新创业', '其他'])

// 方法
const getCategoryText = (category: string) => {
  const categoryMap: Record<string, string> = {
    academic: '学术科技',
    culture: '文化艺术',
    sports: '体育运动',
    volunteer: '志愿服务',
    practice: '社会实践',
    innovation: '创新创业',
  }
  return categoryMap[category] || category
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    cancelled: '已撤销',
  }
  return statusMap[status] || status
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    cancelled: 'info',
  }
  return typeMap[status] || 'info'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const loadApplications = async () => {
  try {
    loading.value = true

    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      status: filterStatus.value,
      category: filterCategory.value,
      keyword: searchKeyword.value,
    }

    const response = await getUserApplications(params)
    const { list, total } = response.data.data
    applications.value = list
    totalNum.value = total

    console.log(applications.value)

    // 更新统计数据
    updateStats(list)
  } catch (error: any) {
    ElMessage.error(error.message || '加载申请记录失败')
  } finally {
    loading.value = false
  }
}

const updateStats = (apps: any[]) => {
  applicationStats.total = apps.length
  applicationStats.pending = apps.filter((app) => app.status === 'pending').length
  applicationStats.approved = apps.filter((app) => app.status === 'approved').length
  applicationStats.rejected = apps.filter((app) => app.status === 'rejected').length
}

const handleFilter = () => {
  currentPage.value = 1
  loadApplications()
}

const resetFilter = () => {
  filterStatus.value = ''
  filterCategory.value = ''
  searchKeyword.value = ''
  currentPage.value = 1
  loadApplications()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadApplications()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadApplications()
}

const viewClubDetail = (clubId: string) => {
  router.push(`/club/${clubId}`)
}

const cancelApplication = async (applicationId: string) => {
  try {
    await ElMessageBox.confirm('确定要撤销这个申请吗？', '撤销申请', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // TODO: 调用撤销申请API
    await clubStore.cancelApplication(applicationId)
    ElMessage.success('申请已撤销')
    loadApplications()
  } catch (error) {
    // 用户取消操作
  }
}

const reapplyToClub = (clubId: string) => {
  reapplyClubId.value = clubId
  reapplyForm.reason = ''
  showReapplyDialog.value = true
}

const confirmReapply = async () => {
  if (!reapplyFormRef.value) return

  try {
    await reapplyFormRef.value.validate()
    reapplyLoading.value = true

    await applyToClub({
      clubId: reapplyClubId.value,
      reason: reapplyForm.reason,
    })

    ElMessage.success('重新申请提交成功')
    showReapplyDialog.value = false
    loadApplications()
  } catch (error: any) {
    ElMessage.error(error.message || '申请提交失败')
  } finally {
    reapplyLoading.value = false
  }
}

const handleApprovedAction = (command: string, application: any) => {
  switch (command) {
    case 'view-activities':
      // TODO: 跳转到社团活动页面
      ElMessage.info('功能开发中...')
      break
    case 'quit-club':
      quitClub(application.club.id)
      break
  }
}

const quitClub = async (clubId: string) => {
  try {
    await ElMessageBox.confirm('确定要退出该社团吗？退出后需要重新申请才能加入。', '退出社团', {
      confirmButtonText: '确定退出',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // TODO: 调用退出社团API
    ElMessage.success('已退出社团')
    loadApplications()
  } catch (error) {
    // 用户取消操作
  }
}

onMounted(() => {
  console.log(clubStore.categories)

  loadApplications()
})
</script>

<style scoped>
.my-applications {
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

.filter-section,
.stats-section,
.applications-section {
  margin-bottom: 20px;
}

.stats-section .stat-card {
  text-align: center;
  transition: transform 0.2s;
}

.stats-section .stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-number.total {
  color: #409eff;
}
.stat-number.pending {
  color: #e6a23c;
}
.stat-number.approved {
  color: #67c23a;
}
.stat-number.rejected {
  color: #f56c6c;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* .applications-list {
  space-y: 20px;
} */

.application-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  transition: all 0.3s;
}

.application-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.application-content {
  display: flex;
  gap: 20px;
}

.club-info {
  display: flex;
  gap: 15px;
  min-width: 300px;
}

.club-logo {
  flex-shrink: 0;
}

.club-details h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
}

.club-details p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.application-info {
  flex: 1;
  min-width: 200px;
}

.application-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.application-info p {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.application-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 15px;
  min-width: 150px;
}

.status-section {
  text-align: right;
}

.review-time {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination-section {
  margin-top: 20px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .application-content {
    flex-direction: column;
    gap: 15px;
  }

  .club-info {
    min-width: auto;
  }

  .application-actions {
    align-items: flex-start;
  }

  .action-buttons {
    width: 100%;
    justify-content: flex-start;
  }

  .stats-section .el-col {
    margin-bottom: 10px;
  }
}
</style>
