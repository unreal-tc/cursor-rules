from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from .config import settings
from .database import create_tables

# 应用启动时执行
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_tables()
    yield


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cursor Rules 分享平台 API",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加请求时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "Something went wrong"
        }
    )


# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to Cursor Rules API",
        "docs": "/docs",
        "health": "/health"
    }


# 导入并注册路由
from .routers import auth, cursor_rules, categories, tags, download

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(cursor_rules.router, prefix="/api/cursor-rules", tags=["Cursor Rules"])
app.include_router(categories.router, prefix="/api/categories", tags=["分类"])
app.include_router(tags.router, prefix="/api/tags", tags=["标签"])
app.include_router(download.router, prefix="/api/download", tags=["下载"]) 