<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon user-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.totalUsers }}</h3>
            <p>总用户数</p>
            <span class="stat-change positive">+{{ stats.newUsers }} 今日新增</span>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon club-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.totalClubs }}</h3>
            <p>社团总数</p>
            <span class="stat-change positive">+{{ stats.newClubs }} 本周新增</span>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon application-icon">
            <el-icon><DocumentAdd /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.pendingApplications }}</h3>
            <p>待审核申请</p>
            <span class="stat-change warning">需要处理</span>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon activity-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stats.activeUsers }}</h3>
            <p>活跃用户</p>
            <span class="stat-change positive">+{{ stats.activeGrowth }}%</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 用户注册趋势 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>用户注册趋势</span>
            <el-button text>查看详情</el-button>
          </div>
        </template>
        <div class="chart-container">
          <div class="chart-placeholder">
            <el-icon><TrendCharts /></el-icon>
            <p>用户注册趋势图表</p>
          </div>
        </div>
      </el-card>

      <!-- 社团活跃度 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>社团活跃度</span>
            <el-button text>查看详情</el-button>
          </div>
        </template>
        <div class="chart-container">
          <div class="chart-placeholder">
            <el-icon><PieChart /></el-icon>
            <p>社团活跃度分布图</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 最近活动 -->
    <div class="recent-activities">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>最近活动</span>
            <el-button text>查看全部</el-button>
          </div>
        </template>

        <el-timeline>
          <el-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :timestamp="activity.time"
            :type="activity.type"
          >
            <div class="activity-content">
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.description }}</p>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-card>
        <template #header>
          <span>快速操作</span>
        </template>

        <div class="action-buttons">
          <el-button type="primary" @click="handleQuickAction('user')">
            <el-icon><UserFilled /></el-icon>
            用户管理
          </el-button>
          <el-button type="success" @click="handleQuickAction('club')">
            <el-icon><OfficeBuilding /></el-icon>
            社团管理
          </el-button>
          <el-button type="warning" @click="handleQuickAction('application')">
            <el-icon><DocumentAdd /></el-icon>
            审核申请
          </el-button>
          <el-button type="info" @click="handleQuickAction('backup')">
            <el-icon><Download /></el-icon>
            数据备份
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  User,
  OfficeBuilding,
  DocumentAdd,
  TrendCharts,
  PieChart,
  UserFilled,
  Download,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 统计数据
const stats = ref({
  totalUsers: 1248,
  newUsers: 23,
  totalClubs: 156,
  newClubs: 5,
  pendingApplications: 42,
  activeUsers: 892,
  activeGrowth: 12,
})

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    title: '新用户注册',
    description: '用户 "张三" 完成注册',
    time: '2分钟前',
    type: 'primary',
  },
  {
    id: 2,
    title: '社团申请',
    description: '计算机社团提交了新的活动申请',
    time: '15分钟前',
    type: 'success',
  },
  {
    id: 3,
    title: '用户举报',
    description: '收到关于不当内容的举报',
    time: '1小时前',
    type: 'warning',
  },
  {
    id: 4,
    title: '系统备份',
    description: '定时数据备份执行完成',
    time: '2小时前',
    type: 'info',
  },
  {
    id: 5,
    title: '社团审核',
    description: '摄影社团通过审核',
    time: '昨天',
    type: 'success',
  },
])

// 快速操作处理
const handleQuickAction = (action: string) => {
  switch (action) {
    case 'user':
      ElMessage.info('跳转到用户管理')
      break
    case 'club':
      ElMessage.info('跳转到社团管理')
      break
    case 'application':
      ElMessage.info('跳转到申请审核')
      break
    case 'backup':
      ElMessage.info('执行数据备份')
      break
  }
}

onMounted(() => {
  // 这里可以加载实际的统计数据
  console.log('数据看板初始化完成')
})
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* 统计卡片 */
.stats-grid {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.user-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.club-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.application-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.activity-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info h3 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-info p {
  margin: 0 0 8px 0;
  color: #909399;
  font-size: 14px;
}

.stat-change {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
}

.stat-change.positive {
  background: #f0f9ff;
  color: #409eff;
}

.stat-change.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

/* 图表区域 */
.charts-grid {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
}

.chart-card {
  border-radius: 12px;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #909399;
}

.chart-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

/* 最近活动 */
.recent-activities {
  grid-column: 1 / -1;
}

.activity-content h4 {
  margin: 0 0 4px 0;
  color: #303133;
}

.activity-content p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

/* 快速操作 */
.quick-actions {
  grid-column: 1 / -1;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 120px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    min-width: auto;
  }
}
</style>
