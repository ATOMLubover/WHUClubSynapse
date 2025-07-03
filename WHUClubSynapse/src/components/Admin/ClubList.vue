<template>
  <div class="club-list">
    <el-card class="main-card" shadow="hover">
      <template #header>
        <div class="header-content">
          <div class="header-left">
            <el-icon class="header-icon"><Management /></el-icon>
            <span class="header-title">社团列表管理</span>
            <el-tag type="info" size="small" class="total-tag">{{ total }}个社团</el-tag>
          </div>
          <div class="header-actions">
            <el-select
              v-model="pageSize"
              placeholder="每页显示"
              @change="handlePageSizeChange"
              class="page-size-select"
            >
              <el-option label="12条/页" :value="12" />
              <el-option label="24条/页" :value="24" />
              <el-option label="48条/页" :value="48" />
            </el-select>
          </div>
        </div>
      </template>
      <div v-loading="loading">
        <el-row :gutter="20">
          <el-col
            v-for="club in clubs"
            :key="club.club_id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            :xl="4"
            class="club-card-col"
          >
            <div class="club-card" @click="viewClubDetail(club)">
              <div class="club-cover">
                <img :src="club.logo_url" :alt="club.club_name" />
                <div class="club-overlay">
                  <el-icon class="view-icon"><View /></el-icon>
                </div>
              </div>
              <div class="club-info">
                <div class="club-header">
                  <h3 class="club-name">{{ club.club_name }}</h3>
                  <el-tag :type="getCategoryType(club.category)" size="small" class="category-tag">
                    {{ categoryMap[club.category] || club.category }}
                  </el-tag>
                </div>
                <div class="club-stats">
                  <div class="stat-item">
                    <el-icon><User /></el-icon>
                    <span>{{ club.member_count }}人</span>
                  </div>
                  <div class="stat-item">
                    <el-icon><Calendar /></el-icon>
                    <span>{{ formatDate(club.created_at) }}</span>
                  </div>
                </div>
              </div>
              <div class="club-actions">
                <el-button size="small" type="primary" @click.stop="viewClubDetail(club)">
                  <el-icon><View /></el-icon>
                  查看详情
                </el-button>
                <el-button size="small" type="danger" @click.stop="deleteClub(club)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>

        <!-- 分页组件 -->
        <div v-if="total > 0" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="total"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>

        <!-- 空状态 -->
        <el-empty v-else-if="!loading" description="暂无社团数据" :image-size="120" />
      </div>
      <el-dialog
        v-model="detailDialogVisible"
        title="社团详情"
        width="800px"
        :close-on-click-modal="false"
      >
        <div v-if="selectedClub" class="club-detail">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="社团名称">{{
              selectedClub.club_name
            }}</el-descriptions-item>
            <el-descriptions-item label="社团类型">{{
              categoryMap[selectedClub.category] || selectedClub.category
            }}</el-descriptions-item>
            <el-descriptions-item label="成员数量"
              >{{ selectedClub.member_count }}人</el-descriptions-item
            >
            <el-descriptions-item label="创建时间">{{
              formatDate(selectedClub.created_at)
            }}</el-descriptions-item>
            <el-descriptions-item label="社团简介" :span="2">{{
              selectedClub.desc || '暂无简介'
            }}</el-descriptions-item>
          </el-descriptions>

          <div class="detail-section">
            <h4>社团标签</h4>
            <div class="tags-container">
              <el-tag
                v-for="tag in selectedClub.tags"
                :key="tag"
                size="small"
                style="margin-right: 8px; margin-bottom: 8px"
              >
                {{ tag }}
              </el-tag>
              <span v-if="!selectedClub.tags || selectedClub.tags.length === 0" class="no-tags"
                >暂无标签</span
              >
            </div>
          </div>

          <div class="detail-section">
            <h4>加入要求</h4>
            <p>{{ selectedClub.requirements || '暂无要求' }}</p>
          </div>
        </div>
        <template #footer>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useClubStore } from '@/stores/club'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Management, View, Delete, User, Calendar } from '@element-plus/icons-vue'
import type { Club, ClubCategory } from '@/types'
import { getClubCategoriesList, deleteClub as deleteClubApi, getClubList } from '@/api/club'

const clubStore = useClubStore()
const clubs = ref<Club[]>([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedClub = ref<Club | null>(null)
const categories = ref<ClubCategory[]>([])

// 分页相关状态
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const categoryMap = computed(() => {
  const map: Record<number, string> = {}
  categories.value.forEach((c) => {
    map[c.category_id] = c.name
  })
  return map
})

const loadClubs = async () => {
  loading.value = true
  try {
    const res = await getClubList({
      page: currentPage.value,
      pageSize: pageSize.value,
    })
    clubs.value = res.list || res
    total.value = res.total || 0
  } catch (error) {
    console.error('加载社团列表失败:', error)
    ElMessage.error('加载社团列表失败')
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadClubs()
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
  loadClubs()
}
const loadCategories = async () => {
  categories.value = await getClubCategoriesList()
}

const viewClubDetail = (club: Club) => {
  selectedClub.value = club
  detailDialogVisible.value = true
}

// 格式化日期
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取分类类型
const getCategoryType = (category: number) => {
  const typeMap: Record<number, string> = {
    0: 'primary', // 学术科技
    1: 'success', // 文艺体育
    2: 'warning', // 志愿服务
    3: 'danger', // 创新创业
    4: 'info', // 其他
  }
  return typeMap[category] || 'info'
}

const deleteClub = async (club: Club) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除社团"${club.club_name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    // 直接调用API删除
    await deleteClubApi(club.club_id)
    ElMessage.success('删除成功')
    loadClubs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除社团失败:', error)
      ElMessage.error('删除失败')
    }
  }
}
onMounted(() => {
  loadClubs()
  loadCategories()
})
</script>

<style scoped>
.club-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.main-card {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.club-card-col {
  margin-bottom: 24px;
}

.club-card {
  border: none;
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
}

.club-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}
.club-cover {
  height: 160px;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.club-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.club-card:hover .club-cover img {
  transform: scale(1.1);
}

.club-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.club-card:hover .club-overlay {
  opacity: 1;
}

.view-icon {
  font-size: 32px;
  color: white;
}
.club-info {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.club-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.club-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  flex: 1;
  margin-right: 12px;
}

.category-tag {
  flex-shrink: 0;
}

.club-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.stat-item .el-icon {
  color: #909399;
  font-size: 16px;
}
.club-actions {
  display: flex;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.club-actions .el-button {
  flex: 1;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.club-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 24px;
  color: #409eff;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.total-tag {
  background: linear-gradient(45deg, #409eff, #67c23a);
  color: white;
  border: none;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.page-size-select {
  width: 120px;
}

.pagination-section {
  margin-top: 32px;
  display: flex;
  justify-content: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.club-detail {
  padding: 20px 0;
}

.detail-section {
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-section h4::before {
  content: '';
  width: 4px;
  height: 18px;
  background: linear-gradient(45deg, #409eff, #67c23a);
  border-radius: 2px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tags-container .el-tag {
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tags-container .el-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.no-tags {
  color: #909399;
  font-style: italic;
  padding: 12px;
  background: rgba(144, 147, 153, 0.1);
  border-radius: 8px;
  border: 1px dashed #d9d9d9;
}
</style>
