<template>
  <div class="user-roles">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色权限管理</span>
          <el-button type="primary" @click="showAddRoleDialog">
            <el-icon><Plus /></el-icon>
            添加角色
          </el-button>
        </div>
      </template>

      <div class="roles-grid">
        <el-card v-for="role in roles" :key="role.id" class="role-card">
          <div class="role-header">
            <h3>{{ role.name }}</h3>
            <div class="role-actions">
              <el-button type="warning" size="small" @click="editRole(role)">编辑</el-button>
              <el-button type="danger" size="small" @click="deleteRole(role)">删除</el-button>
            </div>
          </div>

          <p class="role-description">{{ role.description }}</p>

          <div class="permissions-section">
            <h4>权限列表</h4>
            <div class="permissions-list">
              <el-tag
                v-for="permission in role.permissions"
                :key="permission"
                type="success"
                size="small"
                class="permission-tag"
              >
                {{ getPermissionName(permission) }}
              </el-tag>
            </div>
          </div>

          <div class="role-stats">
            <span>用户数: {{ role.userCount }}</span>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 添加/编辑角色对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="roleForm" :rules="formRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>

        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>

        <el-form-item label="权限设置" prop="permissions">
          <el-checkbox-group v-model="roleForm.permissions">
            <div class="permissions-grid">
              <div v-for="group in permissionGroups" :key="group.name" class="permission-group">
                <h4>{{ group.name }}</h4>
                <el-checkbox
                  v-for="permission in group.permissions"
                  :key="permission.key"
                  :label="permission.key"
                  :value="permission.key"
                >
                  {{ permission.name }}
                </el-checkbox>
              </div>
            </div>
          </el-checkbox-group>
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
import { Plus } from '@element-plus/icons-vue'

// 角色数据
const roles = ref([
  {
    id: '1',
    name: '超级管理员',
    description: '拥有系统所有权限',
    permissions: [
      'user.view',
      'user.create',
      'user.edit',
      'user.delete',
      'club.view',
      'club.create',
      'club.edit',
      'club.delete',
      'system.view',
      'system.edit',
    ],
    userCount: 2,
  },
  {
    id: '2',
    name: '社团管理员',
    description: '管理社团相关功能',
    permissions: [
      'club.view',
      'club.create',
      'club.edit',
      'application.view',
      'application.review',
    ],
    userCount: 15,
  },
  {
    id: '3',
    name: '普通用户',
    description: '基础用户权限',
    permissions: ['club.view', 'application.create'],
    userCount: 1000,
  },
])

// 权限分组
const permissionGroups = ref([
  {
    name: '用户管理',
    permissions: [
      { key: 'user.view', name: '查看用户' },
      { key: 'user.create', name: '创建用户' },
      { key: 'user.edit', name: '编辑用户' },
      { key: 'user.delete', name: '删除用户' },
    ],
  },
  {
    name: '社团管理',
    permissions: [
      { key: 'club.view', name: '查看社团' },
      { key: 'club.create', name: '创建社团' },
      { key: 'club.edit', name: '编辑社团' },
      { key: 'club.delete', name: '删除社团' },
    ],
  },
  {
    name: '申请管理',
    permissions: [
      { key: 'application.view', name: '查看申请' },
      { key: 'application.create', name: '创建申请' },
      { key: 'application.review', name: '审核申请' },
    ],
  },
  {
    name: '系统管理',
    permissions: [
      { key: 'system.view', name: '查看系统设置' },
      { key: 'system.edit', name: '修改系统设置' },
    ],
  },
])

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('添加角色')
const submitLoading = ref(false)
const formRef = ref()

// 角色表单
const roleForm = reactive({
  id: '',
  name: '',
  description: '',
  permissions: [] as string[],
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入角色描述', trigger: 'blur' }],
  permissions: [{ required: true, message: '请选择至少一个权限', trigger: 'change' }],
}

// 获取权限名称
const getPermissionName = (key: string) => {
  for (const group of permissionGroups.value) {
    const permission = group.permissions.find((p) => p.key === key)
    if (permission) {
      return permission.name
    }
  }
  return key
}

// 显示添加角色对话框
const showAddRoleDialog = () => {
  dialogTitle.value = '添加角色'
  dialogVisible.value = true
}

// 编辑角色
const editRole = (role: any) => {
  dialogTitle.value = '编辑角色'
  Object.assign(roleForm, role)
  dialogVisible.value = true
}

// 删除角色
const deleteRole = async (role: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色 "${role.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    ElMessage.success('删除成功')
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

    console.log('提交角色数据:', roleForm)
    await new Promise((resolve) => setTimeout(resolve, 1000))

    ElMessage.success(dialogTitle.value === '添加角色' ? '添加成功' : '更新成功')
    dialogVisible.value = false
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(roleForm, {
    id: '',
    name: '',
    description: '',
    permissions: [],
  })
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

onMounted(() => {
  console.log('角色权限管理页面初始化')
})
</script>

<style scoped>
.user-roles {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.role-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.role-header h3 {
  margin: 0;
  color: #303133;
}

.role-actions {
  display: flex;
  gap: 8px;
}

.role-description {
  color: #606266;
  margin-bottom: 16px;
  line-height: 1.5;
}

.permissions-section h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
}

.permission-tag {
  margin: 0;
}

.role-stats {
  color: #909399;
  font-size: 14px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.permission-group {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
}

.permission-group h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.permission-group .el-checkbox {
  display: block;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .roles-grid {
    grid-template-columns: 1fr;
  }

  .permissions-grid {
    grid-template-columns: 1fr;
  }

  .role-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .role-actions {
    justify-content: center;
  }
}
</style>
