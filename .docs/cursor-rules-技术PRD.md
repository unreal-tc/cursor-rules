# Cursor Rules 网站技术PRD

## 1. 项目概述

### 1.1 项目名称
Cursor Rules - AI开发者cursor规则分享平台

### 1.2 项目背景
为程序员和AI开发者提供一个专业的cursor rules文件管理和分享平台，支持上传、下载、分类管理等功能。

### 1.3 目标用户
- 程序员
- AI开发者
- 使用cursor IDE的技术人员

### 1.4 技术栈
- **前端**: Vue.js 3.x
- **后端**: Python + FastAPI
- **数据库**: MySQL 8.0+
- **部署**: Docker + Nginx

## 2. 功能需求

### 2.1 核心功能模块

#### 2.1.1 用户系统
- 用户注册（用户名 + 密码）
- 用户登录/登出
- 个人中心（管理自己的cursor rules）

#### 2.1.2 Cursor Rules管理
- 创建cursor rules
- 编辑自己的cursor rules
- 删除自己的cursor rules
- 查看cursor rules详情

#### 2.1.3 分类和标签系统
- 一级类目管理（用户可创建）
- 标签管理（用户可创建）
- cursor rules分类展示

#### 2.1.4 下载系统
- 单个cursor rules下载
- 批量下载（复选框选择）
- ZIP格式打包下载

#### 2.1.5 互动系统
- 点赞/点踩功能（无需登录）
- 浏览统计

## 3. 数据库设计

### 3.1 用户表 (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3.2 一级类目表 (categories)
```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### 3.3 标签表 (tags)
```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### 3.4 Cursor Rules表 (cursor_rules)
```sql
CREATE TABLE cursor_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    filename VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    example TEXT,
    author_id INT NOT NULL,
    likes_count INT DEFAULT 0,
    dislikes_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

### 3.5 Cursor Rules标签关联表 (cursor_rules_tags)
```sql
CREATE TABLE cursor_rules_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cursor_rule_id INT NOT NULL,
    tag_id INT NOT NULL,
    FOREIGN KEY (cursor_rule_id) REFERENCES cursor_rules(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    UNIQUE KEY unique_rule_tag (cursor_rule_id, tag_id)
);
```

### 3.6 点赞点踩记录表 (votes)
```sql
CREATE TABLE votes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cursor_rule_id INT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    vote_type ENUM('like', 'dislike') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cursor_rule_id) REFERENCES cursor_rules(id) ON DELETE CASCADE,
    UNIQUE KEY unique_ip_rule (cursor_rule_id, ip_address)
);
```

## 4. API接口设计

### 4.1 用户认证接口
```
POST /api/auth/register        # 用户注册
POST /api/auth/login          # 用户登录
POST /api/auth/logout         # 用户登出
GET  /api/auth/profile        # 获取用户信息
```

### 4.2 Cursor Rules接口
```
GET    /api/cursor-rules           # 获取cursor rules列表
GET    /api/cursor-rules/:id       # 获取单个cursor rule详情
POST   /api/cursor-rules           # 创建cursor rule
PUT    /api/cursor-rules/:id       # 更新cursor rule
DELETE /api/cursor-rules/:id       # 删除cursor rule
GET    /api/cursor-rules/my        # 获取我的cursor rules
```

### 4.3 下载接口
```
GET  /api/download/single/:id     # 单个文件下载
POST /api/download/batch          # 批量下载（传入ID数组）
```

### 4.4 分类和标签接口
```
GET  /api/categories              # 获取所有分类
POST /api/categories              # 创建新分类
GET  /api/tags                    # 获取所有标签
POST /api/tags                    # 创建新标签
```

### 4.5 互动接口
```
POST /api/cursor-rules/:id/vote   # 点赞/点踩
```

## 5. 前端页面设计

### 5.1 页面结构
```
├── 首页 (/)
├── 登录页 (/login)
├── 注册页 (/register)
├── Cursor Rule详情页 (/cursor-rule/:id)
├── 个人中心 (/profile)
├── 创建/编辑页 (/cursor-rule/create 或 /cursor-rule/edit/:id)
```

### 5.2 组件设计

#### 5.2.1 通用组件
- Header组件（导航栏、登录状态）
- Footer组件
- MarkdownEditor组件（说明和内容编辑）
- RichTextEditor组件（例子编辑）

#### 5.2.2 业务组件
- CursorRuleCard组件（列表展示卡片）
- VoteButtons组件（点赞点踩按钮）
- TagSelector组件（标签选择器）
- CategorySelector组件（分类选择器）
- BatchDownload组件（批量下载功能）

### 5.3 UI/UX设计要求
- 响应式设计，支持移动端访问
- 现代化UI风格，使用Element Plus或类似组件库
- 深色/浅色主题切换
- 代码高亮显示

## 6. 技术实现细节

### 6.1 文件下载实现
- 单个文件：生成.mdc格式文件
- 批量下载：创建ZIP包，包含日期前缀命名
- 文件结构：`/.cursor/rules/文件名称.mdc`

### 6.2 安全考虑
- 密码使用bcrypt加密
- JWT Token认证
- SQL注入防护
- XSS攻击防护
- 文件名安全检查（只允许英文、数字、-）

### 6.3 性能优化
- 数据库索引优化
- 静态资源CDN
- API响应缓存
- 图片懒加载

## 7. 部署方案

### 7.1 Docker配置
```dockerfile
# 前端Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

# 后端Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 docker-compose.yml
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:password@mysql:3306/cursor_rules
    depends_on:
      - mysql
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: cursor_rules
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## 8. 开发计划

### 8.1 第一阶段 (2周)
- [ ] 项目环境搭建
- [ ] 数据库设计和创建
- [ ] 用户认证系统
- [ ] 基础CRUD接口

### 8.2 第二阶段 (2周)
- [ ] 前端基础框架搭建
- [ ] 首页列表展示
- [ ] 用户登录注册页面
- [ ] Cursor Rule详情页

### 8.3 第三阶段 (2周)
- [ ] 创建/编辑功能
- [ ] 个人中心
- [ ] 下载功能实现
- [ ] 点赞点踩功能

### 8.4 第四阶段 (1周)
- [ ] UI优化和测试
- [ ] 部署配置
- [ ] 性能优化
- [ ] 文档完善

## 9. 风险评估

### 9.1 技术风险
- Markdown编辑器选择和定制
- 大文件批量下载性能问题
- 并发访问数据库性能

### 9.2 业务风险
- 用户生成内容质量控制
- 恶意上传和滥用防护
- 存储空间管理

### 9.3 解决方案
- 选择成熟的开源Markdown编辑器
- 实现异步下载和进度显示
- 数据库连接池和查询优化
- 内容审核机制
- 文件大小限制和清理策略

## 10. 验收标准

### 10.1 功能验收
- [ ] 所有API接口正常工作
- [ ] 前端页面功能完整
- [ ] 下载功能正确生成文件格式
- [ ] 用户权限控制正确

### 10.2 性能验收
- [ ] 页面加载时间 < 3秒
- [ ] API响应时间 < 500ms
- [ ] 支持100+并发用户访问

### 10.3 安全验收
- [ ] 通过基础安全扫描
- [ ] 用户数据加密存储
- [ ] 防止常见Web攻击

---

**文档版本**: v1.0  
**创建日期**: 2024年12月  
**最后更新**: 2024年12月 