<template>
  <div class="user-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <div class="search-bar">
        <div class="search-left">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用户名、真实姓名、学号..."
            clearable
            style="width: 300px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select
            v-model="searchForm.role"
            placeholder="用户角色"
            clearable
            style="width: 120px"
          >
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>

          <el-select
            v-model="searchForm.status"
            placeholder="用户状态"
            clearable
            style="width: 120px"
          >
            <el-option label="全部" value="" />
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>

          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>

          <el-button @click="resetSearch">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>

        <div class="search-right">
          <el-button type="success" @click="showAddDialog">
            <el-icon><Plus /></el-icon>
            添加用户
          </el-button>

          <el-button type="warning" @click="exportUsers">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 用户表格 -->
    <el-card class="table-card">
      <el-table
        :data="users"
        v-loading="loading"
        style="width: 100%"
        row-key="id"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column prop="avatar_url" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar_url" :size="40">
              {{ row.username.charAt(0).toUpperCase() }}
            </el-avatar>
          </template>
        </el-table-column>

        <el-table-column prop="username" label="用户名" width="120" />

        <el-table-column prop="realName" label="真实姓名" width="100" />

        <el-table-column prop="studentId" label="学号" width="120" />

        <el-table-column prop="email" label="邮箱" width="180" />

        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <!-- <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag> -->
            <el-tag type="success">正常</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="lastLogin" label="最后登录" width="180">
          <template #default="{ row }">
            {{ formatDate(row.last_active) }}
          </template>
        </el-table-column>

        <el-table-column prop="createdAt" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showUserDetail(row)"> 详情 </el-button>
            <el-button type="warning" size="small" @click="editUser(row)"> 编辑 </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pageData.currentPage"
          v-model:page-size="pageData.pageSize"
          :total="pageData.total"
          layout="total, sizes, prev, pager, next, jumper"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="showUserDetailDialog"
      title="用户详情"
      width="700px"
      class="user-detail-dialog"
    >
      <div class="user-detail-container">
        <!-- 用户基本信息卡片 -->
        <div class="user-basic-info">
          <div class="user-avatar-section">
            <el-avatar :src="userDetail?.avatar_url" :size="80" class="user-avatar">
              {{ userDetail?.username?.charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="user-status">
              <el-tag :type="userDetail?.status === 'active' ? 'success' : 'danger'" size="small">
                {{ userDetail?.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </div>
          </div>

          <div class="user-main-info">
            <h3 class="user-name">{{ userDetail?.realName || userDetail?.username }}</h3>
            <p class="user-username">@{{ userDetail?.username }}</p>
            <div class="user-role">
              <el-tag :type="userDetail?.role === 'admin' ? 'danger' : 'primary'" size="small">
                {{ userDetail?.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 详细信息 -->
        <div class="user-detail-sections">
          <!-- 基本信息 -->
          <div class="detail-section">
            <h4 class="section-title">
              <el-icon><User /></el-icon>
              基本信息
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">用户ID</span>
                <span class="info-value">{{ userDetail?.user_id }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">真实姓名</span>
                <span class="info-value">{{ userDetail?.realName || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">学号</span>
                <span class="info-value">{{ userDetail?.studentId || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ userDetail?.email || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">手机号</span>
                <span class="info-value">{{ userDetail?.phone || '未设置' }}</span>
              </div>
            </div>
          </div>

          <!-- 时间信息 -->
          <div class="detail-section">
            <h4 class="section-title">
              <el-icon><Clock /></el-icon>
              时间信息
            </h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ formatDate(userDetail?.createdAt!) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">最后登录</span>
                <span class="info-value">{{ formatDate(userDetail?.last_active!) }}</span>
              </div>
            </div>
          </div>

          <!-- 个人资料 -->
          <div class="detail-section">
            <h4 class="section-title">
              <el-icon><Document /></el-icon>
              个人资料
            </h4>
            <div class="info-content">
              <div class="info-item full-width">
                <span class="info-label">个性签名</span>
                <span class="info-value">{{ userDetail?.bio || '这个人很懒，什么都没写~' }}</span>
              </div>

              <div class="info-item full-width">
                <span class="info-label">个人标签</span>
                <div class="tags-container">
                  <el-tag v-for="tag in userDetail?.tags" :key="tag" size="small" class="user-tag">
                    {{ tag }}
                  </el-tag>
                  <span v-if="!userDetail?.tags || userDetail.tags.length === 0" class="no-tags">
                    暂无标签
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editDialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="editFormRef" :model="editUserForm" :rules="editFormRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editUserForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="editUserForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="学号" prop="studentId">
          <el-input v-model="editUserForm.studentId" placeholder="请输入学号" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editUserForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editUserForm.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="editUserForm.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="editUserForm.status" placeholder="请选择状态">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUser" :loading="submitLoading"> 确定 </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Plus, Download } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types'
import { getUserById } from '@/api/auth'

const authStore = useAuthStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  role: '',
  status: '',
})

// 分页数据
const pageData = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})

// 表格数据
const users = ref<User[]>([])
const loading = ref(false)
const selectedUsers = ref<User[]>([])

// 对话框相关
const editDialogVisible = ref(false)
const editDialogTitle = ref('编辑用户')
const submitLoading = ref(false)
const editFormRef = ref()
const showUserDetailDialog = ref(false)
const userDetail = ref<User | null>(null)

// 用户表单
const editUserForm = ref<Partial<User>>({})

// 表单验证规则
const editFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  studentId: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
}

// 搜索
const handleSearch = () => {
  console.log('搜索用户:', searchForm)
  loadUsers()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    role: '',
    status: '',
  })
  loadUsers()
}

// 获取用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    const offset = (pageData.currentPage - 1) * pageData.pageSize
    const usersData = await authStore.fetchAllUsers({
      offset: offset,
      num: pageData.pageSize,
    })
    users.value = usersData
    // 模拟总数，实际应该从API返回

    pageData.total = 100
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
const showAddDialog = () => {
  editDialogTitle.value = '添加用户'
  editDialogVisible.value = true
}

// 编辑用户
const editUser = (user: any) => {
  editDialogTitle.value = '编辑用户'
  Object.assign(editUserForm, user)
  editDialogVisible.value = true
}

// 查看用户详情
const showUserDetail = (user: any) => {
  showUserDetailDialog.value = true
  userDetail.value = user
}

// 提交表单
const saveUser = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()
    submitLoading.value = true

    const userId = editUserForm.value.user_id || editUserForm.value.id
    if (!userId) {
      ElMessage.error('用户ID不能为空')
      return
    }

    await authStore.updateUser(userId, editUserForm.value)
    ElMessage.success(editDialogTitle.value === '添加用户' ? '添加成功' : '更新成功')
    editDialogVisible.value = false
    loadUsers()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(editUserForm, {
    id: '',
    username: '',
    realName: '',
    studentId: '',
    email: '',
    phone: '',
    role: 'user',
    status: 'active',
  })
  if (editFormRef.value) {
    editFormRef.value.clearValidate()
  }
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedUsers.value = selection
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageData.pageSize = size
  loadUsers()
}

const handleCurrentChange = (page: number) => {
  pageData.currentPage = page
  loadUsers()
}

// 导出用户数据
const exportUsers = () => {
  ElMessage.info('导出用户数据功能')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-card {
  border-radius: 8px;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.search-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.search-right {
  display: flex;
  gap: 8px;
}

.table-card {
  border-radius: 8px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-left .el-input,
  .search-left .el-select {
    width: 100% !important;
  }

  .search-right {
    justify-content: stretch;
  }

  .search-right .el-button {
    flex: 1;
  }
}

.user-detail-dialog .el-dialog__body {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 32px 24px 24px 24px;
}

.user-detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.user-basic-info {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-bottom: 12px;
}

.user-avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.user-avatar {
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.12);
  border: 2px solid #fff;
}

.user-status {
  margin-top: 4px;
}

.user-main-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
}

.user-username {
  color: #909399;
  font-size: 15px;
  margin-bottom: 4px;
}

.user-role {
  margin-top: 4px;
}

.user-detail-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  background: rgba(246, 248, 255, 0.7);
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06);
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #6366f1;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 24px;
}

.info-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.info-label {
  color: #909399;
  font-size: 14px;
  min-width: 70px;
}

.info-value {
  color: #303133;
  font-size: 15px;
  font-weight: 500;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.full-width {
  grid-column: 1 / -1;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-tag {
  background: linear-gradient(90deg, #6e8efb 0%, #a777e3 100%);
  color: #fff;
  border: none;
}

.no-tags {
  color: #bbb;
  font-size: 13px;
  margin-left: 8px;
}
</style>
