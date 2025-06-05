from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import zipfile
from io import BytesIO
import uuid

from ..database import get_db
from ..schemas import BatchDownloadRequest, ResponseModel
from ..models import CursorRule, User, Category, Tag
from ..config import settings

router = APIRouter()


def create_zip_response(cursor_rules: List[CursorRule], filename_prefix: str = "cursor-rules") -> StreamingResponse:
    """创建ZIP文件响应"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for cursor_rule in cursor_rules:
            # 文件路径：.cursor/rules/文件名.mdc
            file_path = f".cursor/rules/{cursor_rule.filename}.mdc"
            zip_file.writestr(file_path, cursor_rule.content)
    
    zip_buffer.seek(0)
    
    # 生成随机文件名
    random_name = str(uuid.uuid4())[:8]
    zip_filename = f"{filename_prefix}-{random_name}.zip"
    
    return StreamingResponse(
        BytesIO(zip_buffer.read()),
        media_type='application/zip',
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )


@router.get("/single/{cursor_rule_id}")
async def download_single(cursor_rule_id: int, db: Session = Depends(get_db)):
    """单个文件下载"""
    cursor_rule = db.query(CursorRule).filter(CursorRule.id == cursor_rule_id).first()
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    # 增加下载计数
    cursor_rule.download_count += 1
    db.commit()
    
    # 生成ZIP响应
    return create_zip_response([cursor_rule], "cursor-rule")


@router.post("/batch")
async def download_batch(
    download_data: BatchDownloadRequest,
    db: Session = Depends(get_db)
):
    """批量下载"""
    if len(download_data.cursor_rule_ids) > settings.MAX_BATCH_DOWNLOAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot download more than {settings.MAX_BATCH_DOWNLOAD} files at once"
        )
    
    cursor_rules = db.query(CursorRule).filter(
        CursorRule.id.in_(download_data.cursor_rule_ids)
    ).all()
    
    if not cursor_rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cursor rules found"
        )
    
    if len(cursor_rules) != len(download_data.cursor_rule_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some cursor rules not found"
        )
    
    # 增加下载计数
    for cursor_rule in cursor_rules:
        cursor_rule.download_count += 1
    db.commit()
    
    # 生成ZIP响应
    return create_zip_response(cursor_rules, "cursor-rules-batch")


@router.get("/stats")
async def download_stats(db: Session = Depends(get_db)):
    """下载统计"""
    total_downloads = db.query(func.sum(CursorRule.download_count)).scalar() or 0
    
    most_downloaded = db.query(CursorRule).order_by(
        CursorRule.download_count.desc()
    ).limit(10).all()
    
    return {
        "total_downloads": total_downloads,
        "most_downloaded": [
            {
                "id": rule.id,
                "title": rule.title,
                "download_count": rule.download_count
            }
            for rule in most_downloaded
        ]
    }


@router.get("/platform-stats")
async def platform_stats(db: Session = Depends(get_db)):
    """平台统计信息"""
    # 统计总用户数
    total_users = db.query(User).count()
    
    # 统计总规则数
    total_rules = db.query(CursorRule).count()
    
    # 统计总下载数
    total_downloads = db.query(func.sum(CursorRule.download_count)).scalar() or 0
    
    # 统计总分类数
    total_categories = db.query(Category).count()
    
    # 统计总标签数
    total_tags = db.query(Tag).count()
    
    return {
        "total_users": total_users,
        "total_rules": total_rules,
        "total_downloads": total_downloads,
        "total_categories": total_categories,
        "total_tags": total_tags
    } 