#!/usr/bin/env python3
"""
初始化学习路径配置数据
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import PathConfig

def init_path_config():
    """初始化学习路径配置"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(PathConfig).count() > 0:
            print("配置数据已存在，跳过初始化")
            return
        
        print("开始初始化学习路径配置...")
        
        # 1. 学习目标选项
        targets_config = PathConfig(
            config_key="targets",
            config_value=[
                "一个学期内达到 B2",
                "半年内达到 B2",
                "一年内达到 C1"
            ],
            description="学习目标选项列表"
        )
        db.add(targets_config)
        
        # 2. 快捷提示语
        quick_prompts_config = PathConfig(
            config_key="quick_prompts",
            config_value=[
                "根据我当前水平安排一节阅读课",
                "帮我出 5 道关于旅行的口语题",
                "帮我批改这段作文，并解释修改"
            ],
            description="AI教练快捷提示语列表"
        )
        db.add(quick_prompts_config)
        
        # 3. 初始欢迎消息
        welcome_message_config = PathConfig(
            config_key="welcome_message",
            config_value="你好！我是你的 AI 学习教练。根据你的分级测试结果，我为你推荐了几个重点学习模块。有什么问题随时问我！",
            description="AI教练初始欢迎消息"
        )
        db.add(welcome_message_config)
        
        db.commit()
        print("✅ 配置初始化完成！")
        print("   - 学习目标: 3 个")
        print("   - 快捷提示: 3 个")
        print("   - 欢迎消息: 1 条")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_path_config()

