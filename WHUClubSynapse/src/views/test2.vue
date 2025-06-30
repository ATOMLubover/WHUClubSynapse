<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">全局Categories测试页面</h1>

    <!-- Categories显示 -->
    <el-card class="mb-6">
      <template #header>
        <div class="flex justify-between items-center">
          <span>全局社团分类数据</span>
          <el-button @click="refreshCategories" type="primary" :loading="loading"
            >刷新数据</el-button
          >
        </div>
      </template>

      <div class="space-y-4">
        <div>
          <h3 class="text-lg font-semibold mb-2">分类列表 ({{ categories.length }}个)</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <el-tag
              v-for="category in categories"
              :key="category.category_id"
              type="primary"
              size="large"
              class="justify-center"
            >
              {{ category.name }} (ID: {{ category.category_id }})
            </el-tag>
          </div>
        </div>

        <el-divider />

        <div>
          <h3 class="text-lg font-semibold mb-2">分类选项 (用于表单)</h3>
          <el-select v-model="selectedCategory" placeholder="选择一个分类" class="w-full">
            <el-option
              v-for="option in getCategoryOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
          <div v-if="selectedCategory" class="mt-2 text-sm text-gray-600">
            选中的分类: {{ getCategoryName(selectedCategory) }} (ID: {{ selectedCategory }})
          </div>
        </div>

        <el-divider />

        <div>
          <h3 class="text-lg font-semibold mb-2">工具方法测试</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <el-input
              v-model="testCategoryId"
              placeholder="输入分类ID"
              type="number"
              @input="testCategoryName = getCategoryName(Number(testCategoryId))"
            >
              <template #prepend>分类ID</template>
            </el-input>
            <el-input v-model="testCategoryName" readonly>
              <template #prepend>分类名称</template>
            </el-input>
          </div>

          <div class="mt-4">
            <el-input
              v-model="testCategoryNameInput"
              placeholder="输入分类名称"
              @input="testFoundId = getCategoryId(testCategoryNameInput)"
            >
              <template #prepend>分类名称</template>
            </el-input>
            <div class="mt-2 text-sm text-gray-600">找到的ID: {{ testFoundId || '未找到' }}</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 统计数据 -->
    <el-card class="mb-6" v-if="Object.keys(categoriesStats).length > 0">
      <template #header>
        <span>分类统计数据</span>
      </template>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="(count, categoryId) in categoriesStats"
          :key="categoryId"
          class="text-center p-4 bg-blue-50 rounded-lg"
        >
          <div class="text-lg font-semibold">{{ getCategoryName(Number(categoryId)) }}</div>
          <div class="text-sm text-gray-600">{{ count }} 个社团</div>
        </div>
      </div>
    </el-card>

    <!-- 调试信息 -->
    <el-card>
      <template #header>
        <span>调试信息</span>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="分类总数">{{ categories.length }}</el-descriptions-item>
        <el-descriptions-item label="统计数据"
          >{{ Object.keys(categoriesStats).length }} 个分类</el-descriptions-item
        >
        <el-descriptions-item label="分类名称列表">
          {{ getCategoryNames.join(', ') }}
        </el-descriptions-item>
        <el-descriptions-item label="分类ID列表">
          {{ getCategoryIds.join(', ') }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="mt-4">
        <h4 class="font-semibold mb-2">原始数据:</h4>
        <el-collapse>
          <el-collapse-item title="分类列表" name="categories">
            <pre class="text-xs bg-gray-100 p-2 rounded">{{
              JSON.stringify(categories, null, 2)
            }}</pre>
          </el-collapse-item>
          <el-collapse-item title="统计数据" name="stats">
            <pre class="text-xs bg-gray-100 p-2 rounded">{{
              JSON.stringify(categoriesStats, null, 2)
            }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCategories } from '@/composables/useCategories'
import { useClubStore } from '@/stores/club'
import { ElMessage } from 'element-plus'

// 使用全局categories功能
const {
  categories,
  categoriesStats,
  getCategoryNames,
  getCategoryIds,
  getCategoryOptions,
  getCategoryName,
  getCategoryId,
  refreshCategories: refreshCategoriesComposable,
} = useCategories()

const clubStore = useClubStore()
const loading = ref(false)

// 测试用的响应式数据
const selectedCategory = ref<number>()
const testCategoryId = ref('')
const testCategoryName = ref('')
const testCategoryNameInput = ref('')
const testFoundId = ref<number | undefined>()

// 刷新分类数据
const refreshCategories = async () => {
  try {
    loading.value = true
    await refreshCategoriesComposable()
    ElMessage.success('分类数据刷新成功')
  } catch (error: any) {
    ElMessage.error(`刷新失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.container {
  max-width: 1200px;
}

.el-tag {
  margin: 2px;
}
</style>
