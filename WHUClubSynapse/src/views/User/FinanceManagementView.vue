<template>
  <div class="finance-management">
    <el-card class="finance-card">
      <template #header>
        <div class="card-header">
          <h2>{{ club?.club_name }} - 经费管理</h2>
          <el-button @click="goBack" size="small">返回</el-button>
        </div>
      </template>

      <div class="finance-content">
        <!-- AI交互区域 -->
        <div class="ai-interaction-section">
          <h3>智能财务助理</h3>
          <p class="ai-description">
            使用自然语言描述财务记录，AI将自动解析并记录财务条目
          </p>
          
          <div class="input-section">
            <el-input
              v-model="financialInput"
              type="textarea"
              :rows="3"
              placeholder="例如：今天活动买了10瓶水和一包零食，一共花了55.8元，从小明那里报销。"
              @keyup.enter.ctrl="submitFinancialRecord"
            />
            <div class="input-actions">
              <el-button 
                type="primary" 
                @click="submitFinancialRecord"
                :loading="submitting"
                :disabled="!financialInput.trim()"
              >
                提交记录
              </el-button>
              <el-button 
                @click="testAIResponse"
                :disabled="!financialInput.trim()"
              >
                测试AI
              </el-button>
              <el-button 
                @click="testAIConnection"
                size="small"
              >
                测试连接
              </el-button>
              <span class="tip">按 Ctrl+Enter 快速提交</span>
            </div>
          </div>
        </div>

        <!-- 财务记录列表 -->
        <div class="financial-records-section">
          <div class="section-header">
            <h3>财务记录</h3>
            <el-button @click="refreshRecords" size="small" :loading="loading">
              <el-icon><Refresh /></el-icon>
              获取报表
            </el-button>
          </div>

          <!-- 财务统计 -->
          <div class="finance-stats">
            <div class="stat-item">
              <span class="stat-label">总收入</span>
              <span class="stat-value income">¥{{ totalIncome.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总支出</span>
              <span class="stat-value expense">¥{{ totalExpense.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">结余</span>
              <span class="stat-value" :class="balanceClass">¥{{ balance.toFixed(2) }}</span>
            </div>
          </div>

          <!-- 财务报表摘要 -->
          <div v-if="financialReport" class="financial-report-summary">
            <h4>AI财务报表摘要</h4>
            <div class="report-content">
              <p>{{ financialReport.report_summary }}</p>
            </div>
          </div>

          <div v-if="loading" class="loading-section">
            <el-skeleton :rows="5" animated />
          </div>

          <div v-else-if="financialRecords.length === 0" class="empty-section">
            <el-empty description="暂无财务记录" />
          </div>

          <div v-else class="records-list">
            <div 
              v-for="(record, index) in financialRecords" 
              :key="index"
              class="record-item"
            >
              <div class="record-header">
                <span class="record-date">{{ formatDate(record.date) }}</span>
                <span class="record-amount" :class="getAmountClass(record.amount)">
                  {{ formatAmount(record.amount) }}
                </span>
              </div>
              <div class="record-content">
                <p class="record-description">{{ record.description }}</p>
                <div class="record-details">
                  <span class="record-category">分类：{{ record.category }}</span>
                  <span class="record-payer">经手人：{{ record.payer }}</span>
                  <span class="record-type">类型：{{ record.type === 'income' ? '收入' : '支出' }}</span>
                  <span v-if="record.remark">备注：{{ record.remark }}</span>
                  <span v-if="record.details">明细：{{ record.details }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import { financialBookkeeping, checkAIStatus, generateFinancialReport } from '@/api/ai'
import type { Club } from '@/types'

const router = useRouter()
const route = useRoute()
const clubStore = useClubStore()

// 响应式数据
const club = ref<Club | null>(null)
const loading = ref(false)
const submitting = ref(false)
const financialInput = ref('')
const financialRecords = ref<any[]>([])
const financialReport = ref<any>(null)
const reportLoading = ref(false)

// 计算财务统计数据
const totalIncome = computed(() => {
  return financialRecords.value
    .filter(record => record.amount > 0)
    .reduce((sum, record) => sum + record.amount, 0)
})

const totalExpense = computed(() => {
  return Math.abs(financialRecords.value
    .filter(record => record.amount < 0)
    .reduce((sum, record) => sum + record.amount, 0))
})

const balance = computed(() => {
  return totalIncome.value - totalExpense.value
})

const balanceClass = computed(() => {
  return balance.value >= 0 ? 'income' : 'expense'
})

// 获取社团信息
const getClubInfo = async () => {
  const clubId = route.params.clubId as string
  console.log('获取社团信息，clubId:', clubId)
  
  if (clubId) {
    try {
      // 使用fetchClubDetail API获取社团信息
      const clubData = await clubStore.fetchClubDetail(clubId)
      console.log('获取到的社团数据:', clubData)
      club.value = clubData
      
      // 暂时注释掉权限检查，先确保基本功能正常
      // const managedClubs = await clubStore.fetchManagedClubs()
      // const isManager = managedClubs.list.some(c => c.club_id === clubId)
      
      // if (!isManager) {
      //   ElMessage.error('您没有权限管理该社团')
      //   router.back()
      //   return
      // }
    } catch (error) {
      console.error('获取社团信息失败:', error)
      ElMessage.error('获取社团信息失败')
      router.back()
    }
  }
}

// 提交财务记录
const submitFinancialRecord = async () => {
  if (!financialInput.value.trim() || !club.value) {
    return
  }

  submitting.value = true
  try {
    const requestData = {
      natural_language_input: financialInput.value,
      club_name: club.value.club_name,
    }
    
    console.log('调用AI财务记账接口，请求数据:', requestData)
    
    const data = await financialBookkeeping(requestData)
    console.log('AI财务记账响应数据:', data)
    
    // 将AI解析的条目添加到记录中
    if (data.parsed_entries && data.parsed_entries.length > 0) {
      const newRecords = data.parsed_entries.map((entry) => ({
        date: new Date(),
        description: entry.description || financialInput.value,
        amount: entry.amount || 0,
        category: entry.category || '其他',
        payer: entry.payer || '未知',
        type: entry.type || 'expense',
      }))
      
      financialRecords.value.unshift(...newRecords)
      ElMessage.success('财务记录已添加')
    } else {
      ElMessage.warning('AI未能解析出有效的财务条目')
    }
    
    financialInput.value = ''
  } catch (error) {
    ElMessage.error('提交财务记录失败')
    console.error('提交财务记录失败:', error)
  } finally {
    submitting.value = false
  }
}

// 测试AI响应（模拟）
const testAIResponse = async () => {
  if (!financialInput.value.trim() || !club.value) {
    return
  }

  submitting.value = true
  try {
    // 模拟AI解析延迟
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 模拟AI解析结果
    const mockAIResponse = {
      parsed_entries: [
        {
          description: financialInput.value,
          amount: -55.8, // 模拟解析出的金额
          category: '活动用品',
          payer: '小明',
          type: 'expense',
        }
      ],
      confirmation_message: '已成功解析财务记录',
      original_input: financialInput.value,
    }
    
    // 将AI解析的条目添加到记录中
    if (mockAIResponse.parsed_entries && mockAIResponse.parsed_entries.length > 0) {
      const newRecords = mockAIResponse.parsed_entries.map((entry: any) => ({
        date: new Date(),
        description: entry.description || financialInput.value,
        amount: entry.amount || 0,
        category: entry.category || '其他',
          payer: entry.payer || '未知',
        type: entry.type || 'expense',
      }))
      
      financialRecords.value.unshift(...newRecords)
      ElMessage.success('财务记录已添加（测试模式）')
    }
    
    financialInput.value = ''
  } catch (error) {
    ElMessage.error('测试AI响应失败')
    console.error('测试AI响应失败:', error)
  } finally {
    submitting.value = false
  }
}

// 测试AI连接
const testAIConnection = async () => {
  try {
    console.log('测试AI连接...')
    
    const isAvailable = await checkAIStatus()
    
    if (isAvailable) {
      console.log('AI连接测试成功')
      ElMessage.success('AI服务器连接正常')
    } else {
      throw new Error('AI服务不可用')
    }
  } catch (error) {
    console.error('AI连接测试失败:', error)
    ElMessage.error('AI服务器连接失败')
  }
}

// 刷新记录
const refreshRecords = async () => {
  if (!club.value) {
    ElMessage.warning('请先选择社团')
    return
  }

  loading.value = true
  reportLoading.value = true
  
  try {
    console.log('开始获取财务报表，社团名称:', club.value.club_name)
    
    const requestData = {
      club_name: club.value.club_name,
    }
    
    const reportData = await generateFinancialReport(requestData)
    console.log('获取到的财务报表数据:', reportData)
    
    // 将AI返回的财务报表数据转换为记录格式
    const records: any[] = []
    
    // 处理支出分类
    if (reportData.expense_breakdown) {
      Object.entries(reportData.expense_breakdown).forEach(([category, amount]) => {
        records.push({
          date: new Date(),
          description: `${category}支出`,
          amount: -Math.abs(amount), // 支出为负数
          category: category,
          payer: '社团',
          type: 'expense',
        })
      })
    }
    
    // 处理收入分类
    if (reportData.income_breakdown) {
      Object.entries(reportData.income_breakdown).forEach(([category, amount]) => {
        records.push({
          date: new Date(),
          description: `${category}收入`,
          amount: Math.abs(amount), // 收入为正数
          category: category,
          payer: '社团',
          type: 'income',
        })
      })
    }
    
    financialRecords.value = records
    financialReport.value = reportData
    
    ElMessage.success('财务报表已更新')
  } catch (error) {
    console.error('获取财务报表失败:', error)
    ElMessage.error('获取财务报表失败')
    
    // 如果AI接口失败，使用模拟数据作为备选
    const mockRecords = [
      {
        date: new Date('2024-01-15T10:30:00'),
        description: '购买活动用品：横幅、海报、宣传单',
        amount: -120.50,
        category: '活动用品',
        payer: '张三',
        type: 'expense',
      },
      {
        date: new Date('2024-01-14T14:20:00'),
        description: '收到会员费',
        amount: 200.00,
        category: '会员费',
        payer: '李四',
        type: 'income',
      },
      {
        date: new Date('2024-01-13T16:45:00'),
        description: '场地租赁费用',
        amount: -300.00,
        category: '场地费',
        payer: '王五',
        type: 'expense',
      },
      {
        date: new Date('2024-01-12T09:15:00'),
        description: '活动门票收入',
        amount: 450.00,
        category: '门票收入',
        payer: '活动参与者',
        type: 'income',
      },
    ]
    
    financialRecords.value = mockRecords
    ElMessage.warning('使用模拟数据作为备选')
  } finally {
    loading.value = false
    reportLoading.value = false
  }
}

// 格式化日期
const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

// 格式化金额
const formatAmount = (amount: number) => {
  return `¥${amount.toFixed(2)}`
}

// 获取金额样式类
const getAmountClass = (amount: number) => {
  return amount > 0 ? 'income' : 'expense'
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 组件挂载时获取数据
onMounted(async () => {
  await getClubInfo()
  // 获取社团信息后自动获取财务报表
  if (club.value) {
    await refreshRecords()
  }
})
</script>

<style scoped>
.finance-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.finance-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.finance-content {
  display: flex;
  flex-direction: row;
  gap: 30px;
}

.ai-interaction-section {
  flex: 1 1 0;
  min-width: 340px;
  max-width: 480px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  box-sizing: border-box;
}

.ai-interaction-section h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.ai-description {
  color: #606266;
  margin-bottom: 20px;
  font-size: 14px;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.input-actions .el-button {
  flex-shrink: 0;
}

.input-actions .el-button:last-of-type {
  margin-left: auto;
}

.tip {
  font-size: 12px;
  color: #909399;
  flex-grow: 1;
  text-align: right;
}

.financial-records-section {
  flex: 1 1 0;
  min-width: 340px;
  max-width: 540px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #303133;
}

.finance-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-weight: bold;
  font-size: 16px;
}

.stat-value.income {
  color: #67c23a;
}

.stat-value.expense {
  color: #f56c6c;
}

.loading-section {
  padding: 20px 0;
}

.empty-section {
  padding: 40px 0;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.record-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.record-item:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-date {
  font-size: 12px;
  color: #909399;
}

.record-amount {
  font-weight: bold;
  font-size: 16px;
}

.record-amount.income {
  color: #67c23a;
}

.record-amount.expense {
  color: #f56c6c;
}

.record-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.record-description {
  margin: 0;
  color: #303133;
  font-size: 14px;
  line-height: 1.5;
}

.record-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
}

.record-category,
.record-payer {
  color: #606266;
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.financial-report-summary {
  margin-top: 20px;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  box-sizing: border-box;
}

.financial-report-summary h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.report-content {
  color: #606266;
  font-size: 14px;
}

@media (max-width: 900px) {
  .finance-content {
    flex-direction: column;
    gap: 20px;
  }
  .ai-interaction-section, .financial-records-section {
    max-width: 100%;
    min-width: 0;
  }
}
</style> 