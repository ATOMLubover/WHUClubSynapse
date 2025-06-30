import axios from 'axios'
import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: "http://localhost:22116",
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 添加token
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  },
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 根据接口文档，后端接口返回格式不统一：
    // - 登录接口：直接返回用户对象，token在Header中
    // - 注册接口：返回 { id, username }
    // - ping接口：返回文本 "pong"
    // - 用户信息接口：直接返回用户对象
    // - 验证码接口：返回文本消息
    // - 用户列表接口：返回用户数组
    
    // 直接返回响应，让各个API函数自己处理数据格式
    return response
  },
  (error) => {
    console.error('响应错误:', error)
    // console.log(error.response.status)
    // 统一错误处理
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          ElMessage.error(data || '请求参数错误')
          break
        case 401:
          ElMessage.error(data||'未授权，请重新登录')
          // localStorage.removeItem('token')
          // window.location.href = '/login'
          break
        case 403:
          ElMessage.error(data || '权限不足')
          break
        case 404:
          ElMessage.error(data||'请求的资源不存在')
          break
        case 500:
          ElMessage.error(data||'服务器内部错误')
          break
        case 503:
          ElMessage.error(data||'服务不可用')
          break
        default:
          ElMessage.error(data||'网络错误')
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败')
    } else {
      ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
  },
)

export default request
