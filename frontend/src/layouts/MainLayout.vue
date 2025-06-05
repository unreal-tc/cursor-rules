<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="container">
        <div class="header-content">
          <!-- Logo和标题 -->
          <div class="logo-section" @click="$router.push('/')">
            <el-icon size="32" color="#409eff">
              <Document />
            </el-icon>
            <h1 class="title">Cursor Rules</h1>
          </div>

          <!-- 导航菜单 -->
          <nav class="nav-menu">
            <el-menu 
              :default-active="activeMenu" 
              mode="horizontal"
              @select="handleMenuSelect"
              class="header-menu"
            >
              <el-menu-item index="/">
                <el-icon><House /></el-icon>
                <span>首页</span>
              </el-menu-item>
              <el-menu-item index="/create" v-if="userStore.isLoggedIn">
                <el-icon><Plus /></el-icon>
                <span>创建</span>
              </el-menu-item>
            </el-menu>
          </nav>

          <!-- 用户区域 -->
          <div class="user-section">
            <template v-if="userStore.isLoggedIn">
              <el-dropdown @command="handleUserCommand">
                <div class="user-info">
                  <el-avatar :size="32">
                    {{ userStore.user?.username?.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <span class="username">{{ userStore.user?.username }}</span>
                  <el-icon><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      个人中心
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" @click="$router.push('/login')">
                登录
              </el-button>
              <el-button @click="$router.push('/register')">
                注册
              </el-button>
            </template>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 底部 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <p>&copy; 2024 Cursor Rules. 专业的程序员AI规则分享平台</p>
          <div class="footer-links">
            <a href="https://github.com" target="_blank">GitHub</a>
            <a href="/docs" target="_blank">API文档</a>
            <a href="mailto:support@cursorrules.com">联系我们</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { 
  Document, House, Plus, User, ArrowDown, SwitchButton 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前激活的菜单项
const activeMenu = computed(() => {
  const path = route.path
  if (path === '/') return '/'
  if (path === '/create') return '/create'
  return '/'
})

// 处理菜单选择
const handleMenuSelect = (index) => {
  router.push(index)
}

// 处理用户下拉菜单命令
const handleUserCommand = (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      userStore.logout()
      router.push('/')
      break
  }
}

// 初始化时检查认证状态
onMounted(() => {
  userStore.checkAuthStatus()
})
</script>

<style lang="scss" scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: var(--bg-color);
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
  }

  .logo-section {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      opacity: 0.8;
    }

    .title {
      font-size: 24px;
      font-weight: 600;
      color: var(--primary-color);
      margin: 0;
    }
  }

  .nav-menu {
    flex: 1;
    margin: 0 40px;

    :deep(.el-menu) {
      border-bottom: none;
      background: transparent;

      .el-menu-item {
        height: 60px;
        line-height: 60px;
        border-bottom: none;
        
        &:hover {
          background-color: var(--fill-light);
        }

        &.is-active {
          background-color: var(--fill-light);
          color: var(--primary-color);
          border-bottom: 2px solid var(--primary-color);
        }
      }
    }
  }

  .user-section {
    display: flex;
    align-items: center;
    gap: 12px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 8px 12px;
      border-radius: 6px;
      transition: background-color 0.3s ease;

      &:hover {
        background-color: var(--fill-light);
      }

      .username {
        font-weight: 500;
        color: var(--text-primary);
      }
    }
  }
}

.main-content {
  flex: 1;
  background-color: var(--bg-light);
}

.footer {
  background: var(--bg-color);
  border-top: 1px solid var(--border-light);
  padding: 20px 0;
  margin-top: auto;

  .footer-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--text-secondary);
    font-size: 14px;

    .footer-links {
      display: flex;
      gap: 20px;

      a {
        color: var(--text-secondary);
        text-decoration: none;
        transition: color 0.3s ease;

        &:hover {
          color: var(--primary-color);
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header {
    .header-content {
      flex-wrap: wrap;
      height: auto;
      padding: 10px 0;
    }

    .nav-menu {
      order: 3;
      flex-basis: 100%;
      margin: 10px 0 0 0;
    }

    .user-section {
      .el-button {
        font-size: 12px;
        padding: 8px 16px;
      }
    }
  }

  .footer {
    .footer-content {
      flex-direction: column;
      gap: 10px;
      text-align: center;

      .footer-links {
        justify-content: center;
      }
    }
  }
}
</style> 