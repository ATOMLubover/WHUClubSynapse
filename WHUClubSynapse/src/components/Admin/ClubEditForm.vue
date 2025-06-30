<template>
  <el-form :model="form" label-width="100px" :rules="rules" ref="formRef" class="club-edit-form">
    <el-form-item label="社团名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入社团名称" />
    </el-form-item>
    <el-form-item label="类型" prop="category">
      <el-select v-model="form.category" placeholder="请选择类型">
        <el-option v-for="cat in categories" :key="cat.category_id" :label="cat.name" :value="cat.category_id" />
      </el-select>
    </el-form-item>
    <el-form-item label="标签">
      <el-select v-model="form.tags" multiple filterable allow-create placeholder="添加标签">
        <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
      </el-select>
    </el-form-item>
    <el-form-item label="封面图片" prop="coverImage">
      <el-upload
        class="avatar-uploader"
        action="#"
        :show-file-list="false"
        :on-change="handleImageChange"
        :before-upload="beforeUpload"
      >
        <img v-if="form.coverImage" :src="form.coverImage" class="avatar" />
        <i v-else class="el-icon-plus avatar-uploader-icon"></i>
      </el-upload>
    </el-form-item>
    <el-form-item label="简介" prop="description">
      <el-input v-model="form.description" type="textarea" rows="2" placeholder="请输入简介" />
    </el-form-item>
    <el-form-item label="详细介绍" prop="introduction">
      <el-input v-model="form.introduction" type="textarea" rows="4" placeholder="请输入详细介绍" />
    </el-form-item>
    <el-form-item label="加入要求" prop="requirements">
      <el-input v-model="form.requirements" type="textarea" rows="2" placeholder="请输入加入要求" />
    </el-form-item>
    <el-form-item label="最大人数" prop="maxMembers">
      <el-input-number v-model="form.maxMembers" :min="1" :max="999" />
    </el-form-item>
    <el-form-item label="联系方式">
      <el-row :gutter="10">
        <el-col :span="12">
          <el-input v-model="form.qq" placeholder="QQ" />
        </el-col>
        <el-col :span="12">
          <el-input v-model="form.wechat" placeholder="微信" />
        </el-col>
        <el-col :span="12" style="margin-top: 8px;">
          <el-input v-model="form.email" placeholder="邮箱" />
        </el-col>
        <el-col :span="12" style="margin-top: 8px;">
          <el-input v-model="form.phone" placeholder="电话" />
        </el-col>
        <el-col :span="24" style="margin-top: 8px;">
          <el-input v-model="form.address" placeholder="地址" />
        </el-col>
      </el-row>
    </el-form-item>
    <el-form-item label="例会时间">
      <el-input v-model="form.meetingTime" placeholder="例会时间" />
    </el-form-item>
    <el-form-item label="例会地点">
      <el-input v-model="form.meetingLocation" placeholder="例会地点" />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getClubCategoriesList } from '@/api/club'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Object, required: true },
})
const emit = defineEmits(['update:modelValue'])
const form = ref({ ...props.modelValue })
const formRef = ref()
const categories = ref<any[]>([])
const allTags = ref<string[]>([])
const rules = {
  name: [{ required: true, message: '请输入社团名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类型', trigger: 'change' }],
  description: [{ required: true, message: '请输入简介', trigger: 'blur' }],
}

watch(() => props.modelValue, (val) => {
  form.value = { ...val }
})
watch(form, (val) => {
  emit('update:modelValue', val)
}, { deep: true })

const handleImageChange = (file: any) => {
  // 模拟图片上传，实际应替换为真实上传逻辑
  const reader = new FileReader()
  reader.onload = (e: any) => {
    form.value.coverImage = e.target.result
  }
  reader.readAsDataURL(file.raw)
}
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
  }
  return isImage
}
onMounted(async () => {
  categories.value = await getClubCategoriesList()
  // 可选：加载全局标签
  allTags.value = ['学术', '文艺', '体育', '公益', '科技', '创新', '兴趣', '其他']
})
</script>

<style scoped>
.club-edit-form {
  max-width: 600px;
  margin: 0 auto;
}
.avatar-uploader {
  display: inline-block;
}
.avatar {
  width: 80px;
  height: 80px;
  display: block;
  border-radius: 8px;
  object-fit: cover;
}
.avatar-uploader-icon {
  font-size: 32px;
  color: #aaa;
  width: 80px;
  height: 80px;
  line-height: 80px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
}
</style> 