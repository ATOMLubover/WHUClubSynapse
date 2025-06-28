<template>
  <div class="member-management">
    <div class="page-header">
      <div class="header-content">
        <div class="back-button" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="header-info">
          <h1>{{ club?.name }} - 成员管理</h1>
          <p>管理社团成员和审核加入申请</p>
        </div>
      </div>
    </div>

    <el-card class="management-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="成员列表" name="members">
          <div class="tab-content">
            <div class="toolbar">
              <div class="search-section">
                <el-input
                  v-model="memberSearchKeyword"
                  placeholder="搜索成员姓名或学号"
                  clearable
                  @input="handleMemberSearch"
                  style="width: 300px"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="filter-section">
                <el-select v-model="memberRoleFilter" placeholder="角色筛选" clearable @change="handleMemberFilter">
                  <el-option label="管理员" value="admin" />
                  <el-option label="普通成员" value="member" />
                </el-select>
                <el-button @click="refreshMembers" :loading="memberLoading" type="primary" size="small">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>

            <el-table v-loading="memberLoading" :data="members" style="width: 100%" row-key="id">
              <el-table-column label="成员信息" min-width="300">
                <template #default="{ row }">
                  <div class="member-info-button" @click="showMemberDetail(row)">
                    <el-avatar :src="row.avatar_url" :size="40" />
                    <div class="member-details">
                      <div class="member-name">{{ row.realName || row.username }}</div>
                      <div class="member-username">@{{ row.username }}</div>
                      <div class="member-student-id">学号: {{ row.studentId || '未填写' }}</div>
                    </div>
                    <div class="member-role">
                      <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
                        {{ row.role === 'admin' ? '管理员' : '成员' }}
                      </el-tag>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="加入时间" width="150">
                <template #default="{ row }">
                  {{ formatDate(row.joinTime) }}
                </template>
              </el-table-column>
            </el-table>

            <div v-if="memberTotal > 0" class="pagination-section">
              <el-pagination
                v-model:current-page="memberCurrentPage"
                v-model:page-size="memberPageSize"
                :total="memberTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleMemberSizeChange"
                @current-change="handleMemberCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="申请审核" name="applications">
          <div class="tab-content">
            <div class="toolbar">
              <div class="search-section">
                <el-input
                  v-model="applicationSearchKeyword"
                  placeholder="搜索申请人姓名或学号"
                  clearable
                  @input="handleApplicationSearch"
                  style="width: 300px"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              <div class="filter-section">
                <el-select v-model="applicationStatusFilter" placeholder="状态筛选" clearable @change="handleApplicationFilter">
                  <el-option label="待审核" value="pending" />
                  <el-option label="已通过" value="approved" />
                  <el-option label="已拒绝" value="rejected" />
                </el-select>
                <el-button @click="refreshApplications" :loading="applicationLoading" type="primary" size="small">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>

            <el-table v-loading="applicationLoading" :data="applications" style="width: 100%" row-key="id">
              <el-table-column label="申请人信息" min-width="200">
                <template #default="{ row }">
                  <div class="applicant-info-button" @click="showApplicationDetail(row)">
                    <el-avatar :src="row.avatar_url" :size="40" />
                    <div class="applicant-details">
                      <div class="applicant-name">{{ row.realName || row.username }}</div>
                      <div class="applicant-username">@{{ row.username }}</div>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="学号" prop="studentId" width="120" />
              <el-table-column label="专业" prop="major" width="150" />
              <el-table-column label="申请理由" min-width="200">
                <template #default="{ row }">
                  <div class="apply-reason-text">{{ row.applyReason }}</div>
                </template>
              </el-table-column>

              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ getStatusText(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="申请时间" width="150">
                <template #default="{ row }">
                  {{ formatDate(row.applyTime) }}
                </template>
              </el-table-column>

              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <div v-if="row.status === 'pending'" class="application-actions">
                    <el-button size="small" type="success" @click="approveApplication(row)">
                      同意
                    </el-button>
                    <el-button size="small" type="danger" @click="rejectApplication(row)">
                      拒绝
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="applicationTotal > 0" class="pagination-section">
              <el-pagination
                v-model:current-page="applicationCurrentPage"
                v-model:page-size="applicationPageSize"
                :total="applicationTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleApplicationSizeChange"
                @current-change="handleApplicationCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 拒绝申请对话框 -->
    <el-dialog v-model="showRejectDialog" title="拒绝申请" width="500px">
      <el-form ref="rejectFormRef" :model="rejectForm" :rules="rejectRules" label-width="100px">
        <el-form-item label="拒绝原因" prop="reason">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmReject" :loading="rejectLoading">
          确认拒绝
        </el-button>
      </template>
    </el-dialog>

    <!-- 移除成员对话框 -->
    <el-dialog v-model="showRemoveDialog" title="移除成员" width="500px">
      <div class="remove-dialog-content">
        <el-icon class="warning-icon" color="#F56C6C"><Warning /></el-icon>
        <p>
          确定要移除成员 <strong>{{ removeMemberData?.realName || removeMemberData?.username }}</strong> 吗？
        </p>
        <el-form ref="removeFormRef" :model="removeForm" :rules="removeRules" label-width="100px">
          <el-form-item label="移除原因" prop="reason">
            <el-input
              v-model="removeForm.reason"
              type="textarea"
              :rows="3"
              placeholder="请输入移除原因（可选）"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showRemoveDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmRemove" :loading="removeLoading">
          确认移除
        </el-button>
      </template>
    </el-dialog>

    <!-- 成员详情对话框 -->
    <el-dialog v-model="showMemberDetailDialog" title="成员详情" width="600px">
      <div v-if="currentMember" class="member-detail-content">
        <div class="member-header">
          <el-avatar :src="currentMember.avatar_url" :size="80" />
          <div class="member-basic-info">
            <h3 class="member-name">{{ currentMember.realName || currentMember.username }}</h3>
            <p class="member-username">@{{ currentMember.username }}</p>
            <el-tag :type="currentMember.role === 'admin' ? 'danger' : 'primary'">
              {{ currentMember.role === 'admin' ? '管理员' : '成员' }}
            </el-tag>
          </div>
        </div>

        <el-divider />

        <div class="member-detail-info">
          <div class="info-section">
            <h4>基本信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">学号:</span>
                <span class="value">{{ currentMember.studentId || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="label">专业:</span>
                <span class="value">{{ currentMember.major || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="label">加入时间:</span>
                <span class="value">{{ formatDate(currentMember.joinTime) }}</span>
              </div>
              <div class="info-item">
                <span class="label">状态:</span>
                <span class="value">
                  <el-tag :type="currentMember.status === 'active' ? 'success' : 'info'">
                    {{ currentMember.status === 'active' ? '活跃' : '非活跃' }}
                  </el-tag>
                </span>
              </div>
            </div>
          </div>

          <div class="info-section">
            <h4>联系方式</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">手机:</span>
                <span class="value">{{ currentMember.phone || '未填写' }}</span>
              </div>
              <div class="info-item">
                <span class="label">邮箱:</span>
                <span class="value">{{ currentMember.email || '未填写' }}</span>
              </div>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="member-actions">
          <h4>管理操作</h4>
          <div class="action-buttons">
            <el-button
              v-if="currentMember.role === 'member'"
              type="primary"
              @click="promoteToAdmin(currentMember)"
              :disabled="!canManageRole(currentMember)"
            >
              设为管理员
            </el-button>
            <el-button
              v-if="currentMember.role === 'admin'"
              type="warning"
              @click="demoteToMember(currentMember)"
              :disabled="!canManageRole(currentMember)"
            >
              取消管理员
            </el-button>
            <el-button
              type="danger"
              @click="removeMemberFromDetail(currentMember)"
              :disabled="!canRemoveMember(currentMember)"
            >
              移除成员
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 申请详情对话框 -->
    <el-dialog v-model="showApplicationDetailDialog" title="申请详情" width="1200px">
      <div v-if="currentApplication" class="application-detail-layout">
        <!-- 左侧：申请者信息 -->
        <div class="application-info-section">
          <div class="member-header">
            <el-avatar :src="currentApplication.avatar_url" :size="80" />
            <div class="member-basic-info">
              <h3 class="member-name">{{ currentApplication.realName || currentApplication.username }}</h3>
              <p class="member-username">@{{ currentApplication.username }}</p>
            </div>
          </div>
          <el-divider />
          <div class="member-detail-info">
            <div class="info-section">
              <h4>基本信息</h4>
              <div class="info-grid">
                <div class="info-item"><span class="label">学号:</span><span class="value">{{ currentApplication.studentId || '未填写' }}</span></div>
                <div class="info-item"><span class="label">专业:</span><span class="value">{{ currentApplication.major || '未填写' }}</span></div>
                <div class="info-item"><span class="label">申请时间:</span><span class="value">{{ formatDate(currentApplication.applyTime) }}</span></div>
              </div>
            </div>
            <div class="info-section">
              <h4>联系方式</h4>
              <div class="info-grid">
                <div class="info-item"><span class="label">手机:</span><span class="value">{{ currentApplication.phone || '未填写' }}</span></div>
                <div class="info-item"><span class="label">邮箱:</span><span class="value">{{ currentApplication.email || '未填写' }}</span></div>
              </div>
            </div>
            <div class="info-section">
              <h4>偏好社团类型</h4>
              <div class="tags-container">
                <el-tag
                  v-for="category in currentApplication.interestedCategories"
                  :key="category"
                  type="primary"
                  class="tag-item"
                >
                  {{ category }}
                </el-tag>
                <span v-if="!currentApplication.interestedCategories?.length" class="no-data">未设置</span>
              </div>
            </div>
            <div class="info-section">
              <h4>特质标签</h4>
              <div class="tags-container">
                <el-tag
                  v-for="tag in currentApplication.tags"
                  :key="tag"
                  type="success"
                  class="tag-item"
                >
                  {{ tag }}
                </el-tag>
                <span v-if="!currentApplication.tags?.length" class="no-data">未设置</span>
              </div>
            </div>
            <div class="info-section">
              <h4>申请理由</h4>
              <div class="apply-reason">
                <p>{{ currentApplication.applyReason }}</p>
              </div>
            </div>
          </div>
          <el-divider />
          <div class="member-actions">
            <h4>审核操作</h4>
            <div class="action-buttons">
              <el-button v-if="currentApplication.status === 'pending'" type="success" @click="approveApplicationFromDetail(currentApplication)">同意</el-button>
              <el-button v-if="currentApplication.status === 'pending'" type="danger" @click="rejectApplicationFromDetail(currentApplication)">拒绝</el-button>
            </div>
          </div>
        </div>
        
        <!-- 右侧：AI审核助手 -->
        <div class="ai-screening-section">
          <AIApplicationScreening 
            :application-data="currentApplication"
            :club-name="currentClub?.name || '未知社团'"
            :required-conditions="currentClub?.tags || []"
          />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Search,
  Warning,
  Refresh,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import AIApplicationScreening from '@/components/Chat/AIApplicationScreening.vue'
import {
  getClubMembers,
  getClubApplications,
  reviewApplication,
  removeMember as removeMemberFromClub,
  changeMemberRole,
} from '@/api/club'
import type {
  Club,
  ClubMember,
  ClubApplication,
} from '@/types'

const router = useRouter()
const route = useRoute()
const clubStore = useClubStore()
const authStore = useAuthStore()

// 防抖函数
const debounce = (func: Function, wait: number) => {
  let timeout: number
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

const activeTab = ref('members')
const club = ref<Club | null>(null)

const memberLoading = ref(false)
const members = ref<ClubMember[]>([])
const memberTotal = ref(0)
const memberCurrentPage = ref(1)
const memberPageSize = ref(10)
const memberSearchKeyword = ref('')
const memberRoleFilter = ref('')
const memberStatusFilter = ref('')

const applicationLoading = ref(false)
const applications = ref<ClubApplication[]>([])
const applicationTotal = ref(0)
const applicationCurrentPage = ref(1)
const applicationPageSize = ref(10)
const applicationSearchKeyword = ref('')
const applicationStatusFilter = ref('')

const showRejectDialog = ref(false)
const showRemoveDialog = ref(false)
const showMemberDetailDialog = ref(false)
const showApplicationDetailDialog = ref(false)
const rejectLoading = ref(false)
const removeLoading = ref(false)
const currentApplication = ref<ClubApplication | null>(null)
const removeMemberData = ref<ClubMember | null>(null)
const currentMember = ref<ClubMember | null>(null)

const rejectForm = ref({
  reason: '',
})

const removeForm = ref({
  reason: '',
})

const rejectRules = {
  reason: [{ required: true, message: '请输入拒绝原因', trigger: 'blur' }],
}

const removeRules = {
  reason: [{ required: false }],
}

const currentUserId = computed(() => authStore.user?.id)

const currentClub = computed(() => club.value)

const canManageRole = (member: ClubMember) => {
  return member.userId !== currentUserId.value?.toString()
}

const canRemoveMember = (member: ClubMember) => {
  return member.userId !== currentUserId.value?.toString()
}

const loadClubInfo = async () => {
  const clubId = route.params.id as string
  try {
    console.log('开始加载社团信息，ID:', clubId)
    const clubData = await clubStore.fetchClubDetail(clubId)
    club.value = clubData
    console.log('社团信息加载完成:', clubData)
  } catch (error) {
    console.error('获取社团信息失败:', error)
    ElMessage.error('获取社团信息失败')
  }
}

const loadMembers = async () => {
  if (!club.value) return

  try {
    memberLoading.value = true
    
    // 使用 nextTick 确保 DOM 更新完成
    await nextTick()
    
    const response = await getClubMembers(club.value.id, {
      page: memberCurrentPage.value,
      pageSize: memberPageSize.value,
      role: memberRoleFilter.value,
      status: memberStatusFilter.value,
      keyword: memberSearchKeyword.value,
    })

    if (response.data.code === 200) {
      members.value = response.data.data.list
      memberTotal.value = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '加载成员列表失败')
    }
  } catch (error) {
    console.error('加载成员列表失败:', error)
    ElMessage.error('加载成员列表失败，请重试')
  } finally {
    memberLoading.value = false
  }
}

const loadApplications = async () => {
  if (!club.value) return

  try {
    applicationLoading.value = true
    
    // 使用 nextTick 确保 DOM 更新完成
    await nextTick()
    
    const response = await getClubApplications(club.value.id, {
      page: applicationCurrentPage.value,
      pageSize: applicationPageSize.value,
      status: applicationStatusFilter.value,
      keyword: applicationSearchKeyword.value,
    })

    if (response.data.code === 200) {
      applications.value = response.data.data.list
      applicationTotal.value = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '加载申请列表失败')
    }
  } catch (error) {
    console.error('加载申请列表失败:', error)
    ElMessage.error('加载申请列表失败，请重试')
  } finally {
    applicationLoading.value = false
  }
}

const handleTabChange = () => {
  // 数据已经预加载，切换时不需要重新加载
  // 如果需要刷新数据，可以在这里添加刷新逻辑
}

const handleMemberSearch = debounce(() => {
  memberCurrentPage.value = 1
  loadMembers()
}, 300)

const handleMemberFilter = () => {
  memberCurrentPage.value = 1
  loadMembers()
}

const handleApplicationSearch = debounce(() => {
  applicationCurrentPage.value = 1
  loadApplications()
}, 300)

const handleApplicationFilter = () => {
  applicationCurrentPage.value = 1
  loadApplications()
}

const handleMemberSizeChange = (size: number) => {
  memberPageSize.value = size
  memberCurrentPage.value = 1
  loadMembers()
}

const handleMemberCurrentChange = (page: number) => {
  memberCurrentPage.value = page
  loadMembers()
}

const handleApplicationSizeChange = (size: number) => {
  applicationPageSize.value = size
  applicationCurrentPage.value = 1
  loadApplications()
}

const handleApplicationCurrentChange = (page: number) => {
  applicationCurrentPage.value = page
  loadApplications()
}

const approveApplication = async (application: ClubApplication) => {
  try {
    await ElMessageBox.confirm(
      `确定同意 ${application.realName || application.username} 的加入申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success',
      }
    )

    const response = await reviewApplication(club.value!.id, {
      applicationId: application.id,
      action: 'approve',
    })

    if (response.data.code === 200) {
      ElMessage.success('申请已通过')
      loadApplications()
      loadMembers()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核申请失败:', error)
      ElMessage.error('审核申请失败')
    }
  }
}

const rejectApplication = (application: ClubApplication) => {
  currentApplication.value = application
  showRejectDialog.value = true
}

const confirmReject = async () => {
  if (!currentApplication.value) return

  try {
    rejectLoading.value = true
    const response = await reviewApplication(club.value!.id, {
      applicationId: currentApplication.value.id,
      action: 'reject',
      reason: rejectForm.value.reason,
    })

    if (response.data.code === 200) {
      ElMessage.success('申请已拒绝')
      
      // 立即更新本地数据
      const index = applications.value.findIndex(app => app.id === currentApplication.value!.id)
      if (index !== -1) {
        applications.value[index].status = 'rejected'
        applications.value[index].reviewTime = new Date().toISOString()
        applications.value[index].reviewerId = authStore.user?.id?.toString()
        applications.value[index].reviewerName = authStore.user?.username
        applications.value[index].rejectReason = rejectForm.value.reason
      }
      
      showRejectDialog.value = false
      rejectForm.value.reason = ''
      currentApplication.value = null
    }
  } catch (error) {
    console.error('拒绝申请失败:', error)
    ElMessage.error('拒绝申请失败')
  } finally {
    rejectLoading.value = false
  }
}

const promoteToAdmin = async (member: ClubMember) => {
  try {
    await ElMessageBox.confirm(
      `确定将 ${member.realName || member.username} 设为管理员吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await changeMemberRole(club.value!.id, member.id, 'admin')
    if (response.data.code === 200) {
      ElMessage.success('角色更改成功')
      loadMembers()
      showMemberDetailDialog.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('更改角色失败:', error)
      ElMessage.error('更改角色失败')
    }
  }
}

const demoteToMember = async (member: ClubMember) => {
  try {
    await ElMessageBox.confirm(
      `确定取消 ${member.realName || member.username} 的管理员权限吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const response = await changeMemberRole(club.value!.id, member.id, 'member')
    if (response.data.code === 200) {
      ElMessage.success('角色更改成功')
      loadMembers()
      showMemberDetailDialog.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('更改角色失败:', error)
      ElMessage.error('更改角色失败')
    }
  }
}

const removeMember = (member: ClubMember) => {
  removeMemberData.value = member
  showRemoveDialog.value = true
}

const removeMemberFromDetail = (member: ClubMember) => {
  removeMemberData.value = member
  showRemoveDialog.value = true
  showMemberDetailDialog.value = false
}

const confirmRemove = async () => {
  if (!removeMemberData.value) return

  try {
    removeLoading.value = true
    const response = await removeMemberFromClub(club.value!.id, removeMemberData.value.id, removeForm.value.reason)
    if (response.data.code === 200) {
      ElMessage.success('成员移除成功')
      showRemoveDialog.value = false
      removeForm.value.reason = ''
      removeMemberData.value = null
      loadMembers()
    }
  } catch (error) {
    console.error('移除成员失败:', error)
    ElMessage.error('移除成员失败')
  } finally {
    removeLoading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
  }
  return textMap[status] || status
}

const goBack = () => {
  router.back()
}

const showMemberDetail = (member: ClubMember) => {
  currentMember.value = member
  showMemberDetailDialog.value = true
}

const showApplicationDetail = (application: ClubApplication) => {
  currentApplication.value = application
  showApplicationDetailDialog.value = true
}

const approveApplicationFromDetail = async (application: ClubApplication) => {
  try {
    await ElMessageBox.confirm(
      `确定同意 ${application.realName || application.username} 的加入申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success',
      }
    )

    const response = await reviewApplication(club.value!.id, {
      applicationId: application.id,
      action: 'approve',
    })

    if (response.data.code === 200) {
      ElMessage.success('申请已通过')
      
      // 立即更新本地数据，避免重新加载
      const index = applications.value.findIndex(app => app.id === application.id)
      if (index !== -1) {
        applications.value[index].status = 'approved'
        applications.value[index].reviewTime = new Date().toISOString()
        applications.value[index].reviewerId = authStore.user?.id?.toString()
        applications.value[index].reviewerName = authStore.user?.username
      }
      
      // 关闭详情弹窗
      showApplicationDetailDialog.value = false
      
      // 异步更新成员列表
      setTimeout(() => {
        loadMembers()
      }, 100)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('审核申请失败:', error)
      ElMessage.error('审核申请失败')
    }
  }
}

const rejectApplicationFromDetail = (application: ClubApplication) => {
  currentApplication.value = application
  showRejectDialog.value = true
}

const refreshMembers = () => {
  memberCurrentPage.value = 1
  loadMembers()
}

const refreshApplications = () => {
  applicationCurrentPage.value = 1
  loadApplications()
}

// 页面加载
onMounted(async () => {
  try {
    // 先加载社团信息
    await loadClubInfo()
    
    // 并行加载两个标签页的数据，确保切换时数据已准备好
    const loadPromises = []
    
    // 加载成员数据
    loadPromises.push(
      loadMembers().catch(error => {
        console.error('加载成员数据失败:', error)
      })
    )
    
    // 加载申请数据
    loadPromises.push(
      loadApplications().catch(error => {
        console.error('加载申请数据失败:', error)
      })
    )
    
    // 等待所有数据加载完成
    await Promise.allSettled(loadPromises)
    
  } catch (error) {
    console.error('页面初始化失败:', error)
    ElMessage.error('页面加载失败，请刷新重试')
  }
})
</script>

<style scoped>
.member-management {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-button:hover {
  background-color: #f5f7fa;
  border-color: #c0c4cc;
}

.header-info h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #303133;
}

.header-info p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.management-card {
  min-height: 600px;
}

.tab-content {
  padding: 20px 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.search-section {
  flex: 1;
}

.filter-section {
  display: flex;
  gap: 12px;
}

.member-info-button {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.member-info-button:hover {
  background-color: #f5f7fa;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.member-info-button:active {
  background-color: #e4e7ed;
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.member-name {
  font-weight: 500;
  color: #303133;
}

.member-username {
  font-size: 12px;
  color: #909399;
}

.member-student-id {
  font-size: 12px;
  color: #909399;
}

.member-role {
  margin-left: 8px;
}

.applicant-info-button {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.applicant-info-button:hover {
  background-color: #f5f7fa;
}

.applicant-info-button:active {
  background-color: #e4e7ed;
}

.applicant-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.applicant-name {
  font-weight: 500;
  color: #303133;
}

.applicant-username {
  font-size: 12px;
  color: #909399;
}

.apply-reason-text {
  color: #606266;
  line-height: 1.5;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.apply-reason {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #409eff;
}

.apply-reason p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}

.application-actions {
  display: flex;
  gap: 8px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.remove-dialog-content {
  text-align: center;
  margin-bottom: 20px;
}

.warning-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.remove-dialog-content p {
  margin: 16px 0;
  color: #606266;
}

.remove-dialog-content strong {
  color: #303133;
}

.member-detail-content {
  padding: 20px;
}

.member-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.member-basic-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.member-basic-info h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.member-basic-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.member-detail-info {
  margin-bottom: 20px;
}

.info-section {
  margin-bottom: 16px;
}

.info-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.value {
  color: #303133;
  font-size: 14px;
}

.member-actions {
  margin-top: 20px;
}

.member-actions h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.application-detail-layout {
  display: flex;
  gap: 20px;
  min-height: 600px;
}

.application-info-section {
  flex: 1;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  overflow-y: auto;
}

.application-info-section .member-header {
  margin-bottom: 16px;
}

.application-info-section .member-basic-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.application-info-section .member-basic-info h3 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.application-info-section .member-basic-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.application-info-section .member-detail-info {
  margin-bottom: 20px;
}

.application-info-section .info-section {
  margin-bottom: 16px;
}

.application-info-section .info-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.application-info-section .info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.application-info-section .info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.application-info-section .info-item .label {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.application-info-section .info-item .value {
  color: #303133;
  font-size: 14px;
}

.application-info-section .member-actions {
  margin-top: 20px;
}

.application-info-section .member-actions h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
}

.application-info-section .member-actions .action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.ai-screening-section {
  flex: 1;
  min-height: 600px;
}

.tags-container {
  margin-top: 12px;
  margin-bottom: 12px;
}

.tag-item {
  margin-right: 8px;
  margin-bottom: 8px;
}

.no-data {
  color: #909399;
  font-size: 12px;
}
</style> 