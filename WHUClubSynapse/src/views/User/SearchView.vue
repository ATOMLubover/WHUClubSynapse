<template>
  <div class="search-container">
    <!-- 搜索栏 -->
    <div class="search-header">
      <div class="search-input-wrapper">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索社团名称、分类、关键词..."
          size="large"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #prepend>
            <el-icon><Search /></el-icon>
          </template>
          <template #append>
            <el-button type="primary" @click="handleSearch"> 搜索 </el-button>
          </template>
        </el-input>
      </div>

      <!-- 快速筛选 -->
      <div class="quick-filters">
        <span class="filter-label">快速筛选：</span>
        <el-tag
          v-for="category in categories"
          :key="category.category_id"
          :type="activeCategory === category.category_id ? 'primary' : ''"
          :effect="activeCategory === category.category_id ? 'dark' : 'plain'"
          @click="handleCategoryFilter(category.category_id)"
          class="category-filter"
        >
          {{ category.name }}
        </el-tag>
        <el-tag
          :type="activeCategory === '' ? 'primary' : ''"
          :effect="activeCategory === '' ? 'dark' : 'plain'"
          @click="handleCategoryFilter('')"
          class="category-filter"
        >
          全部
        </el-tag>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="search-content">
      <!-- 结果统计和排序 -->
      <div class="result-header">
        <div class="result-info">
          <span v-if="searchKeyword" class="search-term"> "{{ searchKeyword }}" 的搜索结果 </span>
          <span class="result-count"> 共找到 {{ clubStore.searchPageData.total }} 个社团 </span>
        </div>

        <div class="sort-controls">
          <el-select
            v-model="sortBy"
            placeholder="排序方式"
            @change="handleSortChange"
            style="width: 140px"
          >
            <el-option label="按相关度" value="relevance" />
            <el-option label="按热度" value="hot" />
            <el-option label="按时间" value="time" />
            <el-option label="按成员数" value="members" />
          </el-select>
        </div>
      </div>

      <!-- 社团列表 -->
      <div v-loading="clubStore.loading" class="search-results">
        <div v-for="club in clubStore.searchResult" :key="club.club_id" class="search-item">
          <ClubCard :club="club" />
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!clubStore.loading && clubStore.searchResult.length === 0"
        :description="searchKeyword ? `未找到 「${searchKeyword}」 相关的社团` : '暂无搜索结果'"
        :image-size="150"
      >
        <el-button type="primary" @click="clearSearch"> 清空搜索条件 </el-button>
      </el-empty>

      <!-- 分页 -->
      <div v-if="clubStore.searchPageData.total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="clubStore.searchPageData.currentPage"
          :page-size="clubStore.searchPageData.pageSize"
          :total="clubStore.searchPageData.total"
          layout="prev, pager, next, jumper, total"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 推荐社团 -->
    <div v-if="clubStore.searchClubs.length === 0 && !clubStore.loading" class="recommendations">
      <h3>推荐社团</h3>
      <div class="recommend-grid">
        <div v-for="club in recommendedClubs" :key="club.club_id" class="recommend-item">
          <ClubCard :club="club" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
//TODO:还是有一些奇怪的逻辑，比如搜索结果的显示，后续会优化
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import ClubCard from '@/components/Club/ClubCard.vue'
import type { ClubCategory, Club } from '@/types'
import { useCategories } from '@/composables/useCategories'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()

const searchKeyword = ref('')
const activeCategory = ref<number | ''>('')
const sortBy = ref<'relevance' | 'hot' | 'time' | 'members'>('relevance')
const recommendedClubs = ref<Club[]>([])

// 分类数据
// 使用全局分类数据
const { categories, getCategoryName } = useCategories()

// 执行搜索
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) return

  // 更新URL参数
  const query: any = { keyword: searchKeyword.value.trim() }
  if (activeCategory.value) {
    query.category = activeCategory.value
  }

  await router.push({ path: '/search', query })
  await performSearch()
}

// 分类筛选
const handleCategoryFilter = async (category: number | string) => {
  activeCategory.value = category as number

  const query: any = {}
  if (searchKeyword.value) {
    query.keyword = searchKeyword.value
  }
  if (category) {
    query.category = category
  }

  await router.push({ path: '/search', query })
  await performSearch()
}

// 排序切换
const handleSortChange = async () => {
  await performSearch()
}

// 分页切换
const handlePageChange = async (page: number) => {
  clubStore.setSearchPage(page)
  await performSearch()
}

const emit = defineEmits(['clearSearch'])

// 清空搜索
const clearSearch = async () => {
  searchKeyword.value = ''
  activeCategory.value = ''
  sortBy.value = 'relevance'
  clubStore.resetSearch()
  emit('clearSearch')
}

// 执行搜索请求
const performSearch = async () => {
  const params = {
    keyword: searchKeyword.value,
    category: activeCategory.value || undefined,
    sortBy: sortBy.value === 'relevance' ? 'hot' : sortBy.value,
    page: clubStore.searchPageData.currentPage,
    pageSize: clubStore.searchPageData.pageSize,
  }

  try {
    if (searchKeyword.value) {
      await clubStore.searchClubs(searchKeyword.value, params)
    } else {
      clubStore.setSearchParams(params)
      await clubStore.fetchClubs()
    }
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 获取推荐社团
const fetchRecommendations = async () => {
  try {
    recommendedClubs.value = await clubStore.fetchRecommendedClubs(6)
  } catch (error) {
    console.error('获取推荐社团失败:', error)
  }
}

// 监听路由变化
watch(
  () => route.query,
  async (newQuery) => {
    searchKeyword.value = (newQuery.keyword as string) || ''
    activeCategory.value = Number(newQuery.category) || ''

    if (newQuery.keyword || newQuery.category) {
      await performSearch()
    } else {
      clubStore.resetSearch()
      await clubStore.searchClubs('')
    }
  },
  { immediate: true },
)

onMounted(async () => {
  // 从URL参数初始化搜索状态
  searchKeyword.value = (route.query.keyword as string) || ''
  activeCategory.value = Number(route.query.category) || ''

  // 获取推荐社团
  await fetchRecommendations()

  // 如果有搜索参数则执行搜索
  if (searchKeyword.value || activeCategory.value) {
    await performSearch()
  } else {
    await clubStore.fetchClubs()
  }
})
</script>

<style scoped>
.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.search-input-wrapper {
  margin-bottom: 20px;
}

.quick-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  color: #606266;
  font-size: 14px;
  margin-right: 8px;
}

.category-filter {
  cursor: pointer;
  transition: all 0.3s;
}

.category-filter:hover {
  transform: translateY(-2px);
}

.search-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.search-term {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.result-count {
  font-size: 14px;
  color: #909399;
}

.search-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.search-item {
  height: 100%;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.recommendations {
  margin-top: 40px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.recommendations h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.recommend-item {
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-container {
    padding: 16px;
  }

  .result-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .search-results {
    grid-template-columns: 1fr;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }

  .quick-filters {
    flex-direction: column;
    align-items: flex-start;
  }

  .filter-label {
    margin-bottom: 8px;
  }
}
</style>
