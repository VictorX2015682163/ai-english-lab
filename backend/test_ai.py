#!/usr/bin/env python3
"""
AI服务测试脚本
用于验证火山方舟AI是否能正常调用
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai import ai_service
from app.config import settings


def test_basic_chat():
    """测试基础对话功能"""
    print("=" * 70)
    print("测试1: 基础对话功能")
    print("=" * 70)
    
    if not settings.VOLCENGINE_ARK_API_KEY:
        print("❌ 错误: API Key未配置，请在 .env 文件中设置 VOLCENGINE_ARK_API_KEY")
        return False
    
    print(f"✓ API Key已配置")
    print(f"✓ 模型: {settings.VOLCENGINE_ARK_MODEL}")
    print(f"✓ 基础URL: {settings.VOLCENGINE_ARK_BASE_URL}")
    print()
    
    print("发送测试消息: '你好'")
    response = ai_service.chat("你好")
    
    if response:
        print(f"✓ AI响应成功!")
        print(f"响应内容: {response}")
        print()
        return True
    else:
        print("❌ AI响应失败")
        print()
        return False


def test_system_prompt():
    """测试带系统提示词的对话"""
    print("=" * 70)
    print("测试2: 带系统提示词的对话")
    print("=" * 70)
    
    system_prompt = "你是一位专业的英语学习助手，请用中文回复。"
    user_message = "请用一句话介绍英语学习的重要性"
    
    print(f"系统提示词: {system_prompt}")
    print(f"用户消息: {user_message}")
    print()
    
    response = ai_service.chat(
        user_message=user_message,
        system_prompt=system_prompt
    )
    
    if response:
        print(f"✓ AI响应成功!")
        print(f"响应内容: {response}")
        print()
        return True
    else:
        print("❌ AI响应失败")
        print()
        return False


def test_conversation_history():
    """测试对话历史"""
    print("=" * 70)
    print("测试3: 对话历史功能")
    print("=" * 70)
    
    conversation_history = [
        {"role": "user", "content": "我喜欢英语"},
        {"role": "assistant", "content": "很好！英语是一门非常有用的语言。"}
    ]
    user_message = "我应该从哪里开始学习？"
    
    print(f"对话历史: {len(conversation_history)}条消息")
    print(f"用户消息: {user_message}")
    print()
    
    response = ai_service.chat(
        user_message=user_message,
        conversation_history=conversation_history
    )
    
    if response:
        print(f"✓ AI响应成功!")
        print(f"响应内容: {response}")
        print()
        return True
    else:
        print("❌ AI响应失败")
        print()
        return False


def test_coach_prompt():
    """测试AI教练提示词"""
    print("=" * 70)
    print("测试4: AI教练提示词（模拟真实场景）")
    print("=" * 70)
    
    from app.services.prompts import PromptTemplates
    
    system_prompt = PromptTemplates.get_coach_prompt(
        user_level="B1 Intermediate",
        level_description="你具备基础的英语交流能力，可以处理日常话题和简单的学术内容。",
        learning_modules="Academic Reading, Essay Writing",
        learning_target="半年内达到 B2"
    )
    
    user_message = "我想提高我的阅读能力，应该怎么做？"
    
    print(f"系统提示词长度: {len(system_prompt)}字符")
    print(f"用户消息: {user_message}")
    print()
    
    response = ai_service.chat(
        user_message=user_message,
        system_prompt=system_prompt
    )
    
    if response:
        print(f"✓ AI响应成功!")
        print(f"响应内容: {response}")
        print()
        return True
    else:
        print("❌ AI响应失败")
        print()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("🚀 火山方舟AI服务测试")
    print("=" * 70 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("基础对话", test_basic_chat()))
    results.append(("系统提示词", test_system_prompt()))
    results.append(("对话历史", test_conversation_history()))
    results.append(("AI教练提示词", test_coach_prompt()))
    
    # 输出测试结果
    print("=" * 70)
    print("📊 测试结果汇总")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"总计: {len(results)}个测试")
    print(f"通过: {passed}个")
    print(f"失败: {failed}个")
    print()
    
    if failed == 0:
        print("🎉 所有测试通过！AI服务配置正确。")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接。")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
