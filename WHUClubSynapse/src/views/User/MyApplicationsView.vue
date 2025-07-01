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
        <el-table :data="applications" style="width: 100%">
          <el-table-column prop="clubName" label="社团名称" min-width="120" />
          <el-table-column prop="category" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getCategoryType(row.category)">
                {{
                  clubStore.categoriesList.find((category) => category.category_id === row.category)
                    ?.name
                }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="maxMembers" label="最大人数" width="80" />
          <el-table-column prop="applyTime" label="申请时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.applyTime) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reviewTime" label="审核时间" width="160">
            <template #default="{ row }">
              {{ row.reviewTime ? formatDate(row.reviewTime) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewApplication(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="total > 0" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[10, 20, 50]"
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

    <!-- 申请详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="申请详情" width="800px">
      <div v-if="selectedApplication" class="application-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="社团名称">{{
            selectedApplication.clubName
          }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{
            selectedApplication.username
          }}</el-descriptions-item>
          <el-descriptions-item label="学号">{{
            selectedApplication.studentId
          }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ selectedApplication.major }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{
            selectedApplication.phone
          }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedApplication.email }}</el-descriptions-item>
          <el-descriptions-item label="社团类型">
            <el-tag :type="getCategoryType(selectedApplication.category)">
              {{
                clubStore.categoriesList.find(
                  (category) => category.category_id === selectedApplication?.category,
                )?.name
              }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大人数"
            >{{ selectedApplication.maxMembers }}人</el-descriptions-item
          >
          <el-descriptions-item label="申请时间">{{
            formatDate(selectedApplication.applyTime)
          }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedApplication.status)">
              {{ getStatusText(selectedApplication.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedApplication.reviewTime" label="审核时间">
            {{ formatDate(selectedApplication.reviewTime) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedApplication.reviewerName" label="审核人">
            {{ selectedApplication.reviewerName }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>社团简介</h4>
          <p>{{ selectedApplication.description }}</p>
        </div>

        <div class="detail-section">
          <h4>详细介绍</h4>
          <p>{{ selectedApplication.introduction || '暂无' }}</p>
        </div>

        <div class="detail-section">
          <h4>加入要求</h4>
          <p>{{ selectedApplication.requirements }}</p>
        </div>

        <div class="detail-section">
          <h4>社团标签</h4>
          <div class="tags-container">
            <el-tag
              v-for="tag in selectedApplication.tags"
              :key="tag"
              size="small"
              style="margin-right: 8px"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="detail-section">
          <h4>联系方式</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="QQ">{{
              selectedApplication.contactInfo?.qq || '暂无'
            }}</el-descriptions-item>
            <el-descriptions-item label="微信">{{
              selectedApplication.contactInfo?.wechat || '暂无'
            }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{
              selectedApplication.contactInfo?.email || '暂无'
            }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{
              selectedApplication.contactInfo?.phone || '暂无'
            }}</el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">{{
              selectedApplication.contactInfo?.address || '暂无'
            }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>例会信息</h4>
          <p>时间：{{ selectedApplication.meetingTime || '暂无' }}</p>
          <p>地点：{{ selectedApplication.meetingLocation || '暂无' }}</p>
        </div>

        <div v-if="selectedApplication.coverImage" class="detail-section">
          <h4>封面图片</h4>
          <img :src="selectedApplication.coverImage" alt="封面图片" class="cover-image" />
        </div>

        <div
          v-if="selectedApplication.status === 'rejected' && selectedApplication.rejectReason"
          class="detail-section"
        >
          <h4>拒绝原因</h4>
          <p class="reject-reason">{{ selectedApplication.rejectReason }}</p>
        </div>

        <div v-if="selectedApplication.status === 'approved'" class="detail-section">
          <h4>审核结果</h4>
          <p class="approve-message">恭喜！您的社团创建申请已通过审核，社团已成功创建。</p>
          <el-button type="primary" @click="goToClubDetail(selectedApplication)">
            查看社团详情
          </el-button>
        </div>
      </div>
    </el-dialog>
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
const pageSize = ref(10)
const filterStatus = ref('')
const detailDialogVisible = ref(false)
const selectedApplication = ref<ClubCreationApplication | null>(null)

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
    applications.value = data.list
    total.value = data.total
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
const viewApplication = (application: ClubCreationApplication) => {
  selectedApplication.value = application
  detailDialogVisible.value = true
}

// 跳转到社团详情（如果申请已通过）
const goToClubDetail = (application: ClubCreationApplication) => {
  // 这里需要根据社团名称查找对应的社团ID
  // 实际项目中应该从后端获取社团ID
  ElMessage.info('跳转到社团详情功能开发中...')
  detailDialogVisible.value = false
}

onMounted(() => {
  clubStore.fetchCategoriesList()
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
  margin-top: 20px;
  display: flex;
  justify-content: center;
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
</style>
