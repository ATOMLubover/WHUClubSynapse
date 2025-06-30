<template>
  <div class="my-favorites">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>我的收藏</h1>
      <p>您收藏的社团都在这里，可以快速查看和管理</p>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-card>
        <el-row :gutter="20" align="middle">
          <el-col :span="6">
            <el-select
              v-model="filterCategory"
              placeholder="筛选类型"
              clearable
              @change="handleFilter"
            >
              <el-option label="全部类型" value="" />
              <el-option
                v-for="category in clubStore.categoriesList"
                :label="category.name"
                :value="category.category_id"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="sortBy" placeholder="排序方式" @change="handleSort">
              <el-option label="收藏时间（最新）" value="createdAt_desc" />
              <el-option label="收藏时间（最早）" value="createdAt_asc" />
              <el-option label="社团名称（A-Z）" value="name_asc" />
              <el-option label="社团人数（多-少）" value="memberCount_desc" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索收藏的社团"
              clearable
              @keyup.enter="handleFilter"
            >
              <template #append>
                <el-button icon="Search" @click="handleFilter" />
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-dropdown @command="handleBatchAction">
              <el-button>
                批量操作 <el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="selectAll">全选</el-dropdown-item>
                  <el-dropdown-item command="selectNone">取消全选</el-dropdown-item>
                  <el-dropdown-item divided command="batchRemove">批量取消收藏</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 收藏列表 -->
    <div class="favorites-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span
              >收藏列表 ({{
                selectedClubs.length > 0
                  ? `已选择 ${selectedClubs.length} 个`
                  : `共 ${favoriteClubs.length} 个`
              }})</span
            >
            <div class="header-actions">
              <el-button @click="loadFavorites" :loading="loading">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button value="card">卡片</el-radio-button>
                <el-radio-button value="list">列表</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>

        <div v-loading="loading">
          <!-- 空状态 -->
          <div v-if="!favoriteClubs.length && !loading" class="empty-state">
            <el-empty description="还没有收藏任何社团">
              <el-button type="primary" @click="$router.push('/')"> 去发现社团 </el-button>
            </el-empty>
          </div>

          <!-- 卡片视图 -->
          <div v-else-if="viewMode === 'card'" class="card-view">
            <el-row :gutter="20">
              <el-col
                v-for="club in paginatedClubs"
                :key="club.club_id"
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                class="club-card-col"
              >
                <div class="club-card" :class="{ selected: selectedClubs.includes(club.club_id) }">
                  <!-- 选择框 -->
                  <el-checkbox
                    v-model="selectedClubs"
                    :value="club.club_id"
                    class="card-checkbox"
                  />

                  <!-- 社团封面 -->
                  <div class="club-cover" @click="viewClubDetail(club.club_id)">
                    <img :src="club.logo_url" :alt="club.club_name" />
                    <div class="cover-overlay">
                      <el-button type="primary" size="small">查看详情</el-button>
                    </div>
                  </div>

                  <!-- 社团信息 -->
                  <div class="club-info">
                    <h3 class="club-name" @click="viewClubDetail(club.club_id)">
                      {{ club.club_name }}
                    </h3>
                    <p class="club-category">{{ getCategoryText(club.category) }}</p>
                    <p class="club-members">{{ club.member_count }}</p>
                    <p class="favorite-time">{{ formatDate(club.favoriteAt) }}</p>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="club-actions">
                    <el-button size="small" @click="viewClubDetail(club.club_id)"> 查看 </el-button>
                    <el-button size="small" type="danger" @click="removeFavorite(club.club_id)">
                      取消收藏
                    </el-button>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 列表视图 -->
          <div v-else class="list-view">
            <div class="list-header">
              <el-checkbox
                v-model="selectAll"
                :indeterminate="isIndeterminate"
                @change="handleSelectAll"
              >
                全选
              </el-checkbox>
            </div>

            <div class="club-list">
              <div
                v-for="club in paginatedClubs"
                :key="club.club_id"
                class="club-list-item"
                :class="{ selected: selectedClubs.includes(club.club_id) }"
              >
                <el-checkbox v-model="selectedClubs" :value="club.club_id" />

                <el-avatar :size="50" :src="club.logo_url" class="club-avatar">
                  <el-icon><UserFilled /></el-icon>
                </el-avatar>

                <div class="club-basic-info">
                  <h4 class="club-name" @click="viewClubDetail(club.club_id)">
                    {{ club.club_name }}
                  </h4>
                  <p class="club-desc">{{ club.desc || '暂无描述' }}</p>
                </div>

                <div class="club-meta">
                  <el-tag size="small">{{ getCategoryText(club.category) }}</el-tag>
                  <span class="club-members">{{ club.member_count }} 人</span>
                </div>

                <div class="club-favorite-time">
                  <span>收藏于</span>
                  <span>{{ formatDate(club.favoriteAt) }}</span>
                </div>

                <div class="club-list-actions">
                  <el-button size="small" @click="viewClubDetail(club.club_id)">
                    查看详情
                  </el-button>
                  <el-button size="small" type="danger" @click="removeFavorite(club.club_id)">
                    取消收藏
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="favoriteClubs.length" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="favoriteClubs.length"
            :page-sizes="[12, 24, 48]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, ArrowDown, UserFilled } from '@element-plus/icons-vue'
import { getClubCategoriesList, getFavoriteClubs, unfavoriteClub } from '@/api/club'
import type { Club, ClubCategory } from '@/types'
import { useClubStore } from '@/stores/club'

// 路由
const router = useRouter()
const clubStore = useClubStore()
// 响应式数据
const loading = ref(false)
const viewMode = ref<'card' | 'list'>('card')
const currentPage = ref(1)
const pageSize = ref(12)

// 筛选和排序
const filterCategory = ref('')
const sortBy = ref('createdAt_desc')
const searchKeyword = ref('')

// 选择相关
const selectedClubs = ref<string[]>([])
const selectAll = ref(false)

// 收藏数据
const favoriteClubs = ref<(Club & { favoriteAt: string })[]>([])
const favoriteStats = reactive({
  total: 0,
  thisWeek: 0,
  categories: 0,
})

// 计算属性
const filteredClubs = computed(() => {
  let clubs = [...favoriteClubs.value]

  // 分类筛选
  if (filterCategory.value) {
    clubs = clubs.filter(
      (club) =>
        clubStore.categoriesList.find((c) => c.category_id === club.category)?.name ===
        filterCategory.value,
    )
  }

  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    clubs = clubs.filter(
      (club) =>
        club.club_name.toLowerCase().includes(keyword) ||
        club.desc?.toLowerCase().includes(keyword),
    )
  }

  // 排序
  clubs.sort((a, b) => {
    switch (sortBy.value) {
      case 'createdAt_desc':
        return new Date(b.favoriteAt).getTime() - new Date(a.favoriteAt).getTime()
      case 'createdAt_asc':
        return new Date(a.favoriteAt).getTime() - new Date(b.favoriteAt).getTime()
      case 'name_asc':
        return a.club_name.localeCompare(b.club_name)
      case 'memberCount_desc':
        return b.member_count - a.member_count
      default:
        return 0
    }
  })

  return clubs
})

const paginatedClubs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredClubs.value.slice(start, end)
})

const isIndeterminate = computed(() => {
  const selectedCount = selectedClubs.value.length
  const totalCount = filteredClubs.value.length
  return selectedCount > 0 && selectedCount < totalCount
})

// 监听选择状态
watch(
  () => selectedClubs.value,
  (newVal) => {
    const totalCount = filteredClubs.value.length
    selectAll.value = newVal.length === totalCount && totalCount > 0
  },
  { deep: true },
)

// 方法
const getCategoryText = (category: number) => {
  const categoryMap: Record<number, string> = {
    0: '学术科技',
    1: '文化艺术',
    2: '体育运动',
    3: '志愿服务',
    4: '社会实践',
    5: '创新创业',
  }
  return categoryMap[category] || category
}

const formatDate = (date: string) => {
  console.log(date)
  return new Date(date).toLocaleDateString('zh-CN')
}

const loadFavorites = async () => {
  try {
    loading.value = true

    const response = await getFavoriteClubs({
      page: 1,
      pageSize: 1000, // 获取全部收藏，前端分页
    })

    const list = response.list
    //TODO: 这里需要修改，favoriteAt应该是从后端获取的,也许不需要这个字段
    favoriteClubs.value = list.map((item: any) => ({
      ...item,
      favoriteAt: new Date().toISOString(),
    }))

    console.log(favoriteClubs)

    // 更新统计数据
    updateStats()
  } catch (error: any) {
    ElMessage.error(error.message || '加载收藏列表失败')
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  const clubs = favoriteClubs.value
  favoriteStats.total = clubs.length

  // 计算本周新增
  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  favoriteStats.thisWeek = clubs.filter((club) => new Date(club.favoriteAt) > oneWeekAgo).length

  // 计算涉及的分类数
  const categories = new Set(clubs.map((club) => club.category))
  favoriteStats.categories = categories.size
}

const handleFilter = () => {
  currentPage.value = 1
  selectedClubs.value = []
}

const handleSort = () => {
  currentPage.value = 1
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

const handleSelectAll = (checked: boolean) => {
  if (checked) {
    selectedClubs.value = filteredClubs.value.map((club) => club.club_id)
  } else {
    selectedClubs.value = []
  }
}

const handleBatchAction = (command: string) => {
  switch (command) {
    case 'selectAll':
      selectedClubs.value = filteredClubs.value.map((club) => club.club_id)
      break
    case 'selectNone':
      selectedClubs.value = []
      break
    case 'batchRemove':
      if (selectedClubs.value.length === 0) {
        ElMessage.warning('请先选择要取消收藏的社团')
        return
      }
      batchRemoveFavorites()
      break
  }
}

const viewClubDetail = (clubId: string) => {
  router.push(`/club/${clubId}`)
}

const removeFavorite = async (clubId: string) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏这个社团吗？', '取消收藏', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    console.log(clubId)
    await unfavoriteClub(clubId)
    ElMessage.success('已取消收藏')

    // 从列表中移除
    favoriteClubs.value = favoriteClubs.value.filter((club) => club.club_id !== clubId)
    selectedClubs.value = selectedClubs.value.filter((id) => id !== clubId)

    // 更新统计
    updateStats()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消收藏失败')
    }
  }
}

const batchRemoveFavorites = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要取消收藏选中的 ${selectedClubs.value.length} 个社团吗？`,
      '批量取消收藏',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    // 批量取消收藏
    const promises = selectedClubs.value.map((clubId) => unfavoriteClub(clubId))
    await Promise.all(promises)

    ElMessage.success(`已取消收藏 ${selectedClubs.value.length} 个社团`)

    // 从列表中移除
    favoriteClubs.value = favoriteClubs.value.filter(
      (club) => !selectedClubs.value.includes(club.club_id),
    )
    selectedClubs.value = []

    // 更新统计
    updateStats()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量操作失败')
    }
  }
}

onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
.my-favorites {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 16px;
}

.toolbar,
.stats-section,
.favorites-section {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 卡片视图样式 */
.card-view {
  min-height: 400px;
}

.club-card-col {
  margin-bottom: 20px;
}

.club-card {
  position: relative;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  background: #fff;
}

.club-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.club-card.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.card-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 2;
  background: transparent;
  border-radius: 4px;
  padding: 2px;
}

.club-cover {
  position: relative;
  height: 150px;
  overflow: hidden;
  cursor: pointer;
}

.club-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.club-cover:hover img {
  transform: scale(1.05);
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.club-cover:hover .cover-overlay {
  opacity: 1;
}

.club-info {
  padding: 16px;
}

.club-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
  transition: color 0.2s;
}

.club-name:hover {
  color: #409eff;
}

.club-category,
.club-members,
.favorite-time {
  margin: 4px 0;
  color: #606266;
  font-size: 13px;
}

.club-actions {
  padding: 0 16px 16px;
  display: flex;
  gap: 8px;
}

/* 列表视图样式 */
.list-view {
  min-height: 400px;
}

.list-header {
  padding: 16px 0;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 16px;
}

.club-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.3s;
}

.club-list-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.club-list-item.selected {
  border-color: #409eff;
  background: #f0f9ff;
}

.club-avatar {
  flex-shrink: 0;
}

.club-basic-info {
  flex: 1;
  min-width: 200px;
}

.club-basic-info .club-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  cursor: pointer;
  transition: color 0.2s;
}

.club-basic-info .club-name:hover {
  color: #409eff;
}

.club-desc {
  margin: 0;
  color: #606266;
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.club-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 100px;
}

.club-members {
  color: #606266;
  font-size: 13px;
}

.club-favorite-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
  color: #909399;
  font-size: 12px;
}

.club-list-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.pagination-section {
  margin-top: 20px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-view .el-col {
    width: 100%;
  }

  .club-list-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .club-meta,
  .club-favorite-time {
    min-width: auto;
    flex-direction: row;
  }

  .club-list-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
