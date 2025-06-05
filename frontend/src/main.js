import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// 样式导入
import 'element-plus/dist/index.css'
import '@/styles/index.scss'

// 进度条
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ 
  showSpinner: false,
  minimum: 0.2,
  speed: 500
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app') 