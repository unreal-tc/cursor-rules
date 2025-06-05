from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import TagCreate, TagResponse, ResponseModel
from ..auth import get_current_user
from ..models import User, Tag

router = APIRouter()


@router.get("", response_model=List[TagResponse])
async def get_tags(db: Session = Depends(get_db)):
    """获取所有标签"""
    tags = db.query(Tag).order_by(Tag.created_at.desc()).all()
    return [TagResponse.from_orm(tag) for tag in tags]


@router.post("", response_model=ResponseModel)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新标签"""
    # 检查标签名是否已存在
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists"
        )
    
    # 创建新标签
    tag = Tag(
        name=tag_data.name,
        created_by=current_user.id
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return ResponseModel(
        success=True,
        message="Tag created successfully",
        data={"tag": TagResponse.from_orm(tag)}
    )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取单个标签详情"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return TagResponse.from_orm(tag) 