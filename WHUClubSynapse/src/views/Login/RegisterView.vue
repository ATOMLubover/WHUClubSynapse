<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>加入 WHU社团联盟</h2>
        <p>发现你的兴趣，找到志同道合的伙伴</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        size="large"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="registerForm.realName" placeholder="请输入真实姓名" clearable />
        </el-form-item>

        <el-form-item label="学号" prop="studentId">
          <el-input v-model="registerForm.studentId" placeholder="请输入学号" clearable />
        </el-form-item>

        <el-form-item label="学院" prop="major">
          <el-select v-model="registerForm.major" placeholder="请选择学院" style="width: 100%">
            <el-option
              v-for="college in colleges"
              :key="college"
              :label="college"
              :value="college"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱地址"
            :prefix-icon="Message"
            clearable
          />
        </el-form-item>

        <el-form-item label="验证码" prop="vrfcode">
          <div class="verify-code-group">
            <el-input
              v-model="registerForm.vrfcode"
              placeholder="请输入4位数字或字母验证码"
              :prefix-icon="Key"
              clearable
              maxlength="4"
            />
            <el-button
              type="primary"
              :loading="sendingCode"
              :disabled="!canSendCode"
              @click="sendVerifyCode"
              class="send-code-btn"
            >
              {{ codeButtonText }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="agreeTerms">
            我已阅读并同意
            <el-link type="primary" @click="showTerms">《服务条款》</el-link>
            和
            <el-link type="primary" @click="showPrivacy">《隐私政策》</el-link>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="authStore.loading"
            :disabled="!agreeTerms"
            @click="handleRegister"
            class="register-btn"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-footer">
        <span>已有账号？</span>
        <el-link type="primary" @click="goToLogin">立即登录</el-link>
      </div>
    </div>

    <!-- 服务条款对话框 -->
    <el-dialog v-model="termsVisible" title="服务条款" width="600px" :before-close="handleClose">
      <div class="terms-content">
        <h4>1. 服务概述</h4>
        <p>WHU社团联盟系统为武汉大学学生提供社团信息浏览、申请和管理服务。</p>

        <h4>2. 用户责任</h4>
        <p>用户应确保注册信息真实有效，不得冒用他人身份或提供虚假信息。</p>

        <h4>3. 隐私保护</h4>
        <p>我们承诺保护用户隐私，不会泄露用户个人信息给第三方。</p>

        <h4>4. 服务变更</h4>
        <p>我们保留随时修改或终止服务的权利，但会提前通知用户。</p>
      </div>
      <template #footer>
        <el-button @click="termsVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 隐私政策对话框 -->
    <el-dialog v-model="privacyVisible" title="隐私政策" width="600px" :before-close="handleClose">
      <div class="privacy-content">
        <h4>1. 信息收集</h4>
        <p>我们仅收集必要的用户信息，包括用户名、邮箱等基本信息。</p>

        <h4>2. 信息使用</h4>
        <p>收集的信息仅用于提供社团服务，不会用于其他商业用途。</p>

        <h4>3. 信息保护</h4>
        <p>我们采用安全技术措施保护用户信息不被泄露、篡改或损毁。</p>

        <h4>4. 用户权利</h4>
        <p>用户有权查看、修改或删除自己的个人信息。</p>
      </div>
      <template #footer>
        <el-button @click="privacyVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message, Key } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import * as authApi from '@/api/auth'
import type { RegisterRequest } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref<FormInstance>()
const agreeTerms = ref(false)
const termsVisible = ref(false)
const privacyVisible = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
const timer = ref<number | null>(null)

// 学院列表
const colleges = ref([
  '计算机学院',
  '数学与统计学院',
  '物理科学与技术学院',
  '化学与分子科学学院',
  '生命科学学院',
  '资源与环境科学学院',
  '水利水电学院',
  '电气与自动化学院',
  '城市设计学院',
  '土木建筑工程学院',
  '机械与制造工程学院',
  '动力与机械学院',
  '遥感信息工程学院',
  '国际软件学院',
  '印刷与包装系',
  '经济与管理学院',
  '法学院',
  '文学院',
  '新闻与传播学院',
  '外国语言文学学院',
  '历史学院',
  '哲学学院',
  '艺术学院',
  '政治与公共管理学院',
  '教育科学研究院',
  '社会学院',
  '信息管理学院',
  '国学院',
  '马克思主义学院',
  '体育部',
])

// 注册表单
const registerForm = reactive<RegisterRequest & { confirmPassword: string }>({
  username: '',
  email: '',
  password: '',
  vrfcode: '',
  confirmPassword: '',
  realName: '',
  studentId: '',
  major: '',
  phone: '',
})

// 计算属性
const canSendCode = computed(() => {
  return (
    registerForm.email &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email) &&
    countdown.value === 0
  )
})

const codeButtonText = computed(() => {
  return countdown.value > 0 ? `重新发送(${countdown.value}s)` : '发送验证码'
})

// 确认密码验证
const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则 - 根据接口文档简化
const registerRules: FormRules<RegisterRequest & { confirmPassword: string }> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  vrfcode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]{4}$/, message: '验证码必须是4位数字或字母', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码必须包含字母和数字', trigger: 'blur' },
  ],
  confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
}

// 发送验证码
const sendVerifyCode = async () => {
  if (!registerForm.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }

  try {
    sendingCode.value = true
    const message = await authApi.sendVerifyEmail({ email: registerForm.email })
    ElMessage.success(message)

    // 开始倒计时
    countdown.value = 60
    timer.value = window.setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer.value!)
        timer.value = null
      }
    }, 1000)
  } catch (error: any) {
    ElMessage.error(error.message || '发送验证码失败')
  } finally {
    sendingCode.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()

    if (!agreeTerms.value) {
      ElMessage.warning('请先同意服务条款和隐私政策')
      return
    }

    const { confirmPassword, ...registerData } = registerForm
    console.log(registerData)
    const result = await authStore.register(registerData)

    ElMessage.success(`注册成功！用户ID: ${result.user_id}`)

    // 注册成功后跳转到登录页面
    router.push('/login')
  } catch (error: any) {
    ElMessage.error(error.message || '注册失败')
    console.error('注册失败:', error)
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 显示服务条款
const showTerms = () => {
  termsVisible.value = true
}

// 显示隐私政策
const showPrivacy = () => {
  privacyVisible.value = true
}

// 关闭对话框
const handleClose = (done: () => void) => {
  done()
}

// 组件销毁时清理定时器
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
  width: 500px;
  max-width: 100%;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.register-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.register-form {
  margin-bottom: 24px;
}

.verify-code-group {
  display: flex;
  gap: 12px;
}

.verify-code-group .el-input {
  flex: 1;
}

.send-code-btn {
  white-space: nowrap;
  min-width: 120px;
}

.register-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

.register-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.register-footer .el-link {
  margin-left: 8px;
}

.terms-content,
.privacy-content {
  line-height: 1.6;
}

.terms-content h4,
.privacy-content h4 {
  margin: 20px 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.terms-content p,
.privacy-content p {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 600px) {
  .register-box {
    width: 100%;
    padding: 30px 20px;
  }

  .register-form :deep(.el-form-item__label) {
    width: 70px !important;
  }

  .verify-code-group {
    flex-direction: column;
  }

  .send-code-btn {
    min-width: auto;
  }
}
</style>
