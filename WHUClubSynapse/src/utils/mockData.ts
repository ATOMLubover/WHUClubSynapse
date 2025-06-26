import type { Application, Club, User, ClubPost, ClubPostReply } from '@/types'

// 模拟社团数据
export const mockClubs: Club[] = [
  {
    id: '1',
    name: '计算机科学协会',
    description:
      '致力于推广计算机科学知识，组织编程竞赛和技术分享活动。为同学们提供学习交流的平台，提升编程能力和技术水平。',
    coverImage: 'https://picsum.photos/400/240?random=1',
    category: '学术科技',
    adminId: 'admin1',
    adminName: '张三',
    currentMembers: 85,
    maxMembers: 100,
    tags: ['编程', '算法', '竞赛'],
    isHot: true,
    status: 'pending',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-20T15:30:00Z',
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学计算机科学协会',
    isFavorite: true,
  },
  {
    id: '2',
    name: '摄影艺术社',
    description:
      '用镜头记录美好，用光影诉说故事。我们定期组织外拍活动，分享摄影技巧，举办摄影展览。',
    coverImage: 'https://picsum.photos/400/240?random=2',
    category: '文艺体育',
    adminId: 'admin2',
    adminName: '李四',
    currentMembers: 60,
    maxMembers: 60,
    tags: ['摄影', '艺术', '创作'],
    isHot: false,
    status: 'not_applied',
    createdAt: '2024-01-10T14:00:00Z',
    updatedAt: '2024-01-18T09:15:00Z',
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学摄影艺术社',
    isFavorite: false,
  },
  {
    id: '3',
    name: '青年志愿者协会',
    description: '奉献爱心，服务社会。组织各类志愿服务活动，传播正能量，为社会贡献青春力量。',
    coverImage: 'https://picsum.photos/400/240?random=3',
    category: '志愿服务',
    adminId: 'admin3',
    adminName: '王五',
    currentMembers: 150,
    maxMembers: 150,
    tags: ['志愿', '公益', '服务'],
    isHot: true,
    status: 'not_applied',
    createdAt: '2024-01-08T16:30:00Z',
    updatedAt: '2024-01-22T11:45:00Z',
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学青年志愿者协会',
    isFavorite: false,
  },
  {
    id: '4',
    name: '创业实践社',
    description: '培养创新思维，践行创业梦想。为有创业想法的同学提供平台，组织创业大赛和项目孵化。',
    coverImage: 'https://picsum.photos/400/240?random=4',
    category: '创新创业',
    adminId: 'admin4',
    adminName: '赵六',
    currentMembers: 35,
    maxMembers: 50,
    tags: ['创业', '创新', '商业'],
    isHot: false,
    status: 'not_applied',
    createdAt: '2024-01-12T08:00:00Z',
    updatedAt: '2024-01-19T14:20:00Z',
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学创业实践社',
    isFavorite: false,
  },
  {
    id: '5',
    name: '篮球社',
    description: '挥洒汗水，释放激情。定期组织篮球训练和比赛，提高球技，增强体质，培养团队精神。',
    coverImage: 'https://picsum.photos/400/240?random=5',
    category: '文艺体育',
    adminId: 'admin5',
    adminName: '孙七',
    currentMembers: 67,
    maxMembers: 80,
    tags: ['篮球', '运动', '团队'],
    isHot: true,
    status: 'not_applied',
    createdAt: '2024-01-05T20:00:00Z',
    updatedAt: '2024-01-25T16:10:00Z',
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学篮球社',
    isFavorite: false,
  },
  {
    id: '6',
    name: '机器人研究社',
    description: '探索人工智能的奥秘，动手制作智能机器人。参与机器人竞赛，推动科技创新发展。',
    coverImage: 'https://picsum.photos/400/240?random=6',
    category: '学术科技',
    adminId: 'admin6',
    adminName: '周八',
    currentMembers: 28,
    maxMembers: 40,
    tags: ['机器人', '人工智能', '科技'],
    isHot: false,
    status: 'not_applied',
    createdAt: '2024-01-18T12:30:00Z',
    updatedAt: '2024-01-24T10:05:00Z',
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学机器人研究社',
    isFavorite: false,
  },
  {
    id: '7',
    name: '音乐社',
    description:
      '用音乐传递情感，用歌声温暖人心。我们有吉他、钢琴、声乐等多个分部，定期举办音乐会。',
    coverImage: 'https://picsum.photos/400/240?random=7',
    category: '文艺体育',
    adminId: 'admin7',
    adminName: '吴九',
    currentMembers: 55,
    maxMembers: 70,
    tags: ['音乐', '演出', '艺术'],
    isHot: false,
    status: 'not_applied',
    createdAt: '2024-01-07T19:15:00Z',
    updatedAt: '2024-01-21T13:40:00Z',
    isFavorite: false,
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学音乐社',
  },
  {
    id: '8',
    name: '环保行动社',
    description: '保护环境，从我做起。组织环保宣传活动，参与垃圾分类推广，倡导绿色生活方式。',
    coverImage: 'https://picsum.photos/400/240?random=8',
    category: '志愿服务',
    adminId: 'admin8',
    adminName: '郑十',
    currentMembers: 73,
    maxMembers: 90,
    tags: ['环保', '绿色', '公益'],
    isHot: true,
    status: 'approved',
    createdAt: '2024-01-14T11:20:00Z',
    updatedAt: '2024-01-23T17:25:00Z',
    isFavorite: false,
    qq: '1234567890',
    details: '加入我们，你将获得：专业的技能培训和指导、丰富的实践项目机会、志同道合的伙伴和导师、个人能力的全面提升',
    activities:  [ {
      id: 1,
      title: '新成员见面会',
      description: '欢迎新成员加入我们的大家庭，一起了解社团文化和未来规划。',
      time: '2024-01-25 14:00',
    },
    {
      id: 2,
      title: '技能培训讲座',
      description: '邀请专业导师分享实用技能，提升成员专业能力。',
      time: '2024-01-20 19:00',
    },
    {
      id: 3,
      title: '团建活动',
      description: '增进成员之间的友谊，加强团队凝聚力。',
      time: '2024-01-18 15:30',
    },],
    location: '武汉大学环保行动社',
  },
]

// 模拟用户数据
export const mockUser: User = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  avatar_url: 'https://avatars.githubusercontent.com/u/1?v=4',
  role: 'user',
  last_active: '2024-01-01T00:00:00Z',
  realName: '测试用户',
  major: '计算机学院',
  phone: '13800138000',
  createdAt: '2024-01-01T00:00:00Z',
  emailVerified: '',
  phoneVerified: '',
  bio: '',
  // 用户统计信息
  stats: {
    appliedClubs: 1,
    favoriteClubs: 1,
    joinedClubs: 3,
    managedClubs: 0
  },
  // 用户偏好设置
  preferences: {
    interestedCategories: ['学术科技', '文艺体育'],
    emailNotifications: true,
    applicationNotifications: true,
    activityNotifications: false,
    profilePublic: true,
    showJoinedClubs: true,
  },
  // 是否已完成偏好设置
  hasCompletedPreferences: true,
  tags: [],
}

export const mockApplications: Application[] = [
  {
    id: '1',
    userId: 'user1',
    clubId: '1',
    clubName: '计算机科学协会',
    clubCoverImage: mockClubs[0].coverImage,
    status: 'pending',
    reason: '希望能够加入学习相关技术',
    applyReason: '对技术很感兴趣',
    createdAt: '2024-01-01T00:00:00Z',
    reviewedAt: '2024-01-01T00:00:00Z',
    clubCategory: '学术科技',
    feedback: '欢迎加入我们，请等待审核',
  },
]

// 用户特质与爱好标签
export const allUserTags: string[] = [
  '开朗外向', '沉稳内敛', '乐观积极', '谨慎细致', '创新冒险', '耐心温和', '直率坦诚', '理性冷静', '感性文艺', '独立果断',
  '团队协作', '领导力强', '善于倾听', '幽默风趣', '追求完美', '适应力强', '抗压性好', '好奇心强', '执行力强', '善于沟通',
  '同理心强', '逻辑清晰', '想象力丰富', '坚韧不拔', '谦逊有礼', '热情奔放', '细心周到', '包容开放', '目标明确', '灵活应变',
  '编程开发', '数据分析', '摄影摄像', '绘画设计', '音乐创作', '乐器演奏（钢琴 / 吉他 / 小提琴等）', '舞蹈表演', '戏剧影视', '文学写作', '诗词鉴赏',
  '历史研究', '哲学思辨', '心理学探索', '户外运动（登山 / 跑步 / 骑行等）', '球类运动（篮球 / 足球 / 羽毛球等）', '棋类游戏（围棋 / 象棋 / 国际象棋等）', '手工制作（陶艺 / 木工 / 编织等）', '志愿服务', '公益活动组织', '商业实践',
  '创新创业', '投资理财', '语言学习（英语 / 日语 / 法语等）', '跨文化交流', '新媒体运营', '社交媒体营销', '短视频创作', '美食烹饪', '咖啡品鉴', '茶文化研究',
  '读书分享', '学术竞赛', '科研项目', '数学建模', '机器人研发', '人工智能', '区块链技术', '虚拟现实', '摄影后期', '平面设计',
  '服装设计', '书法练习', '武术搏击', '瑜伽冥想', '天文观测', '地理探索', '生物多样性保护', '环保行动', '非遗传承', '传统文化研习'
]

export const mockClubPosts: ClubPost[] = [
  {
    id: 'p1',
    clubId: '1',
    title: '新学期社团纳新活动讨论',
    content: '大家对今年的纳新活动有什么建议？欢迎留言讨论！',
    authorId: 1,
    authorName: '小明',
    authorAvatar: '',
    createdAt: '2024-06-01T10:00:00Z',
    replyCount: 2
  },
  {
    id: 'p2',
    clubId: '1',
    title: '编程比赛组队贴',
    content: '有想参加编程比赛的小伙伴吗？可以在这里留言组队！',
    authorId: 2,
    authorName: '小红',
    authorAvatar: '',
    createdAt: '2024-06-02T12:00:00Z',
    replyCount: 1
  },
  {
    id: 'p3',
    clubId: '2',
    title: '摄影外拍活动报名',
    content: '本周末有摄影外拍活动，欢迎大家报名参加！',
    authorId: 3,
    authorName: '小刚',
    authorAvatar: '',
    createdAt: '2024-06-03T09:00:00Z',
    replyCount: 3
  }
]

export const mockClubPostReplies: ClubPostReply[] = [
  // p1
  {
    id: 'r1', postId: 'p1', authorId: 2, authorName: '小红', authorAvatar: '', content: '我觉得可以多做一些线上宣传！', createdAt: '2024-06-01T11:00:00Z'
  },
  {
    id: 'r2', postId: 'p1', authorId: 3, authorName: '小刚', authorAvatar: '', content: '建议邀请学长学姐分享经验。', createdAt: '2024-06-01T12:00:00Z'
  },
  // p2
  {
    id: 'r3', postId: 'p2', authorId: 1, authorName: '小明', authorAvatar: '', content: '我报名！', createdAt: '2024-06-02T13:00:00Z'
  },
  // p3
  {
    id: 'r4', postId: 'p3', authorId: 2, authorName: '小红', authorAvatar: '', content: '我也想参加！', createdAt: '2024-06-03T10:00:00Z'
  },
  {
    id: 'r5', postId: 'p3', authorId: 3, authorName: '小明', authorAvatar: '', content: '请问需要自带相机吗？', createdAt: '2024-06-03T10:30:00Z'
  },
  {
    id: 'r6', postId: 'p3', authorId: 3, authorName: '小刚', authorAvatar: '', content: '可以自带，也可以现场借用。', createdAt: '2024-06-03T11:00:00Z'
  }
]