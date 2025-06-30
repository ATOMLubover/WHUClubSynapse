<template>
  <div class="test-page">
    <h1>经费管理功能测试</h1>
    
    <div class="test-buttons">
      <el-button @click="testRoute('5')" type="primary">
        测试篮球社经费管理 (ID: 5)
      </el-button>
      
      <el-button @click="testRoute('1')" type="success">
        测试计算机科学协会经费管理 (ID: 1)
      </el-button>
      
      <el-button @click="testClubDetail('5')" type="warning">
        测试获取篮球社详情 (ID: 5)
      </el-button>
      
      <el-button @click="testManagedClubs" type="info">
        测试获取管理的社团列表
      </el-button>
      
      <el-button @click="testAIConnection" type="danger">
        测试AI服务器连接
      </el-button>
      
      <el-button @click="testAIFinancial" type="secondary">
        测试AI财务接口
      </el-button>
      
      <el-button @click="testFinancialReport" type="warning">
        测试AI财务报表
      </el-button>
    </div>
    
    <div v-if="testResult" class="test-result">
      <h3>测试结果：</h3>
      <pre>{{ JSON.stringify(testResult, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useClubStore } from '@/stores/club'
import { ElMessage } from 'element-plus'
import { checkAIStatus, financialBookkeeping, generateFinancialReport } from '@/api/ai'

const router = useRouter()
const clubStore = useClubStore()
const testResult = ref<any>(null)

const testRoute = (clubId: string) => {
  console.log('测试路由跳转到:', `/user/club/${clubId}/finance`)
  router.push(`/user/club/${clubId}/finance`)
}

const testClubDetail = async (clubId: string) => {
  try {
    console.log('测试获取社团详情，clubId:', clubId)
    const result = await clubStore.fetchClubDetail(clubId)
    testResult.value = result
    ElMessage.success('获取社团详情成功')
  } catch (error: any) {
    console.error('获取社团详情失败:', error)
    testResult.value = { error: error.message }
    ElMessage.error('获取社团详情失败')
  }
}

const testManagedClubs = async () => {
  try {
    console.log('测试获取管理的社团列表')
    const result = await clubStore.fetchManagedClubs()
    testResult.value = result
    ElMessage.success('获取管理的社团列表成功')
  } catch (error: any) {
    console.error('获取管理的社团列表失败:', error)
    testResult.value = { error: error.message }
    ElMessage.error('获取管理的社团列表失败')
  }
}

const testAIConnection = async () => {
  try {
    console.log('测试AI连接...')
    
    const isAvailable = await checkAIStatus()
    
    if (isAvailable) {
      testResult.value = { success: true, message: 'AI服务器连接正常' }
      ElMessage.success('AI服务器连接正常')
    } else {
      throw new Error('AI服务不可用')
    }
  } catch (error: any) {
    console.error('AI连接测试失败:', error)
    testResult.value = { error: error.message }
    ElMessage.error('AI服务器连接失败')
  }
}

const testAIFinancial = async () => {
  try {
    console.log('测试AI财务接口...')
    
    const requestData = {
      natural_language_input: '今天活动买了10瓶水和一包零食，一共花了55.8元，从小明那里报销。',
      club_name: '篮球社',
    }
    
    const data = await financialBookkeeping(requestData)
    testResult.value = { success: true, data }
    ElMessage.success('AI财务接口测试成功')
  } catch (error: any) {
    console.error('AI财务接口测试失败:', error)
    testResult.value = { error: error.message }
    ElMessage.error('AI财务接口测试失败')
  }
}

const testFinancialReport = async () => {
  try {
    console.log('测试AI财务报表...')
    
    const requestData = {
      club_name: '篮球社',
    }
    
    const data = await generateFinancialReport(requestData)
    testResult.value = { success: true, data }
    ElMessage.success('AI财务报表测试成功')
  } catch (error: any) {
    console.error('AI财务报表测试失败:', error)
    testResult.value = { error: error.message }
    ElMessage.error('AI财务报表测试失败')
  }
}
</script>

<style scoped>
.test-page {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

.test-result {
  margin-top: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.test-result pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
  line-height: 1.4;
}
</style>
