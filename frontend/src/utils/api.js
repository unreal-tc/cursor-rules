import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 处理响应错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未认证，清除token并跳转到登录页
          localStorage.removeItem('token')
          ElMessage.error('登录已过期，请重新登录')
          // 如果不在登录页面，则跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 422:
          // 表单验证错误
          if (data.detail && Array.isArray(data.detail)) {
            const errorMsg = data.detail.map(err => err.msg).join(', ')
            ElMessage.error(errorMsg)
          } else {
            ElMessage.error(data.detail || '请求参数错误')
          }
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.detail || data.message || '请求失败')
      }
    } else if (error.request) {
      // 网络错误
      ElMessage.error('网络连接失败，请检查网络')
    } else {
      // 其他错误
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default api 