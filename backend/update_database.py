"""
更新数据库表结构：添加phone字段
"""
from sqlalchemy import text
from app.database import engine_without_db, engine
from app.config import settings

def update_users_table():
    """更新users表，添加phone字段"""
    try:
        with engine.connect() as conn:
            # 检查phone字段是否存在
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'phone'
            """), {"db_name": settings.DB_NAME})
            
            if result.fetchone() is None:
                print("正在添加phone字段...")
                # 添加phone字段
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN phone VARCHAR(20) NULL AFTER email,
                    ADD UNIQUE INDEX idx_phone (phone)
                """))
                conn.commit()
                print("✅ phone字段添加成功")
            else:
                print("phone字段已存在")
            
            # 检查email字段是否可以为NULL
            result = conn.execute(text("""
                SELECT IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'email'
            """), {"db_name": settings.DB_NAME})
            
            row = result.fetchone()
            if row and row[0] == 'NO':
                print("正在修改email字段为可空...")
                conn.execute(text("ALTER TABLE users MODIFY COLUMN email VARCHAR(100) NULL"))
                conn.commit()
                print("✅ email字段已修改为可空")
            else:
                print("email字段已为可空")
                
            # 检查phone字段是否可以为NULL，如果可以为NULL，改为NOT NULL
            result = conn.execute(text("""
                SELECT IS_NULLABLE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'phone'
            """), {"db_name": settings.DB_NAME})
            
            row = result.fetchone()
            if row and row[0] == 'YES':
                # 先检查是否有NULL值
                result = conn.execute(text("SELECT COUNT(*) FROM users WHERE phone IS NULL"))
                null_count = result.scalar()
                if null_count > 0:
                    print(f"⚠️  警告：有 {null_count} 条记录的phone为NULL，需要先处理")
                    # 为NULL的记录设置临时值
                    conn.execute(text("""
                        UPDATE users 
                        SET phone = CONCAT('temp_', id) 
                        WHERE phone IS NULL
                    """))
                    conn.commit()
                    print("已为NULL的phone设置临时值")
                
                print("正在修改phone字段为必填...")
                conn.execute(text("ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) NOT NULL"))
                conn.commit()
                print("✅ phone字段已修改为必填")
            else:
                print("phone字段已为必填")
                
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("开始更新数据库表结构...")
    print("=" * 60)
    update_users_table()
    print("=" * 60)
    print("数据库更新完成！")
    print("=" * 60)

