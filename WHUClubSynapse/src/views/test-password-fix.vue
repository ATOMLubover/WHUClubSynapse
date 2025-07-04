<template>
  <div class="test-page">
    <div class="container">
      <h1>密码修复测试页面</h1>
      
      <div class="test-section">
        <h2>问题说明</h2>
        <p>之前的问题：个人信息修改后用户无法登录，因为密码被意外修改</p>
        <p>修复方案：在prepareUserForBackend函数中，密码字段传递空字符串("")，让后端知道不修改密码</p>
      </div>

      <div class="test-section">
        <h2>当前用户信息</h2>
        <div v-if="authStore.user" class="user-info">
          <p><strong>用户ID:</strong> {{ authStore.user.user_id }}</p>
          <p><strong>用户名:</strong> {{ authStore.user.username }}</p>
          <p><strong>邮箱:</strong> {{ authStore.user.email }}</p>
          <p><strong>真实姓名:</strong> {{ authStore.user.realName || '未设置' }}</p>
          <p><strong>学号:</strong> {{ authStore.user.studentId || '未设置' }}</p>
          <p><strong>专业:</strong> {{ authStore.user.major || '未设置' }}</p>
          <p><strong>手机号:</strong> {{ authStore.user.phone || '未设置' }}</p>
        </div>
        <div v-else>
          <p>用户未登录</p>
        </div>
      </div>

      <div class="test-section">
        <h2>修改个人信息测试</h2>
        <el-form :model="testForm" label-width="100px" class="test-form">
          <el-form-item label="真实姓名">
            <el-input v-model="testForm.realName" placeholder="请输入真实姓名" />
          </el-form-item>
          <el-form-item label="学号">
            <el-input v-model="testForm.studentId" placeholder="请输入学号" />
          </el-form-item>
          <el-form-item label="专业">
            <el-input v-model="testForm.major" placeholder="请输入专业" />
          </el-form-item>
          <el-form-item label="手机号">
            <el-input v-model="testForm.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item label="个人简介">
            <el-input 
              v-model="testForm.bio" 
              type="textarea" 
              :rows="3"
              placeholder="请输入个人简介" 
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="testUpdate" :loading="loading">
              测试更新信息
            </el-button>
            <el-button @click="resetForm">重置表单</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="test-section">
        <h2>发送到后端的数据预览</h2>
        <div class="data-preview">
          <h3>修复前的数据结构（有问题）:</h3>
          <pre class="code-block error">{{ oldDataStructure }}</pre>
          
          <h3>修复后的数据结构（正确）:</h3>
          <pre class="code-block success">{{ newDataStructure }}</pre>
          
          <div class="explanation">
            <h4>关键修复点：</h4>
            <ul>
              <li>✅ password字段明确设置为空字符串 ""</li>
              <li>✅ 只包含必要的基础字段</li>
              <li>✅ 扩展信息通过extension字段传递</li>
              <li>✅ 不会意外传递敏感信息</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="test-section">
        <h2>登录测试</h2>
        <p>修改信息后，请使用以下方式测试登录是否正常：</p>
        <ol>
          <li>点击上方"测试更新信息"按钮</li>
          <li>等待更新成功提示</li>
          <li>点击下方"退出登录"按钮</li>
          <li>重新登录验证密码是否正常</li>
        </ol>
        
        <div class="login-test-actions">
          <el-button @click="logout" type="warning">退出登录</el-button>
          <el-button @click="goToLogin" type="primary">前往登录页</el-button>
        </div>
      </div>

      <div v-if="updateResult" class="test-section">
        <h2>更新结果</h2>
        <div class="result-display">
          <pre>{{ updateResult }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { prepareUserForBackend } from '@/utils/userExtension'
import type { User } from '@/types'

const authStore = useAuthStore()
const router = useRouter()

const loading = ref(false)
const updateResult = ref('')

const testForm = ref({
  realName: '',
  studentId: '',
  major: '',
  phone: '',
  bio: ''
})

// 模拟修复前的错误数据结构
const oldDataStructure = computed(() => {
  return JSON.stringify({
    user_id: 123,
    username: "testuser",
    email: "test@example.com",
    password: "encrypted_password_hash", // ❌ 问题：包含了密码
    role: "student",
    avatar_url: "/avatars/123.jpg",
    realName: "张三",
    studentId: "2021001",
    // ... 其他所有字段都被包含
    extension: '{"realName":"张三","studentId":"2021001"}'
  }, null, 2)
})

// 修复后的正确数据结构
const newDataStructure = computed(() => {
  return JSON.stringify({
    user_id: 123,
    username: "testuser", 
    email: "test@example.com",
    password: "", // ✅ 修复：密码字段为空字符串
    role: "student",
    avatar_url: "/avatars/123.jpg",
    extension: '{"realName":"张三","studentId":"2021001","major":"计算机科学","phone":"13800138000","bio":"测试简介"}'
  }, null, 2)
})

// 初始化表单
const initForm = () => {
  if (authStore.user) {
    testForm.value = {
      realName: authStore.user.realName || '',
      studentId: authStore.user.studentId || '',
      major: authStore.user.major || '',
      phone: authStore.user.phone || '',
      bio: authStore.user.bio || ''
    }
  }
}

// 重置表单
const resetForm = () => {
  initForm()
}

// 测试更新
const testUpdate = async () => {
  if (!authStore.user) {
    ElMessage.error('请先登录')
    return
  }

  try {
    loading.value = true
    updateResult.value = ''
    
    const updateData: Partial<User> = {
      realName: testForm.value.realName,
      studentId: testForm.value.studentId,
      major: testForm.value.major,
      phone: testForm.value.phone,
      bio: testForm.value.bio
    }
    
    console.log('准备更新的数据:', updateData)
    
    // 显示将要发送到后端的数据
    const currentUser = { ...authStore.user, ...updateData }
    const backendData = prepareUserForBackend(currentUser)
    
    updateResult.value = `发送到后端的数据:\n${JSON.stringify(backendData, null, 2)}`
    
    await authStore.updateUserInfo(updateData)
    ElMessage.success('用户信息更新成功！密码未被修改。')
    
    updateResult.value += `\n\n更新成功！可以测试重新登录了。`
    
  } catch (error: any) {
    console.error('更新失败:', error)
    ElMessage.error(error.message || '更新失败')
    updateResult.value = `更新失败: ${error.message}`
  } finally {
    loading.value = false
  }
}

// 退出登录
const logout = async () => {
  await authStore.logout()
  ElMessage.success('已退出登录，请重新登录测试')
}

// 前往登录页
const goToLogin = () => {
  router.push('/login')
}

onMounted(() => {
  initForm()
})
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  color: #333;
  margin-bottom: 30px;
  text-align: center;
}

.test-section {
  margin-bottom: 40px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.test-section h2 {
  color: #333;
  margin-bottom: 16px;
  font-size: 20px;
}

.test-section p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 12px;
}

.user-info p {
  margin: 8px 0;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
}

.test-form {
  max-width: 600px;
}

.data-preview {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.data-preview h3 {
  color: #333;
  margin: 20px 0 10px 0;
  font-size: 16px;
}

.code-block {
  background: #2d3748;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  overflow-x: auto;
  margin: 10px 0;
}

.code-block.error {
  border-left: 4px solid #f56565;
}

.code-block.success {
  border-left: 4px solid #48bb78;
}

.explanation {
  margin-top: 20px;
  padding: 16px;
  background: #e6fffa;
  border-radius: 8px;
  border-left: 4px solid #38b2ac;
}

.explanation h4 {
  color: #2d3748;
  margin-bottom: 12px;
}

.explanation ul {
  margin: 0;
  padding-left: 20px;
}

.explanation li {
  margin: 8px 0;
  color: #2d3748;
}

.login-test-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}

.result-display {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.result-display pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .test-page {
    padding: 10px;
  }
  
  .container {
    padding: 20px;
  }
  
  .login-test-actions {
    flex-direction: column;
  }
  
  .code-block {
    font-size: 12px;
  }
}
</style> 