<template>
  <el-dialog
    v-model="visible"
    title="设置你的偏好"
    width="90%"
    max-width="800px"
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

      <el-form :model="preferences" label-width="140px" class="preference-form">
        <el-form-item label="感兴趣的社团类型" required>
          <div class="category-selection">
            <el-checkbox-group v-model="preferences.interestedCategories" class="category-group">
              <div class="category-item" v-for="category in categories" :key="category">
                <el-checkbox :label="category" class="category-checkbox">
                  <div class="category-content">
                    <div class="category-name">{{ category }}</div>
                    <div class="category-description">{{ getCategoryDescription(category) }}</div>
                  </div>
                </el-checkbox>
              </div>
            </el-checkbox-group>
          </div>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>你可以选择多个感兴趣的社团类型</span>
          </div>
        </el-form-item>

        <el-form-item label="通知设置">
          <div class="notification-settings">
            <el-switch
              v-model="preferences.emailNotifications"
              active-text="邮件通知"
              class="notification-item"
            />
            <el-switch
              v-model="preferences.applicationNotifications"
              active-text="申请状态通知"
              class="notification-item"
            />
            <el-switch
              v-model="preferences.activityNotifications"
              active-text="活动推送"
              class="notification-item"
            />
          </div>
        </el-form-item>

        <el-form-item label="隐私设置">
          <div class="privacy-settings">
            <el-switch
              v-model="preferences.profilePublic"
              active-text="公开个人资料"
              class="privacy-item"
            />
            <el-switch
              v-model="preferences.showJoinedClubs"
              active-text="显示已加入社团"
              class="privacy-item"
            />
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleSkip" class="skip-button">跳过</el-button>
        <el-button type="primary" @click="handleSave" :loading="loading" :disabled="!isValid">
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

// Props
interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'save': [preferences: UserPreferences]
}>()

// 响应式数据
const loading = ref(false)
const categories: ClubCategory[] = ['学术科技', '文艺体育', '志愿服务', '创新创业', '其他']

// 偏好设置
const preferences = reactive<UserPreferences>({
  interestedCategories: [],
  emailNotifications: true,
  applicationNotifications: true,
  activityNotifications: false,
  profilePublic: true,
  showJoinedClubs: true,
})

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isValid = computed(() => {
  return preferences.interestedCategories.length > 0
})

// 方法
const getCategoryDescription = (category: ClubCategory): string => {
  const descriptions: Record<ClubCategory, string> = {
    '学术科技': '编程、算法、科研等学术类社团',
    '文艺体育': '音乐、舞蹈、运动等文体类社团',
    '志愿服务': '公益、志愿、服务等社会类社团',
    '创新创业': '创业、创新、商业等实践类社团',
    '其他': '其他类型的社团'
  }
  return descriptions[category]
}

const handleSave = async () => {
  if (!isValid.value) {
    ElMessage.warning('请至少选择一个感兴趣的社团类型')
    return
  }

  try {
    loading.value = true
    emit('save', { ...preferences })
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
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.preference-dialog :deep(.el-dialog__body) {
  flex: 1;
  overflow-y: auto;
  padding: 20px 30px;
}

.preference-setup {
  padding: 10px 0;
}

.setup-header {
  text-align: center;
  margin-bottom: 20px;
}

.setup-icon {
  font-size: 40px;
  color: #409eff;
  margin-bottom: 12px;
}

.setup-header h3 {
  margin: 0 0 6px 0;
  font-size: 18px;
  color: #303133;
}

.setup-header p {
  margin: 0;
  color: #606266;
  font-size: 13px;
}

.preference-form {
  margin-top: 15px;
}

.preference-form :deep(.el-form-item__label) {
  white-space: nowrap;
  font-weight: 500;
}

.category-selection {
  margin-bottom: 12px;
}

.category-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.category-item {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  transition: all 0.3s;
}

.category-item:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.category-checkbox {
  width: 100%;
  height: auto;
}

.category-checkbox :deep(.el-checkbox__label) {
  width: 100%;
  padding-left: 6px;
}

.category-content {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.category-description {
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 11px;
}

.notification-settings,
.privacy-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notification-item,
.privacy-item {
  margin-bottom: 6px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
}

.skip-button {
  color: #909399;
}

.skip-button:hover {
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .category-group {
    grid-template-columns: 1fr;
  }
  
  .preference-form :deep(.el-form-item__label) {
    font-size: 13px;
  }
  
  .setup-header h3 {
    font-size: 16px;
  }
  
  .setup-header p {
    font-size: 12px;
  }
}
</style> 