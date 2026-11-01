"""
用户资料相关路由：获取、更新用户信息、头像上传
"""
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas import UserProfileResponse, UserUpdateRequest, MessageResponse
from app.models import User
from app.user_services import UserService
from app.utils import get_current_user_id
from app.config import settings

router = APIRouter(prefix="/profile", tags=["用户资料"])

# 创建头像存储目录
AVATAR_DIR = Path("static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

def get_current_user(authorization: Optional[str] = Header(None, alias="Authorization"), db: Session = Depends(get_db)):
    """获取当前登录用户（依赖注入）"""
    # 检查Authorization header是否存在且非空
    if not authorization or not authorization.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 移除Bearer前缀并清理空白字符
    token = authorization.strip()
    if token.startswith("Bearer "):
        token = token[7:].strip()
    
    # 检查token是否为空
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token格式",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从token中获取用户ID
    user_id = get_current_user_id(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的token或token已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户对象
    user = UserService.get_user_by_id(db, user_id)
    return user

@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户资料"""
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        phone=current_user.phone,
        email=current_user.email,
        avatar=current_user.avatar,
        nickname=current_user.nickname,
        bio=current_user.bio,
        gender=current_user.gender,
        birthday=current_user.birthday,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )

@router.put("/me", response_model=UserProfileResponse)
def update_profile(
    user_data: UserUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    try:
        # 更新可选的字段
        update_data = user_data.model_dump(exclude_unset=True)
        
        # 检查邮箱是否已被其他用户使用
        if "email" in update_data and update_data["email"]:
            existing_user = db.query(User).filter(
                User.email == update_data["email"],
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该邮箱已被其他用户使用"
                )
        
        # 更新用户字段
        for field, value in update_data.items():
            if hasattr(current_user, field) and value is not None:
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            phone=current_user.phone,
            email=current_user.email,
            avatar=current_user.avatar,
            nickname=current_user.nickname,
            bio=current_user.bio,
            gender=current_user.gender,
            birthday=current_user.birthday,
            created_at=current_user.created_at,
            last_login_at=current_user.last_login_at
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"更新用户资料时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新资料失败，请稍后重试"
        )

@router.post("/avatar", response_model=MessageResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传头像"""
    try:
        # 验证文件类型
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型，仅支持：jpg, png, gif, webp"
            )
        
        # 验证文件大小（最大5MB）
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件过大，最大支持5MB"
            )
        
        # 生成文件名（使用用户ID和时间戳，确保唯一性）
        import time
        file_ext = Path(file.filename).suffix.lower() or ".jpg"
        timestamp = int(time.time())
        avatar_filename = f"{current_user.id}_{timestamp}{file_ext}"
        avatar_path = AVATAR_DIR / avatar_filename
        
        # 如果用户已有头像，删除旧头像
        if current_user.avatar:
            old_avatar_path = Path("static") / current_user.avatar.lstrip("/static/")
            if old_avatar_path.exists() and old_avatar_path.is_file():
                try:
                    old_avatar_path.unlink()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"删除旧头像失败: {str(e)}")
        
        # 保存新头像
        with open(avatar_path, "wb") as f:
            f.write(file_content)
        
        # 更新数据库中的头像路径（相对路径，用于API访问）
        avatar_url = f"/static/avatars/{avatar_filename}"
        current_user.avatar = avatar_url
        db.commit()
        db.refresh(current_user)
        
        return MessageResponse(message="头像上传成功", avatar_url=avatar_url)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"上传头像时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="上传头像失败，请稍后重试"
        )

