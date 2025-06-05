<template>
  <div class="home-page">
    <div class="container">
      <!-- 欢迎区域 -->
      <section class="hero-section">
        <div class="hero-content">
          <h1 class="hero-title">欢迎来到 Cursor Rules</h1>
          <p class="hero-subtitle">专业的程序员和AI开发者cursor规则分享平台</p>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="$router.push('/create')" v-if="userStore.isLoggedIn">
              <el-icon><Plus /></el-icon>
              创建规则
            </el-button>
            <el-button size="large" @click="scrollToRules">
              <el-icon><Search /></el-icon>
              浏览规则
            </el-button>
          </div>
        </div>
      </section>

      <!-- 搜索和筛选区域 -->
      <section class="search-section" ref="rulesSection">
        <!-- 分类导航栏 -->
        <div class="category-navigation">
          <div class="category-nav-header">
            <h3>
              <el-icon><Grid /></el-icon>
              按分类浏览
            </h3>
          </div>
          <div class="category-tabs">
            <el-button
              :type="searchParams.category_id === null ? 'primary' : 'default'"
              @click="selectCategory(null)"
              class="category-btn"
              size="small"
            >
              <el-icon><List /></el-icon>
              全部分类 ({{ categoryCounts.total || 0 }})
            </el-button>
            <el-button
              v-for="category in categoriesWithCounts"
              :key="category.id"
              :type="searchParams.category_id === category.id ? 'primary' : 'default'"
              @click="selectCategory(category.id)"
              class="category-btn"
              size="small"
            >
              <el-icon><Folder /></el-icon>
              {{ category.name }} ({{ category.count || 0 }})
            </el-button>
          </div>
        </div>

        <div class="search-filters">
          <div class="search-bar">
            <el-input
              v-model="searchParams.keyword"
              placeholder="搜索 Cursor Rules..."
              size="large"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <template #append>
                <el-button @click="handleSearch">搜索</el-button>
              </template>
            </el-input>
          </div>
          
          <div class="filters">
            <el-select
              v-model="searchParams.category_id"
              placeholder="选择分类"
              clearable
              @change="handleSearch"
              style="width: 200px"
            >
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
            
            <el-select
              v-model="searchParams.sort_by"
              @change="handleSearch"
              style="width: 150px"
            >
              <el-option label="最新创建" value="created_at" />
              <el-option label="最多下载" value="download_count" />
              <el-option label="最多点赞" value="likes_count" />
            </el-select>
            
            <el-button @click="toggleFilters">
              <el-icon><Filter /></el-icon>
              更多筛选
            </el-button>
          </div>
        </div>

        <!-- 高级筛选 -->
        <div v-if="showAdvancedFilters" class="advanced-filters">
          <el-form :model="searchParams" inline>
            <el-form-item label="标签:">
              <el-select
                v-model="selectedTagIds"
                multiple
                placeholder="选择标签"
                style="width: 300px"
                @change="handleTagsChange"
              >
                <el-option
                  v-for="tag in tags"
                  :key="tag.id"
                  :label="tag.name"
                  :value="tag.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="排序:">
              <el-radio-group v-model="searchParams.sort_order" @change="handleSearch">
                <el-radio-button label="desc">降序</el-radio-button>
                <el-radio-button label="asc">升序</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </div>
      </section>

      <!-- 统计信息 -->
      <section class="stats-section" v-if="stats">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stats-item">
              <span class="stats-number">{{ stats.total_rules }}</span>
              <span class="stats-label">总规则数</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stats-item">
              <span class="stats-number">{{ stats.total_downloads }}</span>
              <span class="stats-label">总下载数</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stats-item">
              <span class="stats-number">{{ stats.total_users }}</span>
              <span class="stats-label">注册用户</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stats-item">
              <span class="stats-number">{{ stats.total_categories }}</span>
              <span class="stats-label">分类数量</span>
            </div>
          </el-col>
        </el-row>
      </section>

      <!-- Cursor Rules 列表 -->
      <section class="rules-section">
        <div class="section-header">
          <div class="section-title">
            <h2>Cursor Rules</h2>
            <span v-if="searchParams.category_id" class="current-filter">
              当前分类：{{ categories.find(c => c.id === searchParams.category_id)?.name }}
            </span>
            <span v-else-if="searchParams.keyword" class="current-filter">
              搜索：{{ searchParams.keyword }}
            </span>
          </div>
          <div class="list-actions">
            <el-button-group>
              <el-button
                :type="selectedRules.length > 0 ? 'primary' : 'default'"
                @click="batchDownload"
                :disabled="selectedRules.length === 0"
              >
                <el-icon><Download /></el-icon>
                批量下载 ({{ selectedRules.length }})
              </el-button>
            </el-button-group>
          </div>
        </div>

        <div v-loading="loading" class="rules-list">
          <div v-if="cursorRules.length === 0 && !loading" class="empty-state">
            <el-empty :description="getEmptyStateText()">
              <template #image>
                <el-icon class="empty-icon">
                  <Grid v-if="searchParams.category_id" />
                  <Search v-else-if="searchParams.keyword" />
                  <DocumentAdd v-else />
                </el-icon>
              </template>
              <el-button v-if="!searchParams.category_id && !searchParams.keyword" type="primary" @click="$router.push('/create')" v-show="userStore.isLoggedIn">
                创建第一个规则
              </el-button>
              <el-button v-else type="default" @click="clearFilters">
                查看全部规则
              </el-button>
            </el-empty>
          </div>
          
          <div v-else class="rules-grid">
            <div
              v-for="rule in cursorRules"
              :key="rule.id"
              class="rule-card"
              :class="{ selected: selectedRules.includes(rule.id) }"
              @click="selectRule(rule.id)"
            >
              <div class="rule-header">
                <div class="rule-title-section">
                  <el-checkbox
                    :model-value="selectedRules.includes(rule.id)"
                    @change="toggleRuleSelection(rule.id)"
                    @click.stop
                    class="rule-checkbox"
                  />
                  <h3 class="rule-title" @click.stop="$router.push(`/cursor-rule/${rule.id}`)">
                    {{ rule.title }}
                  </h3>
                </div>
                <div class="rule-actions">
                  <el-button
                    type="primary"
                    size="small"
                    @click.stop="downloadSingle(rule.id)"
                  >
                    <el-icon><Download /></el-icon>
                  </el-button>
                </div>
              </div>
              
              <div class="rule-meta">
                <span class="filename">{{ rule.filename }}.mdc</span>
                <el-tag v-if="rule.category" size="small">{{ rule.category.name }}</el-tag>
              </div>
              
              <p class="rule-description">{{ rule.description || '暂无描述' }}</p>
              
              <div class="rule-tags" v-if="rule.tags && rule.tags.length > 0">
                <el-tag
                  v-for="tag in rule.tags"
                  :key="tag.id"
                  size="small"
                  effect="plain"
                  class="tag-item"
                >
                  {{ tag.name }}
                </el-tag>
              </div>
              
              <div class="rule-footer">
                <div class="rule-stats">
                  <span class="stat-item">
                    <el-icon><User /></el-icon>
                    {{ rule.author?.username }}
                  </span>
                  <span class="stat-item">
                    <el-icon><Download /></el-icon>
                    {{ rule.download_count }}
                  </span>
                  <span class="stat-item">
                    <el-icon><Star /></el-icon>
                    {{ rule.likes_count }}
                  </span>
                </div>
                <span class="rule-date">
                  {{ formatDate(rule.created_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import {
  Plus, Search, Filter, Download, User, Star, Grid, List, Folder, DocumentAdd
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const cursorRules = ref([])
const categories = ref([])
const tags = ref([])
const stats = ref(null)
const selectedRules = ref([])
const selectedTagIds = ref([])
const showAdvancedFilters = ref(false)
const rulesSection = ref(null)
const categoryCounts = ref({})

// 搜索参数
const searchParams = reactive({
  keyword: '',
  category_id: null,
  tag_ids: '',
  sort_by: 'created_at',
  sort_order: 'desc'
})

// 分页参数
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
  pages: 0
})

// 计算属性
const categoriesWithCounts = computed(() => {
  return categories.value.map(category => ({
    ...category,
    count: categoryCounts.value[category.id] || 0
  }))
})

// 生命周期
onMounted(() => {
  // 从URL参数中读取分类筛选
  const urlParams = new URLSearchParams(window.location.search)
  const categoryParam = urlParams.get('category')
  if (categoryParam) {
    searchParams.category_id = parseInt(categoryParam)
  }
  
  loadData()
  loadCategories()
  loadTags()
  loadStats()
})

// 方法
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchParams
    }
    
    const response = await api.get('/cursor-rules', { params })
    cursorRules.value = response.data.items
    pagination.total = response.data.total
    pagination.pages = response.data.pages
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await api.get('/categories')
    categories.value = response.data
    // 加载分类统计
    await loadCategoryCounts()
  } catch (error) {
    console.error('加载分类失败:', error)
  }
}

const loadCategoryCounts = async () => {
  try {
    // 获取总数
    const totalResponse = await api.get('/cursor-rules', { params: { size: 1 } })
    categoryCounts.value.total = totalResponse.data.total

    // 获取每个分类的数量
    const counts = {}
    for (const category of categories.value) {
      const response = await api.get('/cursor-rules', { 
        params: { category_id: category.id, size: 1 } 
      })
      counts[category.id] = response.data.total
    }
    categoryCounts.value = { ...categoryCounts.value, ...counts }
  } catch (error) {
    console.error('加载分类统计失败:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await api.get('/tags')
    tags.value = response.data
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await api.get('/download/platform-stats')
    stats.value = {
      total_rules: response.data.total_rules,
      total_downloads: response.data.total_downloads,
      total_users: response.data.total_users,
      total_categories: response.data.total_categories,
      total_tags: response.data.total_tags
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    // 如果API失败，使用基本的统计信息
    stats.value = {
      total_rules: cursorRules.value.length,
      total_downloads: 0,
      total_users: 0,
      total_categories: categories.value.length,
      total_tags: tags.value.length
    }
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleTagsChange = () => {
  searchParams.tag_ids = selectedTagIds.value.join(',')
  handleSearch()
}

const toggleFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

const handlePageChange = (page) => {
  pagination.page = page
  loadData()
  scrollToTop()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadData()
}

const selectRule = (id) => {
  // 点击卡片时的处理（预留）
}

const toggleRuleSelection = (id) => {
  const index = selectedRules.value.indexOf(id)
  if (index > -1) {
    selectedRules.value.splice(index, 1)
  } else {
    selectedRules.value.push(id)
  }
}

const downloadSingle = async (id) => {
  try {
    const response = await api.get(`/download/single/${id}`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名
    const disposition = response.headers['content-disposition']
    const filename = disposition ? 
      disposition.split('filename=')[1]?.replace(/"/g, '') : 
      `cursor-rule-${id}.zip`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
    loadData() // 刷新数据以更新下载计数
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const batchDownload = async () => {
  if (selectedRules.value.length === 0) {
    ElMessage.warning('请选择要下载的规则')
    return
  }
  
  try {
    const response = await api.post('/download/batch', {
      cursor_rule_ids: selectedRules.value
    }, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    
    const disposition = response.headers['content-disposition']
    const filename = disposition ? 
      disposition.split('filename=')[1]?.replace(/"/g, '') : 
      `cursor-rules-batch.zip`
    
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`成功下载 ${selectedRules.value.length} 个规则`)
    selectedRules.value = []
    loadData()
  } catch (error) {
    ElMessage.error('批量下载失败')
  }
}

const scrollToRules = () => {
  rulesSection.value?.scrollIntoView({ behavior: 'smooth' })
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const selectCategory = (categoryId) => {
  searchParams.category_id = categoryId
  
  // 更新URL参数
  const url = new URL(window.location)
  if (categoryId) {
    url.searchParams.set('category', categoryId)
  } else {
    url.searchParams.delete('category')
  }
  window.history.pushState({}, '', url)
  
  handleSearch()
}

const getEmptyStateText = () => {
  if (searchParams.category_id) {
    return `暂无${categories.value.find(c => c.id === searchParams.category_id)?.name}分类的规则`
  } else if (searchParams.keyword) {
    return `暂无关于"${searchParams.keyword}"的规则`
  } else {
    return '暂无规则'
  }
}

const clearFilters = () => {
  searchParams.category_id = null
  searchParams.keyword = ''
  handleSearch()
}
</script>

<style lang="scss" scoped>
.home-page {
  .hero-section {
    text-align: center;
    padding: 60px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-bottom: 40px;

    .hero-title {
      font-size: 3rem;
      font-weight: 700;
      margin-bottom: 20px;
    }

    .hero-subtitle {
      font-size: 1.2rem;
      margin-bottom: 40px;
      opacity: 0.9;
    }

    .hero-actions {
      display: flex;
      gap: 20px;
      justify-content: center;
    }
  }

  .search-section {
    margin-bottom: 40px;

    .category-navigation {
      margin-bottom: 20px;
      background: var(--bg-color);
      border-radius: 8px;
      padding: 16px;
      border: 1px solid var(--border-light);

      .category-nav-header {
        h3 {
          font-size: 1.2rem;
          font-weight: 600;
          margin: 0 0 12px 0;
          color: var(--text-primary);
          display: flex;
          align-items: center;
          gap: 8px;
          
          .el-icon {
            color: var(--primary-color);
          }
        }
      }

      .category-tabs {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;

        .category-btn {
          padding: 6px 12px;
          font-size: 0.9rem;
          border-radius: 6px;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          gap: 4px;
          
          .el-icon {
            font-size: 14px;
          }
          
          &.el-button--primary {
            background: var(--primary-color);
            border-color: var(--primary-color);
            color: white;
            box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
          }
          
          &.el-button--default {
            background: var(--fill-light);
            border-color: var(--border-light);
            color: var(--text-regular);
            
            &:hover {
              background: var(--primary-color);
              border-color: var(--primary-color);
              color: white;
              transform: translateY(-1px);
              box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
            }
          }
        }
      }
    }

    .search-filters {
      display: flex;
      gap: 20px;
      margin-bottom: 20px;
      align-items: center;

      .search-bar {
        flex: 1;
        max-width: 500px;
      }

      .filters {
        display: flex;
        gap: 15px;
        align-items: center;
      }
    }

    .advanced-filters {
      background: var(--fill-lighter);
      padding: 20px;
      border-radius: 8px;
      border: 1px solid var(--border-light);
    }
  }

  .stats-section {
    margin-bottom: 40px;
    background: var(--bg-color);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }

  .rules-section {
    .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;

      .section-title {
        h2 {
          color: var(--text-primary);
          font-size: 1.8rem;
          font-weight: 600;
          margin: 0;
        }

        .current-filter {
          display: block;
          font-size: 0.9rem;
          color: var(--text-secondary);
          margin-top: 4px;
          padding: 2px 8px;
          background: var(--fill-light);
          border-radius: 4px;
          display: inline-block;
        }
      }
    }

    .rules-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }

    .rule-card {
      background: var(--bg-color);
      border-radius: 8px;
      padding: 20px;
      border: 1px solid var(--border-light);
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
      }

      &.selected {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 1px var(--primary-color);
      }

      .rule-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;

        .rule-title-section {
          display: flex;
          align-items: center;
          gap: 10px;
          flex: 1;

          .rule-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
            cursor: pointer;
            transition: color 0.3s ease;

            &:hover {
              color: var(--primary-color);
            }
          }
        }
      }

      .rule-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;

        .filename {
          font-family: 'Monaco', 'Menlo', monospace;
          font-size: 0.9rem;
          color: var(--text-secondary);
          background: var(--fill-light);
          padding: 2px 6px;
          border-radius: 4px;
        }
      }

      .rule-description {
        color: var(--text-regular);
        margin-bottom: 15px;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .rule-tags {
        margin-bottom: 15px;

        .tag-item {
          margin-right: 8px;
          margin-bottom: 5px;
        }
      }

      .rule-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: var(--text-secondary);
        font-size: 0.9rem;

        .rule-stats {
          display: flex;
          gap: 15px;

          .stat-item {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }

        .rule-date {
          font-size: 0.85rem;
        }
      }
    }

    .empty-state {
      text-align: center;
      padding: 60px 20px;
    }

    .pagination-wrapper {
      display: flex;
      justify-content: center;
      padding: 20px 0;
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .home-page {
    .hero-section {
      padding: 40px 0;

      .hero-title {
        font-size: 2rem;
      }

      .hero-actions {
        flex-direction: column;
        align-items: center;
      }
    }

    .search-section {
      .category-navigation {
        padding: 12px;
        
        .category-tabs {
          gap: 6px;
          
          .category-btn {
            padding: 4px 8px;
            font-size: 0.8rem;
          }
        }
      }

      .search-filters {
        flex-direction: column;
        align-items: stretch;

        .filters {
          justify-content: center;
          flex-wrap: wrap;
        }
      }
    }

    .rules-section {
      .section-header {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
      }

      .rules-grid {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style> 