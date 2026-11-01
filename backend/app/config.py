"""
应用配置
"""
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings:
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "victor_english")
    
    # 数据库URL
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
    # JWT配置（用于token生成，简单实现）
    SECRET_KEY = os.getenv("SECRET_KEY") or __import__("secrets").token_urlsafe(32)
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天
    
    # API配置
    API_V1_PREFIX = "/api/v1"
    
    # CORS配置
    CORS_ORIGINS = ["*"]  # 开发环境允许所有来源
    
    # 短信服务配置（阿里云短信）
    SMS_ACCESS_KEY_ID = os.getenv("SMS_ACCESS_KEY_ID", "")
    SMS_ACCESS_KEY_SECRET = os.getenv("SMS_ACCESS_KEY_SECRET", "")
    SMS_SIGN_NAME = os.getenv("SMS_SIGN_NAME", "英语学习APP")  # 短信签名
    SMS_TEMPLATE_CODE = os.getenv("SMS_TEMPLATE_CODE", "")  # 短信模板代码
    SMS_ENABLED = os.getenv("SMS_ENABLED", "false").lower() == "true"  # 是否启用真实短信发送
    
    # 开发环境：如果未配置短信服务，则直接返回验证码
    SMS_DEV_MODE = not SMS_ENABLED or not SMS_ACCESS_KEY_ID or not SMS_ACCESS_KEY_SECRET
    
    # 火山方舟AI配置
    VOLCENGINE_ARK_API_KEY = os.getenv("VOLCENGINE_ARK_API_KEY", "")
    VOLCENGINE_ARK_BASE_URL = os.getenv("VOLCENGINE_ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    VOLCENGINE_ARK_MODEL = os.getenv("VOLCENGINE_ARK_MODEL", "doubao-seed-1-8-251228")
    VOLCENGINE_ARK_TIMEOUT = int(os.getenv("VOLCENGINE_ARK_TIMEOUT", "60"))  # 请求超时时间（秒）

settings = Settings()

