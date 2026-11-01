"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建数据库引擎（不使用数据库名，用于创建数据库）
engine_without_db = create_engine(
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}?charset=utf8mb4",
    echo=False
)

# 创建数据库（如果不存在）
def create_database():
    """创建数据库（如果不存在）"""
    try:
        with engine_without_db.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(text(f"SHOW DATABASES LIKE '{settings.DB_NAME}'"))
            if result.fetchone() is None:
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                print(f"数据库 {settings.DB_NAME} 创建成功")
            else:
                print(f"数据库 {settings.DB_NAME} 已存在")
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        raise

# 创建数据库
print(f"正在检查/创建数据库: {settings.DB_NAME}")
create_database()
print(f"当前使用的数据库: {settings.DB_NAME}")

# 创建数据库引擎（使用数据库名）
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,   # 1小时后回收连接
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

