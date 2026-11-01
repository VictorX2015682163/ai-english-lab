"""
国际学校模式相关路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import re
from typing import Optional
from app.database import get_db
from app.models import User, TestSession, TestQuestion, TestAnswer, LearningModule, UserLearningModule, ChatMessage, PathConfig
from app.schemas import (
    TestQuestionResponse, SubmitTestRequest, TestResultResponse,
    LearningModuleResponse, ChatRequest, ChatResponse
)
from app.routers.profile import get_current_user
from app.utils import get_current_user_id
from app.services.ai import ai_service
from app.services.prompts import PromptTemplates
from app.services.request_detector import RequestDetector
from datetime import datetime, timezone
import random
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/international", tags=["国际学校模式"])

# 测试结果等级映射（根据正确率）
LEVEL_MAPPING = {
    (0, 40): {
        "level": "A1 Beginner",
        "description": "你处于英语学习的初级阶段，需要打好基础。",
        "suggestions": [
            "适合进阶：基础词汇积累",
            "语法基础需要重点提升",
            "建议加强日常对话练习",
            "可以开始学习基础语法结构"
        ]
    },
    (41, 60): {
        "level": "A2 Elementary",
        "description": "你具备基础的英语交流能力，可以处理简单的日常话题。",
        "suggestions": [
            "适合进阶：日常对话练习",
            "词汇量需要继续扩充",
            "建议加强听力训练",
            "可以开始学习更复杂的语法"
        ]
    },
    (61, 75): {
        "level": "B1 Intermediate",
        "description": "你具备基础的英语交流能力，可以处理日常话题和简单的学术内容。",
        "suggestions": [
            "适合进阶：学术阅读",
            "写作结构需要重点提升",
            "建议加强口语流利度训练",
            "可以开始学习更复杂的语法结构"
        ]
    },
    (76, 85): {
        "level": "B2 Upper-Intermediate",
        "description": "你的英语水平较好，可以处理大部分学术和职业场景。",
        "suggestions": [
            "适合进阶：高级阅读",
            "学术写作需要重点提升",
            "建议加强演讲表达能力",
            "可以开始学习高级语法和表达"
        ]
    },
    (86, 100): {
        "level": "C1 Advanced",
        "description": "你的英语水平很高，可以流利地处理复杂的学术和职业场景。",
        "suggestions": [
            "适合进阶：专业领域英语",
            "可以挑战更高级的写作任务",
            "建议加强专业演讲能力",
            "可以开始学习专业术语和表达"
        ]
    }
}


def calculate_level(correct_rate: float) -> dict:
    """根据正确率计算等级"""
    for (min_rate, max_rate), result in LEVEL_MAPPING.items():
        if min_rate <= correct_rate <= max_rate:
            return result
    return LEVEL_MAPPING[(0, 40)]  # 默认返回最低等级


def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """获取当前用户（可选，支持游览模式）"""
    if not authorization or not authorization.strip():
        return None  # 游览模式，返回None
    
    # 移除Bearer前缀
    token = authorization.strip()
    if token.startswith("Bearer "):
        token = token[7:].strip()
    
    if not token:
        return None
    
    # 尝试获取用户ID
    user_id = get_current_user_id(token)
    if user_id is None:
        return None  # token无效，游览模式
    
    # 获取用户对象
    user = db.query(User).filter(User.id == user_id).first()
    return user


@router.get("/test/questions")
def get_test_questions(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取分级测试题目（支持游览模式）"""
    try:
        # 从数据库获取测试题目
        questions = db.query(TestQuestion).order_by(TestQuestion.order_index).limit(15).all()
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="暂无测试题目，请联系管理员"
            )
        
        # 返回数据库中的题目
        return [
            TestQuestionResponse(
                id=q.id,
                category=q.category,
                question=q.question,
                options=q.options,
                order_index=q.order_index
            ) for q in questions
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取测试题目失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取测试题目失败: {str(e)}"
        )


@router.post("/test/submit", response_model=TestResultResponse)
def submit_test(
    request: SubmitTestRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """提交测试答案（支持游览模式）"""
    try:
        is_guest_mode = current_user is None
        
        # 验证答案不为空
        if not request.answers or len(request.answers) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="答案不能为空"
            )
        
        # 批量获取所有题目（避免 N+1 查询）
        question_ids = [int(qid) for qid in request.answers.keys()]
        db_questions = db.query(TestQuestion).filter(
            TestQuestion.id.in_(question_ids)
        ).all()
        questions_map = {q.id: q for q in db_questions}
        
        # 检查是否有题目不存在
        missing_questions = set(question_ids) - set(questions_map.keys())
        if missing_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"题目不存在: {missing_questions}"
            )
        
        # 计算正确数
        correct = 0
        
        # 计算正确数（不保存到数据库，仅用于计算等级）
        for question_id, user_answer in request.answers.items():
            qid = int(question_id)
            question = questions_map.get(qid)
            
            if not question:
                continue
            
            # 验证单个答案不为空
            if not user_answer or not str(user_answer).strip():
                continue  # 跳过空答案，不计入正确数
            
            # 从数据库获取正确答案
            correct_answer = question.correct_answer
            
            # 判断答案是否正确（不区分大小写，去除空格）
            is_correct = (
                str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            )
            
            # 登录模式：保存答案记录到数据库
            if not is_guest_mode:
                # 创建测试会话（如果还没有）
                if 'session' not in locals():
                    session = TestSession(
                        user_id=current_user.id,
                        status="in_progress"
                    )
                    db.add(session)
                    db.flush()
                
                # 保存答案记录
                test_answer = TestAnswer(
                    session_id=session.id,
                    question_id=qid,
                    user_answer=user_answer,
                    is_correct=is_correct
                )
                db.add(test_answer)
            
            if is_correct:
                correct += 1
        
        # 计算正确率（使用实际提交的答案数，不包括跳过的题目）
        actual_total = len([a for a in request.answers.values() if a and str(a).strip()])
        correct_rate = (correct / actual_total * 100) if actual_total > 0 else 0
        
        # 获取等级信息
        level_info = calculate_level(correct_rate)
        
        # 登录模式：更新会话并保存到数据库
        if not is_guest_mode:
            session.status = "completed"
            session.level = level_info["level"]
            session.description = level_info["description"]
            session.suggestions = level_info["suggestions"]
            session.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"测试完成，用户ID: {current_user.id}, 水平: {level_info['level']}")
        else:
            logger.info(f"测试完成（游览模式），水平: {level_info['level']}")
        
        return TestResultResponse(
            level=level_info["level"],
            description=level_info["description"],
            suggestions=level_info["suggestions"]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交测试失败: {str(e)}"
        )


@router.get("/path/modules", response_model=list[LearningModuleResponse])
def get_learning_modules(
    target_level: str = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """获取学习路径模块列表（支持游览模式，支持AI推荐）"""
    try:
        # 如果未提供target_level，尝试从用户测试结果获取
        if not target_level and current_user:
            latest_test = db.query(TestSession).filter(
                TestSession.user_id == current_user.id,
                TestSession.status == "completed"
            ).order_by(TestSession.completed_at.desc()).first()
            
            if latest_test and latest_test.level:
                # 提取等级（如 "B1 Intermediate" -> "B1"）
                level_parts = latest_test.level.split()
                if level_parts:
                    target_level = level_parts[0]  # 使用 "B1" 作为目标等级
        
        # 从数据库获取模块
        query = db.query(LearningModule).filter(LearningModule.is_active == True)
        
        if target_level:
            # 匹配目标等级（支持部分匹配，如 "B1" 匹配 "B1 Intermediate"）
            query = query.filter(
                or_(
                    LearningModule.target_level == target_level,
                    LearningModule.target_level.like(f"{target_level}%")
                )
            )
        
        modules = query.order_by(LearningModule.order_index).all()
        
        # 如果没有匹配的模块，返回所有模块
        if not modules:
            modules = db.query(LearningModule).filter(
                LearningModule.is_active == True
            ).order_by(LearningModule.order_index).all()
        
        if not modules:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="暂无学习模块，请联系管理员"
            )
        
        # 获取用户已加入的模块（仅登录用户）
        user_module_ids = set()
        if current_user:
            user_modules = db.query(UserLearningModule).filter(
                UserLearningModule.user_id == current_user.id,
                UserLearningModule.is_added == True
            ).all()
            user_module_ids = {um.module_id for um in user_modules}
        
        # 如果用户有测试结果，使用AI推荐排序
        if current_user and target_level:
            latest_test = db.query(TestSession).filter(
                TestSession.user_id == current_user.id,
                TestSession.status == "completed"
            ).order_by(TestSession.completed_at.desc()).first()
            
            if latest_test:
                # 使用AI推荐模块（根据测试结果和建议）
                recommended_modules = _get_ai_recommended_modules(
                    modules, latest_test, user_module_ids
                )
                if recommended_modules:
                    return recommended_modules
        
        # 默认返回：系统推荐的在前，已加入的标记
        return [
            LearningModuleResponse(
                id=m.id,
                name=m.name,
                description=m.description,
                tag=m.tag if m.id not in user_module_ids else "已加入",
                tag_type="recommended" if m.tag_type == "recommended" and m.id not in user_module_ids else m.tag_type,
                added=m.id in user_module_ids
            ) for m in modules
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取学习模块失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习模块失败: {str(e)}"
        )


def _get_ai_recommended_modules(
    modules: list,
    test_session: TestSession,
    user_module_ids: set
) -> Optional[list]:
    """使用AI推荐学习模块"""
    try:
        # 构建推荐提示词
        suggestions_text = ", ".join(test_session.suggestions) if test_session.suggestions else "无"
        
        recommendation_prompt = f"""根据学生的分级测试结果，推荐最适合的学习模块。

测试结果：
- 水平：{test_session.level}
- 描述：{test_session.description}
- 建议：{suggestions_text}

可选模块：
{chr(10).join([f"{i+1}. {m.name} - {m.description}" for i, m in enumerate(modules)])}

请根据测试结果，推荐3-4个最适合的学习模块（返回模块编号，用逗号分隔）。
如果学生已经加入了某些模块，优先推荐其他模块。"""
        
        # 调用AI获取推荐
        ai_response = ai_service.chat(
            user_message="请推荐最适合的学习模块",
            system_prompt=recommendation_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        if not ai_response:
            return None
        
        # 解析AI返回的模块编号
        import re
        numbers = re.findall(r'\d+', ai_response)
        recommended_indices = [int(n) - 1 for n in numbers if 1 <= int(n) <= len(modules)]
        
        if recommended_indices:
            # 重新排序：推荐的在前
            recommended = [modules[i] for i in recommended_indices if 0 <= i < len(modules)]
            others = [m for i, m in enumerate(modules) if i not in recommended_indices]
            
            all_modules = recommended + others
            
            return [
                LearningModuleResponse(
                    id=m.id,
                    name=m.name,
                    description=m.description,
                    tag="AI推荐" if m in recommended else (m.tag if m.id not in user_module_ids else "已加入"),
                    tag_type="recommended" if m in recommended else m.tag_type,
                    added=m.id in user_module_ids
                ) for m in all_modules
            ]
        
        return None
    except Exception as e:
        logger.warning(f"AI推荐模块失败: {str(e)}")
        return None


@router.post("/path/modules/{module_id}/toggle")
def toggle_learning_module(
    module_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换学习模块状态"""
    try:
        # 检查模块是否存在于数据库
        module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
        
        # 如果数据库中没有该模块，可能是示例模块（id 1-4）
        # 为了支持示例模块，我们在数据库中创建它
        if not module and module_id <= 4:
            sample_modules = [
                {
                    "id": 1,
                    "name": "Academic Reading",
                    "description": "提升学术阅读能力，掌握长篇文章的理解和分析技巧",
                    "tag": "系统推荐",
                    "tag_type": "recommended"
                },
                {
                    "id": 2,
                    "name": "Essay Writing",
                    "description": "学习写作结构与逻辑，提升学术写作水平",
                    "tag": "系统推荐",
                    "tag_type": "recommended"
                },
                {
                    "id": 3,
                    "name": "Listening & Note-taking",
                    "description": "训练听力理解能力，掌握快速记笔记的方法",
                    "tag": "可选模块",
                    "tag_type": "optional"
                },
                {
                    "id": 4,
                    "name": "Speaking for Presentation",
                    "description": "提升演讲表达能力，增强口语流利度和自信",
                    "tag": "可选模块",
                    "tag_type": "optional"
                }
            ]
            
            # 创建示例模块到数据库
            for m in sample_modules:
                existing = db.query(LearningModule).filter(LearningModule.id == m["id"]).first()
                if not existing:
                    new_module = LearningModule(
                        id=m["id"],
                        name=m["name"],
                        description=m["description"],
                        tag=m["tag"],
                        tag_type=m["tag_type"],
                        order_index=m["id"] - 1,
                        is_active=True
                    )
                    db.add(new_module)
            
            db.commit()
            module = db.query(LearningModule).filter(LearningModule.id == module_id).first()
        
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习模块不存在"
            )
        
        # 查找用户模块关联
        user_module = db.query(UserLearningModule).filter(
            UserLearningModule.user_id == current_user.id,
            UserLearningModule.module_id == module_id
        ).first()
        
        if user_module:
            # 切换状态
            user_module.is_added = not user_module.is_added
            user_module.updated_at = datetime.now(timezone.utc)
        else:
            # 创建新关联
            user_module = UserLearningModule(
                user_id=current_user.id,
                module_id=module_id,
                is_added=True
            )
            db.add(user_module)
        
        db.commit()
        
        return {"message": "已加入计划" if user_module.is_added else "已移除"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换模块状态失败: {str(e)}"
        )


@router.get("/path/config")
def get_path_config(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习路径页面配置数据"""
    try:
        # 从数据库读取配置
        targets_config = db.query(PathConfig).filter(
            PathConfig.config_key == "targets",
            PathConfig.is_active == True
        ).first()
        
        quick_prompts_config = db.query(PathConfig).filter(
            PathConfig.config_key == "quick_prompts",
            PathConfig.is_active == True
        ).first()
        
        welcome_message_config = db.query(PathConfig).filter(
            PathConfig.config_key == "welcome_message",
            PathConfig.is_active == True
        ).first()
        
        # 如果数据库中没有配置，使用默认值
        targets = targets_config.config_value if targets_config else [
            "一个学期内达到 B2",
            "半年内达到 B2",
            "一年内达到 C1"
        ]
        
        quick_prompts = quick_prompts_config.config_value if quick_prompts_config else [
            "根据我当前水平安排一节阅读课",
            "帮我出 5 道关于旅行的口语题",
            "帮我批改这段作文，并解释修改"
        ]
        
        welcome_message = welcome_message_config.config_value if welcome_message_config else "你好！我是你的 AI 学习教练。根据你的分级测试结果，我为你推荐了几个重点学习模块。有什么问题随时问我！"
        
        return {
            "targets": targets,
            "quick_prompts": quick_prompts,
            "welcome_message": welcome_message
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取配置失败: {str(e)}"
        )


@router.post("/coach/chat", response_model=ChatResponse)
def chat_with_coach(
    request: ChatRequest,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """AI学习教练对话（支持游览模式）"""
    try:
        # 验证消息内容
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="消息内容不能为空"
            )
        
        is_guest_mode = current_user is None
        
        # 保存用户消息（仅登录用户保存到数据库）
        user_message = None
        conversation_history = []
        
        if not is_guest_mode:
            # 登录用户：保存到数据库
            user_message = ChatMessage(
                user_id=current_user.id,
                message_type="user",
                message=request.message.strip()
            )
            db.add(user_message)
            db.flush()
            
            # 1. 获取用户信息
            # 获取用户测试结果（水平）
            latest_test = db.query(TestSession).filter(
                TestSession.user_id == current_user.id,
                TestSession.status == "completed"
            ).order_by(TestSession.completed_at.desc()).first()
            
            user_level = "未测试"
            level_description = ""
            if latest_test:
                user_level = latest_test.level or "未测试"
                level_description = latest_test.description or ""
            
            # 获取用户已加入的学习模块（优化：使用join一次性获取，避免N+1查询）
            user_modules = db.query(LearningModule.name).join(
                UserLearningModule, LearningModule.id == UserLearningModule.module_id
            ).filter(
                UserLearningModule.user_id == current_user.id,
                UserLearningModule.is_added == True,
                LearningModule.is_active == True
            ).all()
            
            # 提取模块名称
            module_names = [name[0] for name in user_modules] if user_modules else []
            learning_modules = ", ".join(module_names) if module_names else "无"
            
            # 获取学习目标（从PathConfig，暂时使用默认值）
            learning_target = "未设置"
            targets_config = db.query(PathConfig).filter(
                PathConfig.config_key == "targets",
                PathConfig.is_active == True
            ).first()
            if targets_config and isinstance(targets_config.config_value, list) and len(targets_config.config_value) > 0:
                learning_target = targets_config.config_value[0]  # 使用第一个目标作为默认
            
            # 2. 获取对话历史（最近10条，用于上下文）
            # 排除当前消息：使用ID判断，因为flush后ID已生成
            recent_messages = db.query(ChatMessage).filter(
                ChatMessage.user_id == current_user.id,
                ChatMessage.id != user_message.id  # 排除当前消息
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            
            # 反转顺序，从旧到新
            recent_messages.reverse()
            
            # 构建对话历史
            for msg in recent_messages:
                role = "user" if msg.message_type == "user" else "assistant"
                conversation_history.append({
                    "role": role,
                    "content": msg.message
                })
        else:
            # 游览模式：使用默认信息
            user_level = "未测试"
            level_description = ""
            learning_modules = "无"
            learning_target = "未设置"
            logger.info("游览模式：使用默认用户信息")
        
        # 3. 检测请求类型并构建相应的系统提示词
        request_type, request_params = RequestDetector.detect_request_type(request.message)
        user_id_str = str(current_user.id) if current_user else "游览模式"
        logger.info(f"检测到请求类型: {request_type}, 用户ID: {user_id_str}, 水平: {user_level}")
        
        # 根据请求类型选择不同的提示词
        if request_type == "essay_correction":
            # 作文批改
            essay_content = RequestDetector.extract_essay_content(request.message)
            if essay_content:
                # 如果提取到了作文内容，使用专门的批改提示词
                system_prompt = PromptTemplates.get_essay_correction_prompt(user_level=user_level)
                # 将作文内容作为用户消息
                user_message_for_ai = f"请批改以下作文：\n\n{essay_content}"
            else:
                # 如果没有提取到，提示用户发送作文
                system_prompt = PromptTemplates.get_coach_prompt(
                    user_level=user_level,
                    level_description=level_description,
                    learning_modules=learning_modules,
                    learning_target=learning_target
                )
                user_message_for_ai = request.message
        elif request_type == "question_generation":
            # 题目生成
            topic = request_params.get("topic", "通用") if request_params else "通用"
            question_type = request_params.get("question_type", "选择题") if request_params else "选择题"
            question_count = request_params.get("count", 5) if request_params else 5
            system_prompt = PromptTemplates.get_question_generation_prompt(
                user_level=user_level,
                topic=topic,
                question_type=question_type,
                question_count=question_count
            )
            user_message_for_ai = request.message
        else:
            # 一般对话：增强提示词，说明AI可以做什么
            enhanced_prompt = PromptTemplates.COACH_BASE_PROMPT + """

你还可以帮助学生完成以下任务：
1. **作文批改**：当学生发送作文内容时，进行详细的批改，包括语法、词汇、结构、内容等方面的分析和建议
2. **题目生成**：当学生要求生成题目时（如"帮我出5道关于旅行的口语题"），根据学生的水平和要求生成相应的练习题
3. **学习建议**：根据学生的水平和学习模块提供个性化的学习建议

请根据学生的具体需求，灵活运用这些功能。"""
            system_prompt = enhanced_prompt.format(
                user_level=user_level,
                level_description=level_description,
                learning_modules=learning_modules,
                learning_target=learning_target
            )
            user_message_for_ai = request.message
        
        # 4. 调用AI服务
        ai_reply = ai_service.chat(
            user_message=user_message_for_ai,
            system_prompt=system_prompt,
            conversation_history=conversation_history if conversation_history else None,
            temperature=0.7,
            max_tokens=3000 if request_type != "general" else 2000  # 作文批改和题目生成需要更多token
        )
        
        # 5. 如果AI调用失败，使用fallback回复
        if not ai_reply:
            logger.warning("AI服务调用失败，使用fallback回复")
            user_msg_lower = request.message.lower()
            
            if "阅读" in user_msg_lower or "reading" in user_msg_lower:
                ai_reply = "好的，我来为你安排一节阅读课。根据你当前的水平，我建议从学术阅读开始，重点训练长篇文章的理解和分析能力。"
            elif "口语" in user_msg_lower or "speaking" in user_msg_lower:
                ai_reply = "好的，我来为你准备口语练习题目。我会根据你的水平设计适合的口语话题，帮助你提升表达流利度。"
            elif "写作" in user_msg_lower or "作文" in user_msg_lower or "writing" in user_msg_lower:
                ai_reply = "好的，我来帮你批改作文。请把你的作文内容发给我，我会详细分析并给出修改建议。"
            elif "听力" in user_msg_lower or "listening" in user_msg_lower:
                ai_reply = "好的，我来为你准备听力练习。我会选择适合你水平的听力材料，帮助你提升听力理解能力。"
            else:
                ai_reply = "好的，我理解了你的需求。让我为你准备相关内容。如果你需要具体的帮助，可以告诉我你想练习哪个方面（阅读、写作、口语、听力）。"
        
        # 6. 保存AI回复（仅登录用户保存到数据库）
        if not is_guest_mode:
            ai_message = ChatMessage(
                user_id=current_user.id,
                message_type="ai",
                message=ai_reply
            )
            db.add(ai_message)
            db.commit()
            logger.info(f"AI对话完成，用户ID: {current_user.id}")
        else:
            logger.info("AI对话完成（游览模式，未保存到数据库）")
        
        return ChatResponse(reply=ai_reply)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"AI对话失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI对话失败: {str(e)}"
        )
