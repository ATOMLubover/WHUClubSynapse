<template>
  <div class="club-audit">
    <el-card>
      <template #header>
        <div class="header-content">
          <span>社团创建申请审核</span>
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
          <el-table-column prop="username" label="申请人" width="100" />
          <el-table-column prop="category" label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getCategoryType(row.category)">
                {{ getCategoryName(row.category) }}
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
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button 
                v-if="row.status === 'pending'"
                type="success" 
                size="small" 
                @click="approveApplication(row)"
              >
                通过
              </el-button>
              <el-button 
                v-if="row.status === 'pending'"
                type="danger" 
                size="small" 
                @click="rejectApplication(row)"
              >
                拒绝
              </el-button>
              <el-button 
                type="primary" 
                size="small" 
                @click="viewApplication(row)"
              >
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
      </div>
    </el-card>

    <!-- 申请详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="申请详情" width="800px">
      <div v-if="selectedApplication" class="application-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="社团名称">{{ selectedApplication.clubName }}</el-descriptions-item>
          <el-descriptions-item label="申请人">{{ selectedApplication.username }}</el-descriptions-item>
          <el-descriptions-item label="学号">{{ selectedApplication.studentId }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ selectedApplication.major }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ selectedApplication.phone }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedApplication.email }}</el-descriptions-item>
          <el-descriptions-item label="社团类型">
            <el-tag :type="getCategoryType(selectedApplication.category)">
              {{ getCategoryName(selectedApplication.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大人数">{{ selectedApplication.maxMembers }}人</el-descriptions-item>
          <el-descriptions-item label="申请时间">{{ formatDate(selectedApplication.applyTime) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedApplication.status)">
              {{ getStatusText(selectedApplication.status) }}
            </el-tag>
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
            <el-tag v-for="tag in selectedApplication.tags" :key="tag" size="small" style="margin-right: 8px;">
              {{ tag }}
            </el-tag>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>联系方式</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="QQ">{{ selectedApplication.contactInfo?.qq || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="微信">{{ selectedApplication.contactInfo?.wechat || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ selectedApplication.contactInfo?.email || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ selectedApplication.contactInfo?.phone || '暂无' }}</el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">{{ selectedApplication.contactInfo?.address || '暂无' }}</el-descriptions-item>
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
        
        <div v-if="selectedApplication.status === 'rejected' && selectedApplication.rejectReason" class="detail-section">
          <h4>拒绝原因</h4>
          <p class="reject-reason">{{ selectedApplication.rejectReason }}</p>
        </div>
      </div>
    </el-dialog>

    <!-- 拒绝原因对话框 -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝申请" width="500px">
      <el-form :model="rejectForm" ref="rejectFormRef" :rules="rejectRules">
        <el-form-item label="拒绝原因" prop="rejectReason">
          <el-input
            v-model="rejectForm.rejectReason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" :loading="rejectLoading">
          确认拒绝
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useClubStore } from '@/stores/club'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ClubCreationApplication } from '@/types'

const clubStore = useClubStore()
const applications = ref<ClubCreationApplication[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const filterStatus = ref('')
const detailDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const selectedApplication = ref<ClubCreationApplication | null>(null)
const rejectLoading = ref(false)

const rejectForm = ref({
  rejectReason: ''
})

const rejectRules = {
  rejectReason: [
    { required: true, message: '请输入拒绝原因', trigger: 'blur' }
  ]
}

const rejectFormRef = ref()

// 获取分类类型
const getCategoryType = (category: number) => {
  const typeMap: Record<number, string> = {
    0: 'primary',   // 学术科技
    1: 'success',   // 文艺体育
    2: 'warning',   // 志愿服务
    3: 'danger',    // 创新创业
    4: 'info'       // 其他
  }
  return typeMap[category] || 'info'
}

// 获取分类名称
const getCategoryName = (category: number) => {
  const nameMap: Record<number, string> = {
    0: '学术科技',
    1: '文艺体育',
    2: '志愿服务',
    3: '创新创业',
    4: '其他'
  }
  return nameMap[category] || '未知'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
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
      status: filterStatus.value || undefined
    })
    applications.value = data.list
    total.value = data.total
  } catch (error) {
    console.error('加载申请列表失败:', error)
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

// 通过申请
const approveApplication = async (application: ClubCreationApplication) => {
  try {
    await ElMessageBox.confirm(
      `确定要通过"${application.clubName}"的创建申请吗？`,
      '确认通过',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await clubStore.reviewClubApplication(application.id, {
      status: 'approved'
    })
    
    loadApplications()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核失败:', error)
    }
  }
}

// 拒绝申请
const rejectApplication = (application: ClubCreationApplication) => {
  selectedApplication.value = application
  rejectForm.value.rejectReason = ''
  rejectDialogVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  if (!selectedApplication.value) return
  
  try {
    await rejectFormRef.value?.validate()
    rejectLoading.value = true
    
    await clubStore.reviewClubApplication(selectedApplication.value.id, {
      status: 'rejected',
      rejectReason: rejectForm.value.rejectReason
    })
    
    rejectDialogVisible.value = false
    loadApplications()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('拒绝申请失败:', error)
    }
  } finally {
    rejectLoading.value = false
  }
}

onMounted(() => {
  loadApplications()
})
</script>

<style scoped>
.club-audit {
  padding: 20px;
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
</style>
