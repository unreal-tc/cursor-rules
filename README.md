# Cursor Rules 分享平台

## 项目简介

Cursor Rules 是一个面向程序员和AI开发者的专业cursor规则分享平台，提供cursor rules文件的上传、管理、分享和下载功能。

## 功能特性

- 🚀 **用户系统**：注册、登录、个人中心
- 📝 **内容管理**：创建、编辑、删除cursor rules
- 🏷️ **分类标签**：一级分类和多标签系统
- 📥 **下载功能**：单文件和批量下载，ZIP格式打包
- 👍 **互动系统**：点赞点踩，浏览统计
- 🔍 **搜索筛选**：按分类、标签、关键词搜索

## 技术栈

### 前端
- Vue.js 3.x - 现代化响应式框架
- Element Plus - UI组件库
- Vue Router 4 - 路由管理
- Pinia - 状态管理
- Axios - HTTP客户端
- Monaco Editor - 代码编辑器

### 后端
- FastAPI - 高性能异步API框架
- SQLAlchemy - ORM框架
- MySQL 8.0+ - 关系型数据库
- Alembic - 数据库迁移工具
- JWT - 用户认证
- bcrypt - 密码加密

### 部署
- Docker - 容器化部署
- Nginx - 反向代理
- docker-compose - 多容器编排

## 项目结构

```
cursor-rules/
├── frontend/                 # 前端Vue.js项目
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                  # 后端FastAPI项目
│   ├── app/
│   ├── alembic/
│   └── requirements.txt
├── docker-compose.yml        # Docker编排文件
├── nginx/                    # Nginx配置
└── README.md
```

## 快速开始

### 环境要求
- Node.js 18+
- Python 3.11+
- MySQL 8.0+
- Docker & Docker Compose

### 开发环境启动

1. **克隆项目**
```bash
git clone <repository-url>
cd cursor-rules
```

2. **使用Docker快速启动**
```bash
docker-compose up -d
```

3. **手动启动（开发模式）**

后端启动：
```bash
cd backend
pip install -r requirements.txt
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

前端启动：
```bash
cd frontend
npm install
npm run dev
```

### 访问地址
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 开发指南

### API文档
启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

### 数据库迁移
```bash
cd backend
alembic upgrade head
```

### 代码规范
- 前端使用ESLint + Prettier
- 后端使用Black + isort

## 部署说明

### Docker部署
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 环境变量配置
复制 `.env.example` 到 `.env` 并配置相应的环境变量。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。 