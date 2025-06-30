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
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="lastLogin" label="最后登录" width="180">
          <template #default="{ row }">
            {{ formatDate(row.lastLogin) }}
          </template>
        </el-table-column>

        <el-table-column prop="createdAt" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="showUserDetail(row)"> 详情 </el-button>
            <el-button type="warning" size="small" @click="editUser(row)"> 编辑 </el-button>
            <el-button
              :type="row.status === 'active' ? 'danger' : 'success'"
              size="small"
              @click="toggleUserStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
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

    <!-- 添加/编辑用户对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="userForm" :rules="formRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="userForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="学号" prop="studentId">
          <el-input v-model="userForm.studentId" placeholder="请输入学号" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" type="email" />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-select v-model="userForm.status" placeholder="请选择状态">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading"> 确定 </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Plus, Download } from '@element-plus/icons-vue'

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
const users = ref([
  {
    id: '1',
    username: 'admin',
    realName: '系统管理员',
    studentId: '2020001001',
    email: 'admin@whu.edu.cn',
    phone: '13800138000',
    role: 'admin',
    status: 'active',
    avatar_url: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    lastLogin: '2024-12-20T10:30:00Z',
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    username: 'user001',
    realName: '张三',
    studentId: '2021001001',
    email: 'zhangsan@whu.edu.cn',
    phone: '13800138001',
    role: 'user',
    status: 'active',
    avatar_url: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
    lastLogin: '2024-12-19T15:20:00Z',
    createdAt: '2024-09-01T00:00:00Z',
  },
])

const loading = ref(false)
const selectedUsers = ref<any[]>([])

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('添加用户')
const submitLoading = ref(false)
const formRef = ref()

// 用户表单
const userForm = reactive({
  id: '',
  username: '',
  realName: '',
  studentId: '',
  email: '',
  phone: '',
  role: 'user',
  status: 'active',
})

// 表单验证规则
const formRules = {
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
  fetchUsers()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    role: '',
    status: '',
  })
  fetchUsers()
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    // 这里应该调用API
    console.log('获取用户列表')
    await new Promise((resolve) => setTimeout(resolve, 1000))
    pageData.total = 100 // 模拟总数
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加用户'
  dialogVisible.value = true
}

// 编辑用户
const editUser = (user: any) => {
  dialogTitle.value = '编辑用户'
  Object.assign(userForm, user)
  dialogVisible.value = true
}

// 查看用户详情
const showUserDetail = (user: any) => {
  ElMessage.info(`查看用户详情: ${user.realName}`)
}

// 切换用户状态
const toggleUserStatus = async (user: any) => {
  const action = user.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${user.realName}" 吗？`, '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    user.status = user.status === 'active' ? 'disabled' : 'active'
    ElMessage.success(`${action}成功`)
  } catch {
    // 用户取消操作
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitLoading.value = true

    // 这里应该调用API
    console.log('提交用户数据:', userForm)
    await new Promise((resolve) => setTimeout(resolve, 1000))

    ElMessage.success(dialogTitle.value === '添加用户' ? '添加成功' : '更新成功')
    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(userForm, {
    id: '',
    username: '',
    realName: '',
    studentId: '',
    email: '',
    phone: '',
    role: 'user',
    status: 'active',
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedUsers.value = selection
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageData.pageSize = size
  fetchUsers()
}

const handleCurrentChange = (page: number) => {
  pageData.currentPage = page
  fetchUsers()
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
  fetchUsers()
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
</style>
