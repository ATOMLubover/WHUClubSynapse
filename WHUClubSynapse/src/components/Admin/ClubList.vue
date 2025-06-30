<template>
  <div class="club-list">
    <el-card>
      <template #header>
        <span>社团列表管理</span>
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
            <div class="club-card">
              <div class="club-cover">
                <img :src="club.logo_url" :alt="club.club_name" />
              </div>
              <div class="club-info">
                <h3 class="club-name">{{ club.club_name }}</h3>
                <p class="club-category">{{ categoryMap[club.category] || club.category }}</p>
                <p class="club-members">{{ club.member_count }}人</p>
                <p class="club-time">创建于 {{ club.created_at }}</p>
              </div>
              <div class="club-actions">
                <el-button size="small" @click="openEditDialog(club)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteClub(club)">删除</el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      <el-dialog v-model="editDialogVisible" title="编辑社团" width="800px" :close-on-click-modal="false">
        <ClubEditForm v-model="editClubForm" />
        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveClub">保存</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useClubStore } from '@/stores/club'
import { ElMessage } from 'element-plus'
import type { Club, ClubCategory } from '@/types'
import { getClubCategoriesList } from '@/api/club'
import ClubEditForm from './ClubEditForm.vue'

const clubStore = useClubStore()
const clubs = ref<Club[]>([])
const loading = ref(false)
const editDialogVisible = ref(false)
const editClubForm = ref<any>({})
const categories = ref<ClubCategory[]>([])

const categoryMap = computed(() => {
  const map: Record<number, string> = {}
  categories.value.forEach(c => { map[c.category_id] = c.name })
  return map
})

const loadClubs = async () => {
  loading.value = true
  const res = await clubStore.fetchClubs()
  clubs.value = res.list || res
  loading.value = false
}
const loadCategories = async () => {
  categories.value = await getClubCategoriesList()
}

const openEditDialog = (club: Club) => {
  // 兼容字段映射
  editClubForm.value = {
    ...club,
    name: club.club_name,
    description: club.desc,
    coverImage: club.logo_url,
    maxMembers: club.maxMembers,
    tags: club.tags || [],
    introduction: club.introduction,
    requirements: club.requirements,
    qq: club.contactInfo?.qq || club.qq,
    wechat: club.contactInfo?.wechat || '',
    email: club.contactInfo?.email || '',
    phone: club.contactInfo?.phone || '',
    address: club.contactInfo?.address || '',
    meetingTime: club.meetingTime,
    meetingLocation: club.meetingLocation,
  }
  editDialogVisible.value = true
}
const saveClub = async () => {
  // 反向映射字段
  const data = {
    club_id: editClubForm.value.club_id,
    club_name: editClubForm.value.name,
    desc: editClubForm.value.description,
    logo_url: editClubForm.value.coverImage,
    category: editClubForm.value.category,
    maxMembers: editClubForm.value.maxMembers,
    tags: editClubForm.value.tags,
    introduction: editClubForm.value.introduction,
    requirements: editClubForm.value.requirements,
    contactInfo: {
      qq: editClubForm.value.qq,
      wechat: editClubForm.value.wechat,
      email: editClubForm.value.email,
      phone: editClubForm.value.phone,
      address: editClubForm.value.address,
    },
    meetingTime: editClubForm.value.meetingTime,
    meetingLocation: editClubForm.value.meetingLocation,
  }
  await clubStore.updateClub(data.club_id, data)
  ElMessage.success('保存成功')
  editDialogVisible.value = false
  loadClubs()
}
const deleteClub = async (club: Club) => {
  await clubStore.deleteClub(club.club_id)
  ElMessage.success('已删除')
  loadClubs()
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
}
.club-card-col {
  margin-bottom: 20px;
}
.club-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.club-cover {
  height: 120px;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}
.club-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.club-info {
  padding: 12px;
}
.club-name {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #303133;
}
.club-category {
  color: #909399;
  font-size: 13px;
}
.club-members {
  color: #606266;
  font-size: 13px;
}
.club-time {
  color: #b1b1b1;
  font-size: 12px;
}
.club-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}
</style>
