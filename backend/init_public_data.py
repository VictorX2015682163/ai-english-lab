#!/usr/bin/env python3
"""
初始化公立学校模式的基础数据（年级、版本、单元）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Grade, TextbookVersion, Unit

def init_public_data():
    """初始化公立学校模式数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(Grade).count() > 0:
            print("数据已存在，跳过初始化")
            return
        
        print("开始初始化公立学校模式数据...")
        
        # 1. 创建年级
        grades_data = [
            {"name": "三年级", "order_index": 1},
            {"name": "四年级", "order_index": 2},
            {"name": "五年级", "order_index": 3},
            {"name": "六年级", "order_index": 4},
            {"name": "初一", "order_index": 5},
            {"name": "初二", "order_index": 6},
            {"name": "初三", "order_index": 7},
        ]
        
        grades_map = {}
        for g_data in grades_data:
            grade = Grade(**g_data)
            db.add(grade)
            grades_map[g_data["name"]] = grade
        
        # 2. 创建教材版本
        versions_data = [
            {"name": "人教版", "order_index": 1},
            {"name": "北师大版", "order_index": 2},
            {"name": "外研版", "order_index": 3},
            {"name": "苏教版", "order_index": 4},
        ]
        
        versions_map = {}
        for v_data in versions_data:
            version = TextbookVersion(**v_data)
            db.add(version)
            versions_map[v_data["name"]] = version
        
        db.flush()  # 获取ID
        
        # 3. 创建单元（为每个年级和版本的组合创建6个单元）
        units_data = [
            "Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", "Unit 6"
        ]
        
        for grade_name, grade_obj in grades_map.items():
            for version_name, version_obj in versions_map.items():
                for idx, unit_name in enumerate(units_data, 1):
                    unit = Unit(
                        grade_id=grade_obj.id,
                        version_id=version_obj.id,
                        name=unit_name,
                        order_index=idx
                    )
                    db.add(unit)
        
        db.commit()
        print("✅ 数据初始化完成！")
        print(f"   - 年级: {len(grades_data)} 个")
        print(f"   - 版本: {len(versions_data)} 个")
        print(f"   - 单元: {len(grades_data) * len(versions_data) * len(units_data)} 个")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_public_data()

