#!/usr/bin/env python3
"""
演示数据生成脚本

运行方式：
    cd backend
    python3 seed_demo_data.py

可选参数：
    --clear     仅清空所有数据，不插入新数据
    --no-clear  不清空旧数据，直接追加（可能导致重复）

默认行为：先清空旧数据，再插入演示数据

演示账号：
    用户名: demo
    手机号: 10000000000
    密码: 123456
"""

import sys
import os
import argparse
from datetime import datetime, timedelta, timezone

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import (
    User, SmsCode, PracticeSession, PracticeQuestion, PracticeAnswer,
    WrongQuestion, WordBook, TestSession, TestQuestion, TestAnswer,
    LearningModule, UserLearningModule, ChatMessage, DailyPractice,
    Grade, TextbookVersion, Unit, PracticeQuestionBank, PathConfig
)
from app.utils import get_password_hash

# 统计信息
stats = {
    "users": 0,
    "grades": 0,
    "textbook_versions": 0,
    "units": 0,
    "practice_question_bank": 0,
    "test_questions": 0,
    "learning_modules": 0,
    "path_configs": 0,
    "practice_sessions": 0,
    "practice_questions": 0,
    "practice_answers": 0,
    "test_sessions": 0,
    "test_answers": 0,
    "wrong_questions": 0,
    "word_book": 0,
    "user_learning_modules": 0,
    "chat_messages": 0,
    "daily_practice": 0,
    "sms_codes": 0
}


def clear_all_data(db: Session):
    """清空所有数据（按依赖顺序删除）"""
    print("\n🗑️  正在清空所有数据...")
    
    # 按外键依赖顺序删除
    tables_to_clear = [
        ("chat_messages", ChatMessage),
        ("user_learning_modules", UserLearningModule),
        ("daily_practice", DailyPractice),
        ("test_answers", TestAnswer),
        ("practice_answers", PracticeAnswer),
        ("wrong_questions", WrongQuestion),
        ("word_book", WordBook),
        ("practice_questions", PracticeQuestion),
        ("practice_sessions", PracticeSession),
        ("test_sessions", TestSession),
        ("practice_question_bank", PracticeQuestionBank),
        ("units", Unit),
        ("textbook_versions", TextbookVersion),
        ("grades", Grade),
        ("test_questions", TestQuestion),
        ("learning_modules", LearningModule),
        ("path_config", PathConfig),
        ("sms_codes", SmsCode),
        ("users", User),
    ]
    
    for table_name, model in tables_to_clear:
        count = db.query(model).count()
        db.query(model).delete()
        print(f"   - {table_name}: 删除 {count} 条记录")
    
    db.commit()
    print("✅ 数据清空完成\n")


def seed_users(db: Session):
    """创建演示用户"""
    print("👤 创建演示用户...")
    
    users_data = [
        {
            "username": "demo",
            "phone": "10000000000",
            "email": "demo@example.invalid",
            "password": "123456",
            "nickname": "演示用户",
            "bio": "这是一个演示账号，欢迎体验AI英语学习助手！",
            "gender": "other",
        },
        {
            "username": "student1",
            "phone": "10000000000",
            "email": "demo@example.invalid",
            "password": "123456",
            "nickname": "小明",
            "bio": "我是一名正在学习英语的小学生",
            "gender": "male",
        },
        {
            "username": "student2",
            "phone": "10000000000",
            "email": "demo@example.invalid",
            "password": "123456",
            "nickname": "小红",
            "bio": "喜欢英语，希望提升口语能力",
            "gender": "female",
        },
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            phone=user_data["phone"],
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            nickname=user_data.get("nickname"),
            bio=user_data.get("bio"),
            gender=user_data.get("gender"),
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            last_login_at=datetime.now(timezone.utc) - timedelta(hours=2)
        )
        db.add(user)
        stats["users"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['users']} 个用户")


def seed_grades(db: Session):
    """创建年级数据"""
    print("📚 创建年级数据...")
    
    grades_data = ['三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三']
    for idx, name in enumerate(grades_data):
        grade = Grade(
            name=name,
            order_index=idx,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(grade)
        stats["grades"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['grades']} 个年级")


def seed_textbook_versions(db: Session):
    """创建教材版本数据"""
    print("📖 创建教材版本数据...")
    
    versions_data = ['人教版', '北师大版', '外研版', '苏教版']
    for idx, name in enumerate(versions_data):
        version = TextbookVersion(
            name=name,
            order_index=idx,
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(version)
        stats["textbook_versions"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['textbook_versions']} 个教材版本")


def seed_units(db: Session):
    """创建单元数据"""
    print("📝 创建单元数据...")
    
    grades = db.query(Grade).all()
    versions = db.query(TextbookVersion).all()
    unit_names = ['Unit 1', 'Unit 2', 'Unit 3', 'Unit 4', 'Unit 5', 'Unit 6']
    
    for grade in grades:
        for version in versions:
            for idx, unit_name in enumerate(unit_names):
                unit = Unit(
                    grade_id=grade.id,
                    version_id=version.id,
                    name=unit_name,
                    order_index=idx,
                    is_active=True,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(unit)
                stats["units"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['units']} 个单元")


def seed_practice_question_bank(db: Session):
    """创建练习题题库"""
    print("📋 创建练习题题库...")
    
    grades = db.query(Grade).all()
    versions = db.query(TextbookVersion).all()
    units = db.query(Unit).limit(10).all()  # 取前10个单元作为示例
    
    # 通用题目
    general_questions = [
        {
            "question_type": "choice",
            "question": "What is the past tense of 'go'?",
            "options": ["goed", "went", "gone", "going"],
            "correct_answer": "went",
            "explanation": "'go' 的过去式是 'went'，这是一个不规则动词。",
            "encouragement": "很好！你掌握了这个不规则动词的变化。",
            "difficulty": "easy"
        },
        {
            "question_type": "choice",
            "question": "I _____ to school every day.",
            "options": ["go", "goes", "went", "going"],
            "correct_answer": "go",
            "explanation": "一般现在时，主语是 'I'，所以用动词原形 'go'。",
            "encouragement": "正确！你理解了一般现在时的用法。",
            "difficulty": "easy"
        },
        {
            "question_type": "fill",
            "question": "Complete the sentence: She _____ (like) reading books.",
            "options": None,
            "correct_answer": "likes",
            "explanation": "第三人称单数主语 'She' 后面，动词要加 's'。",
            "encouragement": "完美！你掌握了第三人称单数的用法。",
            "difficulty": "easy"
        },
        {
            "question_type": "choice",
            "question": "Which word means 'happy'?",
            "options": ["sad", "angry", "glad", "tired"],
            "correct_answer": "glad",
            "explanation": "'glad' 意思是 '高兴的'，与 'happy' 同义。",
            "encouragement": "很棒！你的词汇量不错。",
            "difficulty": "easy"
        },
        {
            "question_type": "fill",
            "question": "Fill in the blank: There _____ (be) many students in the classroom.",
            "options": None,
            "correct_answer": "are",
            "explanation": "'many students' 是复数，所以用 'are'。",
            "encouragement": "正确！你理解了 there be 句型的用法。",
            "difficulty": "medium"
        },
    ]
    
    # 添加通用题目
    for q_data in general_questions:
        question = PracticeQuestionBank(
            grade_id=None,
            version_id=None,
            unit_id=None,
            question_type=q_data["question_type"],
            question=q_data["question"],
            options=q_data.get("options"),
            correct_answer=q_data["correct_answer"],
            explanation=q_data.get("explanation"),
            encouragement=q_data.get("encouragement"),
            difficulty=q_data.get("difficulty", "medium"),
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(question)
        stats["practice_question_bank"] += 1
    
    # 为特定年级、版本、单元添加题目
    specific_questions = [
        {
            "grade": "初一",
            "version": "人教版",
            "unit": "Unit 1",
            "question_type": "choice",
            "question": "Hello, I'm Lily. What's _____ name?",
            "options": ["I", "my", "you", "your"],
            "correct_answer": "your",
            "explanation": "'your' 是形容词性物主代词，修饰名词 'name'。",
            "encouragement": "很棒！你掌握了基本的人称代词用法。",
            "difficulty": "easy"
        },
        {
            "grade": "初一",
            "version": "人教版",
            "unit": "Unit 1",
            "question_type": "fill",
            "question": "My name is Tom. _____ (I) am from China.",
            "options": None,
            "correct_answer": "I",
            "explanation": "句子主语是 'I'。",
            "encouragement": "正确！你理解了主格代词的用法。",
            "difficulty": "easy"
        },
        {
            "grade": "初一",
            "version": "人教版",
            "unit": "Unit 2",
            "question_type": "choice",
            "question": "Is this _____ eraser?",
            "options": ["a", "an", "the", "x"],
            "correct_answer": "an",
            "explanation": "'eraser' 以元音音素开头，所以用 'an'。",
            "encouragement": "很好！你掌握了冠词的用法。",
            "difficulty": "easy"
        },
    ]
    
    for q_data in specific_questions:
        grade = db.query(Grade).filter(Grade.name == q_data["grade"]).first()
        version = db.query(TextbookVersion).filter(TextbookVersion.name == q_data["version"]).first()
        unit = None
        if grade and version:
            unit = db.query(Unit).filter(
                Unit.grade_id == grade.id,
                Unit.version_id == version.id,
                Unit.name == q_data["unit"]
            ).first()
        
        if grade and version and unit:
            question = PracticeQuestionBank(
                grade_id=grade.id,
                version_id=version.id,
                unit_id=unit.id,
                question_type=q_data["question_type"],
                question=q_data["question"],
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                encouragement=q_data.get("encouragement"),
                difficulty=q_data.get("difficulty", "medium"),
                is_active=True,
                created_at=datetime.now(timezone.utc)
            )
            db.add(question)
            stats["practice_question_bank"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['practice_question_bank']} 道练习题")


def seed_test_questions(db: Session):
    """创建测试题目"""
    print("🎯 创建测试题目...")
    
    test_questions_data = [
        {
            "category": "词汇",
            "question": "Choose the word that best completes the sentence: The meeting was very _____, and everyone was engaged.",
            "options": ["boring", "productive", "confusing", "difficult"],
            "correct_answer": "productive",
            "difficulty": "medium",
            "order_index": 0
        },
        {
            "category": "语法",
            "question": "Which sentence is correct?",
            "options": [
                "If I was you, I would study harder.",
                "If I were you, I would study harder.",
                "If I am you, I would study harder.",
                "If I be you, I would study harder."
            ],
            "correct_answer": "If I were you, I would study harder.",
            "difficulty": "medium",
            "order_index": 1
        },
        {
            "category": "阅读",
            "question": "Read the passage: 'The company has seen a significant increase in revenue this quarter.' What does 'significant' mean?",
            "options": ["small", "important", "negative", "temporary"],
            "correct_answer": "important",
            "difficulty": "easy",
            "order_index": 2
        },
        {
            "category": "词汇",
            "question": "What is the synonym of 'enormous'?",
            "options": ["tiny", "huge", "medium", "average"],
            "correct_answer": "huge",
            "difficulty": "easy",
            "order_index": 3
        },
        {
            "category": "语法",
            "question": "Choose the correct form: She _____ to the library every week.",
            "options": ["go", "goes", "went", "going"],
            "correct_answer": "goes",
            "difficulty": "easy",
            "order_index": 4
        },
        {
            "category": "阅读",
            "question": "What is the main idea of the following passage: 'Climate change is one of the most pressing issues of our time. Scientists agree that human activities are the primary cause.'",
            "options": [
                "Scientists are uncertain about climate change",
                "Human activities cause climate change",
                "Climate change is not important",
                "Only scientists care about climate change"
            ],
            "correct_answer": "Human activities cause climate change",
            "difficulty": "medium",
            "order_index": 5
        },
        {
            "category": "词汇",
            "question": "Choose the word that is closest in meaning to 'abundant':",
            "options": ["scarce", "plentiful", "limited", "rare"],
            "correct_answer": "plentiful",
            "difficulty": "medium",
            "order_index": 6
        },
        {
            "category": "语法",
            "question": "Which sentence uses the passive voice correctly?",
            "options": [
                "The book was written by the author.",
                "The book wrote by the author.",
                "The author was written the book.",
                "The book is writing by the author."
            ],
            "correct_answer": "The book was written by the author.",
            "difficulty": "hard",
            "order_index": 7
        },
        {
            "category": "阅读",
            "question": "In the sentence 'The professor, who has published many papers, is highly respected', what does 'who has published many papers' modify?",
            "options": ["The professor", "papers", "published", "respected"],
            "correct_answer": "The professor",
            "difficulty": "hard",
            "order_index": 8
        },
        {
            "category": "词汇",
            "question": "What does 'ambiguous' mean?",
            "options": ["clear", "unclear", "obvious", "certain"],
            "correct_answer": "unclear",
            "difficulty": "hard",
            "order_index": 9
        },
    ]
    
    for q_data in test_questions_data:
        question = TestQuestion(
            category=q_data["category"],
            question=q_data["question"],
            options=q_data["options"],
            correct_answer=q_data["correct_answer"],
            difficulty=q_data["difficulty"],
            order_index=q_data["order_index"],
            created_at=datetime.now(timezone.utc)
        )
        db.add(question)
        stats["test_questions"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['test_questions']} 道测试题")


def seed_learning_modules(db: Session):
    """创建学习模块"""
    print("📦 创建学习模块...")
    
    modules_data = [
        {
            "name": "Academic Reading",
            "description": "提升学术阅读能力，掌握长篇文章的理解和分析技巧",
            "tag": "系统推荐",
            "tag_type": "recommended",
            "target_level": "B1",
            "order_index": 0
        },
        {
            "name": "Essay Writing",
            "description": "学习写作结构与逻辑，提升学术写作水平",
            "tag": "系统推荐",
            "tag_type": "recommended",
            "target_level": "B2",
            "order_index": 1
        },
        {
            "name": "Listening & Note-taking",
            "description": "训练听力理解能力，掌握快速记笔记的方法",
            "tag": "可选模块",
            "tag_type": "optional",
            "target_level": "B1",
            "order_index": 2
        },
        {
            "name": "Speaking for Presentation",
            "description": "提升演讲表达能力，增强口语流利度和自信",
            "tag": "可选模块",
            "tag_type": "optional",
            "target_level": "B2",
            "order_index": 3
        },
        {
            "name": "Grammar Mastery",
            "description": "系统学习英语语法，从基础到高级",
            "tag": "可选模块",
            "tag_type": "optional",
            "target_level": "A2",
            "order_index": 4
        },
        {
            "name": "Vocabulary Building",
            "description": "扩展词汇量，学习高频词汇和学术词汇",
            "tag": "系统推荐",
            "tag_type": "recommended",
            "target_level": "A2",
            "order_index": 5
        },
    ]
    
    for m_data in modules_data:
        module = LearningModule(
            name=m_data["name"],
            description=m_data["description"],
            tag=m_data["tag"],
            tag_type=m_data["tag_type"],
            target_level=m_data.get("target_level"),
            order_index=m_data["order_index"],
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(module)
        stats["learning_modules"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['learning_modules']} 个学习模块")


def seed_path_config(db: Session):
    """创建学习路径配置"""
    print("⚙️  创建学习路径配置...")
    
    configs_data = [
        {
            "config_key": "targets",
            "config_value": [
                "一个学期内达到 B2",
                "半年内达到 B2",
                "一年内达到 C1"
            ],
            "description": "学习目标选项列表"
        },
        {
            "config_key": "quick_prompts",
            "config_value": [
                "根据我当前水平安排一节阅读课",
                "帮我出 5 道关于旅行的口语题",
                "帮我批改这段作文，并解释修改"
            ],
            "description": "AI教练快捷提示语列表"
        },
        {
            "config_key": "welcome_message",
            "config_value": "你好！我是你的 AI 学习教练。根据你的分级测试结果，我为你推荐了几个重点学习模块。有什么问题随时问我！",
            "description": "AI教练初始欢迎消息"
        },
    ]
    
    for c_data in configs_data:
        config = PathConfig(
            config_key=c_data["config_key"],
            config_value=c_data["config_value"],
            description=c_data["description"],
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(config)
        stats["path_configs"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['path_configs']} 个配置项")


def seed_practice_sessions(db: Session):
    """创建练习会话和题目"""
    print("📝 创建练习会话...")
    
    users = db.query(User).all()
    grades = db.query(Grade).filter(Grade.name.in_(["初一", "初二"])).all()
    versions = db.query(TextbookVersion).filter(TextbookVersion.name == "人教版").all()
    
    if not users or not grades or not versions:
        print("   ⚠️  缺少必要数据，跳过练习会话创建")
        return
    
    grade = grades[0]
    version = versions[0]
    units = db.query(Unit).filter(
        Unit.grade_id == grade.id,
        Unit.version_id == version.id
    ).limit(2).all()
    
    if not units:
        print("   ⚠️  缺少单元数据，跳过练习会话创建")
        return
    
    for user in users[:2]:  # 为前2个用户创建会话
        for unit in units[:1]:  # 每个用户1个会话
            session = PracticeSession(
                user_id=user.id,
                grade=grade.name,
                version=version.name,
                unit=unit.name,
                status="completed",
                total_questions=5,
                correct_count=3,
                wrong_count=2,
                started_at=datetime.now(timezone.utc) - timedelta(days=1),
                completed_at=datetime.now(timezone.utc) - timedelta(hours=23),
                created_at=datetime.now(timezone.utc) - timedelta(days=1)
            )
            db.add(session)
            db.flush()
            stats["practice_sessions"] += 1
    
            # 为会话创建题目
    questions_data = [
        {
            "question_type": "choice",
            "question": "What is the past tense of 'go'?",
            "options": ["goed", "went", "gone", "going"],
            "correct_answer": "went",
                    "explanation": "'go' 的过去式是 'went'。",
                    "encouragement": "很好！",
            "order_index": 0
        },
        {
            "question_type": "fill",
                    "question": "She _____ (like) reading books.",
            "options": None,
            "correct_answer": "likes",
                    "explanation": "第三人称单数加 's'。",
                    "encouragement": "正确！",
                    "order_index": 1
                },
            ]
            
    for q_data in questions_data:
        question = PracticeQuestion(
            session_id=session.id,
            question_type=q_data["question_type"],
            question=q_data["question"],
                    options=q_data.get("options"),
            correct_answer=q_data["correct_answer"],
                    explanation=q_data.get("explanation"),
                    encouragement=q_data.get("encouragement"),
                    order_index=q_data["order_index"],
                    created_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(question)
        db.flush()
        stats["practice_questions"] += 1
                
                # 创建答案记录
        answer = PracticeAnswer(
            session_id=session.id,
            question_id=question.id,
                    user_answer=q_data["correct_answer"] if q_data["order_index"] == 0 else "likes",
                    is_correct=True if q_data["order_index"] == 0 else True,
                    answered_at=datetime.now(timezone.utc) - timedelta(hours=23)
        )
        db.add(answer)
        stats["practice_answers"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['practice_sessions']} 个练习会话")
    print(f"   ✅ 创建 {stats['practice_questions']} 道练习题")
    print(f"   ✅ 创建 {stats['practice_answers']} 条答案记录")


def seed_test_sessions(db: Session):
    """创建测试会话"""
    print("🎯 创建测试会话...")
    
    users = db.query(User).all()
    test_questions = db.query(TestQuestion).limit(5).all()
    
    if not users or not test_questions:
        print("   ⚠️  缺少必要数据，跳过测试会话创建")
        return
    
    user = users[0]  # 为第一个用户创建测试会话
    session = TestSession(
        user_id=user.id,
        status="completed",
        level="B1",
        description="你的英语水平处于中级（B1），能够理解日常对话和简单文章。",
        suggestions=[
            "重点加强词汇量，每天学习20个新单词",
            "多练习阅读，选择适合B1水平的文章",
            "加强语法练习，特别是时态和语态"
        ],
        started_at=datetime.now(timezone.utc) - timedelta(days=2),
        completed_at=datetime.now(timezone.utc) - timedelta(days=2, hours=-1),
        created_at=datetime.now(timezone.utc) - timedelta(days=2)
    )
    db.add(session)
    db.flush()
    stats["test_sessions"] += 1
    
    # 创建测试答案
    for idx, question in enumerate(test_questions):
        is_correct = idx % 2 == 0  # 交替正确和错误
        answer = TestAnswer(
            session_id=session.id,
            question_id=question.id,
            user_answer=question.correct_answer if is_correct else question.options[0] if question.options else "wrong",
            is_correct=is_correct,
            answered_at=datetime.now(timezone.utc) - timedelta(days=2, hours=-1)
        )
        db.add(answer)
        stats["test_answers"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['test_sessions']} 个测试会话")
    print(f"   ✅ 创建 {stats['test_answers']} 条测试答案")


def seed_wrong_questions(db: Session):
    """创建错题本"""
    print("❌ 创建错题本...")
    
    users = db.query(User).all()
    
    if not users:
        print("   ⚠️  缺少用户数据，跳过错题本创建")
        return
    
    user = users[0]
    wrong_questions_data = [
        {
            "question_type": "choice",
            "question": "What is the past tense of 'go'?",
            "options": ["goed", "went", "gone", "going"],
            "correct_answer": "went",
            "user_answer": "goed",
            "explanation": "'go' 的过去式是 'went'，这是一个不规则动词。",
            "grade": "初一",
            "version": "人教版",
            "unit": "Unit 1"
        },
        {
            "question_type": "fill",
            "question": "She _____ (like) reading books.",
            "options": None,
            "correct_answer": "likes",
            "user_answer": "like",
            "explanation": "第三人称单数主语 'She' 后面，动词要加 's'。",
            "grade": "初一",
            "version": "人教版",
            "unit": "Unit 1"
        },
    ]
    
    for wq_data in wrong_questions_data:
        wrong_question = WrongQuestion(
            user_id=user.id,
            question_type=wq_data["question_type"],
            question=wq_data["question"],
            options=wq_data.get("options"),
            correct_answer=wq_data["correct_answer"],
            user_answer=wq_data["user_answer"],
            explanation=wq_data.get("explanation"),
            grade=wq_data.get("grade"),
            version=wq_data.get("version"),
            unit=wq_data.get("unit"),
            review_count=0,
            added_at=datetime.now(timezone.utc) - timedelta(days=3)
        )
        db.add(wrong_question)
        stats["wrong_questions"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['wrong_questions']} 道错题")


def seed_word_book(db: Session):
    """创建生词本"""
    print("📖 创建生词本...")
    
    users = db.query(User).all()
    
    if not users:
        print("   ⚠️  缺少用户数据，跳过生词本创建")
        return
    
    user = users[0]
    words_data = [
        {
            "word": "abundant",
            "meaning": "丰富的，充裕的",
            "example": "The region has abundant natural resources."
        },
        {
            "word": "significant",
            "meaning": "重要的，显著的",
            "example": "There has been a significant increase in sales."
        },
        {
            "word": "ambiguous",
            "meaning": "模糊的，不明确的",
            "example": "His statement was ambiguous and could be interpreted in different ways."
        },
        {
            "word": "productive",
            "meaning": "富有成效的，多产的",
            "example": "The meeting was very productive."
        },
    ]
    
    for word_data in words_data:
        word = WordBook(
            user_id=user.id,
            word=word_data["word"],
            meaning=word_data["meaning"],
            example=word_data["example"],
            review_count=0,
            added_at=datetime.now(timezone.utc) - timedelta(days=5)
        )
        db.add(word)
        stats["word_book"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['word_book']} 个生词")


def seed_user_learning_modules(db: Session):
    """创建用户学习模块关联"""
    print("🔗 创建用户学习模块关联...")
    
    users = db.query(User).all()
    modules = db.query(LearningModule).filter(LearningModule.tag_type == "recommended").limit(2).all()
    
    if not users or not modules:
        print("   ⚠️  缺少必要数据，跳过用户学习模块关联创建")
        return
    
    user = users[0]
    for module in modules:
        user_module = UserLearningModule(
            user_id=user.id,
            module_id=module.id,
            is_added=True,
            added_at=datetime.now(timezone.utc) - timedelta(days=1),
            updated_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(user_module)
        stats["user_learning_modules"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['user_learning_modules']} 个用户学习模块关联")


def seed_chat_messages(db: Session):
    """创建AI对话记录"""
    print("💬 创建AI对话记录...")
    
    users = db.query(User).all()
    
    if not users:
        print("   ⚠️  缺少用户数据，跳过对话记录创建")
        return
    
    user = users[0]
    messages_data = [
        {
            "message_type": "user",
            "message": "根据我当前水平安排一节阅读课",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=2)
        },
        {
            "message_type": "ai",
            "message": "好的，我来为你安排一节阅读课。根据你当前的水平，我建议从学术阅读开始，重点训练长篇文章的理解和分析能力。",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=2, minutes=1)
        },
        {
            "message_type": "user",
            "message": "帮我出 5 道关于旅行的口语题",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=1)
        },
        {
            "message_type": "ai",
            "message": "好的，我来为你准备口语练习题目。我会根据你的水平设计适合的口语话题，帮助你提升表达流利度。",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=1, minutes=1)
        },
    ]
    
    for msg_data in messages_data:
        message = ChatMessage(
            user_id=user.id,
            message_type=msg_data["message_type"],
            message=msg_data["message"],
            created_at=msg_data["created_at"]
        )
        db.add(message)
        stats["chat_messages"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['chat_messages']} 条对话记录")


def seed_daily_practice(db: Session):
    """创建每日练习记录"""
    print("📊 创建每日练习记录...")
    
    users = db.query(User).all()
    
    if not users:
        print("   ⚠️  缺少用户数据，跳过每日练习记录创建")
        return
    
    user = users[0]
    # 创建最近7天的练习记录
    for i in range(7):
        practice_date = datetime.now(timezone.utc) - timedelta(days=i)
        daily_practice = DailyPractice(
            user_id=user.id,
            practice_date=practice_date,
            question_count=10 + i * 2,
            correct_count=7 + i,
            practice_type="public",
            created_at=practice_date
        )
        db.add(daily_practice)
        stats["daily_practice"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['daily_practice']} 条每日练习记录")


def seed_sms_codes(db: Session):
    """创建短信验证码（可选，用于测试）"""
    print("📱 创建短信验证码...")
    
    # 创建一些过期的验证码用于测试
    phones = ["10000000000", "10000000000"]
    for phone in phones:
        sms_code = SmsCode(
            phone=phone,
            code="123456",
            purpose="login",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            is_used=True
        )
        db.add(sms_code)
        stats["sms_codes"] += 1
    
    db.commit()
    print(f"   ✅ 创建 {stats['sms_codes']} 条短信验证码记录")


def print_summary():
    """打印数据统计摘要"""
    print("\n" + "="*60)
    print("📊 数据插入统计摘要")
    print("="*60)
    
    total = sum(stats.values())
    print(f"\n总计: {total} 条数据\n")
    
    print("各表数据详情:")
    for table_name, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  • {table_name:30s}: {count:4d} 条")
    
    print("\n" + "="*60)
    print("✅ 所有测试数据已成功插入！")
    print("="*60)
    print("\n💡 提示:")
    print("   - 演示账号: demo / 10000000000 / 123456")
    print("   - 其他账号: student1, student2 (密码均为 123456)")
    print("   - 数据已包含完整的关联关系，所有页面应能正常显示")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成演示数据')
    parser.add_argument('--clear', action='store_true', help='仅清空数据，不插入新数据')
    parser.add_argument('--no-clear', action='store_true', help='不清空旧数据，直接追加')
    
    args = parser.parse_args()
    
    # 确保数据库表存在
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 清空数据（除非指定 --no-clear）
        if not args.no_clear:
            clear_all_data(db)
        
        if args.clear:
            print("✅ 仅清空数据，不插入新数据")
            return
        
        print("\n🌱 开始插入演示数据...\n")
        
        # 按依赖顺序插入数据
        seed_users(db)
        seed_grades(db)
        seed_textbook_versions(db)
        seed_units(db)
        seed_practice_question_bank(db)
        seed_test_questions(db)
        seed_learning_modules(db)
        seed_path_config(db)
        seed_practice_sessions(db)
        seed_test_sessions(db)
        seed_wrong_questions(db)
        seed_word_book(db)
        seed_user_learning_modules(db)
        seed_chat_messages(db)
        seed_daily_practice(db)
        seed_sms_codes(db)
        
        # 打印统计摘要
        print_summary()
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
