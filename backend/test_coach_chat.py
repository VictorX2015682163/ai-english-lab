#!/usr/bin/env python3
"""
测试AI教练对话功能
需要先启动后端服务，并且有测试用户登录
"""
import requests
import json
import sys

# 配置
BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

def test_coach_chat(token: str):
    """测试AI教练对话"""
    print("=" * 70)
    print("测试AI教练对话功能")
    print("=" * 70)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 测试消息
    test_messages = [
        "你好",
        "我想提高我的阅读能力",
        "帮我安排一节阅读课",
        "我应该怎么学习英语？"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n测试 {i}/{len(test_messages)}: {message}")
        print("-" * 70)
        
        data = {
            "message": message
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}{API_PREFIX}/international/coach/chat",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result.get("reply", "")
                print(f"✓ 成功")
                print(f"AI回复: {ai_reply[:200]}..." if len(ai_reply) > 200 else f"AI回复: {ai_reply}")
            else:
                print(f"❌ 失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
        
        print()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 test_coach_chat.py <token>")
        print("\n获取token的方法:")
        print("1. 启动后端服务: python3 start.py")
        print("2. 使用登录接口获取token")
        print("3. 运行: python3 test_coach_chat.py <your_token>")
        sys.exit(1)
    
    token = sys.argv[1]
    
    print("\n" + "=" * 70)
    print("🚀 AI教练对话功能测试")
    print("=" * 70 + "\n")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务运行正常\n")
        else:
            print("⚠️  后端服务响应异常\n")
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {str(e)}")
        print("请确保后端服务已启动: python3 start.py")
        sys.exit(1)
    
    # 测试对话
    test_coach_chat(token)
    
    print("=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
