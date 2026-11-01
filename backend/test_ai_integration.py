#!/usr/bin/env python3
"""
集成测试：测试AI教练对话功能
直接测试后端代码，不需要启动服务
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User, TestSession, LearningModule, UserLearningModule, ChatMessage, PathConfig
from app.services.ai import ai_service
from app.services.prompts import PromptTemplates
from datetime import datetime, timezone

def setup_test_data(db):
    """设置测试数据"""
    # 创建测试用户（如果不存在）
    test_user = db.query(User).filter(User.username == "test_ai_user").first()
    if not test_user:
        from app.utils import get_password_hash
        test_user = User(
            username="test_ai_user",
            phone="10000000000",
            email="demo@example.invalid",
            password_hash=get_password_hash("123456"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✓ 创建测试用户: {test_user.username} (ID: {test_user.id})")
    else:
        print(f"✓ 使用现有测试用户: {test_user.username} (ID: {test_user.id})")
    
    # 创建测试会话（如果不存在）
    test_session = db.query(TestSession).filter(
        TestSession.user_id == test_user.id,
        TestSession.status == "completed"
    ).first()
    
    if not test_session:
        test_session = TestSession(
            user_id=test_user.id,
            status="completed",
            level="B1 Intermediate",
            description="你具备基础的英语交流能力，可以处理日常话题和简单的学术内容。",
            suggestions=["适合进阶：学术阅读", "写作结构需要重点提升"],
            completed_at=datetime.now(timezone.utc)
        )
        db.add(test_session)
        db.commit()
        print(f"✓ 创建测试会话，水平: {test_session.level}")
    else:
        print(f"✓ 使用现有测试会话，水平: {test_session.level}")
    
    # 创建学习模块（如果不存在）
    module = db.query(LearningModule).filter(LearningModule.name == "Academic Reading").first()
    if not module:
        module = LearningModule(
            name="Academic Reading",
            description="提升学术阅读能力",
            tag="系统推荐",
            tag_type="recommended",
            is_active=True
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        print(f"✓ 创建学习模块: {module.name}")
    
    # 关联用户和模块
    user_module = db.query(UserLearningModule).filter(
        UserLearningModule.user_id == test_user.id,
        UserLearningModule.module_id == module.id
    ).first()
    
    if not user_module:
        user_module = UserLearningModule(
            user_id=test_user.id,
            module_id=module.id,
            is_added=True
        )
        db.add(user_module)
        db.commit()
        print(f"✓ 关联用户和学习模块")
    
    return test_user

def test_ai_chat():
    """测试AI对话功能"""
    print("\n" + "=" * 70)
    print("测试AI教练对话功能")
    print("=" * 70 + "\n")
    
    db = SessionLocal()
    
    try:
        # 设置测试数据
        test_user = setup_test_data(db)
        
        # 获取用户信息
        latest_test = db.query(TestSession).filter(
            TestSession.user_id == test_user.id,
            TestSession.status == "completed"
        ).order_by(TestSession.completed_at.desc()).first()
        
        user_level = latest_test.level if latest_test else "未测试"
        level_description = latest_test.description if latest_test else ""
        
        # 获取学习模块
        user_modules = db.query(UserLearningModule).filter(
            UserLearningModule.user_id == test_user.id,
            UserLearningModule.is_added == True
        ).all()
        
        module_names = []
        for um in user_modules:
            module = db.query(LearningModule).filter(LearningModule.id == um.module_id).first()
            if module:
                module_names.append(module.name)
        
        learning_modules = ", ".join(module_names) if module_names else "无"
        learning_target = "半年内达到 B2"
        
        print(f"\n用户信息:")
        print(f"  水平: {user_level}")
        print(f"  学习模块: {learning_modules}")
        print(f"  学习目标: {learning_target}")
        print()
        
        # 构建系统提示词
        system_prompt = PromptTemplates.get_coach_prompt(
            user_level=user_level,
            level_description=level_description,
            learning_modules=learning_modules,
            learning_target=learning_target
        )
        
        print("系统提示词长度:", len(system_prompt), "字符")
        print()
        
        # 测试对话
        test_messages = [
            "你好",
            "我想提高我的阅读能力，应该怎么做？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"测试 {i}: {message}")
            print("-" * 70)
            
            # 获取对话历史
            recent_messages = db.query(ChatMessage).filter(
                ChatMessage.user_id == test_user.id
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            recent_messages.reverse()
            
            conversation_history = []
            for msg in recent_messages:
                role = "user" if msg.message_type == "user" else "assistant"
                conversation_history.append({
                    "role": role,
                    "content": msg.message
                })
            
            # 调用AI
            response = ai_service.chat(
                user_message=message,
                system_prompt=system_prompt,
                conversation_history=conversation_history if conversation_history else None
            )
            
            if response:
                print(f"✓ AI响应成功")
                print(f"回复: {response[:300]}..." if len(response) > 300 else f"回复: {response}")
                
                # 保存对话记录
                user_msg = ChatMessage(
                    user_id=test_user.id,
                    message_type="user",
                    message=message
                )
                db.add(user_msg)
                
                ai_msg = ChatMessage(
                    user_id=test_user.id,
                    message_type="ai",
                    message=response
                )
                db.add(ai_msg)
                db.commit()
            else:
                print("❌ AI响应失败")
            
            print()
        
        print("=" * 70)
        print("✓ 测试完成")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_ai_chat()
