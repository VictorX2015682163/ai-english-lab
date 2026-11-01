#!/usr/bin/env python3
"""
检查后端服务状态
"""
import requests
import sys

def check_service():
    """检查服务状态"""
    print("=" * 70)
    print("检查后端服务状态")
    print("=" * 70 + "\n")
    
    # 检查健康检查接口
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务运行正常")
            print(f"  响应: {response.json()}")
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("\n解决方案:")
        print("1. 启动后端服务:")
        print("   cd backend")
        print("   python3 start.py")
        print("\n2. 或者使用:")
        print("   python3 main.py")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False
    
    # 检查测试题目接口
    print("\n检查测试题目接口...")
    try:
        response = requests.get(
            "http://127.0.0.1:8000/api/v1/international/test/questions",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 测试题目接口正常")
            print(f"  题目数量: {len(data)}")
            return True
        else:
            print(f"❌ 测试题目接口异常: {response.status_code}")
            print(f"  错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 测试题目接口失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_service()
    sys.exit(0 if success else 1)
