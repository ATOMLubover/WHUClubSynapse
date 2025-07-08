import { computed } from 'vue'
import { useClubStore } from '@/stores/club'
import type { ClubCategory } from '@/types'

/**
 * 社团分类相关的composable
 * 提供便捷的方法来访问和使用全局的社团分类数据
 */
export function useCategories() {
  const clubStore = useClubStore()

  // 获取分类列表
  const categories = computed<ClubCategory[]>(() => clubStore.categoriesList)

  // 获取分类统计数据（从categoriesList计算得出）
  const categoriesStats = computed<Record<string, number>>(() => {
    const stats: Record<string, number> = {}
    categories.value.forEach(cat => {
      stats[cat.category_id] = 0 // 初始化为0，实际数据需要从API获取
    })
    return stats
  })

  // 根据分类ID获取分类名称
  const getCategoryName = (categoryId: number): string => {
    const category = categories.value.find(cat => cat.category_id === categoryId)
    return category?.name || '未知分类'
  }

  // 根据分类名称获取分类ID
  const getCategoryId = (categoryName: string): number | undefined => {
    const category = categories.value.find(cat => cat.name === categoryName)
    return category?.category_id
  }

  // 获取所有分类名称
  const getCategoryNames = computed<string[]>(() => {
    return categories.value.map(cat => cat.name)
  })

  // 获取所有分类ID
  const getCategoryIds = computed<number[]>(() => {
    return categories.value.map(cat => cat.category_id)
  })

  // 检查分类是否存在
  const isCategoryExists = (categoryId: number): boolean => {
    return categories.value.some(cat => cat.category_id === categoryId)
  }

  // 获取分类选项（用于表单选择器）
  const getCategoryOptions = computed(() => {
    return categories.value.map(cat => ({
      label: cat.name,
      value: cat.category_id
    }))
  })

  // 刷新分类数据
  const refreshCategories = async () => {
    try {
      await clubStore.fetchCategoriesList()
    } catch (error) {
      console.error('刷新分类数据失败:', error)
      throw error
    }
  }

  // 获取分类颜色类型（用于Element Plus标签）
  const getCategoryType = (categoryId: number): string => {
    const typeMap: Record<number, string> = {
      1: 'primary',   // 学术科技
      2: 'success',   // 文艺体育  
      3: 'warning',   // 志愿服务
      4: 'danger',    // 创新创业
      5: 'info',      // 其他
    }
    return typeMap[categoryId] || 'info'
  }

  // 根据分类名称获取颜色类型
  const getCategoryTypeByName = (categoryName: string): string => {
    const category = categories.value.find(cat => cat.name === categoryName)
    return category ? getCategoryType(category.category_id) : 'info'
  }

  return {
    // 响应式数据
    categories,
    categoriesStats,
    getCategoryNames,
    getCategoryIds,
    getCategoryOptions,

    // 工具方法
    getCategoryName,
    getCategoryId,
    getCategoryType,
    getCategoryTypeByName,
    isCategoryExists,
    refreshCategories,
  }
} 