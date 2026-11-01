"""
更新数据库表结构：添加头像和个人资料字段
"""
from sqlalchemy import text, inspect
from app.database import engine
from app.config import settings

def update_users_table_profile_fields():
    """更新users表，添加头像和个人资料字段"""
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = {col['name']: col for col in inspector.get_columns('users')}
            
            # 添加avatar字段
            if 'avatar' not in columns:
                print("正在添加avatar字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN avatar VARCHAR(500) NULL COMMENT '头像文件路径'
                """))
                conn.commit()
                print("✅ avatar字段添加成功")
            else:
                print("avatar字段已存在")
            
            # 添加nickname字段
            if 'nickname' not in columns:
                print("正在添加nickname字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN nickname VARCHAR(50) NULL COMMENT '昵称'
                """))
                conn.commit()
                print("✅ nickname字段添加成功")
            else:
                print("nickname字段已存在")
            
            # 添加bio字段
            if 'bio' not in columns:
                print("正在添加bio字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN bio VARCHAR(500) NULL COMMENT '个人简介'
                """))
                conn.commit()
                print("✅ bio字段添加成功")
            else:
                print("bio字段已存在")
            
            # 添加gender字段
            if 'gender' not in columns:
                print("正在添加gender字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN gender VARCHAR(10) NULL COMMENT '性别：male/female/other'
                """))
                conn.commit()
                print("✅ gender字段添加成功")
            else:
                print("gender字段已存在")
            
            # 添加birthday字段
            if 'birthday' not in columns:
                print("正在添加birthday字段...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN birthday DATETIME NULL COMMENT '生日'
                """))
                conn.commit()
                print("✅ birthday字段添加成功")
            else:
                print("birthday字段已存在")
                
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("开始更新数据库表结构（添加头像和个人资料字段）...")
    print("=" * 60)
    update_users_table_profile_fields()
    print("=" * 60)
    print("数据库更新完成！")
    print("=" * 60)

