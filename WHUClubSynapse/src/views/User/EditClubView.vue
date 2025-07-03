<template>
  <div class="edit-club-view">
    <!-- 页面头部 -->
    <div class="header-content">
      <div class="header-left">
        <el-button @click="goBack" type="text" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1>编辑社团信息</h1>
      </div>
      <div class="header-right">
        <el-button @click="saveClub" type="primary" :loading="saving">
          <el-icon><Check /></el-icon>
          提交更改申请
        </el-button>
      </div>
    </div>

    <div v-loading="loading" class="edit-form-container">
      <!-- 基本信息 -->
      <div class="form-section">
        <h2 class="section-title">
          <el-icon><InfoFilled /></el-icon>
          基本信息
        </h2>
        <el-form ref="basicFormRef" :model="basicForm" :rules="basicRules" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="社团名称" prop="name">
                <el-input v-model="basicForm.name" placeholder="请输入社团名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="社团类型" prop="category_id">
                <el-select v-model="basicForm.category_id" placeholder="请选择社团类型">
                  <el-option
                    v-for="category in clubStore.categoriesList"
                    :key="category.category_id"
                    :label="category.name"
                    :value="category.category_id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="社团标签">
                <el-select
                  v-model="basicForm.tags"
                  multiple
                  filterable
                  allow-create
                  placeholder="请选择或输入标签"
                >
                  <el-option label="编程" value="编程" />
                  <el-option label="算法" value="算法" />
                  <el-option label="竞赛" value="竞赛" />
                  <el-option label="篮球" value="篮球" />
                  <el-option label="音乐" value="音乐" />
                  <el-option label="舞蹈" value="舞蹈" />
                  <el-option label="志愿服务" value="志愿服务" />
                  <el-option label="创业" value="创业" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="社团简介" prop="description">
            <el-input
              v-model="basicForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入社团简介"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>
          <!-- 
          <el-form-item label="封面图片">
            <el-upload
              class="cover-uploader"
              action="#"
              :show-file-list="false"
              :before-upload="beforeCoverUpload"
            >
              <img v-if="basicForm.coverImage" :src="basicForm.coverImage" class="cover-preview" />
              <el-icon v-else class="cover-uploader-icon"><Plus /></el-icon>
            </el-upload>
            <div class="upload-tip">
              建议尺寸：400x300px，支持 JPG、PNG 格式，文件大小不超过 2MB
            </div>
          </el-form-item> -->
        </el-form>
      </div>

      <!-- 详细介绍 -->
      <div class="form-section">
        <h2 class="section-title">
          <el-icon><Document /></el-icon>
          详细介绍
        </h2>
        <el-form ref="detailFormRef" :model="detailForm" label-width="120px">
          <el-form-item label="社团介绍" prop="introduction">
            <el-input
              v-model="detailForm.introduction"
              type="textarea"
              :rows="6"
              placeholder="请详细介绍社团的历史、特色、活动等内容"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="加入要求" prop="requirements">
            <el-input
              v-model="detailForm.requirements"
              type="textarea"
              :rows="4"
              placeholder="请说明加入社团的要求和条件"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 联系方式 -->
      <div class="form-section">
        <h2 class="section-title">
          <el-icon><Phone /></el-icon>
          联系方式
        </h2>
        <el-form ref="contactFormRef" :model="contactForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="QQ群" prop="qq">
                <el-input v-model="contactForm.qq" placeholder="请输入QQ群号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="微信号" prop="wechat">
                <el-input v-model="contactForm.wechat" placeholder="请输入微信号" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="contactForm.email" placeholder="请输入邮箱地址" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" prop="phone">
                <el-input v-model="contactForm.phone" placeholder="请输入联系电话" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="地址" prop="address">
            <el-input v-model="contactForm.address" placeholder="请输入社团活动地址" />
          </el-form-item>
        </el-form>
      </div>

      <!-- 例会信息 -->
      <div class="form-section">
        <h2 class="section-title">
          <el-icon><Calendar /></el-icon>
          例会信息
        </h2>
        <el-form ref="meetingFormRef" :model="meetingForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="例会时间" prop="meetingTime">
                <el-input v-model="meetingForm.meetingTime" placeholder="例如：每周三晚上7点" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="例会地点" prop="meetingLocation">
                <el-input v-model="meetingForm.meetingLocation" placeholder="请输入例会地点" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <!-- 社团公告 -->
      <div class="form-section">
        <h2 class="section-title">
          <el-icon><Bell /></el-icon>
          社团公告
        </h2>
        <div class="announcements-container">
          <div v-if="announcements.length === 0" class="empty-announcements">
            <el-empty description="暂无公告">
              <el-button type="primary" @click="addAnnouncement">添加公告</el-button>
            </el-empty>
          </div>

          <div v-else class="announcements-list">
            <div
              v-for="(announcement, index) in announcements"
              :key="index"
              class="announcement-item"
            >
              <el-input
                v-model="announcements[index]"
                type="textarea"
                :rows="2"
                placeholder="请输入公告内容"
                maxlength="200"
                show-word-limit
              />
              <el-button
                type="danger"
                size="small"
                @click="removeAnnouncement(index)"
                class="remove-btn"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>

            <el-button type="primary" @click="addAnnouncement" class="add-announcement-btn">
              <el-icon><Plus /></el-icon>
              添加公告
            </el-button>
          </div>
        </div>
      </div>

      <!-- 社团动态 -->
      <div class="form-section">
        <h2 class="section-title">
          <el-icon><Calendar /></el-icon>
          社团动态
        </h2>
        <div class="activities-container">
          <div v-if="activities.length === 0" class="empty-activities">
            <el-empty description="暂无动态">
              <el-button type="primary" @click="addActivity">添加动态</el-button>
            </el-empty>
          </div>

          <div v-else class="activities-list">
            <div v-for="(activity, index) in activities" :key="activity.id" class="activity-item">
              <el-card>
                <template #header>
                  <div class="activity-header">
                    <span>动态 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeActivity(index)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </div>
                </template>

                <el-form-item label="动态标题" :prop="`activities.${index}.title`">
                  <el-input
                    v-model="activity.title"
                    placeholder="请输入动态标题"
                    maxlength="100"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="动态描述" :prop="`activities.${index}.description`">
                  <el-input
                    v-model="activity.description"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入动态描述"
                    maxlength="500"
                    show-word-limit
                  />
                </el-form-item>

                <el-form-item label="动态时间" :prop="`activities.${index}.time`">
                  <el-date-picker
                    v-model="activity.time"
                    type="datetime"
                    placeholder="选择动态时间"
                    style="width: 100%"
                    format="YYYY-MM-DD HH:mm"
                    value-format="YYYY-MM-DD HH:mm:ss"
                  />
                </el-form-item>
              </el-card>
            </div>

            <el-button type="primary" @click="addActivity" class="add-activity-btn">
              <el-icon><Plus /></el-icon>
              添加动态
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Check,
  InfoFilled,
  Document,
  Phone,
  Calendar,
  Bell,
  Plus,
  Delete,
} from '@element-plus/icons-vue'
import { useClubStore } from '@/stores/club'
import type { Club, Activity } from '@/types'
import { uploadClubLogo } from '@/api/club'

const route = useRoute()
const router = useRouter()
const clubStore = useClubStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const clubId = route.params.id as string

// 表单引用
const basicFormRef = ref()
const detailFormRef = ref()
const contactFormRef = ref()
const meetingFormRef = ref()

// 基本信息表单
const basicForm = reactive({
  name: '',
  description: '',
  category_id: 0,
  maxMembers: 50,
  tags: [] as string[],
  coverImage: '',
})

// 保存原始文件对象用于上传
const coverImageFile = ref<File | null>(null)

// 详细介绍表单
const detailForm = reactive({
  introduction: '',
  requirements: '',
})

// 联系方式表单
const contactForm = reactive({
  qq: '',
  wechat: '',
  email: '',
  phone: '',
  address: '',
})

// 例会信息表单
const meetingForm = reactive({
  meetingTime: '',
  meetingLocation: '',
})

// 社团公告
const announcements = ref<string[]>([])

// 社团动态
const activities = ref<Activity[]>([])

// 表单验证规则
const basicRules = {
  name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入社团简介', trigger: 'blur' }],
  category: [{ required: true, message: '请选择社团类型', trigger: 'change' }],
  maxMembers: [{ required: true, message: '请输入最大成员数', trigger: 'blur' }],
}

// 加载社团信息
const loadClubInfo = async () => {
  try {
    loading.value = true
    const club = await clubStore.fetchClubDetail(clubId)

    // 填充基本信息
    basicForm.name = club?.club_name || ''
    basicForm.description = club?.desc || ''
    basicForm.category_id = club?.category || 0
    basicForm.maxMembers = club?.maxMembers || 50
    basicForm.tags = club?.tags || []
    basicForm.coverImage = club?.logo_url || ''

    // 填充详细介绍
    detailForm.introduction = club?.introduction || ''
    detailForm.requirements = club?.requirements || ''

    // 填充联系方式
    if (club?.contactInfo) {
      contactForm.qq = club?.contactInfo.qq || ''
      contactForm.wechat = club?.contactInfo.wechat || ''
      contactForm.email = club?.contactInfo.email || ''
      contactForm.phone = club.contactInfo.phone || ''
      contactForm.address = club.contactInfo.address || ''
    }

    // 填充例会信息
    meetingForm.meetingTime = club?.meetingTime || ''
    meetingForm.meetingLocation = club?.meetingLocation || ''

    // 填充公告
    announcements.value = club?.announcements || []

    // 填充动态
    activities.value = club?.activities || []
  } catch (error) {
    console.error('加载社团信息失败:', error)
    ElMessage.error('加载社团信息失败')
  } finally {
    loading.value = false
  }
}

// 封面图片上传前处理
const beforeCoverUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  // 保存原始文件对象用于上传
  coverImageFile.value = file

  // 生成预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    basicForm.coverImage = e.target?.result as string
  }
  reader.readAsDataURL(file)

  return false // 阻止自动上传
}

// 添加公告
const addAnnouncement = () => {
  announcements.value.push('')
}

// 删除公告
const removeAnnouncement = (index: number) => {
  announcements.value.splice(index, 1)
}

// 添加动态
const addActivity = () => {
  activities.value.push({
    id: Date.now(), // 生成临时ID
    title: '',
    description: '',
    time: new Date().toISOString().slice(0, 19).replace('T', ' '), // 默认当前时间
    isNew: true,
  })
}

// 删除动态
const removeActivity = (index: number) => {
  activities.value.splice(index, 1)
}

// 保存社团信息
const saveClub = async () => {
  try {
    // 验证基本信息表单
    await basicFormRef.value?.validate()

    saving.value = true

    const updateData = {
      // 基本信息
      name: basicForm.name,
      desc: basicForm.description,
      category_id: basicForm.category_id,
      tags: basicForm.tags,
      requirements: detailForm.requirements,
    }
    await clubStore.updateClub(clubId, updateData)

    // TODO: 只有当用户上传了新图片时才调用上传接口
    // if (coverImageFile.value) {
    //   await uploadClubLogo(clubId, coverImageFile.value)
    // }

    ElMessage.success('提交更新申请成功')

    // 返回管理页面
    router.push('/user/clubs/managed')
  } catch (error) {
    console.error('保存社团信息失败:', error)
    ElMessage.error('保存失败，请检查表单信息')
  } finally {
    saving.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 页面加载时获取社团信息
onMounted(async () => {
  await clubStore.fetchCategoriesList()
  if (clubId) {
    loadClubInfo()
  } else {
    ElMessage.error('社团ID无效')
    router.push('/user/clubs/managed')
  }
})
</script>

<style scoped>
.edit-club-view {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  font-size: 16px;
  color: #606266;
}

.header-left h1 {
  margin: 0;
  font-size: 28px;
  color: #303133;
}

.edit-form-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  margin-bottom: 40px;
  padding: 30px;
  border-bottom: 1px solid #f0f0f0;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 24px 0;
  font-size: 20px;
  color: #303133;
  font-weight: 600;
}

.section-title .el-icon {
  color: #409eff;
}

.cover-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 200px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-uploader:hover {
  border-color: #409eff;
}

.cover-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 200px;
  height: 150px;
  text-align: center;
  line-height: 150px;
}

.cover-preview {
  width: 200px;
  height: 150px;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.announcements-container {
  margin-top: 20px;
}

.empty-announcements {
  text-align: center;
  padding: 40px 20px;
}

.announcements-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.announcement-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.announcement-item .el-input {
  flex: 1;
}

.remove-btn {
  flex-shrink: 0;
  margin-top: 8px;
}

.add-announcement-btn {
  align-self: flex-start;
}

.activities-container {
  margin-top: 20px;
}

.empty-activities {
  text-align: center;
  padding: 40px 20px;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.activity-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.activity-item .el-card {
  flex: 1;
}

.activity-item .el-card .el-form-item {
  margin-bottom: 12px;
}

.activity-item .el-card .el-form-item:last-child {
  margin-bottom: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.add-activity-btn {
  align-self: flex-start;
}

@media (max-width: 768px) {
  .edit-club-view {
    padding: 10px;
  }

  .header-content h1 {
    font-size: 24px;
  }

  .edit-form-container {
    max-width: 100%;
  }

  .form-section {
    margin-bottom: 30px;
    padding: 15px;
  }

  .announcement-item {
    flex-direction: column;
  }

  .remove-btn {
    align-self: flex-end;
  }
}
</style>
