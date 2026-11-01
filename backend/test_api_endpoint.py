#!/usr/bin/env python3
"""
测试API端点是否正常工作
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务运行正常")
            return True
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端服务已启动: python3 start.py")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def test_get_questions_guest():
    """测试游览模式获取题目"""
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/international/test/questions",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 游览模式获取题目成功")
            print(f"  题目数量: {len(data)}")
            if data:
                print(f"  第一题: {data[0].get('question', '')[:50]}...")
            return True
        else:
            print(f"❌ 获取题目失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("测试API端点")
    print("=" * 70 + "\n")
    
    # 测试健康检查
    if not test_health():
        print("\n请先启动后端服务:")
        print("  cd backend")
        print("  python3 start.py")
        return
    
    print()
    
    # 测试获取题目（游览模式）
    test_get_questions_guest()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
