#!/usr/bin/env python3
"""
初始化练习题题库数据
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import PracticeQuestionBank, Grade, TextbookVersion, Unit

def init_practice_questions():
    """初始化练习题题库"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(PracticeQuestionBank).count() > 0:
            print("题目数据已存在，跳过初始化")
            return
        
        print("开始初始化练习题题库...")
        
        # 通用题目（所有年级版本都可以使用）
        common_questions = [
            {
                "question_type": "choice",
                "question": "What is the past tense of 'go'?",
                "options": ["goed", "went", "gone", "going"],
                "correct_answer": "went",
                "explanation": "'go' 的过去式是 'went'，这是一个不规则动词。",
                "encouragement": "很好！你掌握了这个不规则动词的变化。"
            },
            {
                "question_type": "choice",
                "question": "I _____ to school every day.",
                "options": ["go", "goes", "went", "going"],
                "correct_answer": "go",
                "explanation": "一般现在时，主语是 'I'，所以用动词原形 'go'。",
                "encouragement": "正确！你理解了一般现在时的用法。"
            },
            {
                "question_type": "fill",
                "question": "Complete the sentence: She _____ (like) reading books.",
                "options": None,
                "correct_answer": "likes",
                "explanation": "第三人称单数主语 'She' 后面，动词要加 's'。",
                "encouragement": "完美！你掌握了第三人称单数的用法。"
            },
            {
                "question_type": "choice",
                "question": "Which word means 'happy'?",
                "options": ["sad", "angry", "glad", "tired"],
                "correct_answer": "glad",
                "explanation": "'glad' 意思是 '高兴的'，与 'happy' 同义。",
                "encouragement": "很棒！你的词汇量不错。"
            },
            {
                "question_type": "fill",
                "question": "Fill in the blank: There _____ (be) many students in the classroom.",
                "options": None,
                "correct_answer": "are",
                "explanation": "'many students' 是复数，所以用 'are'。",
                "encouragement": "正确！你理解了 there be 句型的用法。"
            },
            {
                "question_type": "choice",
                "question": "What is the plural form of 'child'?",
                "options": ["childs", "children", "childes", "child"],
                "correct_answer": "children",
                "explanation": "'child' 的复数是 'children'，这是一个不规则复数。",
                "encouragement": "很好！你掌握了不规则复数的变化。"
            },
            {
                "question_type": "fill",
                "question": "Fill in the blank: I _____ (be) a student.",
                "options": None,
                "correct_answer": "am",
                "explanation": "主语是 'I'，be 动词用 'am'。",
                "encouragement": "正确！你掌握了 be 动词的用法。"
            },
            {
                "question_type": "choice",
                "question": "Which sentence is correct?",
                "options": [
                    "He don't like apples.",
                    "He doesn't like apples.",
                    "He not like apples.",
                    "He doesn't likes apples."
                ],
                "correct_answer": "He doesn't like apples.",
                "explanation": "第三人称单数否定句，用 'doesn't'，后面跟动词原形。",
                "encouragement": "完美！你掌握了第三人称单数否定句的用法。"
            },
            {
                "question_type": "fill",
                "question": "Fill in the blank: They _____ (play) football every weekend.",
                "options": None,
                "correct_answer": "play",
                "explanation": "一般现在时，主语是复数 'They'，用动词原形。",
                "encouragement": "正确！你理解了一般现在时的用法。"
            },
            {
                "question_type": "choice",
                "question": "What is the opposite of 'hot'?",
                "options": ["warm", "cool", "cold", "cooled"],
                "correct_answer": "cold",
                "explanation": "'hot' 的反义词是 'cold'。",
                "encouragement": "很好！你的词汇量不错。"
            }
        ]
        
        # 添加通用题目
        for q_data in common_questions:
            question = PracticeQuestionBank(
                grade_id=None,
                version_id=None,
                unit_id=None,
                **q_data
            )
            db.add(question)
        
        db.commit()
        print("✅ 题目初始化完成！")
        print(f"   - 通用题目: {len(common_questions)} 道")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_practice_questions()

