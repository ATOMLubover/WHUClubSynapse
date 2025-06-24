<template>
  <!-- 主内容区 -->
  <div class="user-main">
    <!-- 用户头部信息 -->
    <div class="user-header">
      <div class="user-avatar-section">
        <el-avatar :size="80" :src="userInfo?.avatar || ''" class="user-avatar">
          <el-icon><User /></el-icon>
        </el-avatar>
        <el-button size="small" @click="showAvatarUpload = true">更换头像</el-button>
      </div>

      <div class="user-basic-info">
        <h2 class="user-name">{{ userInfo?.realName || userInfo?.username }}</h2>
        <p class="user-role">
          <el-tag :type="userInfo?.role === 'admin' ? 'danger' : 'primary'">
            {{ getUserRoleText(userInfo?.role) }}
          </el-tag>
        </p>
        <p class="user-college">{{ userInfo?.college }}</p>
        <p class="user-join-time">加入时间：{{ formatDate(userInfo?.createdAt) }}</p>
      </div>

      <div class="user-stats">
        <div class="stat-item">
          <div class="stat-number">{{ userStats.appliedClubs }}</div>
          <div class="stat-label">申请社团</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ userStats.favoriteClubs }}</div>
          <div class="stat-label">收藏社团</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ userStats.joinedClubs }}</div>
          <div class="stat-label">已加入</div>
        </div>
      </div>
    </div>

    <!-- 功能导航 -->
    <div class="user-nav">
      <el-button-group>
        <el-button :type="activeTab === 'info' ? 'primary' : ''" @click="activeTab = 'info'">
          个人信息
        </el-button>
        <el-button
          :type="activeTab === 'security' ? 'primary' : ''"
          @click="activeTab = 'security'"
        >
          安全设置
        </el-button>
        <el-button
          :type="activeTab === 'preferences' ? 'primary' : ''"
          @click="activeTab = 'preferences'"
        >
          偏好设置
        </el-button>
      </el-button-group>
    </div>

    <!-- 内容区域 -->
    <div class="user-content">
      <!-- 个人信息编辑 -->
      <div v-if="activeTab === 'info'" class="content-section">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>个人信息</span>
              <el-button :type="editMode ? 'success' : 'primary'" @click="handleEditToggle">
                {{ editMode ? '保存' : '编辑' }}
              </el-button>
            </div>
          </template>

          <el-form
            ref="userFormRef"
            :model="editableUserInfo"
            :rules="userInfoRules"
            label-width="100px"
            :disabled="!editMode"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="用户名" prop="username">
                  <el-input v-model="editableUserInfo.username" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="真实姓名" prop="realName">
                  <el-input v-model="editableUserInfo.realName" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="学号" prop="studentId">
                  <el-input v-model="editableUserInfo.studentId" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="学院" prop="college">
                  <el-select v-model="editableUserInfo.college" placeholder="请选择学院">
                    <el-option
                      v-for="college in colleges"
                      :key="college"
                      :label="college"
                      :value="college"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="editableUserInfo.email" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="editableUserInfo.phone" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="个人简介" prop="bio">
              <el-input
                v-model="editableUserInfo.bio"
                type="textarea"
                :rows="3"
                placeholder="介绍一下自己吧..."
              />
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 安全设置 -->
      <div v-if="activeTab === 'security'" class="content-section">
        <el-card>
          <template #header>
            <span>安全设置</span>
          </template>

          <div class="security-items">
            <!-- 密码修改项 -->
            <div class="security-item">
              <div class="security-info">
                <h4>登录密码</h4>
                <p>建议定期更换密码以保护账户安全</p>
              </div>
              <div class="security-actions">
                <el-button @click="showPasswordDialog = true">修改密码</el-button>
              </div>
            </div>

            <el-divider />

            <!-- 邮箱验证项 -->
            <div class="security-item">
              <div class="security-info">
                <h4>邮箱验证</h4>
                <p>
                  {{ userInfo?.email }}
                  <el-tag :type="userInfo?.emailVerified ? 'success' : 'warning'" size="small">
                    {{ userInfo?.emailVerified ? '已验证' : '未验证' }}
                  </el-tag>
                </p>
              </div>
              <div class="security-actions">
                <el-button
                  v-if="!userInfo?.emailVerified"
                  @click="sendVerificationEmail"
                  :loading="verificationLoading"
                >
                  发送验证邮件
                </el-button>
                <el-button @click="handleChangeEmail"> 更换邮箱 </el-button>
              </div>
            </div>

            <el-divider />

            <!-- 手机验证项 -->
            <div class="security-item">
              <div class="security-info">
                <h4>手机验证</h4>
                <p>
                  {{ userInfo?.phone || '未绑定' }}
                  <el-tag
                    v-if="userInfo?.phone"
                    :type="userInfo?.phoneVerified ? 'success' : 'warning'"
                    size="small"
                  >
                    {{ userInfo?.phoneVerified ? '已验证' : '未验证' }}
                  </el-tag>
                </p>
              </div>
              <div class="security-actions">
                <el-button v-if="!userInfo?.phone" @click="showPhoneDialog = true">
                  绑定手机号
                </el-button>
                <el-button v-else @click="handleChangePhone"> 更换手机号 </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 偏好设置 -->
      <div v-if="activeTab === 'preferences'" class="content-section">
        <el-card>
          <template #header>
            <span>偏好设置</span>
          </template>

          <el-form label-width="120px">
            <el-form-item label="感兴趣的社团类型">
              <el-checkbox-group v-model="preferences.interestedCategories">
                <el-checkbox label="学术科技">学术科技</el-checkbox>
                <el-checkbox label="文化艺术">文化艺术</el-checkbox>
                <el-checkbox label="体育运动">体育运动</el-checkbox>
                <el-checkbox label="志愿服务">志愿服务</el-checkbox>
                <el-checkbox label="社会实践">社会实践</el-checkbox>
                <el-checkbox label="创新创业">创新创业</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="通知设置">
              <el-switch v-model="preferences.emailNotifications" active-text="邮件通知" />
              <br /><br />
              <el-switch
                v-model="preferences.applicationNotifications"
                active-text="申请状态通知"
              />
              <br /><br />
              <el-switch v-model="preferences.activityNotifications" active-text="活动推送" />
            </el-form-item>

            <el-form-item label="隐私设置">
              <el-switch v-model="preferences.profilePublic" active-text="公开个人资料" />
              <br /><br />
              <el-switch v-model="preferences.showJoinedClubs" active-text="显示已加入社团" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="savePreferences">保存偏好设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="500px">
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handlePasswordChange" :loading="passwordLoading"
          >确定</el-button
        >
      </template>
    </el-dialog>

    <!-- 头像上传对话框 -->
    <el-dialog v-model="showAvatarUpload" title="更换头像" width="400px">
      <el-upload
        class="avatar-uploader"
        :show-file-list="false"
        :before-upload="beforeAvatarUpload"
        :http-request="uploadAvatar"
      >
        <img v-if="uploadedAvatar" :src="uploadedAvatar" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>
      <div class="upload-tips">
        <p>支持 JPG、PNG 格式，文件大小不超过 2MB</p>
      </div>

      <template #footer>
        <el-button @click="showAvatarUpload = false">取消</el-button>
        <el-button type="primary" @click="confirmAvatarUpload" :disabled="!uploadedAvatar"
          >确定</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus } from '@element-plus/icons-vue'
import type { FormInstance, UploadRawFile } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { getCurrentUser, changePassword } from '@/api/auth'
import type { User as UserType } from '@/types'
import UserSidebar from '@/components/User/UserSidebar.vue'

// Stores
const authStore = useAuthStore()

// 响应式数据
const activeTab = ref('info')
const editMode = ref(false)
const showPasswordDialog = ref(false)
const showAvatarUpload = ref(false)
const showPhoneDialog = ref(false)
const verificationLoading = ref(false)
const passwordLoading = ref(false)
const uploadedAvatar = ref('')

// 用户信息
const userInfo = ref<UserType | null>(null)
const editableUserInfo = reactive({
  username: '',
  realName: '',
  studentId: '',
  college: '',
  email: '',
  phone: '',
  bio: '',
})

// 用户统计数据
const userStats = reactive({
  appliedClubs: 0,
  favoriteClubs: 0,
  joinedClubs: 0,
})

// 用户偏好设置
const preferences = reactive({
  interestedCategories: [] as string[],
  emailNotifications: true,
  applicationNotifications: true,
  activityNotifications: false,
  profilePublic: true,
  showJoinedClubs: true,
})

// 密码修改表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// 表单引用
const userFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

// 学院列表
const colleges = [
  '计算机学院',
  '信息管理学院',
  '电子信息学院',
  '遥感信息工程学院',
  '测绘学院',
  '水利水电学院',
  '城市设计学院',
  '土木建筑工程学院',
  '机械学院',
  '动力与机械学院',
  '电气与自动化学院',
  '材料科学与工程学院',
  '化学与化工学院',
  '生命科学学院',
  '物理科学与技术学院',
  '数学与统计学院',
  '资源与环境科学学院',
  '经济与管理学院',
  '社会学院',
  '外国语言文学学院',
  '新闻与传播学院',
  '艺术学院',
  '哲学学院',
  '法学院',
  '政治与公共管理学院',
  '教育科学研究院',
  '体育部',
  '马克思主义学院',
]

// 表单验证规则
const userInfoRules = {
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  phone: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }],
}

const passwordRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 方法
const getUserRoleText = (role?: string) => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    student: '学生',
    teacher: '教师',
  }
  return roleMap[role || 'student'] || '学生'
}

const formatDate = (date?: string) => {
  if (!date) return '未知'
  return new Date(date).toLocaleDateString('zh-CN')
}

const handleEditToggle = async () => {
  if (editMode.value) {
    // 保存模式
    if (!userFormRef.value) return

    try {
      await userFormRef.value.validate()
      // TODO: 调用更新用户信息API
      ElMessage.success('保存成功')
      editMode.value = false

      // 更新userInfo
      Object.assign(userInfo.value!, editableUserInfo)
    } catch (error) {
      ElMessage.error('请检查表单填写')
    }
  } else {
    // 编辑模式
    editMode.value = true
  }
}

const handlePasswordChange = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true

    await changePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword,
    })

    ElMessage.success('密码修改成功')
    showPasswordDialog.value = false

    // 重置表单
    Object.assign(passwordForm, {
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
    })
  } catch (error: any) {
    ElMessage.error(error.message || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

const sendVerificationEmail = async () => {
  try {
    verificationLoading.value = true
    // TODO: 调用发送验证邮件API
    ElMessage.success('验证邮件已发送，请检查邮箱')
  } catch (error: any) {
    ElMessage.error(error.message || '发送失败')
  } finally {
    verificationLoading.value = false
  }
}

const beforeAvatarUpload = (rawFile: UploadRawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png') {
    ElMessage.error('头像图片只能是 JPG/PNG 格式!')
    return false
  }
  if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像图片大小不能超过 2MB!')
    return false
  }
  return true
}

const uploadAvatar = (params: any) => {
  // 创建预览URL
  const file = params.file
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedAvatar.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

const confirmAvatarUpload = () => {
  // TODO: 上传头像到服务器
  userInfo.value!.avatar = uploadedAvatar.value
  showAvatarUpload.value = false
  uploadedAvatar.value = ''
  ElMessage.success('头像更新成功')
}

const savePreferences = () => {
  // TODO: 保存偏好设置到服务器
  ElMessage.success('偏好设置已保存')
}
//更换邮箱手机号

// 更换手机号逻辑
const handleChangePhone = async () => {
  try {
    // 弹出输入框，让用户输入新手机号
    const { value: newPhone } = await ElMessageBox.prompt('请输入新的手机号', '更换手机号', {
      inputType: 'text', // 输入类型设为文本，也可根据需求改 inputType: 'tel'
      inputPlaceholder: '请输入新手机号',
    })
    // 这里可扩展：调用实际的接口，比如 updatePhone(newPhone) 去更新服务端数据
    // 示例仅做提示，实际需结合后端 API
    ElMessage.success(`已更换手机号为：${newPhone}`)

    // 如果需要更新前端 userInfo 展示，可这样写：
    if (userInfo.value) {
      userInfo.value.phone = newPhone
      // 同时更新可编辑对象（如果需要在编辑页同步显示）
      editableUserInfo.phone = newPhone
    }
  } catch (error) {
    // 点击取消会进入 catch，可根据需求处理
    ElMessage.info('已取消更换手机号')
  }
}

// 更换邮箱逻辑
const handleChangeEmail = async () => {
  try {
    // 弹出输入框，让用户输入新邮箱
    const { value: newEmail } = await ElMessageBox.prompt('请输入新的邮箱', '更换邮箱', {
      inputType: 'email', // 输入类型设为 email，会有格式校验
      inputPlaceholder: '请输入新邮箱',
    })
    // 这里可扩展：调用实际的接口，比如 updateEmail(newEmail) 去更新服务端数据
    // 示例仅做提示，实际需结合后端 API
    ElMessage.success(`已更换邮箱为：${newEmail}`)

    // 如果需要更新前端 userInfo 展示，可这样写：
    if (userInfo.value) {
      userInfo.value.email = newEmail
      // 同时更新可编辑对象（如果需要在编辑页同步显示）
      editableUserInfo.email = newEmail
    }
  } catch (error) {
    // 点击取消会进入 catch，可根据需求处理
    ElMessage.info('已取消更换邮箱')
  }
}
// 加载用户数据
const loadUserData = async () => {
  try {
    const response = await getCurrentUser()
    userInfo.value = response.data.data

    // 复制到可编辑对象
    Object.assign(editableUserInfo, {
      username: userInfo.value.username,
      realName: userInfo.value.realName || '',
      studentId: userInfo.value.studentId || '',
      college: userInfo.value.college || '',
      email: userInfo.value.email || '',
      phone: userInfo.value.phone || '',
      bio: userInfo.value.bio || '',
    })

    // TODO: 加载用户统计数据和偏好设置
    userStats.appliedClubs = 5
    userStats.favoriteClubs = 8
    userStats.joinedClubs = 3
  } catch (error: any) {
    ElMessage.error(error.message || '加载用户信息失败')
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-main {
  width: 100%;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 30px;
}

.user-avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  border: 3px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
}

.user-basic-info {
  flex: 1;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.user-role {
  margin: 8px 0;
}

.user-college {
  margin: 4px 0;
  opacity: 0.9;
  font-size: 16px;
}

.user-join-time {
  margin: 4px 0 0 0;
  opacity: 0.8;
  font-size: 14px;
}

.user-stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.user-nav {
  text-align: center;
  margin-bottom: 30px;
}

.content-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* .security-items {
  space-y: 20px;
} */

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.security-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #303133;
}

.security-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.avatar-uploader {
  text-align: center;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 6px;
  object-fit: cover;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.avatar-uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}

.upload-tips {
  text-align: center;
  margin-top: 10px;
}

.upload-tips p {
  margin: 0;
  color: #909399;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-header {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .user-stats {
    gap: 20px;
  }

  .security-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
  }

  .security-actions {
    display: flex;
    gap: 10px;
  }
}
</style>
