<template>
  <el-dialog
    v-model="visible"
    title="设置你的偏好"
    width="520px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    class="preference-dialog"
  >
    <div class="preference-setup">
      <div class="setup-header">
        <el-icon class="setup-icon"><Setting /></el-icon>
        <h3>欢迎加入WHU社团联盟！</h3>
        <p>请选择你感兴趣的社团类型，我们将为你推荐相关内容</p>
      </div>

      <el-form :model="preferences" label-width="100px" class="preference-form" size="small">
        <el-form-item label="感兴趣类型" required>
          <div class="category-selection">
            <el-checkbox-group v-model="preferences.interestedCategories" class="category-group">
              <div class="category-item" v-for="category in categories" :key="category.category_id">
                <el-checkbox :label="category" :value="category" class="category-checkbox">
                  <template #default>
                    <div class="category-content">
                      <div class="category-name">{{ category.name }}</div>
                      <div class="category-description">
                        {{ getCategoryDescription(category.name) }}
                      </div>
                    </div>
                  </template>
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </div>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>可选择多个类型</span>
          </div>
        </el-form-item>

        <el-form-item label="通知设置">
          <div class="notification-settings">
            <el-switch
              v-model="preferences.emailNotifications"
              active-text="邮件通知"
              size="small"
              class="notification-item"
            />
            <el-switch
              v-model="preferences.applicationNotifications"
              active-text="申请通知"
              size="small"
              class="notification-item"
            />
            <el-switch
              v-model="preferences.activityNotifications"
              active-text="活动推送"
              size="small"
              class="notification-item"
            />
          </div>
        </el-form-item>

        <el-form-item label="隐私设置">
          <div class="privacy-settings">
            <el-switch
              v-model="preferences.profilePublic"
              active-text="公开资料"
              size="small"
              class="privacy-item"
            />
            <el-switch
              v-model="preferences.showJoinedClubs"
              active-text="显示社团"
              size="small"
              class="privacy-item"
            />
          </div>
        </el-form-item>

        <el-form-item label="个人标签" required>
          <div class="tag-selection">
            <el-select
              v-model="preferences.tags"
              multiple
              filterable
              allow-create
              default-first-option
              :reserve-keyword="false"
              :filter-method="filterTag"
              :collapse-tags="false"
              placeholder="选择特质/爱好标签（限4字以内）"
              size="small"
              class="tag-group"
            >
              <el-option
                v-for="tag in filteredTags"
                :key="tag"
                :label="tag"
                :value="tag"
              ></el-option>
            </el-select>
          </div>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>可自定义标签</span>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleSkip" class="skip-button" size="small">跳过</el-button>
        <el-button
          type="primary"
          @click="handleSave"
          :loading="loading"
          :disabled="!isValid"
          size="small"
        >
          保存并继续
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, InfoFilled } from '@element-plus/icons-vue'
import type { ClubCategory, UserPreferences } from '@/types'
import { allUserTags } from '@/utils/mockData'
import { useCategories } from '@/composables/useCategories'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
// Props
interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 响应式数据
const loading = ref(false)
// 使用全局分类数据
const { categories } = useCategories()

// 偏好设置
const preferences = reactive<UserPreferences>({
  interestedCategories: [],
  emailNotifications: true,
  applicationNotifications: true,
  activityNotifications: false,
  profilePublic: true,
  showJoinedClubs: true,
  tags: [],
})

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const isValid = computed(() => {
  return preferences.interestedCategories.length > 0
})

const tagInput = ref('')

const filteredTags = computed(() => {
  // 只显示未被选中的、包含输入内容的标签
  const input = tagInput.value.trim()
  const selected = preferences.tags || []
  let base = allUserTags.filter((tag) => !selected.includes(tag))
  if (input) {
    base = base.filter((tag) => tag.includes(input))
  }
  // 如果输入4字以内且不在已有标签和已选中标签中，则允许自定义
  if (
    input &&
    input.length > 0 &&
    input.length <= 4 &&
    !allUserTags.includes(input) &&
    !selected.includes(input)
  ) {
    return [input, ...base]
  }
  return base
})

const filterTag = (query: string) => {
  tagInput.value = query
}

// 方法
const getCategoryDescription = (categoryName: string): string => {
  const descriptions: Record<string, string> = {
    学术科技: '编程、算法、科研等学术类社团',
    文艺体育: '音乐、舞蹈、运动等文体类社团',
    志愿服务: '公益、志愿、服务等社会类社团',
    创新创业: '创业、创新、商业等实践类社团',
    其他: '其他类型的社团',
  }
  return descriptions[categoryName] || '社团相关活动'
}

const handleSave = async () => {
  if (!isValid.value) {
    ElMessage.warning('请至少选择一个感兴趣的社团类型')
    return
  }

  try {
    loading.value = true
    console.log('PreferenceSetupDialog保存的偏好设置:', preferences)
    console.log('包含的标签:', preferences.tags)

    // 使用新的updateUserInfo方法保存偏好设置
    await authStore.updateUserInfo({
      preferences: preferences,
      tags: preferences.tags,
    })

    visible.value = false
    ElMessage.success('偏好设置保存成功')
  } catch (error) {
    console.error('保存偏好设置失败:', error)
    ElMessage.error('保存失败，请重试')
  } finally {
    loading.value = false
  }
}

const handleSkip = () => {
  visible.value = false
  ElMessage.info('已跳过偏好设置，你可以在个人中心中随时修改')
}
</script>

<style scoped>
.preference-dialog :deep(.el-dialog) {
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
}

.preference-dialog :deep(.el-dialog__header) {
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin: 0;
}

.preference-dialog :deep(.el-dialog__title) {
  color: white;
  font-size: 16px;
  font-weight: 500;
}

.preference-dialog :deep(.el-dialog__body) {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  background: #fafafa;
}

.preference-setup {
  padding: 0;
}

.setup-header {
  text-align: center;
  margin-bottom: 16px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.setup-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 8px;
}

.setup-header h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.setup-header p {
  margin: 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

.preference-form {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.preference-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.preference-form :deep(.el-form-item__label) {
  white-space: nowrap;
  font-weight: 500;
  font-size: 13px;
  color: #303133;
}

.category-selection {
  margin-bottom: 8px;
}

.category-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
}

.category-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 8px 10px;
  transition: all 0.3s;
  background: #fafbfc;
}

.category-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
  transform: translateY(-1px);
}

.category-checkbox {
  width: 100%;
  height: auto;
}

.category-checkbox :deep(.el-checkbox__label) {
  width: 100%;
  padding-left: 4px;
}

.category-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.category-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.category-description {
  font-size: 10px;
  color: #909399;
  line-height: 1.3;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 3px;
  color: #909399;
  font-size: 10px;
  margin-top: 4px;
}

.form-tip .el-icon {
  font-size: 12px;
}

.notification-settings,
.privacy-settings {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.notification-item,
.privacy-item {
  flex: 1;
  min-width: 120px;
}

.notification-item :deep(.el-switch__label),
.privacy-item :deep(.el-switch__label) {
  font-size: 12px;
}

.tag-selection {
  margin-bottom: 8px;
}

.tag-group {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.skip-button {
  color: #909399;
  border: none;
  background: none;
  padding: 6px 12px;
}

.skip-button:hover {
  color: #606266;
  background: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preference-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }

  .category-group {
    grid-template-columns: 1fr;
  }

  .notification-settings,
  .privacy-settings {
    flex-direction: column;
    gap: 8px;
  }

  .notification-item,
  .privacy-item {
    min-width: auto;
  }

  .preference-form :deep(.el-form-item__label) {
    font-size: 12px;
  }

  .setup-header h3 {
    font-size: 14px;
  }

  .setup-header p {
    font-size: 11px;
  }
}

/* 动画效果 */
.preference-dialog :deep(.el-dialog) {
  animation: slideInDown 0.3s ease-out;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
