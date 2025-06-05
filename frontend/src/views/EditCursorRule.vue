<template>
  <div class="edit-cursor-rule">
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <!-- 编辑表单 -->
      <div v-else-if="originalRule" class="form-container">
        <div class="form-header">
          <h1>编辑 Cursor Rule</h1>
          <p>编辑您的 cursor rule 内容</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="rule-form"
          @submit.prevent="handleSubmit"
        >
          <!-- 基本信息 -->
          <div class="form-section">
            <h3>基本信息</h3>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="规则标题" prop="title">
                  <el-input
                    v-model="form.title"
                    placeholder="请输入规则标题"
                    maxlength="200"
                    show-word-limit
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="文件名" prop="filename">
                  <el-input
                    v-model="form.filename"
                    placeholder="请输入文件名（不含扩展名）"
                    maxlength="100"
                    show-word-limit
                  >
                    <template #suffix>
                      <span>.mdc</span>
                    </template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="分类" prop="category_id">
                  <el-select
                    v-model="form.category_id"
                    placeholder="请选择分类"
                    filterable
                    allow-create
                    default-first-option
                    :reserve-keyword="false"
                    @change="handleCategoryChange"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="category in categories"
                      :key="category.id"
                      :label="category.name"
                      :value="category.id"
                    />
                  </el-select>
                  <div class="form-help">
                    如果没有合适的分类，可以直接输入新分类名称
                  </div>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="标签" prop="tags">
                  <el-select
                    v-model="form.tags"
                    placeholder="请选择或创建标签"
                    multiple
                    filterable
                    allow-create
                    default-first-option
                    :reserve-keyword="false"
                    :multiple-limit="10"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="tag in tags"
                      :key="tag.id"
                      :label="tag.name"
                      :value="tag.name"
                    />
                  </el-select>
                  <div class="form-help">
                    选择相关标签，或输入新标签名称（最多10个）
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <!-- 规则描述 -->
          <div class="form-section">
            <h3>规则描述</h3>
            <el-form-item prop="description">
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="4"
                placeholder="请简要描述这个规则的用途和特点（支持 Markdown 格式）"
                maxlength="1000"
                show-word-limit
              />
            </el-form-item>
          </div>

          <!-- 规则内容 -->
          <div class="form-section">
            <h3>
              规则内容 <span class="required">*</span>
              <el-tooltip content="这里是cursor rule的主要内容，将保存为.mdc文件" placement="top">
                <el-icon class="info-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </h3>
            <el-form-item prop="content">
              <div class="editor-container">
                <div class="editor-toolbar">
                  <div class="toolbar-left">
                    <span class="editor-label">规则内容编辑器</span>
                  </div>
                  <div class="toolbar-right">
                    <el-button 
                      size="small" 
                      @click="formatContent"
                      :disabled="!form.content"
                    >
                      <el-icon><MagicStick /></el-icon>
                      格式化
                    </el-button>
                    <el-button 
                      size="small" 
                      @click="resetContent"
                      :disabled="!hasContentChanged"
                    >
                      <el-icon><RefreshLeft /></el-icon>
                      重置
                    </el-button>
                  </div>
                </div>
                <div 
                  ref="contentEditorRef" 
                  class="monaco-editor"
                  style="height: 400px; border: 1px solid #dcdfe6; border-radius: 4px;"
                ></div>
              </div>
            </el-form-item>
          </div>

          <!-- 使用示例 -->
          <div class="form-section">
            <h3>
              使用示例
              <el-tooltip content="可选：提供使用示例帮助其他开发者理解如何使用" placement="top">
                <el-icon class="info-icon"><QuestionFilled /></el-icon>
              </el-tooltip>
            </h3>
            <el-form-item prop="example">
              <div class="editor-container">
                <div class="editor-toolbar">
                  <div class="toolbar-left">
                    <span class="editor-label">示例编辑器（支持 Markdown）</span>
                  </div>
                  <div class="toolbar-right">
                    <el-button 
                      size="small" 
                      @click="previewExample = !previewExample"
                      :type="previewExample ? 'primary' : 'default'"
                    >
                      <el-icon><View /></el-icon>
                      {{ previewExample ? '编辑模式' : '预览模式' }}
                    </el-button>
                  </div>
                </div>
                <div v-if="!previewExample" 
                     ref="exampleEditorRef" 
                     class="monaco-editor"
                     style="height: 300px; border: 1px solid #dcdfe6; border-radius: 4px;"
                ></div>
                <div v-else class="markdown-preview" style="height: 300px;">
                  <div class="preview-content" v-html="parseMarkdown(form.example)"></div>
                </div>
              </div>
            </el-form-item>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <el-button size="large" @click="handleCancel">
              取消
            </el-button>
            <el-button 
              type="primary" 
              size="large" 
              @click="handleSubmit" 
              :loading="submitting"
              :disabled="!hasChanges"
            >
              <el-icon><Upload /></el-icon>
              保存修改
            </el-button>
          </div>
        </el-form>
      </div>

      <!-- 错误状态 -->
      <div v-else class="error-container">
        <el-result
          icon="warning"
          title="规则不存在或无权限编辑"
          sub-title="抱歉，您访问的规则不存在或您没有编辑权限"
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

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  QuestionFilled, MagicStick, RefreshLeft, View, Upload 
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import * as monaco from 'monaco-editor'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 检查登录状态
if (!userStore.isLoggedIn) {
  ElMessage.error('请先登录')
  router.push('/login')
}

// 引用
const formRef = ref(null)
const contentEditorRef = ref(null)
const exampleEditorRef = ref(null)

// 状态
const loading = ref(true)
const submitting = ref(false)
const previewExample = ref(false)
const categories = ref([])
const tags = ref([])
const originalRule = ref(null)

// Monaco编辑器实例
let contentEditor = null
let exampleEditor = null

// 表单数据
const form = reactive({
  title: '',
  filename: '',
  category_id: '',
  tags: [],
  description: '',
  content: '',
  example: ''
})

// 原始数据备份
const originalForm = reactive({
  title: '',
  filename: '',
  category_id: '',
  tags: [],
  description: '',
  content: '',
  example: ''
})

// 验证规则
const rules = {
  title: [
    { required: true, message: '请输入规则标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度应在 2 到 200 个字符', trigger: 'blur' }
  ],
  filename: [
    { required: true, message: '请输入文件名', trigger: 'blur' },
    { 
      pattern: /^[a-zA-Z0-9_-]+$/, 
      message: '文件名只能包含字母、数字、下划线和连字符', 
      trigger: 'blur' 
    },
    { min: 1, max: 100, message: '文件名长度应在 1 到 100 个字符', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入规则内容', trigger: 'blur' },
    { min: 10, message: '规则内容至少需要 10 个字符', trigger: 'blur' }
  ]
}

// 计算属性 - 检查是否有变更
const hasChanges = computed(() => {
  return form.title !== originalForm.title ||
         form.filename !== originalForm.filename ||
         form.category_id !== originalForm.category_id ||
         JSON.stringify(form.tags) !== JSON.stringify(originalForm.tags) ||
         form.description !== originalForm.description ||
         form.content !== originalForm.content ||
         form.example !== originalForm.example
})

const hasContentChanged = computed(() => {
  return form.content !== originalForm.content
})

// 获取规则详情
const fetchRuleDetail = async () => {
  try {
    loading.value = true
    const response = await api.get(`/cursor-rules/${route.params.id}`)
    const rule = response.data
    
    // 检查编辑权限
    if (!userStore.isLoggedIn || rule.author.id !== userStore.user?.id) {
      originalRule.value = null
      return
    }
    
    originalRule.value = rule
    
    // 填充表单数据
    form.title = rule.title
    form.filename = rule.filename
    form.category_id = rule.category.id
    form.tags = rule.tags.map(tag => tag.name)
    form.description = rule.description || ''
    form.content = rule.content
    form.example = rule.example || ''
    
    // 备份原始数据
    Object.assign(originalForm, {
      title: rule.title,
      filename: rule.filename,
      category_id: rule.category.id,
      tags: [...rule.tags.map(tag => tag.name)],
      description: rule.description || '',
      content: rule.content,
      example: rule.example || ''
    })
    
  } catch (error) {
    console.error('获取规则详情失败:', error)
    originalRule.value = null
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const fetchCategories = async () => {
  try {
    const response = await api.get('/categories')
    categories.value = response.data
  } catch (error) {
    console.error('获取分类失败:', error)
  }
}

// 获取标签列表
const fetchTags = async () => {
  try {
    const response = await api.get('/tags')
    tags.value = response.data
  } catch (error) {
    console.error('获取标签失败:', error)
  }
}

// 分类变化处理
const handleCategoryChange = (value) => {
  if (typeof value === 'string') {
    form.category_id = value
  }
}

// 初始化Monaco编辑器
const initMonacoEditors = async () => {
  await nextTick()
  
  // 内容编辑器
  if (contentEditorRef.value) {
    contentEditor = monaco.editor.create(contentEditorRef.value, {
      value: form.content,
      language: 'markdown',
      theme: 'vs',
      automaticLayout: true,
      wordWrap: 'on',
      lineNumbers: 'on',
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      tabSize: 2,
      insertSpaces: true
    })
    
    contentEditor.onDidChangeModelContent(() => {
      form.content = contentEditor.getValue()
    })
  }
  
  // 示例编辑器
  if (exampleEditorRef.value) {
    exampleEditor = monaco.editor.create(exampleEditorRef.value, {
      value: form.example,
      language: 'markdown',
      theme: 'vs',
      automaticLayout: true,
      wordWrap: 'on',
      lineNumbers: 'on',
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      tabSize: 2,
      insertSpaces: true
    })
    
    exampleEditor.onDidChangeModelContent(() => {
      form.example = exampleEditor.getValue()
    })
  }
}

// 格式化内容
const formatContent = () => {
  if (contentEditor) {
    contentEditor.getAction('editor.action.formatDocument').run()
  }
}

// 重置内容到原始状态
const resetContent = async () => {
  try {
    await ElMessageBox.confirm('确定要重置内容到原始状态吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (contentEditor) {
      contentEditor.setValue(originalForm.content)
    }
  } catch {
    // 用户取消
  }
}

// Markdown解析
const parseMarkdown = (content) => {
  if (!content) return ''
  
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

// 取消编辑
const handleCancel = async () => {
  if (hasChanges.value) {
    try {
      await ElMessageBox.confirm('您有未保存的修改，确定要离开吗？', '提示', {
        confirmButtonText: '确定离开',
        cancelButtonText: '继续编辑',
        type: 'warning'
      })
    } catch {
      return // 用户选择继续编辑
    }
  }
  
  router.push(`/cursor-rule/${route.params.id}`)
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 验证表单
    const valid = await formRef.value.validate()
    if (!valid) return
    
    submitting.value = true
    
    // 准备提交数据
    const submitData = {
      title: form.title.trim(),
      filename: form.filename.trim(),
      category_id: form.category_id,
      description: form.description.trim(),
      content: form.content.trim(),
      example: form.example.trim(),
      tags: form.tags.filter(tag => tag.trim()).map(tag => tag.trim())
    }
    
    // 如果分类是字符串（新建分类），需要先创建分类
    if (typeof submitData.category_id === 'string') {
      const categoryResponse = await api.post('/categories', {
        name: submitData.category_id,
        description: `${submitData.category_id}分类`
      })
      submitData.category_id = categoryResponse.data.data.category.id
    }
    
    // 更新cursor rule
    await api.put(`/cursor-rules/${route.params.id}`, submitData)
    
    ElMessage.success('规则更新成功！')
    
    // 跳转到详情页
    router.push(`/cursor-rule/${route.params.id}`)
    
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.response?.data?.detail || '更新失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  // 并行获取数据
  await Promise.all([
    fetchCategories(),
    fetchTags(),
    fetchRuleDetail()
  ])
  
  // 如果成功获取到规则数据，初始化编辑器
  if (originalRule.value) {
    await initMonacoEditors()
  }
})

onBeforeUnmount(() => {
  if (contentEditor) {
    contentEditor.dispose()
  }
  if (exampleEditor) {
    exampleEditor.dispose()
  }
})
</script>

<style lang="scss" scoped>
.edit-cursor-rule {
  min-height: calc(100vh - 120px);
  background: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.loading-container, .error-container {
  padding: 60px 20px;
}

.form-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.form-header {
  padding: 24px 24px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 24px;
  
  h1 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
  }
  
  p {
    margin: 0 0 24px 0;
    color: #666;
    font-size: 14px;
  }
}

.rule-form {
  padding: 0 24px 24px;
}

.form-section {
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
    font-weight: 600;
    color: #1a1a1a;
    display: flex;
    align-items: center;
    gap: 8px;
    
    .required {
      color: #f56c6c;
    }
    
    .info-icon {
      font-size: 16px;
      color: #909399;
      cursor: help;
    }
  }
}

.form-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.4;
}

.editor-container {
  width: 100%;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #dcdfe6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  
  .toolbar-left {
    .editor-label {
      font-size: 12px;
      color: #666;
      font-weight: 500;
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.monaco-editor {
  border-radius: 0 0 4px 4px;
}

.markdown-preview {
  border: 1px solid #dcdfe6;
  border-radius: 0 0 4px 4px;
  background: white;
  overflow: auto;
  
  .preview-content {
    padding: 16px;
    
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
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  margin-top: 32px;
}

// 响应式设计
@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
  
  .form-header, .rule-form {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .editor-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
    
    .toolbar-right {
      justify-content: flex-end;
    }
  }
}
</style> 