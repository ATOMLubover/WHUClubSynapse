<template>
  <div class="member-management">
    <div class="page-header">
      <div class="header-content">
        <div class="back-button" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="header-info">
          <h1>{{ club?.club_name }} - 成员管理</h1>
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
                <el-select
                  v-model="memberRoleFilter"
                  placeholder="角色筛选"
                  clearable
                  @change="handleMemberFilter"
                >
                  <el-option label="社长" value="leader" />
                  <el-option label="管理员" value="admin" />
                  <el-option label="普通成员" value="member" />
                </el-select>
                <el-button
                  @click="refreshMembers"
                  :loading="memberLoading"
                  type="primary"
                  size="small"
                >
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>

            <!-- 成员卡片网格 -->
            <div v-loading="memberLoading" class="members-grid">
              <div v-if="!members.length && !memberLoading" class="empty-state">
                <el-empty description="暂无成员" :image-size="120" />
              </div>

              <div
                v-for="member in members"
                :key="member.member_id"
                class="member-card"
                @click="showMemberDetail(member)"
              >
                <div class="member-card-inner">
                  <div class="member-card-header">
                    <div class="avatar-container">
                      <el-avatar :src="member.avatar_url" :size="64" class="member-avatar">
                        <el-icon size="32"><User /></el-icon>
                      </el-avatar>
                      <div class="online-indicator" v-if="member.status === 'active'"></div>
                    </div>
                    <div class="member-role-badge">
                      <el-tag
                        :type="member.role_in_club === 'leader' ? 'danger' : member.role_in_club === 'admin' ? 'warning' : 'primary'"
                        size="small"
                        effect="dark"
                        round
                      >
                        {{ member.role_in_club === 'leader' ? '社长' : member.role_in_club === 'admin' ? '管理员' : '成员' }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="member-card-body">
                    <h4 class="member-name">{{ member.realName || member.username }}</h4>
                    <p class="member-username">@{{ member.username }}</p>
                    
                    <div class="member-info-list">
                      <div class="info-item" v-if="member.studentId">
                        <el-icon class="info-icon"><CreditCard /></el-icon>
                        <span class="info-text">{{ member.studentId }}</span>
                      </div>
                      
                      <div class="info-item" v-if="member.major">
                        <el-icon class="info-icon"><School /></el-icon>
                        <span class="info-text">{{ member.major }}</span>
                      </div>
                      
                      <div class="info-item">
                        <el-icon class="info-icon"><Calendar /></el-icon>
                        <span class="info-text">{{ formatDate(member.joined_at) }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="member-card-footer">
                    <div class="member-status">
                      <el-tag 
                        :type="member.status === 'active' ? 'success' : 'info'" 
                        size="small"
                        effect="light"
                        round
                      >
                        {{ member.status === 'active' ? '活跃' : '非活跃' }}
                      </el-tag>
                    </div>
                    <div class="member-actions">
                      <el-button size="small" type="primary" link>
                        <el-icon><View /></el-icon>
                        详情
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

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
                <el-select
                  v-model="applicationStatusFilter"
                  placeholder="状态筛选"
                  clearable
                  @change="handleApplicationFilter"
                >
                  <el-option label="待审核" value="pending" />
                  <el-option label="已通过" value="approved" />
                  <el-option label="已拒绝" value="rejected" />
                </el-select>
                <el-button
                  @click="refreshApplications"
                  :loading="applicationLoading"
                  type="primary"
                  size="small"
                >
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </div>

            <!-- 申请卡片网格 -->
            <div v-loading="applicationLoading" class="applications-grid">
              <div v-if="!applications.length && !applicationLoading" class="empty-state">
                <el-empty description="暂无申请" :image-size="120" />
              </div>

              <div
                v-for="application in applications"
                :key="application.appli_id"
                class="application-card"
                :class="{ 'pending': application.status === 'pending', 'approved': application.status === 'approved', 'rejected': application.status === 'rejected' }"
                @click="showApplicationDetail(application)"
              >
                <div class="application-card-inner">
                  <div class="application-card-header">
                    <div class="avatar-container">
                      <el-avatar
                        :src="application.avatar_url || ''"
                        :size="50"
                        class="applicant-avatar"
                      >
                        <el-icon size="24"><User /></el-icon>
                      </el-avatar>
                      <div class="application-priority" v-if="application.status === 'pending'">
                        <el-icon color="#F56C6C"><Bell /></el-icon>
                      </div>
                    </div>
                    <div class="application-status-badge">
                      <el-tag 
                        :type="getStatusType(application.status)" 
                        size="small" 
                        effect="light"
                        round
                      >
                        {{ getStatusText(application.status) }}
                      </el-tag>
                    </div>
                  </div>

                  <div class="application-card-body">
                    <div class="applicant-header">
                      <h4 class="applicant-name">{{ application.realName || application.username || '申请人' }}</h4>
                      <p class="application-id">#{{ application.appli_id }} · {{ formatDate(application.applied_at) }}</p>
                    </div>

                    <div class="application-info-list">
                      <div class="info-item" v-if="application.studentId">
                        <el-icon class="info-icon"><CreditCard /></el-icon>
                        <span class="info-text">{{ application.studentId }}</span>
                      </div>
                      <div class="info-item" v-if="application.major">
                        <el-icon class="info-icon"><School /></el-icon>
                        <span class="info-text">{{ application.major }}</span>
                      </div>
                      <div class="info-item" v-if="application.phone">
                        <el-icon class="info-icon"><Phone /></el-icon>
                        <span class="info-text">{{ application.phone }}</span>
                      </div>
                    </div>

                    <div class="application-reason" v-if="application.reason">
                      <div class="reason-label">
                        <el-icon><Message /></el-icon>
                        申请理由
                      </div>
                      <p class="reason-text">{{ application.reason }}</p>
                    </div>

                    <div v-if="application.reject_reason" class="reject-reason">
                      <div class="reason-label">
                        <el-icon color="#F56C6C"><Warning /></el-icon>
                        拒绝原因
                      </div>
                      <p class="reject-text">{{ application.reject_reason }}</p>
                    </div>
                  </div>

                  <div class="application-card-footer">
                    <div v-if="application.status === 'pending'" class="application-actions">
                      <el-button
                        size="small"
                        type="success"
                        @click.stop="approveApplication(application)"
                        round
                      >
                        <el-icon><CircleCheck /></el-icon>
                        同意
                      </el-button>
                      <el-button
                        size="small"
                        type="danger"
                        @click.stop="rejectApplication(application)"
                        round
                      >
                        <el-icon><CircleClose /></el-icon>
                        拒绝
                      </el-button>
                    </div>

                    <div v-else class="application-actions">
                      <el-button size="small" type="primary" link>
                        <el-icon><View /></el-icon>
                        详情
                      </el-button>
                      <div class="reviewed-info" v-if="application.reviewed_at">
                        <el-icon><Clock /></el-icon>
                        <span>{{ formatDate(application.reviewed_at) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

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
          确定要移除成员
          <strong>{{ removeMemberData?.realName || removeMemberData?.username }}</strong> 吗？
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
            <el-tag :type="currentMember.role_in_club === 'leader' ? 'danger' : currentMember.role_in_club === 'admin' ? 'warning' : 'primary'">
              {{ currentMember.role_in_club === 'leader' ? '社长' : currentMember.role_in_club === 'admin' ? '管理员' : '成员' }}
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
                <span class="value">{{ formatDate(currentMember.joined_at) }}</span>
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
              v-if="currentMember.role_in_club === 'member'"
              type="primary"
              @click="promoteToAdmin(currentMember)"
              :disabled="!canManageRole(currentMember)"
            >
              设为管理员
            </el-button>
            <el-button
              v-if="currentMember.role_in_club === 'admin'"
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
              <h3 class="member-name">
                {{ currentApplication.realName || currentApplication.username }}
              </h3>
              <p class="member-username">@{{ currentApplication.username }}</p>
            </div>
          </div>
          <el-divider />
          <div class="member-detail-info">
            <div class="info-section">
              <h4>基本信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">学号:</span
                  ><span class="value">{{ currentApplication.studentId || '未填写' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">专业:</span
                  ><span class="value">{{ currentApplication.major || '未填写' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">申请时间:</span
                  ><span class="value">{{ formatDate(currentApplication.applied_at) }}</span>
                </div>
              </div>
            </div>
            <div class="info-section">
              <h4>联系方式</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">手机:</span
                  ><span class="value">{{ currentApplication.phone || '未填写' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">邮箱:</span
                  ><span class="value">{{ currentApplication.email || '未填写' }}</span>
                </div>
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
                <span v-if="!currentApplication.interestedCategories?.length" class="no-data"
                  >未设置</span
                >
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
                <p>{{ currentApplication.reason }}</p>
              </div>
            </div>
          </div>
          <el-divider />
          <div class="member-actions">
            <h4>审核操作</h4>
            <div class="action-buttons">
              <el-button
                v-if="currentApplication.status === 'pending'"
                type="success"
                @click="approveApplicationFromDetail(currentApplication)"
                >同意</el-button
              >
              <el-button
                v-if="currentApplication.status === 'pending'"
                type="danger"
                @click="rejectApplicationFromDetail(currentApplication)"
                >拒绝</el-button
              >
            </div>
          </div>
        </div>

        <!-- 右侧：AI审核助手 -->
        <div class="ai-screening-section">
          <AIApplicationScreening
            :application-data="currentApplication"
            :club-name="currentClub?.club_name || '未知社团'"
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
  User,
  Calendar,
  Phone,
  Location,
  View,
  Message,
  Clock,
  CircleCheck,
  CircleClose,
  CreditCard,
  School,
  Bell,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { useAuthStore } from '@/stores/auth'
import AIApplicationScreening from '@/components/Chat/AIApplicationScreening.vue'
import {
  getClubMembers,
  getClubApplications,
  getClubJoinApplications,
  reviewApplication,
  reviewJoinApplication,
  removeMember as removeMemberFromClub,
  changeMemberRole,
} from '@/api/club'
import type { Club, ClubMember, ClubApplication } from '@/types'

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
  return member.user_id !== currentUserId.value?.toString()
}

const canRemoveMember = (member: ClubMember) => {
  return member.user_id !== currentUserId.value?.toString()
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

    const response = await getClubMembers(club.value.club_id, {
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

    // 使用新的API获取社团加入申请列表
    const response = await getClubJoinApplications(club.value.club_id, {
      page: applicationCurrentPage.value,
      pageSize: applicationPageSize.value,
      status: applicationStatusFilter.value,
      keyword: applicationSearchKeyword.value,
    })

    applications.value = response.list
    applicationTotal.value = response.total
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
      `确定同意申请人的加入申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success',
      },
    )

    const response = await reviewJoinApplication(application.appli_id, {
      result: 'approve'
    })

    if (response.data.code === 200) {
      ElMessage.success('申请已通过')
      
      // 立即更新本地数据
      const index = applications.value.findIndex(
        (app) => app.appli_id === application.appli_id,
      )
      if (index !== -1) {
        applications.value[index].status = 'approved'
        applications.value[index].reviewed_at = new Date().toISOString()
        applications.value[index].reviewerId = authStore.user?.id?.toString()
        applications.value[index].reviewerName = authStore.user?.username
      }
      
      loadMembers()
    } else {
      ElMessage.error(response.data.message || '审核申请失败')
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
    const response = await reviewJoinApplication(currentApplication.value.appli_id, {
      result: 'reject',
      reason: rejectForm.value.reason,
    })

    if (response.data.code === 200) {
      ElMessage.success('申请已拒绝')

      // 立即更新本地数据
      const index = applications.value.findIndex(
        (app) => app.appli_id === currentApplication.value!.appli_id,
      )
      if (index !== -1) {
        applications.value[index].status = 'rejected'
        applications.value[index].reviewed_at = new Date().toISOString()
        applications.value[index].reviewerId = authStore.user?.id?.toString()
        applications.value[index].reviewerName = authStore.user?.username
        applications.value[index].reject_reason = rejectForm.value.reason
      }

      showRejectDialog.value = false
      rejectForm.value.reason = ''
      currentApplication.value = null
    } else {
      ElMessage.error(response.data.message || '拒绝申请失败')
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
      },
    )

    const response = await changeMemberRole(club.value!.club_id, member.member_id, 'admin')
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
      },
    )

    const response = await changeMemberRole(club.value!.club_id, member.member_id, 'member')
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
    const response = await removeMemberFromClub(
      club.value!.club_id,
      removeMemberData.value.member_id,
      removeForm.value.reason,
    )
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
      `确定同意申请人的加入申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'success',
      },
    )

    const response = await reviewJoinApplication(application.appli_id, {
      result: 'approve'
    })

    if (response.data.code === 200) {
      ElMessage.success('申请已通过')

      // 立即更新本地数据，避免重新加载
      const index = applications.value.findIndex((app) => app.appli_id === application.appli_id)
      if (index !== -1) {
        applications.value[index].status = 'approved'
        applications.value[index].reviewed_at = new Date().toISOString()
        applications.value[index].reviewerId = authStore.user?.id?.toString()
        applications.value[index].reviewerName = authStore.user?.username
      }

      // 关闭详情弹窗
      showApplicationDetailDialog.value = false

      // 异步更新成员列表
      setTimeout(() => {
        loadMembers()
      }, 100)
    } else {
      ElMessage.error(response.data.message || '审核申请失败')
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
      loadMembers().catch((error) => {
        console.error('加载成员数据失败:', error)
      }),
    )

    // 加载申请数据
    loadPromises.push(
      loadApplications().catch((error) => {
        console.error('加载申请数据失败:', error)
      }),
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
  padding: 20px;
  max-width: 1800px;
  margin: 0 auto;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.page-header {
  margin-bottom: 32px;
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
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
  padding: 12px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  border: none;
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.header-info h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #2c3e50;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 16px;
}

.management-card {
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: none;
  overflow: hidden;
  background: white;
  min-height: 600px;
}

.tab-content {
  padding: 24px;
  max-width: 100%;
  width: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  border: 1px solid #e9ecef;
  gap: 20px;
}

.search-section {
  flex: 1;
}

.filter-section {
  display: flex;
  gap: 16px;
}

/* 成员网格布局 */
.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 32px;
  margin-bottom: 32px;
}

/* 大屏幕优化 */
@media (min-width: 1400px) {
  .members-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 36px;
  }
}

@media (min-width: 1800px) {
  .members-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 40px;
  }
}

.member-card {
  background: white;
  border: 2px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  position: relative;
}

.member-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.member-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.member-card:hover::before {
  opacity: 1;
}

.member-card-inner {
  padding: 24px;
}

.member-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.avatar-container {
  position: relative;
}

.member-avatar {
  border: 4px solid #f8f9fa;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.member-card:hover .member-avatar {
  border-color: #667eea;
  transform: scale(1.05);
}

.online-indicator {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: #52c41a;
  border: 3px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(82, 196, 26, 0.3);
}

.member-role-badge {
  margin-top: 4px;
}

.member-card-body {
  margin-bottom: 20px;
}

.member-name {
  margin: 0 0 6px 0;
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.3;
}

.member-username {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.member-info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.info-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.info-icon {
  color: #667eea;
  font-size: 16px;
  min-width: 16px;
}

.info-text {
  color: #495057;
  font-size: 14px;
  font-weight: 500;
}

.member-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #f1f3f4;
}

/* 申请网格布局 */
.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
  max-width: none;
}

.application-card {
  background: white;
  border: 2px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.4s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  position: relative;
}

.application-card.pending {
  border-left: 4px solid #f39c12;
}

.application-card.approved {
  border-left: 4px solid #27ae60;
}

.application-card.rejected {
  border-left: 4px solid #e74c3c;
}

.application-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.application-card.pending:hover {
  border-color: #f39c12;
  box-shadow: 0 12px 40px rgba(243, 156, 18, 0.2);
}

.application-card.approved:hover {
  border-color: #27ae60;
  box-shadow: 0 12px 40px rgba(39, 174, 96, 0.2);
}

.application-card.rejected:hover {
  border-color: #e74c3c;
  box-shadow: 0 12px 40px rgba(231, 76, 60, 0.2);
}

.application-card-inner {
  padding: 16px;
}

.application-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.application-priority {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(245, 108, 108, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.applicant-avatar {
  border: 3px solid #f8f9fa;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.application-card:hover .applicant-avatar {
  transform: scale(1.05);
}

.application-status-badge {
  margin-top: 4px;
}

.application-card-body {
  margin-bottom: 16px;
}

.applicant-header {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f3f4;
}

.applicant-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.3;
}

.application-id {
  margin: 0;
  font-size: 13px;
  color: #7f8c8d;
  font-weight: 500;
}

.application-reason {
  margin-bottom: 12px;
  padding: 10px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.reason-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.reason-text {
  margin: 0;
  color: #495057;
  line-height: 1.6;
  font-size: 14px;
}

.application-info-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.reject-reason {
  margin-bottom: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #fef2f2 0%, #fde8e8 100%);
  border-radius: 12px;
  border-left: 4px solid #f56c6c;
}

.reject-text {
  margin: 0;
  color: #dc2626;
  line-height: 1.6;
  font-size: 14px;
  font-weight: 500;
}

.application-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid #f1f3f4;
}

.application-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.reviewed-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #7f8c8d;
  padding: 4px 8px;
  background: #f8f9fa;
  border-radius: 6px;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 16px;
  border: 2px dashed #dee2e6;
}

.pagination-section {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 16px;
}

.member-info-button {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: white;
  border: 2px solid #f1f3f4;
}

.member-info-button:hover {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.member-info-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.member-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.member-student-id {
  font-size: 13px;
  color: #7f8c8d;
  font-weight: 500;
}

.member-role {
  margin-left: 8px;
}

.applicant-info-button {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: white;
  border: 2px solid #f1f3f4;
}

.applicant-info-button:hover {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.applicant-info-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.applicant-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.applicant-username {
  font-size: 13px;
  color: #7f8c8d;
  font-weight: 500;
}

.apply-reason-text {
  color: #495057;
  line-height: 1.6;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.apply-reason {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.apply-reason p {
  margin: 0;
  color: #495057;
  line-height: 1.6;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 900px) {
  .members-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .toolbar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-section,
  .filter-section {
    justify-content: center;
  }
}

@media (max-width: 600px) {
  .applications-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .member-management {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .member-card-inner,
  .application-card-inner {
    padding: 16px;
  }
  
  .member-card:hover,
  .application-card:hover {
    transform: translateY(-4px);
  }
}

@media (max-width: 480px) {
  .member-management {
    padding: 12px;
  }
  
  .page-header {
    padding: 16px;
  }
  
  .header-info h1 {
    font-size: 24px;
  }
  
  .toolbar {
    padding: 16px;
  }
  
  .members-grid,
  .applications-grid {
    gap: 12px;
  }
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
