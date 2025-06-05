<template>
  <div class="cursor-rule-detail">
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 详情内容 -->
      <div v-else-if="rule" class="detail-content">
        <!-- 头部信息 -->
        <div class="detail-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item @click="$router.push('/')">首页</el-breadcrumb-item>
              <el-breadcrumb-item @click="$router.push(`/?category=${rule.category.id}`)">
                {{ rule.category.name }}
              </el-breadcrumb-item>
              <el-breadcrumb-item>{{ rule.title }}</el-breadcrumb-item>
            </el-breadcrumb>
            
            <h1 class="rule-title">{{ rule.title }}</h1>
            
            <div class="rule-meta">
              <el-tag>{{ rule.category.name }}</el-tag>
              <el-tag 
                v-for="tag in rule.tags" 
                :key="tag.id" 
                type="info" 
                size="small"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
              <span class="meta-info">
                <el-icon><User /></el-icon>
                {{ rule.author.username }}
              </span>
              <span class="meta-info">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(rule.created_at) }}
              </span>
              <span class="meta-info">
                <el-icon><View /></el-icon>
                浏览 {{ rule.view_count || 0 }}
              </span>
              <span class="meta-info">
                <el-icon><Download /></el-icon>
                下载 {{ rule.download_count }}
              </span>
            </div>
          </div>

          <div class="header-actions">
            <!-- 投票按钮 -->
            <div class="vote-buttons">
              <el-button 
                :type="rule.user_vote === 'like' ? 'primary' : 'default'"
                @click="handleVote('like')"
                :loading="voteLoading"
              >
                <el-icon><Star /></el-icon>
                {{ rule.likes_count }}
              </el-button>
              <el-button 
                :type="rule.user_vote === 'dislike' ? 'danger' : 'default'"
                @click="handleVote('dislike')"
                :loading="voteLoading"
              >
                <el-icon><Close /></el-icon>
                {{ rule.dislikes_count }}
              </el-button>
            </div>

            <!-- 下载按钮 -->
            <el-button 
              type="primary" 
              size="large"
              @click="handleDownload"
              :loading="downloadLoading"
            >
              <el-icon><Download /></el-icon>
              下载规则
            </el-button>

            <!-- 编辑按钮（仅作者可见） -->
            <el-button 
              v-if="canEdit"
              type="default"
              @click="$router.push(`/edit/${rule.id}`)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </div>

        <!-- 规则描述 -->
        <div v-if="rule.description" class="rule-description">
          <h3>规则描述</h3>
          <div class="markdown-content" v-html="parseMarkdown(rule.description)"></div>
        </div>

        <!-- 规则内容 -->
        <div class="rule-content">
          <div class="content-header">
            <h3>规则内容</h3>
            <el-button size="small" @click="copyContent">
              <el-icon><DocumentCopy /></el-icon>
              复制内容
            </el-button>
          </div>
          <div class="code-container">
            <pre><code class="language-markdown">{{ rule.content }}</code></pre>
          </div>
        </div>

        <!-- 使用示例 -->
        <div v-if="rule.example" class="rule-example">
          <h3>使用示例</h3>
          <div class="markdown-content" v-html="parseMarkdown(rule.example)"></div>
        </div>

        <!-- 相关推荐 -->
        <div v-if="relatedRules.length > 0" class="related-rules">
          <h3>相关推荐</h3>
          <div class="related-grid">
            <div 
              v-for="relatedRule in relatedRules" 
              :key="relatedRule.id"
              class="related-item"
              @click="$router.push(`/cursor-rule/${relatedRule.id}`)"
            >
              <h4>{{ relatedRule.title }}</h4>
              <p>{{ relatedRule.description || '暂无描述' }}</p>
              <div class="related-meta">
                <span><el-icon><Star /></el-icon> {{ relatedRule.likes_count }}</span>
                <span><el-icon><Download /></el-icon> {{ relatedRule.download_count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-container">
        <el-result
          icon="warning"
          title="规则不存在"
          sub-title="抱歉，您访问的规则不存在或已被删除"
        >
          <template #extra>
            <el-button type="primary" @click="$router.push('/')">
              返回首页
            </el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Calendar, View, Download, Edit, DocumentCopy,
  Star, Close
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(true)
const downloadLoading = ref(false)
const voteLoading = ref(false)
const rule = ref(null)
const relatedRules = ref([])

// 计算属性
const canEdit = computed(() => {
  return userStore.isLoggedIn && 
         rule.value && 
         rule.value.author.id === userStore.user?.id
})

// 获取规则详情
const fetchRuleDetail = async () => {
  try {
    loading.value = true
    const response = await api.get(`/cursor-rules/${route.params.id}`)
    rule.value = response.data
    
    // 获取相关推荐
    await fetchRelatedRules()
    
    // 记录浏览量
    await recordView()
  } catch (error) {
    console.error('获取规则详情失败:', error)
    rule.value = null
  } finally {
    loading.value = false
  }
}

// 获取相关推荐
const fetchRelatedRules = async () => {
  try {
    if (!rule.value) return
    
    const response = await api.get('/cursor-rules', {
      params: {
        category_id: rule.value.category.id,
        limit: 4,
        exclude_id: rule.value.id
      }
    })
    relatedRules.value = response.data.items.slice(0, 3)
  } catch (error) {
    console.error('获取相关推荐失败:', error)
  }
}

// 记录浏览量
const recordView = async () => {
  try {
    await api.post(`/cursor-rules/${rule.value.id}/view`)
  } catch (error) {
    // 忽略浏览量记录错误
  }
}

// 处理投票
const handleVote = async (voteType) => {
  try {
    voteLoading.value = true
    
    const response = await api.post(`/cursor-rules/${rule.value.id}/vote`, {
      vote_type: voteType
    })
    
    // 直接使用后端返回的最新数据更新前端状态
    const { likes_count, dislikes_count, user_vote } = response.data
    
    rule.value.likes_count = likes_count
    rule.value.dislikes_count = dislikes_count
    rule.value.user_vote = user_vote
    
    // 确保DOM更新
    await nextTick()
    
    // 根据最终状态显示消息
    const message = user_vote === voteType 
      ? (voteType === 'like' ? '点赞成功' : '点踩成功')
      : '取消投票成功'
    
    ElMessage.success(message)
  } catch (error) {
    console.error('投票失败:', error)
    ElMessage.error(error.response?.data?.detail || '投票失败')
  } finally {
    voteLoading.value = false
  }
}

// 处理下载
const handleDownload = async () => {
  try {
    downloadLoading.value = true
    
    const response = await api.get(`/download/single/${rule.value.id}`, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/zip' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 从响应头获取文件名，或使用默认名称
    const contentDisposition = response.headers['content-disposition']
    let filename = `cursor-rule-${rule.value.filename}.zip`
    if (contentDisposition) {
      const matches = contentDisposition.match(/filename=(.+)/)
      if (matches) {
        filename = matches[1].replace(/"/g, '')
      }
    }
    
    link.download = filename
    document.body.appendChild(link)
    link.click()
    
    // 清理
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    ElMessage.success('下载开始')
  } catch (error) {
    ElMessage.error('下载失败')
  } finally {
    downloadLoading.value = false
  }
}

// 复制内容
const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(rule.value.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// Markdown解析
const parseMarkdown = (content) => {
  if (!content) return ''
  
  // 配置marked
  marked.setOptions({
    highlight: function(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        return hljs.highlight(code, { language: lang }).value
      } else {
        return hljs.highlightAuto(code).value
      }
    },
    breaks: true,
    gfm: true
  })
  
  return marked(content)
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchRuleDetail()
})
</script>

<style lang="scss" scoped>
.cursor-rule-detail {
  min-height: calc(100vh - 120px);
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.loading-container, .error-container {
  padding: 60px 20px;
}

.detail-content {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.detail-header {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  
  .header-left {
    flex: 1;
    
    .rule-title {
      margin: 16px 0 12px 0;
      font-size: 28px;
      font-weight: 600;
      color: #1a1a1a;
      line-height: 1.4;
    }
    
    .rule-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      
      .tag-item {
        margin-left: 8px;
      }
      
      .meta-info {
        display: flex;
        align-items: center;
        gap: 4px;
        color: #666;
        font-size: 14px;
        
        .el-icon {
          font-size: 16px;
        }
      }
    }
  }
  
  .header-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-end;
    
    .vote-buttons {
      display: flex;
      gap: 8px;
    }
  }
}

.rule-description, .rule-content, .rule-example, .related-rules {
  padding: 24px;
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
  
  h3 {
    margin: 0 0 16px 0;
    font-size: 20px;
    font-weight: 600;
    color: #1a1a1a;
  }
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h3 {
    margin: 0;
  }
}

.code-container {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: auto;
  
  pre {
    margin: 0;
    padding: 16px;
    font-family: 'Monaco', 'Consolas', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.5;
    color: #24292e;
    
    code {
      background: none;
      padding: 0;
      border: none;
      border-radius: 0;
    }
  }
}

.markdown-content {
  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    margin: 16px 0 8px 0;
    font-weight: 600;
  }
  
  :deep(p) {
    margin: 8px 0;
    line-height: 1.6;
  }
  
  :deep(ul), :deep(ol) {
    margin: 8px 0;
    padding-left: 24px;
  }
  
  :deep(li) {
    margin: 4px 0;
    line-height: 1.6;
  }
  
  :deep(code) {
    background: #f1f3f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Monaco', 'Consolas', 'Ubuntu Mono', monospace;
    font-size: 0.9em;
  }
  
  :deep(pre) {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 16px;
    overflow: auto;
    margin: 12px 0;
    
    code {
      background: none;
      padding: 0;
    }
  }
  
  :deep(blockquote) {
    border-left: 4px solid #dfe2e5;
    padding: 0 16px;
    margin: 12px 0;
    color: #6a737d;
  }
  
  :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    
    th, td {
      border: 1px solid #dfe2e5;
      padding: 6px 13px;
      text-align: left;
    }
    
    th {
      background: #f6f8fa;
      font-weight: 600;
    }
  }
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.related-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
  
  h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    line-height: 1.4;
  }
  
  p {
    margin: 0 0 12px 0;
    color: #666;
    font-size: 14px;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .related-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #999;
    
    span {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: stretch;
    
    .header-actions {
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      
      .vote-buttons {
        order: 2;
      }
    }
  }
  
  .rule-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .related-grid {
    grid-template-columns: 1fr;
  }
}
</style>