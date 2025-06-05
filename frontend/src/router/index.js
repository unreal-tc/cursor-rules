import { createRouter, createWebHistory } from 'vue-router'
import NProgress from 'nprogress'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/cursor-rule/:id',
        name: 'CursorRuleDetail',
        component: () => import('@/views/CursorRuleDetail.vue'),
        meta: { title: 'Cursor Rule详情' }
      },
      {
        path: '/create',
        name: 'CreateCursorRule',
        component: () => import('@/views/CreateCursorRule.vue'),
        meta: { title: '创建Cursor Rule', requiresAuth: true }
      },
      {
        path: '/edit/:id',
        name: 'EditCursorRule',
        component: () => import('@/views/EditCursorRule.vue'),
        meta: { title: '编辑Cursor Rule', requiresAuth: true }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 全局前置守卫
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - Cursor Rules` : 'Cursor Rules'
  
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    const userStore = useUserStore()
    
    // 异步检查认证状态
    const isAuthenticated = await userStore.checkAuthStatus()
    
    if (!isAuthenticated) {
      ElMessage.warning('请先登录')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 如果已登录用户访问登录/注册页面，重定向到首页
  if ((to.name === 'Login' || to.name === 'Register')) {
    const userStore = useUserStore()
    const isAuthenticated = await userStore.checkAuthStatus()
    if (isAuthenticated) {
      next({ name: 'Home' })
      return
    }
  }
  
  next()
})

// 全局后置守卫
router.afterEach(() => {
  NProgress.done()
})

export default router 