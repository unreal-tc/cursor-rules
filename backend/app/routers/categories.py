from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import CategoryCreate, CategoryResponse, ResponseModel
from ..auth import get_current_user
from ..models import User, Category

router = APIRouter()


@router.get("", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(Category).order_by(Category.created_at.desc()).all()
    return [CategoryResponse.from_orm(category) for category in categories]


@router.post("", response_model=ResponseModel)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新分类（支持幂等操作）"""
    # 检查分类名是否已存在
    existing_category = db.query(Category).filter(Category.name == category_data.name).first()
    if existing_category:
        # 如果分类已存在，直接返回现有分类（幂等操作）
        return ResponseModel(
            success=True,
            message="Category already exists",
            data={"category": CategoryResponse.from_orm(existing_category)}
        )
    
    # 创建新分类
    category = Category(
        name=category_data.name,
        description=category_data.description,
        created_by=current_user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return ResponseModel(
        success=True,
        message="Category created successfully",
        data={"category": CategoryResponse.from_orm(category)}
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取单个分类详情"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return CategoryResponse.from_orm(category) 