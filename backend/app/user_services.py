"""
服务层：业务逻辑
"""
import random
import string
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
from app.models import User, SmsCode
from app.utils import get_password_hash, verify_password, generate_reset_token
from app.schemas import UserRegister, UserLogin
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserRegister) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )
        
        # 检查手机号是否已存在
        existing_phone = db.query(User).filter(User.phone == user_data.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被注册"
            )
        
        # 创建新用户
        try:
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                username=user_data.username,
                phone=user_data.phone,
                password_hash=hashed_password,
                is_active=True
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            # 检查是哪个字段违反唯一约束
            if "username" in error_msg.lower() or "users.username" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该用户名已被使用"
                )
            elif "phone" in error_msg.lower() or "users.phone" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已被注册"
                )
            logger.error(f"创建用户时数据库错误: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败，请稍后重试"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"创建用户时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败，请稍后重试"
            )
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User:
        """验证用户（支持用户名或手机号登录）"""
        # 查找用户（支持用户名或手机号）
        user = db.query(User).filter(
            or_(User.username == username, User.phone == username)
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        # 更新最后登录时间
        try:
            user.last_login_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            logger.error(f"更新登录时间时发生错误: {str(e)}")
            # 即使更新失败，也返回用户对象（登录时间不是关键）
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """根据ID获取用户"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """根据邮箱获取用户"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="该邮箱未注册"
            )
        return user
    
    @staticmethod
    def request_password_reset(db: Session, email: str) -> str:
        """请求重置密码（生成重置token）"""
        user = UserService.get_user_by_email(db, email)
        
        # 生成重置token
        try:
            reset_token = generate_reset_token()
            user.reset_token = reset_token
            user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # 1小时有效期
            
            db.commit()
            db.refresh(user)
            return reset_token
        except Exception as e:
            db.rollback()
            logger.error(f"生成重置token时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="生成重置token失败，请稍后重试"
            )
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> User:
        """重置密码"""
        user = db.query(User).filter(User.reset_token == token).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的重置token"
            )
        
        if user.reset_token_expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重置token已过期"
            )
        
        # 更新密码并清除重置token
        try:
            user.password_hash = get_password_hash(new_password)
            user.reset_token = None
            user.reset_token_expires = None
            
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"重置密码时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="重置密码失败，请稍后重试"
            )

    @staticmethod
    def get_user_by_phone(db: Session, phone: str) -> User:
        """根据手机号获取用户"""
        user = db.query(User).filter(User.phone == phone).first()
        return user

    @staticmethod
    def get_or_create_user_by_phone(db: Session, phone: str) -> User:
        """根据手机号获取或创建用户"""
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            # 自动创建用户
            username = f"user_{phone[-4:]}"
            # 确保用户名唯一
            base_username = username
            counter = 1
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}_{counter}"
                counter += 1
            
            # 创建用户（使用随机密码，因为是手机验证码登录）
            try:
                random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                user = User(
                    username=username,
                    phone=phone,
                    password_hash=get_password_hash(random_password),
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            except IntegrityError as e:
                db.rollback()
                # 如果创建失败（可能并发），重新查询
                user = db.query(User).filter(User.phone == phone).first()
                if not user:
                    error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
                    logger.error(f"自动创建用户时数据库错误: {error_msg}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="创建用户失败，请稍后重试"
                    )
            except Exception as e:
                db.rollback()
                logger.error(f"自动创建用户时发生错误: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建用户失败，请稍后重试"
                )
        
        return user


class SmsService:
    """短信服务类"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """生成随机验证码"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def send_sms_code(db: Session, phone: str, purpose: str = "login") -> str:
        """发送短信验证码"""
        # 检查是否在60秒内已发送过
        recent_code = db.query(SmsCode).filter(
            SmsCode.phone == phone,
            SmsCode.purpose == purpose,
            SmsCode.created_at > datetime.now(timezone.utc) - timedelta(seconds=60)
        ).first()
        
        if recent_code:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请60秒后再试"
            )
        
        # 生成验证码
        code = SmsService.generate_code()
        
        # 保存到数据库
        try:
            sms_code = SmsCode(
                phone=phone,
                code=code,
                purpose=purpose,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=5)  # 5分钟有效期
            )
            db.add(sms_code)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"保存验证码到数据库时发生错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="发送验证码失败，请稍后重试"
            )
        
        # 发送短信（真实短信或开发模式）
        from app.sms_sender import send_sms
        send_success = send_sms(phone, code, purpose)
        
        if not send_success:
            # 如果发送失败，可以选择是否抛出异常
            # 这里记录日志但不阻止流程（因为验证码已保存到数据库）
            logger.warning(f"短信发送失败，但验证码已保存: {phone}")
        
        return code
    
    @staticmethod
    def verify_sms_code(db: Session, phone: str, code: str, purpose: str = "login") -> bool:
        """验证短信验证码"""
        sms_code = db.query(SmsCode).filter(
            SmsCode.phone == phone,
            SmsCode.code == code,
            SmsCode.purpose == purpose,
            SmsCode.is_used == False,
            SmsCode.expires_at > datetime.now(timezone.utc)
        ).order_by(SmsCode.created_at.desc()).first()
        
        if not sms_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误或已过期"
            )
        
        # 标记为已使用
        try:
            sms_code.is_used = True
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"标记验证码为已使用时发生错误: {str(e)}")
            # 即使标记失败，验证码已经验证成功，返回True
            return True
    
    @staticmethod
    def sms_login(db: Session, phone: str, code: str) -> User:
        """短信验证码登录"""
        # 验证验证码
        SmsService.verify_sms_code(db, phone, code, "login")
        
        # 获取或创建用户
        user = UserService.get_or_create_user_by_phone(db, phone)
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账户已被禁用"
            )
        
        # 更新最后登录时间
        try:
            user.last_login_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            logger.error(f"更新登录时间时发生错误: {str(e)}")
            # 即使更新失败，也返回用户对象（登录时间不是关键）
        
        return user

