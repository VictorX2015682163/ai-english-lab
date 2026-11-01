#!/usr/bin/env python3
"""
测试AI功能：作文批改、题目生成、学习路径推荐
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.request_detector import RequestDetector
from app.services.ai import ai_service
from app.services.prompts import PromptTemplates

def test_request_detection():
    """测试请求类型检测"""
    print("=" * 70)
    print("测试请求类型检测")
    print("=" * 70 + "\n")
    
    test_cases = [
        ("帮我批改这段作文", "essay_correction"),
        ("帮我出5道关于旅行的口语题", "question_generation"),
        ("我想提高阅读能力", "general"),
        ("帮我生成10道阅读题", "question_generation"),
        ("请批改我的作文：I like travel...", "essay_correction"),
    ]
    
    for message, expected_type in test_cases:
        request_type, params = RequestDetector.detect_request_type(message)
        status = "✓" if request_type == expected_type else "❌"
        print(f"{status} 消息: {message}")
        print(f"   检测类型: {request_type} (期望: {expected_type})")
        if params:
            print(f"   参数: {params}")
        print()

def test_essay_correction():
    """测试作文批改"""
    print("=" * 70)
    print("测试作文批改功能")
    print("=" * 70 + "\n")
    
    essay = """I like to travel. Travel is very interesting. I go to many places. I see many things. Travel make me happy."""
    
    system_prompt = PromptTemplates.get_essay_correction_prompt(user_level="B1 Intermediate")
    user_message = f"请批改以下作文：\n\n{essay}"
    
    print(f"系统提示词长度: {len(system_prompt)}字符")
    print(f"作文内容: {essay[:50]}...")
    print()
    
    response = ai_service.chat(
        user_message=user_message,
        system_prompt=system_prompt
    )
    
    if response:
        print(f"✓ AI响应成功")
        print(f"回复长度: {len(response)}字符")
        print(f"回复预览: {response[:200]}...")
    else:
        print("❌ AI响应失败")
    print()

def test_question_generation():
    """测试题目生成"""
    print("=" * 70)
    print("测试题目生成功能")
    print("=" * 70 + "\n")
    
    system_prompt = PromptTemplates.get_question_generation_prompt(
        user_level="B1 Intermediate",
        topic="旅行",
        question_type="口语题",
        question_count=5
    )
    user_message = "请生成5道关于旅行的口语题"
    
    print(f"系统提示词长度: {len(system_prompt)}字符")
    print(f"用户消息: {user_message}")
    print()
    
    response = ai_service.chat(
        user_message=user_message,
        system_prompt=system_prompt,
        temperature=0.7,
        max_tokens=3000
    )
    
    if response:
        print(f"✓ AI响应成功")
        print(f"回复长度: {len(response)}字符")
        print(f"回复预览: {response[:300]}...")
    else:
        print("❌ AI响应失败")
    print()

def test_parameter_extraction():
    """测试参数提取"""
    print("=" * 70)
    print("测试参数提取")
    print("=" * 70 + "\n")
    
    test_messages = [
        "帮我出5道关于旅行的口语题",
        "生成10道阅读题",
        "给我出3个关于科技的写作题",
    ]
    
    for message in test_messages:
        request_type, params = RequestDetector.detect_request_type(message)
        print(f"消息: {message}")
        print(f"类型: {request_type}")
        if params:
            print(f"参数: 数量={params.get('count')}, 主题={params.get('topic')}, 题型={params.get('question_type')}")
        print()

def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🚀 AI功能测试")
    print("=" * 70 + "\n")
    
    # 测试请求检测
    test_request_detection()
    
    # 测试参数提取
    test_parameter_extraction()
    
    # 测试作文批改
    test_essay_correction()
    
    # 测试题目生成
    test_question_generation()
    
    print("=" * 70)
    print("✅ 测试完成")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
