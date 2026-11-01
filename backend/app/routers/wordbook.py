"""
生词本相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import WordBook
from app.schemas import WordResponse, AddWordRequest, MessageResponse
from app.routers.profile import get_current_user

router = APIRouter(prefix="/wordbook", tags=["生词本"])


@router.get("/list")
def get_wordbook_list(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取生词本列表（带分页信息）"""
    try:
        # 获取总数
        total = db.query(func.count(WordBook.id)).filter(
            WordBook.user_id == current_user.id
        ).scalar() or 0
        
        # 获取分页数据
        words = db.query(WordBook).filter(
            WordBook.user_id == current_user.id
        ).order_by(WordBook.added_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        items = [
            WordResponse(
                id=w.id,
                word=w.word,
                meaning=w.meaning,
                example=w.example,
                added_at=w.added_at
            ) for w in words
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
            detail=f"获取生词本失败: {str(e)}"
        )


@router.post("/add", response_model=MessageResponse)
def add_word(
    request: AddWordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加生词"""
    try:
        # 检查是否已存在
        existing = db.query(WordBook).filter(
            WordBook.user_id == current_user.id,
            WordBook.word == request.word
        ).first()
        
        if existing:
            return MessageResponse(message="该单词已在生词本中")
        
        word = WordBook(
            user_id=current_user.id,
            word=request.word,
            meaning=request.meaning,
            example=request.example
        )
        db.add(word)
        db.commit()
        
        return MessageResponse(message="已添加到生词本")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加生词失败: {str(e)}"
        )


@router.delete("/{word_id}", response_model=MessageResponse)
def delete_word(
    word_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除生词"""
    try:
        word = db.query(WordBook).filter(
            WordBook.id == word_id,
            WordBook.user_id == current_user.id
        ).first()
        
        if not word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="生词不存在"
            )
        
        db.delete(word)
        db.commit()
        
        return MessageResponse(message="已删除生词")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除生词失败: {str(e)}"
        )


@router.get("/review", response_model=list[WordResponse])
def get_review_words(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取生词复习列表"""
    try:
        # 获取需要复习的生词（复习次数少的优先）
        words = db.query(WordBook).filter(
            WordBook.user_id == current_user.id
        ).order_by(WordBook.review_count.asc(), WordBook.added_at.desc()).limit(20).all()
        
        return [
            WordResponse(
                id=w.id,
                word=w.word,
                meaning=w.meaning,
                example=w.example,
                added_at=w.added_at
            ) for w in words
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取复习列表失败: {str(e)}"
        )
