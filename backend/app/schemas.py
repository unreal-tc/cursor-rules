from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .models import VoteType


# 基础响应模型
class ResponseModel(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: str = "Success"
    data: Optional[dict] = None


# 用户相关模型
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 分类相关模型
class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")


class CategoryCreate(CategoryBase):
    """分类创建模型"""
    pass


class CategoryResponse(CategoryBase):
    """分类响应模型"""
    id: int
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# 标签相关模型
class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")


class TagCreate(TagBase):
    """标签创建模型"""
    pass


class TagResponse(TagBase):
    """标签响应模型"""
    id: int
    created_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Cursor Rule相关模型
class CursorRuleBase(BaseModel):
    """Cursor Rule基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    filename: str = Field(..., min_length=1, max_length=100, description="文件名")
    category_id: int = Field(..., description="分类ID")
    description: Optional[str] = Field(None, description="描述")
    content: str = Field(..., min_length=1, description="内容")
    example: Optional[str] = Field(None, description="使用示例")


class CursorRuleCreate(CursorRuleBase):
    """Cursor Rule创建模型"""
    tag_ids: List[int] = Field(default=[], description="标签ID列表")


class CursorRuleUpdate(BaseModel):
    """Cursor Rule更新模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="标题")
    filename: Optional[str] = Field(None, min_length=1, max_length=100, description="文件名")
    category_id: Optional[int] = Field(None, description="分类ID")
    description: Optional[str] = Field(None, description="描述")
    content: Optional[str] = Field(None, min_length=1, description="内容")
    example: Optional[str] = Field(None, description="使用示例")
    tag_ids: Optional[List[int]] = Field(None, description="标签ID列表")


class CursorRuleResponse(CursorRuleBase):
    """Cursor Rule响应模型"""
    id: int
    author_id: int
    likes_count: int = 0
    dislikes_count: int = 0
    download_count: int = 0
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    user_vote: Optional[VoteType] = None
    
    # 关联数据
    author: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class CursorRuleListResponse(BaseModel):
    """Cursor Rule列表响应模型"""
    id: int
    title: str
    filename: str
    description: Optional[str]
    likes_count: int = 0
    dislikes_count: int = 0
    download_count: int = 0
    view_count: int = 0
    created_at: datetime
    
    # 关联数据
    author: Optional[UserResponse] = None
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


# 分页模型
class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int


# 搜索和筛选模型
class CursorRuleFilter(BaseModel):
    """Cursor Rule筛选模型"""
    keyword: Optional[str] = Field(None, description="关键词搜索")
    category_id: Optional[int] = Field(None, description="分类筛选")
    tag_ids: Optional[List[int]] = Field(None, description="标签筛选")
    author_id: Optional[int] = Field(None, description="作者筛选")
    sort_by: Optional[str] = Field("created_at", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")


# 投票模型
class VoteRequest(BaseModel):
    """投票请求模型"""
    vote_type: VoteType = Field(..., description="投票类型")


class VoteResponse(BaseModel):
    """投票响应模型"""
    likes_count: int
    dislikes_count: int
    user_vote: Optional[VoteType] = None


# 批量下载模型
class BatchDownloadRequest(BaseModel):
    """批量下载请求模型"""
    cursor_rule_ids: List[int] = Field(..., min_items=1, max_items=50, description="Cursor Rule ID列表")


# 统计模型
class StatsResponse(BaseModel):
    """统计响应模型"""
    total_rules: int
    total_downloads: int
    total_users: int
    total_categories: int
    total_tags: int