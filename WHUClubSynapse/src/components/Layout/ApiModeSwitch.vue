<template>
  <div v-if="!isProduction" class="api-mode-switch">
    <el-tooltip effect="dark" content="开发模式：切换API数据源" placement="bottom">
      <el-switch
        v-model="isCurrentlyMock"
        class="mode-switch"
        active-text="Mock"
        inactive-text="Real"
        @change="handleModeChange"
      />
    </el-tooltip>

    <!-- 模式状态标签 -->
    <el-tag :type="isCurrentlyMock ? 'success' : 'warning'" size="small" class="mode-tag">
      {{ isCurrentlyMock ? 'Mock数据' : '真实API' }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useConfigStore } from '@/stores/config'

// 检查是否为生产环境
const isProduction = import.meta.env.PROD

// 使用配置Store
const configStore = useConfigStore()

// 响应式的当前模式状态
const isCurrentlyMock = ref(configStore.isUsingMockAPI)

// 监听配置变化
const currentApiMode = computed(() => configStore.apiMode)

// 处理模式切换
const handleModeChange = async (value: boolean) => {
  const targetMode = value ? 'mock' : 'real'

  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要切换到 ${targetMode === 'mock' ? 'Mock数据模式' : '真实API模式'} 吗？`,
      '切换API模式',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    // 执行切换
    configStore.setApiMode(targetMode)

    // 更新本地状态
    isCurrentlyMock.value = value

    // 成功提示
    ElMessage.success({
      message: `已切换到${targetMode === 'mock' ? 'Mock数据模式' : '真实API模式'}`,
      duration: 2000,
    })

    // 调试信息
    if (configStore.apiDebug) {
      console.log('🔄 API模式切换成功:', {
        newMode: targetMode,
        config: configStore.getConfigSummary(),
      })
    }
  } catch (error) {
    // 用户取消或出错，恢复原状态
    isCurrentlyMock.value = !value

    if (error !== 'cancel') {
      ElMessage.error('切换API模式失败')
      console.error('API模式切换错误:', error)
    }
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 恢复用户偏好
  configStore.restoreUserPreference()

  // 同步状态
  isCurrentlyMock.value = configStore.isUsingMockAPI

  // 调试信息
  if (configStore.apiDebug) {
    console.log('🔧 ApiModeSwitch 初始化:', {
      currentMode: configStore.apiMode,
      isProduction,
      config: configStore.getConfigSummary(),
    })
  }
})
</script>

<style scoped>
.api-mode-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-switch {
  --el-switch-on-color: #67c23a;
  --el-switch-off-color: #e6a23c;
}

.mode-tag {
  margin-left: 4px;
  font-size: 12px;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .api-mode-switch {
    gap: 4px;
  }

  .mode-tag {
    display: none;
  }
}
</style>
