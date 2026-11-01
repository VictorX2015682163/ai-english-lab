"""
公立学校模式相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import PracticeSession, PracticeQuestion, PracticeAnswer, DailyPractice, Grade, TextbookVersion, Unit, PracticeQuestionBank
from app.schemas import (
    StartPracticeRequest, PracticeSessionResponse, QuestionResponse,
    SubmitAnswerRequest, AnswerResultResponse, EndPracticeRequest,
    PracticeSummaryResponse
)
from app.routers.profile import get_current_user
from datetime import datetime, timezone
import random

router = APIRouter(prefix="/public", tags=["公立学校模式"])


def generate_questions(grade: str, version: str, unit: str, db: Session) -> list[dict]:
    """根据年级、版本、单元从数据库生成练习题"""
    # 获取年级、版本、单元对象
    grade_obj = db.query(Grade).filter(Grade.name == grade, Grade.is_active == True).first()
    version_obj = db.query(TextbookVersion).filter(TextbookVersion.name == version, TextbookVersion.is_active == True).first()
    unit_obj = None
    if grade_obj and version_obj:
        unit_obj = db.query(Unit).filter(
            Unit.grade_id == grade_obj.id,
            Unit.version_id == version_obj.id,
            Unit.name == unit,
            Unit.is_active == True
        ).first()
    
    # 查询题目：优先匹配单元，其次匹配版本，最后匹配年级，最后使用通用题目
    query = db.query(PracticeQuestionBank).filter(PracticeQuestionBank.is_active == True)
    
    # 构建查询条件：尝试匹配最具体的题目
    questions = []
    
    # 1. 优先：匹配单元
    if unit_obj:
        unit_questions = query.filter(PracticeQuestionBank.unit_id == unit_obj.id).all()
        if unit_questions:
            questions = unit_questions
        else:
            # 2. 其次：匹配版本
            if version_obj:
                version_questions = query.filter(
                    PracticeQuestionBank.version_id == version_obj.id,
                    PracticeQuestionBank.unit_id.is_(None)
                ).all()
                if version_questions:
                    questions = version_questions
                else:
                    # 3. 再次：匹配年级
                    if grade_obj:
                        grade_questions = query.filter(
                            PracticeQuestionBank.grade_id == grade_obj.id,
                            PracticeQuestionBank.version_id.is_(None),
                            PracticeQuestionBank.unit_id.is_(None)
                        ).all()
                        if grade_questions:
                            questions = grade_questions
    
    # 4. 最后：使用通用题目（所有字段都为空）
    if not questions:
        questions = query.filter(
            PracticeQuestionBank.grade_id.is_(None),
            PracticeQuestionBank.version_id.is_(None),
            PracticeQuestionBank.unit_id.is_(None)
        ).all()
    
    # 如果还是没有题目，返回空列表
    if not questions:
        return []
    
    # 随机选择5-10道题
    num_questions = random.randint(5, min(10, len(questions)))
    selected = random.sample(questions, num_questions)
    
    # 转换为字典格式
    return [
        {
            "question_type": q.question_type,
            "question": q.question,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "encouragement": q.encouragement
        }
        for q in selected
    ]


@router.get("/grades")
def get_grades(db: Session = Depends(get_db)):
    """获取年级列表"""
    grades = db.query(Grade).filter(Grade.is_active == True).order_by(Grade.order_index).all()
    return {"grades": [grade.name for grade in grades]}


@router.get("/versions")
def get_versions(db: Session = Depends(get_db)):
    """获取教材版本列表"""
    versions = db.query(TextbookVersion).filter(TextbookVersion.is_active == True).order_by(TextbookVersion.order_index).all()
    return {"versions": [version.name for version in versions]}


@router.get("/units")
def get_units(grade: str = None, version: str = None, db: Session = Depends(get_db)):
    """获取单元列表"""
    query = db.query(Unit).filter(Unit.is_active == True)
    
    if grade:
        grade_obj = db.query(Grade).filter(Grade.name == grade, Grade.is_active == True).first()
        if grade_obj:
            query = query.filter(Unit.grade_id == grade_obj.id)
    
    if version:
        version_obj = db.query(TextbookVersion).filter(TextbookVersion.name == version, TextbookVersion.is_active == True).first()
        if version_obj:
            query = query.filter(Unit.version_id == version_obj.id)
    
    units = query.order_by(Unit.order_index).all()
    return {"units": [unit.name for unit in units]}


@router.post("/practice/start", response_model=PracticeSessionResponse)
def start_practice(
    request: StartPracticeRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """开始练习"""
    try:
        # 创建练习会话
        session = PracticeSession(
            user_id=current_user.id,
            grade=request.grade,
            version=request.version,
            unit=request.unit,
            status="in_progress"
        )
        db.add(session)
        db.flush()
        
        # 生成题目
        questions_data = generate_questions(request.grade, request.version, request.unit, db)
        
        # 检查是否有题目
        if not questions_data or len(questions_data) == 0:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到匹配的练习题，请检查年级、版本和单元设置，或联系管理员添加题目"
            )
        
        # 创建题目记录
        questions = []
        for idx, q_data in enumerate(questions_data):
            question = PracticeQuestion(
                session_id=session.id,
                question_type=q_data["question_type"],
                question=q_data["question"],
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                encouragement=q_data.get("encouragement"),
                order_index=idx
            )
            db.add(question)
            questions.append(question)
        
        session.total_questions = len(questions)
        db.commit()
        db.refresh(session)
        
        # 返回响应
        question_responses = [
            QuestionResponse(
                id=q.id,
                question_type=q.question_type,
                question=q.question,
                options=q.options,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                encouragement=q.encouragement,
                order_index=q.order_index
            ) for q in questions
        ]
        
        return PracticeSessionResponse(
            session_id=session.id,
            questions=question_responses
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"开始练习失败: {str(e)}"
        )


@router.get("/practice/questions")
def get_practice_questions(
    session_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取练习题列表"""
    try:
        session = db.query(PracticeSession).filter(
            PracticeSession.id == session_id,
            PracticeSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="练习会话不存在"
            )
        
        questions = db.query(PracticeQuestion).filter(
            PracticeQuestion.session_id == session_id
        ).order_by(PracticeQuestion.order_index).all()
        
        return [
            QuestionResponse(
                id=q.id,
                question_type=q.question_type,
                question=q.question,
                options=q.options,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                encouragement=q.encouragement,
                order_index=q.order_index
            ) for q in questions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取题目失败: {str(e)}"
        )


@router.post("/practice/submit", response_model=AnswerResultResponse)
def submit_answer(
    request: SubmitAnswerRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交答案"""
    try:
        # 验证会话
        session = db.query(PracticeSession).filter(
            PracticeSession.id == request.session_id,
            PracticeSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="练习会话不存在"
            )
        
        # 检查会话是否已结束
        if session.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="练习会话已结束"
            )
        
        # 获取题目
        question = db.query(PracticeQuestion).filter(
            PracticeQuestion.id == request.question_id,
            PracticeQuestion.session_id == request.session_id
        ).first()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="题目不存在"
            )
        
        # 检查是否已答过该题（防止重复提交）
        existing_answer = db.query(PracticeAnswer).filter(
            PracticeAnswer.session_id == request.session_id,
            PracticeAnswer.question_id == request.question_id
        ).first()
        
        if existing_answer:
            # 已答过，直接返回之前的结果
            return AnswerResultResponse(
                is_correct=existing_answer.is_correct,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                encouragement=question.encouragement if existing_answer.is_correct else None
            )
        
        # 验证答案不为空
        if not request.answer or not request.answer.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="答案不能为空"
            )
        
        # 判断答案是否正确（不区分大小写，去除空格）
        is_correct = (
            request.answer.strip().lower() == question.correct_answer.strip().lower()
        )
        
        # 保存答案记录
        answer = PracticeAnswer(
            session_id=request.session_id,
            question_id=request.question_id,
            user_answer=request.answer,
            is_correct=is_correct
        )
        db.add(answer)
        
        # 更新会话统计
        if is_correct:
            session.correct_count += 1
        else:
            session.wrong_count += 1
        
        # 记录每日练习（使用 UTC 时区）
        today = datetime.now(timezone.utc).date()
        daily_practice = db.query(DailyPractice).filter(
            DailyPractice.user_id == current_user.id,
            func.date(DailyPractice.practice_date) == today,
            DailyPractice.practice_type == "public"
        ).first()
        
        if not daily_practice:
            daily_practice = DailyPractice(
                user_id=current_user.id,
                practice_date=datetime.now(timezone.utc),
                practice_type="public",
                question_count=1,
                correct_count=1 if is_correct else 0
            )
            db.add(daily_practice)
        else:
            daily_practice.question_count += 1
            if is_correct:
                daily_practice.correct_count += 1
        
        db.commit()
        
        return AnswerResultResponse(
            is_correct=is_correct,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            encouragement=question.encouragement if is_correct else None
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交答案失败: {str(e)}"
        )


@router.post("/practice/end", response_model=PracticeSummaryResponse)
def end_practice(
    request: EndPracticeRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """结束练习会话"""
    try:
        session = db.query(PracticeSession).filter(
            PracticeSession.id == request.session_id,
            PracticeSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="练习会话不存在"
            )
        
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        db.commit()
        
        return PracticeSummaryResponse(
            total=session.total_questions,
            correct=session.correct_count,
            wrong=session.wrong_count
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"结束练习失败: {str(e)}"
        )
