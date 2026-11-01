"""
错题本相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import WrongQuestion, PracticeQuestion
from app.schemas import (
    WrongQuestionResponse, AddWrongQuestionRequest, ReviewQuestionsResponse,
    QuestionResponse, MessageResponse
)
from app.routers.profile import get_current_user

router = APIRouter(prefix="/wrongbook", tags=["错题本"])


@router.get("/list")
def get_wrongbook_list(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取错题本列表（带分页信息）"""
    try:
        # 获取总数
        total = db.query(func.count(WrongQuestion.id)).filter(
            WrongQuestion.user_id == current_user.id
        ).scalar() or 0
        
        # 获取分页数据
        wrong_questions = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id
        ).order_by(WrongQuestion.added_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [
            WrongQuestionResponse(
                id=wq.id,
                question_type=wq.question_type,
                question=wq.question,
                options=wq.options,
                correct_answer=wq.correct_answer,
                user_answer=wq.user_answer,
                explanation=wq.explanation,
                added_at=wq.added_at
            ) for wq in wrong_questions
        ]
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if total > 0 else 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取错题本失败: {str(e)}"
        )


@router.post("/add", response_model=MessageResponse)
def add_wrong_question(
    request: AddWrongQuestionRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加错题到错题本"""
    try:
        # 检查是否已存在（通过题目ID或题目内容）
        if request.question_id:
            existing = db.query(WrongQuestion).filter(
                WrongQuestion.user_id == current_user.id,
                WrongQuestion.question_id == request.question_id
            ).first()
            if existing:
                return MessageResponse(message="该题目已在错题本中")
        
        wrong_question = WrongQuestion(
            user_id=current_user.id,
            question_id=request.question_id,
            question_type=request.question_type,
            question=request.question,
            options=request.options,
            correct_answer=request.correct_answer,
            user_answer=request.user_answer,
            explanation=request.explanation,
            grade=request.grade,
            version=request.version,
            unit=request.unit
        )
        db.add(wrong_question)
        db.commit()
        
        return MessageResponse(message="已添加到错题本")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加错题失败: {str(e)}"
        )


@router.delete("/{wrong_id}", response_model=MessageResponse)
def delete_wrong_question(
    wrong_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除错题"""
    try:
        wrong_question = db.query(WrongQuestion).filter(
            WrongQuestion.id == wrong_id,
            WrongQuestion.user_id == current_user.id
        ).first()
        
        if not wrong_question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="错题不存在"
            )
        
        db.delete(wrong_question)
        db.commit()
        
        return MessageResponse(message="已删除错题")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除错题失败: {str(e)}"
        )


@router.post("/review", response_model=ReviewQuestionsResponse)
def review_wrong_questions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成错题复习题目"""
    try:
        # 获取用户的错题
        wrong_questions = db.query(WrongQuestion).filter(
            WrongQuestion.user_id == current_user.id
        ).order_by(WrongQuestion.added_at.desc()).limit(10).all()
        
        questions = [
            QuestionResponse(
                id=wq.id,
                question_type=wq.question_type,
                question=wq.question,
                options=wq.options,
                correct_answer=wq.correct_answer,
                explanation=wq.explanation,
                encouragement=None,
                order_index=idx
            ) for idx, wq in enumerate(wrong_questions)
        ]
        
        return ReviewQuestionsResponse(questions=questions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成复习题目失败: {str(e)}"
        )
