"""
学习统计相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models import User, PracticeSession, TestSession, DailyPractice, UserLearningModule, ChatMessage
from app.schemas import LearningStatsResponse, PublicInfoResponse, InternationalInfoResponse
from app.routers.profile import get_current_user

router = APIRouter(prefix="/learning", tags=["学习统计"])


@router.get("/stats", response_model=LearningStatsResponse)
def get_learning_stats(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习统计信息"""
    try:
        # 获取本周7天的练习情况
        today = datetime.now(timezone.utc)
        week_start = today - timedelta(days=today.weekday())
        week_days = []
        
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # 检查当天是否有练习记录
            practice_count = db.query(DailyPractice).filter(
                and_(
                    DailyPractice.user_id == current_user.id,
                    DailyPractice.practice_date >= day_start,
                    DailyPractice.practice_date <= day_end
                )
            ).count()
            
            week_days.append(practice_count > 0)
        
        # 获取累计完成题目数
        total_questions = db.query(func.sum(DailyPractice.question_count)).filter(
            DailyPractice.user_id == current_user.id
        ).scalar() or 0
        
        # 获取公立模式信息
        public_info = None
        latest_public_session = db.query(PracticeSession).filter(
            PracticeSession.user_id == current_user.id
        ).order_by(PracticeSession.created_at.desc()).first()
        
        if latest_public_session:
            public_info = {
                "grade": latest_public_session.grade,
                "version": latest_public_session.version,
                "unit": latest_public_session.unit,
                "completed": latest_public_session.correct_count + latest_public_session.wrong_count,
                "total": latest_public_session.total_questions,
                "last_practice_time": latest_public_session.completed_at or latest_public_session.started_at
            }
        
        # 获取国际模式信息
        international_info = None
        latest_test = db.query(TestSession).filter(
            TestSession.user_id == current_user.id,
            TestSession.status == "completed"
        ).order_by(TestSession.completed_at.desc()).first()
        
        if latest_test:
            modules_count = db.query(UserLearningModule).filter(
                UserLearningModule.user_id == current_user.id,
                UserLearningModule.is_added == True
            ).count()
            
            # 获取最近对话时间
            latest_chat = db.query(ChatMessage).filter(
                ChatMessage.user_id == current_user.id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            international_info = {
                "level": latest_test.level,
                "modules_count": modules_count,
                "last_conversation_time": latest_chat.created_at if latest_chat else None
            }
        
        return LearningStatsResponse(
            week_days=week_days,
            total_questions=int(total_questions),
            public_info=public_info,
            international_info=international_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习统计失败: {str(e)}"
        )


@router.get("/public/info", response_model=PublicInfoResponse)
def get_public_info(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取公立学校模式学习信息"""
    try:
        latest_session = db.query(PracticeSession).filter(
            PracticeSession.user_id == current_user.id
        ).order_by(PracticeSession.created_at.desc()).first()
        
        if not latest_session:
            return PublicInfoResponse()
        
        return PublicInfoResponse(
            grade=latest_session.grade,
            version=latest_session.version,
            unit=latest_session.unit,
            completed=latest_session.correct_count + latest_session.wrong_count,
            total=latest_session.total_questions,
            last_practice_time=latest_session.completed_at or latest_session.started_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取公立模式信息失败: {str(e)}"
        )


@router.get("/international/info", response_model=InternationalInfoResponse)
def get_international_info(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取国际学校模式学习信息"""
    try:
        latest_test = db.query(TestSession).filter(
            TestSession.user_id == current_user.id,
            TestSession.status == "completed"
        ).order_by(TestSession.completed_at.desc()).first()
        
        if not latest_test:
            return InternationalInfoResponse()
        
        modules_count = db.query(UserLearningModule).filter(
            UserLearningModule.user_id == current_user.id,
            UserLearningModule.is_added == True
        ).count()
        
        # 获取最近对话时间
        latest_chat = db.query(ChatMessage).filter(
            ChatMessage.user_id == current_user.id
        ).order_by(ChatMessage.created_at.desc()).first()
        
        return InternationalInfoResponse(
            level=latest_test.level,
            modules_count=modules_count,
            last_conversation_time=latest_chat.created_at if latest_chat else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取国际模式信息失败: {str(e)}"
        )
