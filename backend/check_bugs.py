#!/usr/bin/env python3
"""
Bug检查脚本
检查AI教练对话功能的潜在问题
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_code_issues():
    """检查代码问题"""
    issues = []
    
    print("=" * 70)
    print("🔍 Bug检查报告")
    print("=" * 70 + "\n")
    
    # 1. 检查N+1查询问题
    print("1. 检查数据库查询效率...")
    with open("app/routers/international.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "for um in user_modules:" in content and "db.query(LearningModule)" in content:
            issues.append({
                "severity": "medium",
                "type": "性能问题",
                "description": "N+1查询问题：在循环中查询数据库",
                "location": "app/routers/international.py:460-463",
                "fix": "使用join查询一次性获取所有模块信息"
            })
            print("  ❌ 发现N+1查询问题")
        else:
            print("  ✓ 无N+1查询问题")
    
    # 2. 检查空消息验证
    print("\n2. 检查输入验证...")
    if 'if not request.message' not in content and 'if request.message.strip()' not in content:
        issues.append({
            "severity": "low",
            "type": "输入验证",
            "description": "缺少空消息验证",
            "location": "app/routers/international.py:429",
            "fix": "添加消息非空验证"
        })
        print("  ⚠️  缺少空消息验证")
    else:
        print("  ✓ 有输入验证")
    
    # 3. 检查消息长度限制
    print("\n3. 检查消息长度限制...")
    if "len(request.message)" not in content or "max_length" not in content.lower():
        issues.append({
            "severity": "low",
            "type": "输入验证",
            "description": "缺少消息长度限制",
            "location": "app/routers/international.py:429",
            "fix": "添加消息长度限制（如5000字符）"
        })
        print("  ⚠️  缺少消息长度限制")
    else:
        print("  ✓ 有消息长度限制")
    
    # 4. 检查对话历史排除逻辑
    print("\n4. 检查对话历史逻辑...")
    if "if msg.id != user_message.id:" in content:
        # 检查flush后id是否已生成
        if "db.flush()" in content and "user_message.id" in content:
            # 这个逻辑可能有问题，因为flush后id可能还没有生成
            issues.append({
                "severity": "medium",
                "type": "逻辑问题",
                "description": "对话历史排除逻辑可能有问题：flush后id可能未生成",
                "location": "app/routers/international.py:487",
                "fix": "使用created_at时间戳或其他方式排除当前消息"
            })
            print("  ⚠️  对话历史排除逻辑可能有问题")
        else:
            print("  ✓ 对话历史逻辑正常")
    else:
        print("  ✓ 对话历史逻辑正常")
    
    # 5. 检查错误处理
    print("\n5. 检查错误处理...")
    if "except HTTPException:" in content and "except Exception as e:" in content:
        print("  ✓ 错误处理完善")
    else:
        issues.append({
            "severity": "high",
            "type": "错误处理",
            "description": "错误处理不完善",
            "location": "app/routers/international.py",
            "fix": "添加完整的错误处理"
        })
        print("  ❌ 错误处理不完善")
    
    # 6. 检查AI服务调用失败处理
    print("\n6. 检查AI服务失败处理...")
    if "if not ai_reply:" in content:
        print("  ✓ 有AI失败fallback机制")
    else:
        issues.append({
            "severity": "high",
            "type": "错误处理",
            "description": "缺少AI服务失败处理",
            "location": "app/routers/international.py:504",
            "fix": "添加AI失败时的fallback机制"
        })
        print("  ❌ 缺少AI失败处理")
    
    # 7. 检查日志记录
    print("\n7. 检查日志记录...")
    if "logger.info" in content or "logger.error" in content:
        print("  ✓ 有日志记录")
    else:
        issues.append({
            "severity": "low",
            "type": "可维护性",
            "description": "缺少日志记录",
            "location": "app/routers/international.py",
            "fix": "添加关键操作的日志记录"
        })
        print("  ⚠️  缺少日志记录")
    
    # 输出问题汇总
    print("\n" + "=" * 70)
    print("📊 问题汇总")
    print("=" * 70)
    
    if issues:
        high_issues = [i for i in issues if i["severity"] == "high"]
        medium_issues = [i for i in issues if i["severity"] == "medium"]
        low_issues = [i for i in issues if i["severity"] == "low"]
        
        print(f"\n严重问题: {len(high_issues)}个")
        for issue in high_issues:
            print(f"  ❌ [{issue['type']}] {issue['description']}")
            print(f"     位置: {issue['location']}")
            print(f"     修复: {issue['fix']}\n")
        
        print(f"中等问题: {len(medium_issues)}个")
        for issue in medium_issues:
            print(f"  ⚠️  [{issue['type']}] {issue['description']}")
            print(f"     位置: {issue['location']}")
            print(f"     修复: {issue['fix']}\n")
        
        print(f"轻微问题: {len(low_issues)}个")
        for issue in low_issues:
            print(f"  ℹ️  [{issue['type']}] {issue['description']}")
            print(f"     位置: {issue['location']}")
            print(f"     修复: {issue['fix']}\n")
        
        print(f"\n总计: {len(issues)}个问题")
        return issues
    else:
        print("\n✓ 未发现明显问题")
        return []

if __name__ == "__main__":
    issues = check_code_issues()
    sys.exit(0 if len(issues) == 0 else 1)
