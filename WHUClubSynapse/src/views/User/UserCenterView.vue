<template>
  <!-- 主内容区 -->
  <div class="user-main">
    <!-- 用户信息卡片 -->
    <el-card class="profile-card" shadow="hover">
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar-container" @click="showAvatarUpload = true">
            <el-avatar :size="100" :src="userInfo?.avatar_url || ''" class="user-avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="avatar-overlay">
              <el-icon><Plus /></el-icon>
            </div>
          </div>
          <div class="user-info">
            <h2 class="user-name">{{ userInfo?.realName || userInfo?.username }}</h2>
            <div class="user-meta">
              <el-tag
                :type="userInfo?.role === 'admin' ? 'danger' : 'primary'"
                effect="light"
                class="role-tag"
              >
                {{ getUserRoleText(userInfo?.role) }}
              </el-tag>
              <span class="user-college">{{ userInfo?.major }}</span>
            </div>
            <p class="user-join-time">
              <el-icon><Calendar /></el-icon>
              加入时间：{{ formatDate(userInfo?.createdAt) }}
            </p>
          </div>
        </div>

        <div class="stats-section">
          <div
            class="stat-card clickable"
            v-for="(stat, index) in statsData"
            :key="index"
            @click="handleStatClick(index)"
          >
            <div class="stat-icon">
              <el-icon :color="stat.color">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 导航标签页 -->
    <el-card class="nav-card" shadow="never">
      <el-tabs v-model="activeTab" class="user-tabs">
        <el-tab-pane label="个人信息" name="info">
          <template #label>
            <div class="tab-label">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </div>
          </template>
        </el-tab-pane>
        <el-tab-pane label="安全设置" name="security">
          <template #label>
            <div class="tab-label">
              <el-icon><Lock /></el-icon>
              <span>安全设置</span>
            </div>
          </template>
        </el-tab-pane>
        <el-tab-pane label="偏好设置" name="preferences">
          <template #label>
            <div class="tab-label">
              <el-icon><Setting /></el-icon>
              <span>偏好设置</span>
            </div>
          </template>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- 个人信息编辑 -->
      <div v-show="activeTab === 'info'" class="content-section">
        <el-card class="form-card" shadow="hover">
          <template #header>
            <div class="section-header">
              <div class="header-info">
                <el-icon class="header-icon"><User /></el-icon>
                <div>
                  <h3>个人信息</h3>
                  <p>管理你的基本信息</p>
                </div>
              </div>
              <el-button
                :type="editMode ? 'success' : 'primary'"
                :icon="editMode ? 'Check' : 'Edit'"
                @click="handleEditToggle"
              >
                {{ editMode ? '保存' : '编辑' }}
              </el-button>
            </div>
          </template>

          <el-form
            ref="userFormRef"
            :model="editableUserInfo"
            :rules="userInfoRules"
            label-width="0"
            :disabled="!editMode"
            class="modern-form"
          >
            <div class="form-grid">
              <div class="form-item">
                <label class="form-label">用户名</label>
                <el-input
                  v-model="editableUserInfo.username"
                  disabled
                  class="form-input"
                  placeholder="用户名"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </div>

              <div class="form-item">
                <label class="form-label">真实姓名</label>
                <el-input
                  v-model="editableUserInfo.realName"
                  class="form-input"
                  placeholder="请输入真实姓名"
                >
                  <template #prefix>
                    <el-icon><Avatar /></el-icon>
                  </template>
                </el-input>
              </div>

              <div class="form-item">
                <label class="form-label">学号</label>
                <el-input
                  v-model="editableUserInfo.studentId"
                  class="form-input"
                  placeholder="请输入学号"
                >
                  <template #prefix>
                    <el-icon><CreditCard /></el-icon>
                  </template>
                </el-input>
              </div>

              <div class="form-item">
                <label class="form-label">学院</label>
                <el-select
                  v-model="editableUserInfo.college"
                  placeholder="请选择学院"
                  class="form-input"
                >
                  <el-option
                    v-for="college in colleges"
                    :key="college"
                    :label="college"
                    :value="college"
                  />
                </el-select>
              </div>
            </div>

            <div class="form-item full-width">
              <label class="form-label">个人简介</label>
              <el-input
                v-model="editableUserInfo.bio"
                type="textarea"
                :rows="4"
                placeholder="介绍一下自己吧..."
                class="form-textarea"
              />
            </div>
          </el-form>
        </el-card>
      </div>

      <!-- 安全设置 -->
      <div v-show="activeTab === 'security'" class="content-section">
        <el-card class="form-card" shadow="hover">
          <template #header>
            <div class="section-header">
              <div class="header-info">
                <el-icon class="header-icon"><Lock /></el-icon>
                <div>
                  <h3>安全设置</h3>
                  <p>保护你的账户安全</p>
                </div>
              </div>
            </div>
          </template>

          <div class="security-content">
            <div class="security-card">
              <div class="security-icon">
                <el-icon color="#409eff"><Lock /></el-icon>
              </div>
              <div class="security-info">
                <h4>登录密码</h4>
                <p>建议定期更换密码以保护账户安全</p>
              </div>
              <div class="security-actions">
                <el-button type="primary" plain @click="showPasswordDialog = true">
                  修改密码
                </el-button>
              </div>
            </div>

            <div class="security-card">
              <div class="security-icon">
                <el-icon color="#67c23a"><Message /></el-icon>
              </div>
              <div class="security-info">
                <h4>邮箱验证</h4>
                <div class="info-row">
                  <span>{{ userInfo?.email }}</span>
                  <el-tag
                    :type="userInfo?.emailVerified ? 'success' : 'warning'"
                    size="small"
                    effect="light"
                  >
                    {{ userInfo?.emailVerified ? '已验证' : '未验证' }}
                  </el-tag>
                </div>
              </div>
              <div class="security-actions">
                <el-button
                  v-if="!userInfo?.emailVerified"
                  type="success"
                  plain
                  @click="sendVerificationEmail"
                  :loading="verificationLoading"
                  size="small"
                >
                  发送验证邮件
                </el-button>
                <el-button type="primary" plain size="small" @click="handleChangeEmail">
                  更换邮箱
                </el-button>
              </div>
            </div>

            <div class="security-card">
              <div class="security-icon">
                <el-icon color="#f56c6c"><Phone /></el-icon>
              </div>
              <div class="security-info">
                <h4>手机验证</h4>
                <div class="info-row">
                  <span>{{ userInfo?.phone || '未绑定' }}</span>
                  <el-tag
                    v-if="userInfo?.phone"
                    :type="userInfo?.phoneVerified ? 'success' : 'warning'"
                    size="small"
                    effect="light"
                  >
                    {{ userInfo?.phoneVerified ? '已验证' : '未验证' }}
                  </el-tag>
                </div>
              </div>
              <div class="security-actions">
                <el-button
                  v-if="!userInfo?.phone"
                  type="warning"
                  plain
                  size="small"
                  @click="showPhoneDialog = true"
                >
                  绑定手机号
                </el-button>
                <el-button v-else type="primary" plain size="small" @click="handleChangePhone">
                  更换手机号
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 偏好设置 -->
      <div v-show="activeTab === 'preferences'" class="content-section">
        <el-card class="form-card" shadow="hover">
          <template #header>
            <div class="section-header">
              <div class="header-info">
                <el-icon class="header-icon"><Setting /></el-icon>
                <div>
                  <h3>偏好设置</h3>
                  <p>个性化你的使用体验</p>
                </div>
              </div>
              <el-button type="primary" @click="savePreferences" :loading="preferencesLoading">
                保存设置
              </el-button>
            </div>
          </template>

          <div class="preferences-content">
            <div class="preference-section">
              <h4 class="preference-title">
                <el-icon><Star /></el-icon>
                感兴趣的社团类型
              </h4>
              <el-checkbox-group v-model="preferences.interestedCategories" class="checkbox-grid">
                <el-checkbox label="学术科技" class="checkbox-item">学术科技</el-checkbox>
                <el-checkbox label="文艺体育" class="checkbox-item">文艺体育</el-checkbox>
                <el-checkbox label="志愿服务" class="checkbox-item">志愿服务</el-checkbox>
                <el-checkbox label="创新创业" class="checkbox-item">创新创业</el-checkbox>
                <el-checkbox label="其他" class="checkbox-item">其他</el-checkbox>
              </el-checkbox-group>
            </div>

            <div class="preference-section">
              <h4 class="preference-title">
                <el-icon><Bell /></el-icon>
                通知设置
              </h4>
              <div class="switch-grid">
                <div class="switch-item">
                  <div class="switch-info">
                    <span class="switch-label">邮件通知</span>
                    <span class="switch-desc">接收重要信息的邮件提醒</span>
                  </div>
                  <el-switch v-model="preferences.emailNotifications" />
                </div>
                <div class="switch-item">
                  <div class="switch-info">
                    <span class="switch-label">申请状态通知</span>
                    <span class="switch-desc">社团申请状态变化时通知</span>
                  </div>
                  <el-switch v-model="preferences.applicationNotifications" />
                </div>
                <div class="switch-item">
                  <div class="switch-info">
                    <span class="switch-label">活动推送</span>
                    <span class="switch-desc">接收感兴趣的活动推荐</span>
                  </div>
                  <el-switch v-model="preferences.activityNotifications" />
                </div>
              </div>
            </div>

            <div class="preference-section">
              <h4 class="preference-title">
                <el-icon><View /></el-icon>
                隐私设置
              </h4>
              <div class="switch-grid">
                <div class="switch-item">
                  <div class="switch-info">
                    <span class="switch-label">公开个人资料</span>
                    <span class="switch-desc">允许其他用户查看你的基本信息</span>
                  </div>
                  <el-switch v-model="preferences.profilePublic" />
                </div>
                <div class="switch-item">
                  <div class="switch-info">
                    <span class="switch-label">显示已加入社团</span>
                    <span class="switch-desc">在个人资料中显示你加入的社团</span>
                  </div>
                  <el-switch v-model="preferences.showJoinedClubs" />
                </div>
              </div>
            </div>

            <div class="preference-section">
              <h4 class="preference-title">
                <el-icon><Price-tag /></el-icon>
                特质标签
              </h4>
              <el-select
                v-model="preferences.tags"
                multiple
                filterable
                allow-create
                default-first-option
                :reserve-keyword="false"
                :filter-method="filterTag"
                :collapse-tags="false"
                placeholder="添加个人特质标签，让别人更了解你"
                class="tag-selector"
              >
                <el-option v-for="tag in filteredTags" :key="tag" :label="tag" :value="tag" />
              </el-select>
              <div class="tag-hint">
                <el-icon><Info-filled /></el-icon>
                <span>标签限制4字以内，最多可添加8个标签</span>
              </div>
            </div>
          </div>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Plus,
  Calendar,
  Lock,
  Setting,
  Edit,
  Check,
  Avatar,
  CreditCard,
  Star,
  Trophy,
  Collection,
  Message,
  Phone,
  Bell,
  View,
  PriceTag,
  InfoFilled,
} from '@element-plus/icons-vue'
import type { FormInstance, UploadRawFile } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { getCurrentUser, changePassword } from '@/api/auth'
import type { User as UserType, UserStats, UserPreferences, ClubCategory } from '@/types'
import UserSidebar from '@/components/User/UserSidebar.vue'
import { allUserTags } from '@/utils/mockData'
import { useRouter } from 'vue-router'

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
const preferencesLoading = ref(false)
const uploadedAvatar = ref('')
const tagLoading = ref(false)
const tagOptions = ref<string[]>([])
const tagInput = ref('')

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

// 移除独立的userStats对象，现在直接使用userInfo.stats

// 用户偏好设置
const preferences = reactive<UserPreferences>({
  interestedCategories: [] as ClubCategory[],
  emailNotifications: true,
  applicationNotifications: true,
  activityNotifications: false,
  profilePublic: true,
  showJoinedClubs: true,
  tags: [],
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
  // 注意：根据接口文档，后端暂时没有提供修改密码接口
  ElMessage.warning('修改密码功能暂未开放，请联系管理员')
  showPasswordDialog.value = false
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
  if (userInfo.value) {
    userInfo.value.avatar_url = uploadedAvatar.value
  }
  showAvatarUpload.value = false
  uploadedAvatar.value = ''
  ElMessage.success('头像更新成功')
}

const savePreferences = async () => {
  // 注意：根据接口文档，后端暂时没有提供更新偏好设置接口
  ElMessage.warning('偏好设置功能暂未开放，请联系管理员')
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
    // 使用 authStore 中的用户信息，而不是调用已删除的 getCurrentUser API
    const currentUser = authStore.user
    if (!currentUser) {
      // 如果没有用户信息，尝试重新获取
      await authStore.fetchUserInfo()
      userInfo.value = authStore.user
    } else {
      userInfo.value = currentUser
    }

    console.log(userInfo.value)

    if (!userInfo.value) {
      throw new Error('无法获取用户信息')
    }

    // 复制到可编辑对象
    Object.assign(editableUserInfo, {
      username: userInfo.value.username,
      realName: userInfo.value.realName || '',
      studentId: userInfo.value.studentId || '',
      college: userInfo.value.major || '', // 注意：使用 major 而不是 college
      email: userInfo.value.email || '',
      phone: userInfo.value.phone || '',
      bio: userInfo.value.bio || '',
    })

    // 加载用户偏好设置（如果存在）
    if (userInfo.value.preferences) {
      console.log(userInfo.value.preferences)
      Object.assign(preferences, userInfo.value.preferences)
      console.log(preferences)
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载用户信息失败')
  }
}

const searchTags = async (query: string) => {
  if (query.length < 2) {
    tagOptions.value = []
    return
  }

  try {
    tagLoading.value = true
    tagOptions.value = allUserTags.filter((tag) => tag.toLowerCase().includes(query.toLowerCase()))
  } catch (error: any) {
    ElMessage.error(error.message || '搜索标签失败')
  } finally {
    tagLoading.value = false
  }
}

const filteredTags = computed(() => {
  const input = tagInput.value.trim()
  const selected = preferences.tags || []
  let base = allUserTags.filter((tag) => !selected.includes(tag))
  if (input) {
    base = base.filter((tag) => tag.includes(input))
  }
  if (
    input &&
    input.length > 0 &&
    input.length <= 4 &&
    !allUserTags.includes(input) &&
    !selected.includes(input)
  ) {
    return [input, ...base]
  }
  return base
})

// 统计数据
const statsData = computed(() => [
  {
    label: '申请社团',
    value: userInfo.value?.stats?.appliedClubs || 0,
    icon: 'Star',
    color: '#409eff',
  },
  {
    label: '收藏社团',
    value: userInfo.value?.stats?.favoriteClubs || 0,
    icon: 'Collection',
    color: '#f56c6c',
  },
  {
    label: '已加入',
    value: userInfo.value?.stats?.joinedClubs || 0,
    icon: 'Trophy',
    color: '#67c23a',
  },
])

const filterTag = (query: string) => {
  tagInput.value = query
}

const router = useRouter()

const handleStatClick = (index: number) => {
  if (index === 0) {
    router.push('/user/applications')
  } else if (index === 1) {
    router.push('/api/club/my_favorites')
  } else if (index === 2) {
    router.push('/user/clubs/joined')
  }
}

onMounted(() => {
  loadUserData()
})
</script>

<style scoped>
.user-main {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #f8fafc;
  min-height: 100vh;
}

/* 个人资料卡片 */
.profile-card {
  margin-bottom: 24px;
  border-radius: 16px;
  border: none;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.profile-card :deep(.el-card__body) {
  padding: 0;
}

.profile-header {
  padding: 32px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-container {
  position: relative;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.avatar-container:hover {
  transform: scale(1.05);
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.user-avatar {
  border: 4px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  color: white;
  font-size: 24px;
}

.user-info {
  flex: 1;
}

.user-name {
  margin: 0 0 12px 0;
  font-size: 32px;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.role-tag {
  font-weight: 500;
}

.user-college {
  font-size: 16px;
  opacity: 0.9;
}

.user-join-time {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  opacity: 0.8;
  font-size: 14px;
}

.stats-section {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 140px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  font-weight: 500;
}

/* 导航卡片 */
.nav-card {
  margin-bottom: 24px;
  border-radius: 16px;
  border: none;
}

.nav-card :deep(.el-card__body) {
  padding: 0;
}

.user-tabs :deep(.el-tabs__header) {
  margin: 0;
  background: white;
  border-radius: 16px 16px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
}

.user-tabs :deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
  justify-content: space-between;
}

.user-tabs :deep(.el-tabs__item) {
  flex: 1 1 0;
  text-align: center;
  padding: 20px 0;
  font-weight: 500;
  font-size: 18px;
  border-radius: 16px;
  margin: 0 16px;
  background: linear-gradient(135deg, #f8fafc 60%, #e3e6f3 100%);
  transition: box-shadow 0.2s, background 0.2s, color 0.2s, transform 0.2s;
  box-shadow: 0 2px 8px rgba(64,158,255,0.04);
  cursor: pointer;
}

.user-tabs :deep(.el-tabs__item.is-active) {
  background: linear-gradient(135deg, #667eea 60%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 4px 16px rgba(64,158,255,0.18);
  transform: scale(1.08);
}

.user-tabs :deep(.el-tabs__item):hover {
  background: linear-gradient(135deg, #e0e7ff 60%, #c7d2fe 100%);
  color: #5a67d8;
  box-shadow: 0 4px 16px rgba(64,158,255,0.12);
  transform: scale(1.04);
}

.user-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 内容区域 */
.content-area {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-section {
  margin-bottom: 24px;
}

.form-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.header-info h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a202c;
}

.header-info p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

/* 现代表单样式 */
.modern-form {
  padding: 32px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-item.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
  margin-bottom: 8px;
}

.form-input {
  border-radius: 12px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-textarea :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.form-textarea :deep(.el-textarea__inner:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.form-textarea :deep(.el-textarea__inner:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 安全设置样式 */
.security-content {
  padding: 32px;
}

.security-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.security-card:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.security-card:last-child {
  margin-bottom: 0;
}

.security-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.security-info {
  flex: 1;
}

.security-info h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.security-info p {
  margin: 0;
  color: #718096;
  font-size: 14px;
  line-height: 1.5;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.info-row span {
  color: #4a5568;
  font-weight: 500;
}

.security-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 偏好设置样式 */
.preferences-content {
  padding: 32px;
}

.preference-section {
  margin-bottom: 32px;
  padding: 24px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.preference-section:last-child {
  margin-bottom: 0;
}

.preference-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
}

.preference-title .el-icon {
  color: #667eea;
  font-size: 20px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.checkbox-item :deep(.el-checkbox__label) {
  font-weight: 500;
  color: #4a5568;
}

.checkbox-item :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #667eea;
  border-color: #667eea;
}

.switch-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.switch-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.switch-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.switch-info {
  flex: 1;
}

.switch-label {
  display: block;
  font-weight: 600;
  color: #1a202c;
  font-size: 16px;
  margin-bottom: 4px;
}

.switch-desc {
  display: block;
  color: #718096;
  font-size: 14px;
}

.switch-item .el-switch {
  margin-left: 16px;
}

.switch-item .el-switch :deep(.el-switch__core) {
  border-color: #667eea;
}

.switch-item .el-switch.is-checked :deep(.el-switch__core) {
  background-color: #667eea;
}

.tag-selector {
  width: 100%;
  margin-bottom: 12px;
}

.tag-selector :deep(.el-select__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  min-height: 80px;
  padding: 12px;
}

.tag-selector :deep(.el-select__wrapper:hover) {
  border-color: #667eea;
}

.tag-selector :deep(.el-select__wrapper.is-focused) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.tag-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #718096;
  font-size: 13px;
  padding: 8px 0;
}

.tag-hint .el-icon {
  color: #a0aec0;
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
@media (max-width: 1024px) {
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 32px;
  }

  .avatar-section {
    flex-direction: column;
    text-align: center;
  }

  .stats-section {
    justify-content: center;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .user-main {
    padding: 16px;
  }

  .profile-header {
    padding: 24px;
  }

  .user-name {
    font-size: 24px;
  }

  .stats-section {
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .stat-card {
    min-width: 200px;
  }

  .security-card {
    flex-direction: column;
    align-items: flex-start;
    text-align: center;
    gap: 16px;
  }

  .security-actions {
    width: 100%;
    justify-content: center;
  }

  .switch-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .switch-item .el-switch {
    margin-left: 0;
    align-self: flex-end;
  }

  .checkbox-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-info {
    width: 100%;
  }

  .modern-form,
  .security-content,
  .preferences-content {
    padding: 20px;
  }

  .preference-section {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .user-main {
    padding: 12px;
  }

  .profile-header {
    padding: 20px;
  }

  .user-name {
    font-size: 20px;
  }

  .user-tabs :deep(.el-tabs__nav-wrap) {
    padding: 0 16px;
  }

  .tab-label span {
    display: none;
  }

  .modern-form,
  .security-content,
  .preferences-content {
    padding: 16px;
  }
}

.stat-card.clickable {
  cursor: pointer;
  transition: box-shadow 0.2s, background 0.2s;
}
.stat-card.clickable:hover {
  background: rgba(255,255,255,0.3);
  box-shadow: 0 4px 16px rgba(64,158,255,0.18);
}
</style>
