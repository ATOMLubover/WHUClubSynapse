import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  VerifyEmailRequest,
  UserListParams,
  RegisterResponse,
  ApiResponse,
  UserPreferences
} from '@/types'
import { config } from '@/config'

// 模拟延迟
const delay = (ms: number = config.mockDelay) => new Promise((resolve) => setTimeout(resolve, ms))

// 模拟管理员用户
export const mockAdmin: User = {
  user_id: 1,
  username: 'admin',
  email: 'admin@whu.edu.cn',
  avatar_url: 'https://picsum.photos/100/100?random=1',
  role: 'admin',
  last_active: '2024-01-25T10:30:00Z',
  id: 1, // 兼容字段
  realName: '系统管理员',
  studentId: '2021001001',
  major: '计算机科学与技术',
  phone: '13800138001',
  created_at: '2024-01-01T00:00:00Z',
  status: 'active'
}

// 模拟普通用户
export const mockUser: User = {
  user_id: 2,
  username: 'testuser',
  email: 'test@whu.edu.cn',
  avatar_url: 'https://picsum.photos/100/100?random=2',
  role: 'user',
  last_active: '2024-01-25T09:15:00Z',
  id: 2, // 兼容字段
  realName: '测试用户',
  studentId: '2021002001',
  major: '软件工程',
  phone: '13800138002',
  created_at: '2024-01-15T10:00:00Z',
  status: 'active',
  stats: {
    appliedClubs: 2,
    joinedClubs: 3,
    managedClubs: 1,
    favoriteClubs: 5,
  },
  preferences: {
    interestedCategories: [
      { category_id: 0, name: '学术科技' },
      { category_id: 1, name: '文艺体育' }
    ],
    emailNotifications: true,
    applicationNotifications: true,
    activityNotifications: false,
    profilePublic: true,
    showJoinedClubs: true,
    tags: ['编程', '音乐', '运动'],
  },
  hasCompletedPreferences: true,
  tags: ['编程', '音乐', '运动'],
}

// 1. 模拟用户登录
export const mockLogin = async (
  data: LoginRequest,
): Promise<{ data: User; token: string }> => {
  await delay()

  // 简单的模拟验证
  if (data.username === 'demo' && data.password === '123456') {
    return {
      data: mockUser,
      token: 'mock_jwt_token_' + Date.now(),
    }
  } else if (data.username === 'admin' && data.password === 'admin123') {
    return {
      data: mockAdmin,
      token: 'mock_jwt_token_admin_' + Date.now(),
    }
  } else {
    throw new Error('用户名或密码错误')
  }
}

// 2. 模拟发送邮箱验证码
export const mockSendVerifyEmail = async (
  data: VerifyEmailRequest,
): Promise<string> => {
  await delay(800)
  
  // 模拟已存在验证码的情况（返回202状态码的模拟）
  if (data.email === 'existing@example.com') {
    throw new Error('验证码已存在')
  }
  
  return `邮件已发送至${data.email}`
}

// 3. 模拟用户注册
export const mockRegister = async (
  data: RegisterRequest,
): Promise<RegisterResponse> => {
  await delay(1200)

  // 模拟验证码验证
  if (data.vrfcode !== '1234') {
    throw new Error('验证码错误或失效')
  }

  // 模拟用户名或邮箱已存在
  if (data.username === 'admin' || data.email === 'admin@example.com') {
    throw new Error('用户名或邮箱已存在')
  }

  return {
    user_id: Date.now(),
    username: data.username,
  }
}

// 4. 模拟根据ID获取用户信息
export const mockGetUserById = async (id: number): Promise<User> => {
  await delay(500)

  if (id === 1) {
    return mockAdmin
  } else if (id === 2233) {
    return mockUser
  } else {
    throw new Error('用户不存在')
  }
}

// 5. 模拟管理员获取用户列表
export const mockGetUserList = async (params: UserListParams): Promise<User[]> => {
  await delay(600)

  // 模拟权限检查
  // 在实际使用中，这个检查应该在请求拦截器中处理
  
  // 生成模拟用户数据
  const mockUsers: User[] = [
    {
      user_id: 1,
      username: 'admin',
      email: 'admin@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=1',
      role: 'admin',
      last_active: '2024-01-25T10:30:00Z',
      id: 1, // 兼容字段
      realName: '系统管理员',
      studentId: '2021001001',
      major: '计算机科学与技术',
      phone: '13800138001',
      created_at: '2024-01-01T00:00:00Z',
      status: 'active'
    },
    {
      user_id: 2,
      username: 'zhangsan',
      email: 'zhangsan@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=2',
      role: 'user',
      last_active: '2024-01-25T09:15:00Z',
      id: 2, // 兼容字段
      realName: '张三',
      studentId: '2021002001',
      major: '软件工程',
      phone: '13800138002',
      created_at: '2024-01-15T10:00:00Z',
      status: 'active'
    },
    {
      user_id: 3,
      username: 'lisi',
      email: 'lisi@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=3',
      role: 'user',
      last_active: '2024-01-24T16:45:00Z',
      id: 3, // 兼容字段
      realName: '李四',
      studentId: '2021003001',
      major: '信息安全',
      phone: '13800138003',
      created_at: '2024-01-10T14:30:00Z',
      status: 'active'
    },
    {
      user_id: 4,
      username: 'wangwu',
      email: 'wangwu@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=4',
      role: 'user',
      last_active: '2024-01-23T11:20:00Z',
      id: 4, // 兼容字段
      realName: '王五',
      studentId: '2021004001',
      major: '人工智能',
      phone: '13800138004',
      created_at: '2024-01-05T09:15:00Z',
      status: 'disabled'
    },
    {
      user_id: 5,
      username: 'zhaoliu',
      email: 'zhaoliu@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=5',
      role: 'user',
      last_active: '2024-01-25T08:30:00Z',
      id: 5, // 兼容字段
      realName: '赵六',
      studentId: '2021005001',
      major: '数据科学',
      phone: '13800138005',
      created_at: '2024-01-20T16:00:00Z',
      status: 'active'
    },
    {
      user_id: 6,
      username: 'qianqi',
      email: 'qianqi@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=6',
      role: 'user',
      last_active: '2024-01-22T13:45:00Z',
      id: 6, // 兼容字段
      realName: '钱七',
      studentId: '2021006001',
      major: '网络工程',
      phone: '13800138006',
      created_at: '2024-01-12T11:30:00Z',
      status: 'active'
    },
    {
      user_id: 7,
      username: 'sunba',
      email: 'sunba@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=7',
      role: 'user',
      last_active: '2024-01-21T15:20:00Z',
      id: 7, // 兼容字段
      realName: '孙八',
      studentId: '2021007001',
      major: '计算机科学与技术',
      phone: '13800138007',
      created_at: '2024-01-08T10:45:00Z',
      status: 'active'
    },
    {
      user_id: 8,
      username: 'zhoujiu',
      email: 'zhoujiu@whu.edu.cn',
      avatar_url: 'https://picsum.photos/100/100?random=8',
      role: 'user',
      last_active: '2024-01-20T12:10:00Z',
      id: 8, // 兼容字段
      realName: '周九',
      studentId: '2021008001',
      major: '软件工程',
      phone: '13800138008',
      created_at: '2024-01-03T14:20:00Z',
      status: 'active'
    }
  ]
  
  // 模拟分页返回
  const start = params.offset
  const end = start + params.num
  
  return mockUsers.slice(start, end)
}

// 6. 模拟ping
export const mockPing = async (): Promise<string> => {
  await delay(100)
  return 'pong'
}

// 模拟获取当前用户信息
export const mockGetCurrentUser = async (): Promise<User> => {
  await delay(500)
  return mockUser
}

// 模拟用户退出登录
export const mockLogout = async (): Promise<ApiResponse<null>> => {
  await delay(300)
  return {
    code: 200,
    message: '退出成功',
    data: null,
  }
}

//模拟更新用户偏好
export const mockUpdateUserPreferences=async(preferences: UserPreferences)=>{
  await delay(300)
  mockUser.hasCompletedPreferences=true;
  mockUser.preferences=preferences;
  return {data:mockUser}

}


