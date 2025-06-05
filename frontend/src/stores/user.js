import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 设置用户信息
  const setUser = (userData) => {
    user.value = userData
  }

  // 设置token
  const setToken = (tokenValue) => {
    token.value = tokenValue
    if (tokenValue) {
      localStorage.setItem('token', tokenValue)
      // 设置API默认header
      api.defaults.headers.common['Authorization'] = `Bearer ${tokenValue}`
    } else {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    }
  }

  // 用户登录
  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials)
      const { access_token, user: userData } = response.data
      
      setToken(access_token)
      setUser(userData)
      
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '登录失败')
      return false
    }
  }

  // 用户注册
  const register = async (userInfo) => {
    try {
      await api.post('/auth/register', userInfo)
      ElMessage.success('注册成功，请登录')
      return true
    } catch (error) {
      ElMessage.error(error.response?.data?.detail || '注册失败')
      return false
    }
  }

  // 用户登出
  const logout = () => {
    setToken('')
    setUser(null)
    ElMessage.success('已退出登录')
  }

  // 获取用户信息
  const getUserInfo = async () => {
    try {
      const response = await api.get('/auth/profile')
      setUser(response.data)
      return response.data
    } catch (error) {
      // token可能已过期
      logout()
      throw error
    }
  }

  // 检查认证状态
  const checkAuthStatus = async () => {
    if (token.value && !user.value) {
      try {
        await getUserInfo()
        return true
      } catch (error) {
        // token无效，清除状态
        logout()
        return false
      }
    }
    // 如果有token且有user，表示已登录
    if (token.value && user.value) {
      return true
    }
    // 没有token，表示未登录
    return false
  }

  // 初始化时设置API header
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  return {
    // 状态
    user: readonly(user),
    token: readonly(token),
    
    // 计算属性
    isLoggedIn,
    
    // 方法
    setUser,
    setToken,
    login,
    register,
    logout,
    getUserInfo,
    checkAuthStatus
  }
}) 