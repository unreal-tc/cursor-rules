<template>
  <div class="profile">
    <div class="container">
      <!-- 用户信息区域 -->
      <div class="profile-header">
        <div class="user-avatar">
          <el-avatar :size="80" class="avatar">
            {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
        </div>
        <div class="user-info">
          <h1>{{ userStore.user?.username }}</h1>
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-number">{{ myRules.length }}</span>
              <span class="stat-label">创建的规则</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ totalDownloads }}</span>
              <span class="stat-label">总下载数</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ totalLikes }}</span>
              <span class="stat-label">总点赞数</span>
            </div>
          </div>
          <div class="user-meta">
            <span class="join-date">
              <el-icon><Calendar /></el-icon>
              加入时间：{{ formatDate(userStore.user?.created_at) }}
            </span>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="$router.push('/create')">
            <el-icon><Plus /></el-icon>
            创建新规则
          </el-button>
        </div>
      </div>

      <!-- 规则管理区域 -->
      <div class="rules-section">
        <div class="section-header">
          <h2>我的规则</h2>
          <div class="header-tools">
            <el-input
              v-model="searchQuery"
              placeholder="搜索我的规则..."
              style="width: 300px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select v-model="sortBy" placeholder="排序方式" style="width: 150px">
              <el-option label="创建时间" value="created_at" />
              <el-option label="更新时间" value="updated_at" />
              <el-option label="下载数量" value="download_count" />
              <el-option label="点赞数量" value="likes_count" />
            </el-select>
            <el-button-group>
              <el-button 
                :type="viewMode === 'grid' ? 'primary' : 'default'"
                @click="viewMode = 'grid'"
              >
                <el-icon><Grid /></el-icon>
              </el-button>
              <el-button 
                :type="viewMode === 'list' ? 'primary' : 'default'"
                @click="viewMode = 'list'"
              >
                <el-icon><List /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <!-- 规则列表 -->
        <div v-else-if="filteredRules.length > 0" :class="['rules-container', viewMode]">
          <!-- 网格视图 -->
          <div v-if="viewMode === 'grid'" class="rules-grid">
            <div 
              v-for="rule in filteredRules" 
              :key="rule.id"
              class="rule-card"
            >
              <div class="card-header">
                <h3 class="rule-title" @click="$router.push(`/cursor-rule/${rule.id}`)">
                  {{ rule.title }}
                </h3>
                <el-dropdown @command="handleAction">
                  <el-button type="text" size="small">
                    <el-icon><MoreFilled /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'view', rule }">
                        <el-icon><View /></el-icon>
                        查看
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'edit', rule }">
                        <el-icon><Edit /></el-icon>
                        编辑
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'download', rule }">
                        <el-icon><Download /></el-icon>
                        下载
                      </el-dropdown-item>
                      <el-dropdown-item 
                        :command="{ action: 'delete', rule }"
                        divided
                        style="color: #f56c6c"
                      >
                        <el-icon><Delete /></el-icon>
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>

              <div class="card-content">
                <p class="rule-description">
                  {{ rule.description || '暂无描述' }}
                </p>
                <div class="rule-tags">
                  <el-tag 
                    v-for="tag in rule.tags.slice(0, 3)" 
                    :key="tag.id"
                    size="small"
                    type="info"
                  >
                    {{ tag.name }}
                  </el-tag>
                  <span v-if="rule.tags.length > 3" class="more-tags">
                    +{{ rule.tags.length - 3 }}
                  </span>
                </div>
              </div>

              <div class="card-footer">
                <div class="rule-stats">
                  <span><el-icon><Star /></el-icon> {{ rule.likes_count }}</span>
                  <span><el-icon><Download /></el-icon> {{ rule.download_count }}</span>
                </div>
                <div class="rule-date">
                  {{ formatDate(rule.updated_at) }}
                </div>
              </div>
            </div>
          </div>

          <!-- 列表视图 -->
          <div v-else class="rules-table">
            <el-table :data="filteredRules" style="width: 100%">
              <el-table-column prop="title" label="标题" min-width="200">
                <template #default="{ row }">
                  <el-link 
                    type="primary" 
                    @click="$router.push(`/cursor-rule/${row.id}`)"
                    class="rule-link"
                  >
                    {{ row.title }}
                  </el-link>
                </template>
              </el-table-column>
              
              <el-table-column prop="category" label="分类" width="120">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.category.name }}</el-tag>
                </template>
              </el-table-column>
              
              <el-table-column prop="tags" label="标签" width="200">
                <template #default="{ row }">
                  <div class="table-tags">
                    <el-tag 
                      v-for="tag in row.tags.slice(0, 2)" 
                      :key="tag.id"
                      size="small"
                      type="info"
                    >
                      {{ tag.name }}
                    </el-tag>
                    <span v-if="row.tags.length > 2" class="more-tags">
                      +{{ row.tags.length - 2 }}
                    </span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="stats" label="统计" width="180">
                <template #default="{ row }">
                  <div class="table-stats">
                    <span><el-icon><Star /></el-icon> {{ row.likes_count }}</span>
                    <span><el-icon><Download /></el-icon> {{ row.download_count }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column prop="updated_at" label="更新时间" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.updated_at) }}
                </template>
              </el-table-column>
              
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button-group size="small">
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="$router.push(`/edit/${row.id}`)"
                    >
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small"
                      @click="handleDeleteRule(row)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无规则">
            <template #image>
              <el-icon class="empty-icon"><DocumentAdd /></el-icon>
            </template>
            <el-button type="primary" @click="$router.push('/create')">
              创建第一个规则
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Calendar, Plus, Search, Grid, List, MoreFilled, View, Edit, 
  Download, Delete, Star, DocumentAdd
} from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(true)
const myRules = ref([])
const searchQuery = ref('')
const sortBy = ref('updated_at')
const viewMode = ref('grid')

// 计算属性
const totalDownloads = computed(() => {
  if (!Array.isArray(myRules.value)) return 0
  return myRules.value.reduce((sum, rule) => sum + (rule.download_count || 0), 0)
})

const totalLikes = computed(() => {
  if (!Array.isArray(myRules.value)) return 0
  return myRules.value.reduce((sum, rule) => sum + (rule.likes_count || 0), 0)
})

const filteredRules = computed(() => {
  if (!Array.isArray(myRules.value)) return []
  let filtered = myRules.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(rule => 
      rule.title.toLowerCase().includes(query) ||
      rule.description?.toLowerCase().includes(query) ||
      rule.tags.some(tag => tag.name.toLowerCase().includes(query))
    )
  }

  // 排序
  filtered.sort((a, b) => {
    const aValue = a[sortBy.value] || 0
    const bValue = b[sortBy.value] || 0
    
    if (sortBy.value === 'created_at' || sortBy.value === 'updated_at') {
      return new Date(bValue) - new Date(aValue)
    } else {
      return bValue - aValue
    }
  })

  return filtered
})

// 获取我的规则列表
const fetchMyRules = async () => {
  try {
    loading.value = true
    const response = await api.get('/cursor-rules/my')
    myRules.value = response.data.items || []
  } catch (error) {
    console.error('获取我的规则失败:', error)
    ElMessage.error('获取规则列表失败')
    myRules.value = [] // 确保在错误情况下也是数组
  } finally {
    loading.value = false
  }
}

// 处理操作
const handleAction = ({ action, rule }) => {
  switch (action) {
    case 'view':
      router.push(`/cursor-rule/${rule.id}`)
      break
    case 'edit':
      router.push(`/edit/${rule.id}`)
      break
    case 'download':
      handleDownloadRule(rule)
      break
    case 'delete':
      handleDeleteRule(rule)
      break
  }
}

// 下载规则
const handleDownloadRule = async (rule) => {
  try {
    const response = await api.get(`/download/single/${rule.id}`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const contentDisposition = response.headers['content-disposition']
    let filename = `cursor-rule-${rule.filename}.zip`
    if (contentDisposition) {
      const matches = contentDisposition.match(/filename=(.+)/)
      if (matches) {
        filename = matches[1].replace(/"/g, '')
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    ElMessage.success('下载开始')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 删除规则
const handleDeleteRule = async (rule) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则"${rule.title}"吗？此操作不可恢复。`, 
      '删除确认', 
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    
    await api.delete(`/cursor-rules/${rule.id}`)
    
    // 从列表中移除
    const index = myRules.value.findIndex(r => r.id === rule.id)
    if (index > -1) {
      myRules.value.splice(index, 1)
    }
    
    ElMessage.success('规则删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除规则失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  // 小于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 小于1小时
  if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  }
  
  // 小于1天
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  
  // 小于7天
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  
  // 其他情况显示具体日期
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchMyRules()
})
</script>

<style lang="scss" scoped>
.profile {
  min-height: calc(100vh - 120px);
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.profile-header {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 24px;
  
  .user-avatar {
    .avatar {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-size: 24px;
      font-weight: 600;
    }
  }
  
  .user-info {
    flex: 1;
    
    h1 {
      margin: 0 0 16px 0;
      font-size: 28px;
      font-weight: 600;
      color: #1a1a1a;
    }
    
    .user-stats {
      display: flex;
      gap: 32px;
      margin-bottom: 12px;
      
      .stat-item {
        text-align: center;
        
        .stat-number {
          display: block;
          font-size: 24px;
          font-weight: 600;
          color: #409eff;
          line-height: 1;
        }
        
        .stat-label {
          display: block;
          font-size: 12px;
          color: #666;
          margin-top: 4px;
        }
      }
    }
    
    .user-meta {
      .join-date {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #666;
        font-size: 14px;
      }
    }
  }
  
  .header-actions {
    flex-shrink: 0;
  }
}

.rules-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  padding: 24px 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 24px;
  
  h2 {
    margin: 0 0 24px 0;
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
  }
  
  .header-tools {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
  }
}

.loading-container {
  padding: 24px;
}

.rules-container {
  padding: 0 24px 24px;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.rule-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: white;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
  
  .card-header {
    padding: 16px 16px 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    
    .rule-title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #1a1a1a;
      cursor: pointer;
      flex: 1;
      line-height: 1.4;
      
      &:hover {
        color: #409eff;
      }
    }
  }
  
  .card-content {
    padding: 0 16px 12px;
    
    .rule-description {
      margin: 0 0 12px 0;
      color: #666;
      font-size: 14px;
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .rule-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      align-items: center;
      
      .more-tags {
        font-size: 12px;
        color: #999;
      }
    }
  }
  
  .card-footer {
    padding: 12px 16px 16px;
    border-top: 1px solid #f5f5f5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .rule-stats {
      display: flex;
      gap: 12px;
      
      .stat {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #666;
      }
    }
    
    .rule-date {
      font-size: 12px;
      color: #999;
    }
  }
}

.rules-table {
  .rule-link {
    font-weight: 500;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
  
  .table-tags {
    display: flex;
    gap: 4px;
    align-items: center;
    flex-wrap: wrap;
    
    .more-tags {
      font-size: 12px;
      color: #999;
    }
  }
  
  .table-stats {
    display: flex;
    gap: 8px;
    
    .stat {
      display: flex;
      align-items: center;
      gap: 2px;
      font-size: 12px;
      color: #666;
    }
  }
}

.empty-state {
  padding: 60px 24px;
  text-align: center;
  
  .empty-icon {
    font-size: 64px;
    color: #ddd;
    margin-bottom: 16px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
  
  .profile-header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
    
    .user-stats {
      justify-content: center;
    }
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    
    .header-tools {
      flex-direction: column;
      align-items: stretch;
      
      .el-input, .el-select {
        width: 100% !important;
      }
    }
  }
  
  .rules-grid {
    grid-template-columns: 1fr;
  }
  
  .rules-table {
    overflow-x: auto;
  }
}
</style> 