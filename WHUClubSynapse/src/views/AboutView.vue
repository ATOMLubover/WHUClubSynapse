<template>
  <div class="about-container">
    <!-- 顶部 Banner -->
    <el-backtop />
    <div class="hero-section">
      <el-row class="hero-content" justify="center" align="middle">
        <el-col :xs="24" :sm="20" :md="16" :lg="12">
          <div class="hero-text">
            <h1 class="hero-title">
              <el-icon class="hero-icon"><Star /></el-icon>
              WHU Club Synapse
            </h1>
            <p class="hero-subtitle">武汉大学社团管理系统</p>
            <div class="hero-tags">
              <el-tag type="primary" size="large" effect="dark">Vue 3</el-tag>
              <el-tag type="success" size="large" effect="dark">TypeScript</el-tag>
              <el-tag type="warning" size="large" effect="dark">Element Plus</el-tag>
              <el-tag type="danger" size="large" effect="dark">Pinia</el-tag>
            </div>
            <div class="hero-buttons">
              <el-button type="primary" size="large" @click="scrollToSection('features')">
                <el-icon><View /></el-icon>
                探索功能
              </el-button>
              <el-button size="large" @click="openGithub">
                <el-icon><Link /></el-icon>
                GitHub
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 统计数据 -->
    <el-row class="stats-section" :gutter="30" justify="center">
      <el-col :xs="12" :sm="6" :md="6" :lg="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" :style="{ color: stat.color }">
              <component :is="stat.icon" />
            </el-icon>
            <div class="stat-number">
              <el-statistic
                :value="stat.value"
                :precision="0"
                :value-style="{ color: stat.color, fontSize: '24px', fontWeight: 'bold' }"
              />
            </div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能特色 -->
    <div id="features" class="features-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><Cpu /></el-icon>
          核心功能
        </h2>
        <p class="section-subtitle">现代化的社团管理解决方案</p>
      </div>

      <el-row :gutter="30" justify="center">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="feature in features" :key="feature.title">
          <el-card class="feature-card" shadow="hover" @click="showFeatureDetails(feature)">
            <template #header>
              <div class="feature-header">
                <el-icon class="feature-icon" :style="{ color: feature.color }">
                  <component :is="feature.icon" />
                </el-icon>
                <span class="feature-title">{{ feature.title }}</span>
              </div>
            </template>
            <div class="feature-content">
              <p>{{ feature.description }}</p>
              <div class="feature-progress">
                <el-progress
                  :percentage="feature.progress"
                  :color="feature.color"
                  :stroke-width="8"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 技术栈展示 -->
    <div class="tech-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><Setting /></el-icon>
          技术栈
        </h2>
      </div>

      <el-row :gutter="20" justify="center">
        <el-col :span="16">
          <el-carousel height="300px" :interval="4000" indicator-position="outside">
            <el-carousel-item v-for="techGroup in techStacks" :key="techGroup.category">
              <div class="tech-slide">
                <h3 class="tech-category">{{ techGroup.category }}</h3>
                <div class="tech-grid">
                  <div
                    v-for="tech in techGroup.technologies"
                    :key="tech.name"
                    class="tech-item"
                    @click="showTechDetails(tech)"
                  >
                    <el-tooltip :content="tech.description" placement="top">
                      <el-tag :type="tech.type" size="large" effect="dark" class="tech-tag">
                        <el-icon class="tech-tag-icon">
                          <component :is="tech.icon" />
                        </el-icon>
                        {{ tech.name }}
                      </el-tag>
                    </el-tooltip>
                  </div>
                </div>
              </div>
            </el-carousel-item>
          </el-carousel>
        </el-col>
      </el-row>
    </div>

    <!-- 项目时间线 -->
    <div class="timeline-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><Clock /></el-icon>
          开发历程
        </h2>
      </div>

      <el-timeline>
        <el-timeline-item
          v-for="milestone in milestones"
          :key="milestone.date"
          :timestamp="milestone.date"
          :type="milestone.type"
          :icon="milestone.icon"
          :size="milestone.size"
        >
          <el-card class="timeline-card">
            <h4>{{ milestone.title }}</h4>
            <p>{{ milestone.description }}</p>
            <div v-if="milestone.tags" class="timeline-tags">
              <el-tag v-for="tag in milestone.tags" :key="tag" size="small" class="timeline-tag">
                {{ tag }}
              </el-tag>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 团队介绍 -->
    <div class="team-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon><User /></el-icon>
          开发团队
        </h2>
        <p class="section-subtitle">武汉大学计算机学院2024级本科生</p>
      </div>

      <el-row :gutter="30" justify="center">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="member in teamMembers" :key="member.name">
          <el-card class="team-card" shadow="hover">
            <div class="team-avatar">
              <el-avatar :size="80" :src="member.avatar" :icon="UserFilled" />
              <div class="team-status">
                <el-badge :value="member.commits" :max="99" class="commit-badge">
                  <el-icon><EditPen /></el-icon>
                </el-badge>
              </div>
            </div>
            <div class="team-info">
              <h3 class="team-name">{{ member.name }}</h3>
              <p class="team-role">{{ member.role }}</p>
              <div class="team-skills">
                <el-tag v-for="skill in member.skills" :key="skill" size="small" class="skill-tag">
                  {{ skill }}
                </el-tag>
              </div>
              <div class="team-contact">
                <el-button
                  v-for="contact in member.contacts"
                  :key="contact.type"
                  :icon="contact.icon"
                  circle
                  size="small"
                  @click="openLink(contact.url)"
                />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 互动评分区域 -->
    <div class="rating-section">
      <el-card class="rating-card">
        <template #header>
          <div class="rating-header">
            <el-icon><Star /></el-icon>
            <span>为项目评分</span>
          </div>
        </template>
        <div class="rating-content">
          <el-rate
            v-model="userRating"
            size="large"
            show-text
            :texts="ratingTexts"
            @change="handleRatingChange"
          />
          <div class="rating-stats">
            <el-progress
              v-for="(count, index) in ratingStats"
              :key="index"
              :percentage="(count / totalRatings) * 100"
              :format="() => `${index + 1}星 (${count})`"
              class="rating-bar"
            />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 联系我们 -->
    <div class="contact-section">
      <el-row :gutter="30">
        <el-col :xs="24" :md="12">
          <el-card class="contact-card">
            <template #header>
              <h3>
                <el-icon><Message /></el-icon> 联系方式
              </h3>
            </template>
            <div class="contact-info">
              <div class="contact-item">
                <el-icon><Location /></el-icon>
                <span>武汉大学计算机学院</span>
              </div>
              <div class="contact-item">
                <el-icon><Message /></el-icon>
                <span>club-system@whu.edu.cn</span>
              </div>
              <div class="contact-item">
                <el-icon><Link /></el-icon>
                <el-link href="https://github.com/ATOMLubover/WHUClubSynapse/" target="_blank">
                  GitHub 仓库
                </el-link>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="12">
          <el-card class="feedback-card">
            <template #header>
              <h3>
                <el-icon><ChatDotRound /></el-icon> 反馈建议
              </h3>
            </template>
            <el-form ref="feedbackForm" :model="feedback" label-position="top">
              <el-form-item label="您的建议">
                <el-input
                  v-model="feedback.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入您的建议或反馈..."
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitFeedback" :loading="submitting">
                  <el-icon><Position /></el-icon>
                  提交反馈
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  Star,
  View,
  Link,
  User,
  UserFilled,
  EditPen,
  Cpu,
  Setting,
  Clock,
  Message,
  Location,
  ChatDotRound,
  Position,
  DataLine, // 数据线
  Finished,
  Tools,
  Management,
  Search,
  Bell,
  TrendCharts,
} from '@element-plus/icons-vue'

// 统计数据
const stats = ref([
  { icon: User, value: 1000, label: '注册用户', color: '#409EFF' },
  { icon: Management, value: 50, label: '活跃社团', color: '#67C23A' },
  { icon: Finished, value: 200, label: '成功申请', color: '#E6A23C' },
  { icon: TrendCharts, value: 95, label: '满意度%', color: '#F56C6C' },
])

// 功能特色
const features = ref([
  {
    icon: Search,
    title: '智能搜索',
    description: '支持多维度筛选，快速找到心仪社团',
    progress: 95,
    color: '#409EFF',
  },
  {
    icon: Management,
    title: '社团管理',
    description: '完善的社团管理系统，提升管理效率',
    progress: 90,
    color: '#67C23A',
  },
  {
    icon: Bell,
    title: '消息通知',
    description: '实时消息推送，不错过任何重要信息',
    progress: 85,
    color: '#E6A23C',
  },
])

// 技术栈
const techStacks = ref([
  {
    category: '前端技术',
    technologies: [
      { name: 'Vue 3', type: 'primary', icon: 'View', description: '渐进式 JavaScript 框架' },
      { name: 'TypeScript', type: 'success', icon: 'Document', description: '静态类型检查' },
      { name: 'Element Plus', type: 'warning', icon: 'Star', description: 'Vue 3 组件库' },
      { name: 'Pinia', type: 'danger', icon: 'DataLine', description: '状态管理库' },
    ],
  },
  {
    category: '开发工具',
    technologies: [
      { name: 'Vite', type: 'primary', icon: 'Lightning', description: '快速构建工具' },
      { name: 'ESLint', type: 'success', icon: 'Check', description: '代码检查工具' },
      { name: 'Git', type: 'warning', icon: 'ForkSpoon', description: '版本控制系统' },
      { name: 'VS Code', type: 'danger', icon: 'Edit', description: '代码编辑器' },
    ],
  },
])

// 开发里程碑
const milestones = ref([
  {
    date: '2024-12',
    title: '项目启动',
    description: '确定项目需求，开始技术选型和架构设计',
    type: 'primary',
    icon: 'Star',
    size: 'large',
    tags: ['需求分析', '技术选型'],
  },
  {
    date: '2024-12',
    title: '前端开发',
    description: '完成用户界面设计，实现核心功能模块',
    type: 'success',
    icon: 'Check',
    size: 'large',
    tags: ['UI设计', '组件开发'],
  },
  {
    date: '2024-12',
    title: '功能完善',
    description: '优化用户体验，添加高级功能和动画效果',
    type: 'warning',
    icon: 'Tools',
    size: 'large',
    tags: ['性能优化', '用户体验'],
  },
  {
    date: '2024-12',
    title: '项目发布',
    description: '完成测试，正式发布第一个版本',
    type: 'danger',
    icon: 'Trophy',
    size: 'large',
    tags: ['测试', '发布'],
  },
])

// 团队成员
const teamMembers = ref([
  {
    name: '马之涵',
    role: '项目负责人 & 全栈开发',
    avatar: '',
    skills: ['Vue 3', 'TypeScript', 'Node.js', '项目管理'],
    commits: 156,
    contacts: [
      { type: 'github', icon: 'Link', url: 'https://github.com/ATOMLubover' },
      { type: 'email', icon: 'Message', url: 'mailto:mazihan@whu.edu.cn' },
    ],
  },
])

// 评分系统
const userRating = ref(0)
const ratingTexts = ['太差了', '差', '一般', '好', '太棒了']
const ratingStats = ref([12, 5, 8, 25, 45]) // 1-5星的统计
const totalRatings = ref(95)

// 反馈表单
const feedback = reactive({
  content: '',
})
const submitting = ref(false)

// 方法
const scrollToSection = (sectionId: string) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const openGithub = () => {
  window.open('https://github.com/ATOMLubover/WHUClubSynapse/', '_blank')
}

const openLink = (url: string) => {
  window.open(url, '_blank')
}

const showFeatureDetails = (feature: any) => {
  ElNotification({
    title: feature.title,
    message: feature.description,
    type: 'info',
    duration: 3000,
  })
}

const showTechDetails = (tech: any) => {
  ElMessage({
    message: `${tech.name}: ${tech.description}`,
    type: 'info',
  })
}

const handleRatingChange = (value: number) => {
  ElMessage({
    message: `感谢您的评分：${value}星`,
    type: 'success',
  })
}

const submitFeedback = async () => {
  if (!feedback.content.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }

  submitting.value = true

  // 模拟提交
  setTimeout(() => {
    submitting.value = false
    feedback.content = ''
    ElMessage.success('反馈提交成功，感谢您的建议！')
  }, 1000)
}
</script>

<style scoped>
.about-container {
  min-height: 100vh;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 100px 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.hero-content {
  position: relative;
  z-index: 2;
}

.hero-title {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInDown 1s ease-out;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translate3d(0, -100%, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.hero-icon {
  font-size: 3rem;
  margin-right: 1rem;
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0.9;
  animation: slideInUp 1s ease-out 0.3s both;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translate3d(0, 100%, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.hero-tags {
  margin-bottom: 2rem;
  animation: fadeIn 1s ease-out 0.6s both;
}

.hero-tags .el-tag {
  margin: 0 0.5rem;
  font-size: 1rem;
  padding: 0.5rem 1rem;
}

.hero-buttons {
  animation: fadeIn 1s ease-out 0.9s both;
}

.hero-buttons .el-button {
  margin: 0 1rem;
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Stats Section */
.stats-section {
  padding: 80px 20px;
  background: linear-gradient(45deg, #f0f2f5 0%, #ffffff 100%);
}

.stat-card {
  text-align: center;
  border: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.stat-content {
  padding: 1rem;
}

.stat-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
}

.stat-number {
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #666;
  font-size: 1rem;
  font-weight: 500;
}

/* Section Headers */
.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-title {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.section-subtitle {
  font-size: 1.2rem;
  color: #666;
}

/* Features Section */
.features-section {
  padding: 80px 20px;
  background: #fff;
}

.feature-card {
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.feature-icon {
  font-size: 1.5rem;
}

.feature-title {
  font-weight: 600;
  font-size: 1.1rem;
}

.feature-content p {
  margin-bottom: 1rem;
  color: #666;
  line-height: 1.6;
}

.feature-progress {
  margin-top: 1rem;
}

/* Tech Section */
.tech-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tech-slide {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
}

.tech-category {
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  width: 100%;
  max-width: 600px;
}

.tech-item {
  display: flex;
  justify-content: center;
}

.tech-tag {
  padding: 0.8rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tech-tag:hover {
  transform: scale(1.1);
}

.tech-tag-icon {
  font-size: 1.1rem;
}

/* Timeline Section */
.timeline-section {
  padding: 80px 20px;
  background: #f8f9fa;
}

.timeline-card {
  margin-left: 1rem;
}

.timeline-card h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.2rem;
}

.timeline-card p {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.timeline-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.timeline-tag {
  margin: 0;
}

/* Team Section */
.team-section {
  padding: 80px 20px;
  background: #fff;
}

.team-card {
  text-align: center;
  height: 100%;
  transition: all 0.3s ease;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.team-avatar {
  position: relative;
  margin-bottom: 1rem;
}

.team-status {
  position: absolute;
  top: 0;
  right: 50%;
  transform: translateX(50%);
}

.commit-badge {
  background: transparent;
}

.team-info {
  padding: 1rem;
}

.team-name {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
  color: #333;
}

.team-role {
  color: #666;
  margin-bottom: 1rem;
  font-style: italic;
}

.team-skills {
  margin-bottom: 1rem;
}

.skill-tag {
  margin: 0.2rem;
}

.team-contact {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

/* Rating Section */
.rating-section {
  padding: 80px 20px;
  background: linear-gradient(45deg, #f0f2f5 0%, #ffffff 100%);
  text-align: center;
}

.rating-card {
  max-width: 600px;
  margin: 0 auto;
}

.rating-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.rating-content {
  padding: 2rem;
}

.rating-stats {
  margin-top: 2rem;
}

.rating-bar {
  margin-bottom: 1rem;
}

/* Contact Section */
.contact-section {
  padding: 80px 20px;
  background: #fff;
}

.contact-card,
.feedback-card {
  height: 100%;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
  font-size: 1.1rem;
}

.contact-item .el-icon {
  color: #409eff;
  font-size: 1.2rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .section-title {
    font-size: 2rem;
    flex-direction: column;
    gap: 0.5rem;
  }

  .hero-buttons .el-button {
    display: block;
    margin: 0.5rem auto;
    width: 200px;
  }

  .hero-tags .el-tag {
    display: block;
    margin: 0.3rem auto;
    width: fit-content;
  }
}

/* 自定义动画 */
.bounce-enter-active {
  animation: bounce-in 0.5s;
}

.bounce-leave-active {
  animation: bounce-in 0.5s reverse;
}

@keyframes bounce-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}
</style>
