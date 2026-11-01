"""
Pydantic模型：用于请求和响应验证
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserRegister(BaseModel):
    """用户注册请求模型"""
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的手机号')
        return v

class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名或手机号")
    password: str = Field(..., description="密码")

class SendSmsCodeRequest(BaseModel):
    """发送短信验证码请求模型"""
    phone: str = Field(..., description="手机号")
    purpose: str = Field(default="login", description="用途：login/register/reset")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的手机号')
        return v

class SmsLoginRequest(BaseModel):
    """短信验证码登录请求模型"""
    phone: str = Field(..., description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="验证码")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('请输入有效的手机号')
        return v

class ForgotPasswordRequest(BaseModel):
    """忘记密码请求模型"""
    email: EmailStr = Field(..., description="邮箱")

class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""
    token: str = Field(..., description="重置密码token")
    new_password: str = Field(..., min_length=6, description="新密码")

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    phone: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    avatar: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    avatar_url: Optional[str] = None

class SmsCodeResponse(BaseModel):
    """短信验证码响应模型（开发环境）"""
    message: str
    code: Optional[str] = None  # 开发环境返回验证码，生产环境不返回

class UserUpdateRequest(BaseModel):
    """更新用户资料请求模型"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    gender: Optional[str] = Field(None, description="性别：male/female/other")
    birthday: Optional[datetime] = Field(None, description="生日")
    email: Optional[EmailStr] = Field(None, description="邮箱")

class UserProfileResponse(BaseModel):
    """用户资料响应模型"""
    id: int
    username: str
    phone: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 学习统计相关 ==========

class LearningStatsResponse(BaseModel):
    """学习统计响应模型"""
    week_days: list[bool] = Field(..., description="本周7天练习情况")
    total_questions: int = Field(..., description="累计完成题目数")
    public_info: Optional[dict] = None
    international_info: Optional[dict] = None


class PublicInfoResponse(BaseModel):
    """公立模式信息响应模型"""
    grade: Optional[str] = None
    version: Optional[str] = None
    unit: Optional[str] = None
    completed: int = 0
    total: int = 0
    last_practice_time: Optional[datetime] = None


class InternationalInfoResponse(BaseModel):
    """国际模式信息响应模型"""
    level: Optional[str] = None
    modules_count: int = 0
    last_conversation_time: Optional[datetime] = None


# ========== 公立学校模式相关 ==========

class StartPracticeRequest(BaseModel):
    """开始练习请求模型"""
    grade: str = Field(..., description="年级")
    version: str = Field(..., description="教材版本")
    unit: str = Field(..., description="单元")


class QuestionResponse(BaseModel):
    """题目响应模型"""
    id: int
    question_type: str
    question: str
    options: Optional[list] = None
    correct_answer: str
    explanation: Optional[str] = None
    encouragement: Optional[str] = None
    order_index: int

    class Config:
        from_attributes = True


class PracticeSessionResponse(BaseModel):
    """练习会话响应模型"""
    session_id: int
    questions: list[QuestionResponse]


class SubmitAnswerRequest(BaseModel):
    """提交答案请求模型"""
    session_id: int
    question_id: int
    answer: str


class AnswerResultResponse(BaseModel):
    """答案结果响应模型"""
    is_correct: bool
    correct_answer: str
    explanation: Optional[str] = None
    encouragement: Optional[str] = None


class EndPracticeRequest(BaseModel):
    """结束练习请求模型"""
    session_id: int


class PracticeSummaryResponse(BaseModel):
    """练习总结响应模型"""
    total: int
    correct: int
    wrong: int


# ========== 国际学校模式相关 ==========

class TestQuestionResponse(BaseModel):
    """测试题目响应模型"""
    id: int
    category: str
    question: str
    options: list
    order_index: int

    class Config:
        from_attributes = True


class SubmitTestRequest(BaseModel):
    """提交测试请求模型"""
    answers: dict[int, str] = Field(..., description="题目ID和答案的映射")


class TestResultResponse(BaseModel):
    """测试结果响应模型"""
    level: str
    description: str
    suggestions: list[str]


class LearningModuleResponse(BaseModel):
    """学习模块响应模型"""
    id: int
    name: str
    description: Optional[str] = None
    tag: Optional[str] = None
    tag_type: str
    added: bool = False

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """AI教练对话请求模型"""
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息")


class ChatResponse(BaseModel):
    """AI对话响应模型"""
    reply: str


# ========== 错题本相关 ==========

class WrongQuestionResponse(BaseModel):
    """错题响应模型"""
    id: int
    question_type: str
    question: str
    options: Optional[list] = None
    correct_answer: str
    user_answer: str
    explanation: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True


class AddWrongQuestionRequest(BaseModel):
    """添加错题请求模型"""
    question_id: Optional[int] = None
    question_type: str
    question: str
    options: Optional[list] = None
    correct_answer: str
    user_answer: str
    explanation: Optional[str] = None
    grade: Optional[str] = None
    version: Optional[str] = None
    unit: Optional[str] = None


class ReviewQuestionsResponse(BaseModel):
    """复习题目响应模型"""
    questions: list[QuestionResponse]


# ========== 生词本相关 ==========

class WordResponse(BaseModel):
    """生词响应模型"""
    id: int
    word: str
    meaning: Optional[str] = None
    example: Optional[str] = None
    added_at: datetime

    class Config:
        from_attributes = True


class AddWordRequest(BaseModel):
    """添加生词请求模型"""
    word: str = Field(..., min_length=1, description="单词")
    meaning: Optional[str] = None
    example: Optional[str] = None

