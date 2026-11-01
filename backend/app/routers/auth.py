"""
认证相关路由：注册、登录、忘记密码、短信验证码登录
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, MessageResponse,
    SendSmsCodeRequest, SmsLoginRequest, SmsCodeResponse
)
from app.user_services import UserService, SmsService
from app.utils import create_access_token
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 创建用户
    user = UserService.create_user(db, user_data)
    
    # 生成token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    )

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录（支持用户名或手机号）"""
    # 验证用户
    user = UserService.authenticate_user(db, login_data.username, login_data.password)
    
    # 生成token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
    )

@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """忘记密码：发送重置token"""
    try:
        reset_token = UserService.request_password_reset(db, request.email)
        
        # 在实际应用中，这里应该发送邮件
        # 为了简化，我们直接返回token（生产环境应该通过邮件发送）
        return MessageResponse(
            message=f"密码重置token已生成（开发环境直接返回，生产环境应通过邮件发送）: {reset_token}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求时出错: {str(e)}"
        )

@router.post("/reset-password", response_model=MessageResponse)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """重置密码"""
    try:
        UserService.reset_password(db, request.token, request.new_password)
        return MessageResponse(message="密码重置成功")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理请求时出错: {str(e)}"
        )

@router.post("/send-sms-code", response_model=SmsCodeResponse)
def send_sms_code(request: SendSmsCodeRequest, db: Session = Depends(get_db)):
    """发送短信验证码"""
    try:
        code = SmsService.send_sms_code(db, request.phone, request.purpose)
        
        # 根据配置决定是否返回验证码（开发模式返回，生产模式不返回）
        from app.config import settings
        if settings.SMS_DEV_MODE:
            return SmsCodeResponse(
                message="验证码已发送（开发模式：验证码直接返回）",
                code=code
            )
        else:
            return SmsCodeResponse(
                message="验证码已发送，请查收短信",
                code=None  # 生产环境不返回验证码
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送验证码失败: {str(e)}"
        )

@router.post("/sms-login", response_model=TokenResponse)
def sms_login(request: SmsLoginRequest, db: Session = Depends(get_db)):
    """短信验证码登录（如果手机号未注册，会自动创建账号）"""
    try:
        # 验证码登录
        user = SmsService.sms_login(db, request.phone, request.code)
        
        # 生成token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                phone=user.phone,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login_at=user.last_login_at
            )
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

