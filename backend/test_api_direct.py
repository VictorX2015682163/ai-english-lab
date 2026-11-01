#!/usr/bin/env python3
"""
直接测试API接口
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import TestQuestion

def check_test_questions():
    """检查数据库中是否有测试题目"""
    db = SessionLocal()
    try:
        questions = db.query(TestQuestion).limit(5).all()
        print(f"数据库中的测试题目数量: {len(questions)}")
        
        if questions:
            print("\n前5道题目:")
            for i, q in enumerate(questions, 1):
                print(f"{i}. ID: {q.id}, 分类: {q.category}")
                print(f"   题目: {q.question[:50]}...")
        else:
            print("\n⚠️  数据库中没有测试题目！")
            print("需要初始化测试题目数据。")
        
        return len(questions) > 0
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 70)
    print("检查测试题目数据")
    print("=" * 70 + "\n")
    
    has_questions = check_test_questions()
    
    if not has_questions:
        print("\n" + "=" * 70)
        print("解决方案:")
        print("1. 运行初始化脚本: python3 init_practice_questions.py")
        print("2. 或者手动添加测试题目到数据库")
        print("=" * 70)
