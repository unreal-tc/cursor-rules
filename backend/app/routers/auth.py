from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import UserCreate, UserLogin, UserResponse, Token, ResponseModel
from ..auth import authenticate_user, create_access_token, create_user, get_current_user
from ..models import User

router = APIRouter()


@router.post("/register", response_model=ResponseModel)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        user = create_user(db, user_data.username, user_data.password)
        return ResponseModel(
            success=True,
            message="User registered successfully",
            data={"user": UserResponse.from_orm(user)}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=ResponseModel)
async def logout():
    """用户登出（前端处理，删除token）"""
    return ResponseModel(
        success=True,
        message="Logged out successfully"
    ) 