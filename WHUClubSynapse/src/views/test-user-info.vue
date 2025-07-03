<template>
  <div class="test-container">
    <el-card header="用户扩展信息功能测试">
      <div class="test-section">
        <h3>当前用户信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">{{ userInfo?.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userInfo?.email }}</el-descriptions-item>
          <el-descriptions-item label="真实姓名">{{ userInfo?.realName || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="学号">{{ userInfo?.studentId || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ userInfo?.major || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ userInfo?.phone || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="个人简介">{{ userInfo?.bio || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="特质标签">
            <el-tag v-for="tag in userInfo?.tags" :key="tag" style="margin-right: 4px;">{{ tag }}</el-tag>
            <span v-if="!userInfo?.tags?.length">未设置</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="test-section">
        <h3>更新用户信息测试</h3>
        <el-form :model="testForm" label-width="100px">
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
          <el-form-item label="特质标签">
            <el-tag
              v-for="tag in testForm.tags"
              :key="tag"
              closable
              @close="removeTag(tag)"
              style="margin-right: 8px;"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="inputVisible"
              ref="InputRef"
              v-model="inputValue"
              size="small"
              style="width: 100px;"
              @keyup.enter="handleInputConfirm"
              @blur="handleInputConfirm"
            />
            <el-button v-else size="small" @click="showInput">+ 新标签</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="testUpdate" :loading="loading">
              测试更新
            </el-button>
            <el-button @click="refreshUserInfo">刷新用户信息</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="test-section">
        <h3>Extension字段原始数据</h3>
        <el-input
          v-model="extensionText"
          type="textarea"
          :rows="6"
          readonly
          placeholder="扩展信息JSON"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElInput } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types'

const authStore = useAuthStore()
const loading = ref(false)

// 用户信息
const userInfo = computed(() => authStore.user)

// 测试表单
const testForm = reactive({
  realName: '',
  studentId: '',
  major: '',
  phone: '',
  bio: '',
  tags: [] as string[]
})

// 标签输入相关
const inputVisible = ref(false)
const inputValue = ref('')
const InputRef = ref<InstanceType<typeof ElInput>>()

// Extension原始数据
const extensionText = computed(() => {
  if (!userInfo.value?.extension) return ''
  try {
    return JSON.stringify(JSON.parse(userInfo.value.extension), null, 2)
  } catch {
    return userInfo.value.extension
  }
})

// 初始化表单数据
const initForm = () => {
  if (userInfo.value) {
    testForm.realName = userInfo.value.realName || ''
    testForm.studentId = userInfo.value.studentId || ''
    testForm.major = userInfo.value.major || ''
    testForm.phone = userInfo.value.phone || ''
    testForm.bio = userInfo.value.bio || ''
    testForm.tags = [...(userInfo.value.tags || [])]
  }
}

// 标签操作
const removeTag = (tag: string) => {
  testForm.tags.splice(testForm.tags.indexOf(tag), 1)
}

const showInput = () => {
  inputVisible.value = true
  nextTick(() => {
    InputRef.value!.input!.focus()
  })
}

const handleInputConfirm = () => {
  if (inputValue.value && !testForm.tags.includes(inputValue.value)) {
    testForm.tags.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

// 测试更新
const testUpdate = async () => {
  try {
    loading.value = true
    
    const updateData: Partial<User> = {
      realName: testForm.realName,
      studentId: testForm.studentId,
      major: testForm.major,
      phone: testForm.phone,
      bio: testForm.bio,
      tags: testForm.tags
    }
    
    console.log('准备更新的数据:', updateData)
    console.log('当前表单标签:', testForm.tags)
    
    await authStore.updateUserInfo(updateData)
    ElMessage.success('用户信息更新成功！')
    
    // 等待一下再刷新，确保后端已经保存
    setTimeout(() => {
      refreshUserInfo()
    }, 500)
    
  } catch (error: any) {
    console.error('更新失败:', error)
    ElMessage.error(error.message || '更新失败')
  } finally {
    loading.value = false
  }
}

// 刷新用户信息
const refreshUserInfo = async () => {
  try {
    await authStore.fetchUserInfo()
    initForm()
    ElMessage.success('用户信息已刷新')
  } catch (error: any) {
    ElMessage.error('刷新失败')
  }
}

onMounted(() => {
  initForm()
})
</script>

<style scoped>
.test-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.test-section h3 {
  margin-bottom: 15px;
  color: #303133;
}
</style> 