"""
快速检查当前配置的数据库名称
"""
from app.config import settings

print("=" * 50)
print("当前数据库配置:")
print(f"  数据库名: {settings.DB_NAME}")
print(f"  数据库URL: {settings.DATABASE_URL}")
print("=" * 50)
print("\n如果看到 'my_app'，说明有环境变量覆盖了配置")
print("请检查是否有环境变量 DB_NAME=my_app")

