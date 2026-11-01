# 英语学习APP后端

基于FastAPI框架开发的用户认证系统，提供注册、登录和忘记密码功能。

## 技术栈

- **FastAPI**: Web框架
- **SQLAlchemy**: ORM框架
- **PyMySQL**: MySQL数据库驱动
- **Passlib**: 密码加密
- **python-jose**: JWT token生成和验证
- **Pydantic**: 数据验证

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置文件
│   ├── database.py        # 数据库连接和会话管理
│   ├── models.py          # 数据库模型
│   ├── schemas.py         # Pydantic模型（请求/响应验证）
│   ├── services.py        # 业务逻辑层
│   ├── utils.py           # 工具函数（密码加密、JWT等）
│   └── routers/
│       ├── __init__.py
│       └── auth.py        # 认证相关路由
├── main.py                # FastAPI主应用
├── requirements.txt       # 依赖包
└── README.md             # 说明文档
```

## 安装和运行

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置数据库

确保MySQL服务已启动，数据库配置在 `app/config.py` 中：

- 地址：127.0.0.1:3306
- 用户名：root
- 密码：12345678
- 数据库名：victor_english

**注意**：启动应用时会自动创建数据库和表，无需手动执行SQL。

### 3. 启动服务

```bash
python main.py
```

或者使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/health

## API接口

### 1. 用户注册

**POST** `/api/v1/auth/register`

请求体：
```json
{
  "username": "testuser",
  "email": "demo@example.invalid",
  "password": "123456"
}
```

响应：
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "demo@example.invalid",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "last_login_at": null
  }
}
```

### 2. 用户登录

**POST** `/api/v1/auth/login`

请求体：
```json
{
  "username": "testuser",  // 支持用户名或邮箱
  "password": "123456"
}
```

响应：同注册接口

### 3. 忘记密码

**POST** `/api/v1/auth/forgot-password`

请求体：
```json
{
  "email": "demo@example.invalid"
}
```

响应：
```json
{
  "message": "密码重置token已生成（开发环境直接返回，生产环境应通过邮件发送）: <token>"
}
```

### 4. 重置密码

**POST** `/api/v1/auth/reset-password`

请求体：
```json
{
  "token": "<reset_token>",
  "new_password": "newpassword123"
}
```

响应：
```json
{
  "message": "密码重置成功"
}
```

## 数据库模型

### User表

- `id`: 主键，自增
- `username`: 用户名，唯一，3-20字符
- `email`: 邮箱，唯一
- `password_hash`: 密码哈希（bcrypt加密）
- `is_active`: 是否激活
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `last_login_at`: 最后登录时间
- `reset_token`: 重置密码token
- `reset_token_expires`: 重置token过期时间

## 安全特性

1. **密码加密**：使用bcrypt算法加密存储
2. **JWT认证**：使用JWT token进行身份验证
3. **Token过期**：登录token默认30天过期
4. **重置Token过期**：密码重置token 1小时过期
5. **CORS配置**：支持跨域请求（开发环境）

## 注意事项

1. 生产环境请修改 `app/config.py` 中的 `SECRET_KEY`
2. 忘记密码功能在生产环境应通过邮件发送重置链接，当前为简化实现
3. 数据库连接配置可通过环境变量覆盖

## 开发说明

- 使用同步SQLAlchemy（非异步）
- 启动时自动创建数据库和表
- 支持用户名或邮箱登录
- 完整的错误处理和验证

