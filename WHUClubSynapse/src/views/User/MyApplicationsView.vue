<template>
  <div class="my-applications">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>我的社团申请</h1>
      <p>查看您提交的社团创建申请状态</p>
    </div>

    <el-card>
      <template #header>
        <div class="header-content">
          <span>申请记录</span>
          <div class="header-actions">
            <el-select v-model="filterStatus" placeholder="筛选状态" @change="loadApplications">
              <el-option label="全部" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
            <el-button type="primary" @click="loadApplications">刷新</el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <!-- 卡片布局替代表格 -->
        <div v-if="applications.length > 0" class="applications-grid">
          <el-card
            v-for="application in applications"
            :key="application.appli_id"
            class="application-card"
            shadow="hover"
          >
            <div class="card-content">
              <!-- 社团信息头部 -->
              <div class="club-header">
                <el-avatar
                  :size="60"
                  :src="
                    application.club?.logo_url ||
                    'https://cdn.jsdelivr.net/gh/whu-asset/static/club-default.png'
                  "
                  class="club-avatar"
                />
                <div class="club-info">
                  <h3 class="club-name">
                    <el-link
                      :underline="false"
                      @click="goToClubDetail(application.club_id)"
                      class="club-link"
                    >
                      {{ application.club?.club_name || '未知社团' }}
                    </el-link>
                  </h3>
                  <el-tag
                    :type="getCategoryType(application.club?.category)"
                    size="small"
                    class="category-tag"
                  >
                    {{
                      clubStore.categoriesList.find(
                        (category) => category.category_id === application.club?.category,
                      )?.name || '未知类型'
                    }}
                  </el-tag>
                </div>
                <div class="status-area">
                  <el-tag :type="getStatusType(application.status)" size="large">
                    状态： {{ getStatusText(application.status) }}
                  </el-tag>
                </div>
              </div>

              <!-- 申请信息 -->
              <div class="application-info">
                <div class="info-row">
                  <span class="label">申请时间：</span>
                  <span class="value">{{ formatDate(application.applied_at) }}</span>
                </div>

                <div v-if="application.reviewed_at" class="info-row">
                  <span class="label">审核时间：</span>
                  <span class="value">{{ formatDate(application.reviewed_at) }}</span>
                </div>

                <!-- 申请理由 -->
                <div v-if="application.reason" class="reason-section">
                  <span class="label">申请理由：</span>
                  <div class="reason-content">
                    {{ application.reason }}
                  </div>
                </div>

                <!-- 拒绝理由（仅当状态为rejected时显示） -->
                <div
                  v-if="application.status === 'rejected' && application.reject_reason"
                  class="reject-reason-section"
                >
                  <span class="label reject-label">拒绝理由：</span>
                  <div class="reject-reason-content">
                    {{ application.reject_reason }}
                  </div>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="card-actions">
                <el-button
                  type="primary"
                  size="small"
                  @click="goToClubDetail(application.club_id)"
                  :disabled="!application.club_id"
                >
                  查看社团详情
                </el-button>
                <el-button
                  v-if="application.status === 'approved'"
                  type="success"
                  size="small"
                  @click="goToClubDetail(application.club_id)"
                >
                  进入社团
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <div v-if="total > 0" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[6, 12, 18, 24]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>

        <el-empty v-else-if="!loading" description="暂无申请记录" :image-size="120">
          <el-button type="primary" @click="$router.push('/user/managed-clubs?isOpen=true')">
            申请创建社团
          </el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import { ElMessage } from 'element-plus'
import type { ClubApplication, ClubCreationApplication } from '@/types'

const router = useRouter()
const clubStore = useClubStore()
const applications = ref<ClubApplication[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(6)
const filterStatus = ref('')
const detailDialogVisible = ref(false)
const selectedApplication = ref<ClubApplication | null>(null)

// 获取分类类型
const getCategoryType = (category: number) => {
  const typeMap: Record<number, string> = {
    0: 'primary', // 学术科技
    1: 'success', // 文艺体育
    2: 'warning', // 志愿服务
    3: 'danger', // 创新创业
    4: 'info', // 其他
  }
  return typeMap[category] || 'info'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return textMap[status] || '未知'
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载申请列表
const loadApplications = async () => {
  try {
    loading.value = true
    const data = await clubStore.fetchPendingClubApplications({
      page: currentPage.value,
      pageSize: pageSize.value,
      status: filterStatus.value as 'pending' | 'approved' | 'rejected' | undefined,
    })
    applications.value = data.list as ClubApplication[]
    total.value = data.total
    console.log('applications.value', applications.value)
  } catch (error) {
    console.error('加载申请列表失败:', error)
    ElMessage.error('加载申请列表失败')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  loadApplications()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadApplications()
}

// 查看申请详情
const viewApplication = (application: ClubApplication) => {
  selectedApplication.value = application
  detailDialogVisible.value = true
}

// 跳转到社团详情（如果申请已通过）
const goToClubDetail = (clubId: string) => {
  router.push(`/club/${clubId}`)
}

onMounted(() => {
  clubStore.fetchCategoriesList()
  console.log('clubStore.categoriesList', clubStore.categoriesList)
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-section {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.application-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.detail-section p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cover-image {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  object-fit: cover;
}

.reject-reason {
  color: #f56c6c;
  background-color: #fef0f0;
  padding: 10px;
  border-radius: 4px;
  border-left: 4px solid #f56c6c;
}

.approve-message {
  color: #67c23a;
  background-color: #f0f9ff;
  padding: 10px;
  border-radius: 4px;
  border-left: 4px solid #67c23a;
}

.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 350px));
  gap: 24px;
  margin-bottom: 24px;
}

.application-card {
  width: 100%;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
}

.application-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-content {
  padding: 0;
}

.club-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 20px 20px 0 20px;
}

.club-avatar {
  margin-right: 16px;
  border: 2px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.club-info {
  flex: 1;
  min-width: 0;
}

.club-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.club-link {
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s ease;
}

.club-link:hover {
  color: #66b1ff;
}

.category-tag {
  margin-top: 4px;
}

.status-area {
  margin-left: 16px;
  display: flex;
  align-items: center;
}

.application-info {
  padding: 0 20px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  flex-shrink: 0;
}

.value {
  color: #303133;
  margin-left: 8px;
}

.reason-section,
.reject-reason-section {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.reason-section .label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #409eff;
}

.reason-content {
  margin: 0;
  padding: 0;
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
}

.reject-reason-section {
  background-color: #fef0f0;
  border: 1px solid #fde2e2;
}

.reject-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #f56c6c;
}

.reject-reason-content {
  margin: 0;
  padding: 0;
  color: #f56c6c;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
}

.card-actions {
  padding: 0 20px 20px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .applications-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .applications-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .club-header {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }

  .club-avatar {
    margin-right: 0;
    margin-bottom: 12px;
  }

  .status-area {
    margin-left: 0;
    margin-top: 8px;
  }

  .card-actions {
    flex-direction: column;
    gap: 8px;
  }

  .card-actions .el-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .club-header,
  .application-info,
  .card-actions {
    padding-left: 16px;
    padding-right: 16px;
  }

  .club-name {
    font-size: 16px;
  }
}
</style>
