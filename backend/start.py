#!/usr/bin/env python3
"""
启动脚本 - 显示数据库信息并启动服务
"""
import sys
from app.config import settings
from app.database import engine
from sqlalchemy import text

print("\n" + "="*70)
print("🚀 英语学习APP后端服务启动")
print("="*70)
print(f"📊 数据库配置:")
print(f"   主机: {settings.DB_HOST}:{settings.DB_PORT}")
print(f"   数据库名: {settings.DB_NAME} ⬅️ 这是新项目的数据库")
print(f"   用户: {settings.DB_USER}")
print("="*70)

# 检查实际连接的数据库
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT DATABASE()'))
        actual_db = result.scalar()
        print(f"✅ 实际连接的数据库: {actual_db}")
        
        # 查看表
        result = conn.execute(text('SHOW TABLES'))
        tables = [row[0] for row in result]
        print(f"📋 数据库中的表: {', '.join(tables) if tables else '(无表)'}")
        
        if 'users' in tables:
            result = conn.execute(text('SELECT COUNT(*) FROM users'))
            count = result.scalar()
            print(f"👥 用户数量: {count}")
except Exception as e:
    print(f"❌ 数据库连接错误: {e}")
    sys.exit(1)

print("="*70)
print("⚠️  注意: 如果你看到 'my_app' 数据库，那是之前项目的数据库")
print("   当前项目使用的是 'victor_english' 数据库（全新独立）")
print("="*70 + "\n")

# 启动服务
if __name__ == "__main__":
    from main import app
    import uvicorn
    print("🌐 服务启动在: http://127.0.0.1:8000")
    print("📚 API文档: http://127.0.0.1:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)

