from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本配置
    APP_NAME: str = "Cursor Rules API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置 - 暂时使用SQLite进行测试
    DATABASE_URL: str = "sqlite:///./cursor_rules.db"
    DATABASE_ECHO: bool = True
    
    # JWT配置
    SECRET_KEY: str = "your-super-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30天
    
    # CORS配置
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # 下载配置
    MAX_BATCH_DOWNLOAD: int = 50  # 最大批量下载文件数
    
    # 速率限制配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings() 