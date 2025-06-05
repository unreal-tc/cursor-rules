from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, asc
from typing import List, Optional
import math

from ..database import get_db
from ..schemas import (
    CursorRuleCreate, CursorRuleUpdate, CursorRuleResponse, CursorRuleListResponse,
    PaginatedResponse, VoteRequest, VoteResponse, ResponseModel
)
from ..auth import get_current_user, get_current_user_optional
from ..models import User, CursorRule, Category, Tag, CursorRuleTag, Vote, VoteType

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """获取客户端IP地址"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host


@router.get("", response_model=PaginatedResponse)
async def get_cursor_rules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    category_id: Optional[int] = Query(None, description="分类筛选"),
    tag_ids: Optional[str] = Query(None, description="标签筛选(逗号分隔)"),
    author_id: Optional[int] = Query(None, description="作者筛选"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    db: Session = Depends(get_db)
):
    """获取cursor rules列表"""
    query = db.query(CursorRule).options(
        joinedload(CursorRule.author),
        joinedload(CursorRule.category),
        joinedload(CursorRule.tags)
    )
    
    # 关键词搜索
    if keyword:
        search_filter = or_(
            CursorRule.title.contains(keyword),
            CursorRule.description.contains(keyword),
            CursorRule.content.contains(keyword)
        )
        query = query.filter(search_filter)
    
    # 分类筛选
    if category_id:
        query = query.filter(CursorRule.category_id == category_id)
    
    # 标签筛选
    if tag_ids:
        tag_id_list = [int(tid.strip()) for tid in tag_ids.split(",") if tid.strip().isdigit()]
        if tag_id_list:
            query = query.join(CursorRuleTag).filter(CursorRuleTag.tag_id.in_(tag_id_list))
    
    # 作者筛选
    if author_id:
        query = query.filter(CursorRule.author_id == author_id)
    
    # 排序
    if hasattr(CursorRule, sort_by):
        order_column = getattr(CursorRule, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(order_column))
    
    # 分页
    total = query.count()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 转换为响应格式
    cursor_rules = []
    for item in items:
        cursor_rule_data = CursorRuleListResponse.from_orm(item)
        cursor_rules.append(cursor_rule_data.dict())
    
    return PaginatedResponse(
        items=cursor_rules,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size)
    )


@router.get("/my", response_model=PaginatedResponse)
async def get_my_cursor_rules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的cursor rules"""
    query = db.query(CursorRule).options(
        joinedload(CursorRule.category),
        joinedload(CursorRule.tags)
    ).filter(CursorRule.author_id == current_user.id).order_by(desc(CursorRule.created_at))
    
    total = query.count()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    cursor_rules = []
    for item in items:
        cursor_rule_data = CursorRuleListResponse.from_orm(item)
        cursor_rules.append(cursor_rule_data.dict())
    
    return PaginatedResponse(
        items=cursor_rules,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size)
    )


@router.get("/{cursor_rule_id}", response_model=CursorRuleResponse)
async def get_cursor_rule(
    cursor_rule_id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取单个cursor rule详情"""
    cursor_rule = db.query(CursorRule).options(
        joinedload(CursorRule.author),
        joinedload(CursorRule.category),
        joinedload(CursorRule.tags)
    ).filter(CursorRule.id == cursor_rule_id).first()
    
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    # 获取用户投票状态（优先使用用户ID，其次使用IP地址）
    ip_address = get_client_ip(request)
    if current_user:
        user_vote = db.query(Vote).filter(
            Vote.cursor_rule_id == cursor_rule_id,
            Vote.user_id == current_user.id
        ).first()
    else:
        user_vote = db.query(Vote).filter(
            Vote.cursor_rule_id == cursor_rule_id,
            Vote.ip_address == ip_address,
            Vote.user_id.is_(None)
        ).first()
    
    # 实时计算统计数据
    likes_count = db.query(Vote).filter(
        Vote.cursor_rule_id == cursor_rule_id,
        Vote.vote_type == VoteType.LIKE
    ).count()
    
    dislikes_count = db.query(Vote).filter(
        Vote.cursor_rule_id == cursor_rule_id,
        Vote.vote_type == VoteType.DISLIKE
    ).count()
    
    # 转换为响应模型
    response_data = CursorRuleResponse.from_orm(cursor_rule)
    response_data.user_vote = user_vote.vote_type if user_vote else None
    response_data.likes_count = likes_count
    response_data.dislikes_count = dislikes_count
    
    return response_data


@router.get("/{cursor_rule_id}/view", response_model=CursorRuleResponse)
async def view_cursor_rule(cursor_rule_id: int, db: Session = Depends(get_db)):
    """查看单个cursor rule详情（view路由别名）"""
    cursor_rule = db.query(CursorRule).options(
        joinedload(CursorRule.author),
        joinedload(CursorRule.category),
        joinedload(CursorRule.tags)
    ).filter(CursorRule.id == cursor_rule_id).first()
    
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    return CursorRuleResponse.from_orm(cursor_rule)


@router.post("/{cursor_rule_id}/view", response_model=CursorRuleResponse)
async def record_view(cursor_rule_id: int, db: Session = Depends(get_db)):
    """记录浏览量"""
    cursor_rule = db.query(CursorRule).options(
        joinedload(CursorRule.author),
        joinedload(CursorRule.category),
        joinedload(CursorRule.tags)
    ).filter(CursorRule.id == cursor_rule_id).first()
    
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    # 增加浏览计数
    cursor_rule.view_count += 1
    db.commit()
    db.refresh(cursor_rule)
    
    return CursorRuleResponse.from_orm(cursor_rule)


@router.post("", response_model=ResponseModel)
async def create_cursor_rule(
    cursor_rule_data: CursorRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建cursor rule"""
    # 验证分类是否存在
    category = db.query(Category).filter(Category.id == cursor_rule_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # 验证标签是否存在
    if cursor_rule_data.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(cursor_rule_data.tag_ids)).all()
        if len(existing_tags) != len(cursor_rule_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some tags not found"
            )
    
    # 创建cursor rule
    cursor_rule = CursorRule(
        title=cursor_rule_data.title,
        filename=cursor_rule_data.filename,
        category_id=cursor_rule_data.category_id,
        description=cursor_rule_data.description,
        content=cursor_rule_data.content,
        example=cursor_rule_data.example,
        author_id=current_user.id
    )
    db.add(cursor_rule)
    db.flush()  # 获取ID
    
    # 添加标签关联
    if cursor_rule_data.tag_ids:
        for tag_id in cursor_rule_data.tag_ids:
            cursor_rule_tag = CursorRuleTag(cursor_rule_id=cursor_rule.id, tag_id=tag_id)
            db.add(cursor_rule_tag)
    
    db.commit()
    db.refresh(cursor_rule)
    
    return ResponseModel(
        success=True,
        message="Cursor rule created successfully",
        data={"cursor_rule_id": cursor_rule.id}
    )


@router.put("/{cursor_rule_id}", response_model=ResponseModel)
async def update_cursor_rule(
    cursor_rule_id: int,
    cursor_rule_data: CursorRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新cursor rule"""
    cursor_rule = db.query(CursorRule).filter(CursorRule.id == cursor_rule_id).first()
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    # 检查权限
    if cursor_rule.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this cursor rule"
        )
    
    # 更新字段
    update_data = cursor_rule_data.dict(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)
    
    for field, value in update_data.items():
        setattr(cursor_rule, field, value)
    
    # 更新标签关联
    if tag_ids is not None:
        # 删除旧的标签关联
        db.query(CursorRuleTag).filter(CursorRuleTag.cursor_rule_id == cursor_rule_id).delete()
        
        # 添加新的标签关联
        if tag_ids:
            for tag_id in tag_ids:
                cursor_rule_tag = CursorRuleTag(cursor_rule_id=cursor_rule_id, tag_id=tag_id)
                db.add(cursor_rule_tag)
    
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Cursor rule updated successfully"
    )


@router.delete("/{cursor_rule_id}", response_model=ResponseModel)
async def delete_cursor_rule(
    cursor_rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除cursor rule"""
    cursor_rule = db.query(CursorRule).filter(CursorRule.id == cursor_rule_id).first()
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    # 检查权限
    if cursor_rule.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this cursor rule"
        )
    
    db.delete(cursor_rule)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="Cursor rule deleted successfully"
    )


@router.post("/{cursor_rule_id}/vote", response_model=VoteResponse)
async def vote_cursor_rule(
    cursor_rule_id: int,
    vote_data: VoteRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """投票（点赞/点踩）"""
    # 检查cursor rule是否存在
    cursor_rule = db.query(CursorRule).filter(CursorRule.id == cursor_rule_id).first()
    if not cursor_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cursor rule not found"
        )
    
    ip_address = get_client_ip(request)
    
    # 检查是否已投票
    if current_user:
        # 登录用户：先检查user_id约束
        existing_vote = db.query(Vote).filter(
            Vote.cursor_rule_id == cursor_rule_id,
            Vote.user_id == current_user.id
        ).first()
        
        # 如果没有找到用户投票记录，检查是否有相同IP的记录（可能是之前未登录时投的票）
        if not existing_vote:
            existing_vote = db.query(Vote).filter(
                Vote.cursor_rule_id == cursor_rule_id,
                Vote.ip_address == ip_address
            ).first()
            # 如果找到了相同IP的记录，将其转换为登录用户的记录
            if existing_vote:
                existing_vote.user_id = current_user.id
    else:
        # 未登录用户：检查ip_address约束（不管user_id是什么）
        existing_vote = db.query(Vote).filter(
            Vote.cursor_rule_id == cursor_rule_id,
            Vote.ip_address == ip_address
        ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_data.vote_type:
            # 取消投票
            db.delete(existing_vote)
        else:
            # 更新投票类型
            existing_vote.vote_type = vote_data.vote_type
    else:
        # 新增投票
        new_vote = Vote(
            cursor_rule_id=cursor_rule_id,
            user_id=current_user.id if current_user else None,
            ip_address=ip_address,
            vote_type=vote_data.vote_type
        )
        db.add(new_vote)
    
    # 提交投票操作
    db.commit()
    
    # 重新计算统计数据（确保数据一致性）
    likes_count = db.query(Vote).filter(
        Vote.cursor_rule_id == cursor_rule_id,
        Vote.vote_type == VoteType.LIKE
    ).count()
    
    dislikes_count = db.query(Vote).filter(
        Vote.cursor_rule_id == cursor_rule_id,
        Vote.vote_type == VoteType.DISLIKE
    ).count()
    
    # 更新cursor_rule表中的计数
    cursor_rule.likes_count = likes_count
    cursor_rule.dislikes_count = dislikes_count
    
    # 再次提交更新的计数
    db.commit()
    
    # 获取用户当前投票状态
    if current_user:
        # 登录用户：根据user_id查询
        current_vote = db.query(Vote).filter(
            Vote.cursor_rule_id == cursor_rule_id,
            Vote.user_id == current_user.id
        ).first()
    else:
        # 未登录用户：根据ip_address查询（不管user_id是什么）
        current_vote = db.query(Vote).filter(
            Vote.cursor_rule_id == cursor_rule_id,
            Vote.ip_address == ip_address
        ).first()
    
    return VoteResponse(
        likes_count=likes_count,
        dislikes_count=dislikes_count,
        user_vote=current_vote.vote_type if current_vote else None
    )