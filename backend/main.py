"""
FastAPI主应用文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.config import settings
from app.routers import auth, profile, learning, public, international, wrongbook, wordbook
import os

# 打印数据库配置信息
print("=" * 50)
print(f"数据库配置信息:")
print(f"  主机: {settings.DB_HOST}:{settings.DB_PORT}")
print(f"  数据库名: {settings.DB_NAME}")
print(f"  用户: {settings.DB_USER}")
print("=" * 50)

# 创建数据库表
print(f"正在创建/更新数据库表...")
Base.metadata.create_all(bind=engine)
print(f"数据库表创建完成！")

# 创建FastAPI应用
app = FastAPI(
    title="英语学习APP后端API",
    description="提供用户注册、登录、忘记密码等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(profile.router, prefix=settings.API_V1_PREFIX)
app.include_router(learning.router, prefix=settings.API_V1_PREFIX)
app.include_router(public.router, prefix=settings.API_V1_PREFIX)
app.include_router(international.router, prefix=settings.API_V1_PREFIX)
app.include_router(wrongbook.router, prefix=settings.API_V1_PREFIX)
app.include_router(wordbook.router, prefix=settings.API_V1_PREFIX)

# 创建静态文件目录
static_dir = "static"
os.makedirs(static_dir, exist_ok=True)
os.makedirs("static/avatars", exist_ok=True)

# 挂载静态文件服务（用于访问头像）
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    """根路径"""
    return {"message": "英语学习APP后端API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

