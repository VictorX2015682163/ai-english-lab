"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=True, comment="邮箱")
    phone = Column(String(20), unique=True, index=True, nullable=False, comment="手机号")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    
    # 忘记密码相关字段
    reset_token = Column(String(255), nullable=True, comment="重置密码token")
    reset_token_expires = Column(DateTime(timezone=True), nullable=True, comment="重置token过期时间")
    
    # 个人资料相关字段
    avatar = Column(String(500), nullable=True, comment="头像文件路径")
    nickname = Column(String(50), nullable=True, comment="昵称")
    bio = Column(String(500), nullable=True, comment="个人简介")
    gender = Column(String(10), nullable=True, comment="性别：male/female/other")
    birthday = Column(DateTime(timezone=True), nullable=True, comment="生日")


class SmsCode(Base):
    """短信验证码模型"""
    __tablename__ = "sms_codes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(20), index=True, nullable=False, comment="手机号")
    code = Column(String(6), nullable=False, comment="验证码")
    purpose = Column(String(20), nullable=False, default="login", comment="用途：login/register/reset")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="过期时间")
    is_used = Column(Boolean, default=False, comment="是否已使用")


class PracticeSession(Base):
    """公立学校模式练习会话"""
    __tablename__ = "practice_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    grade = Column(String(20), nullable=False, comment="年级")
    version = Column(String(50), nullable=False, comment="教材版本")
    unit = Column(String(50), nullable=False, comment="单元")
    status = Column(String(20), default="in_progress", comment="状态：in_progress/completed")
    total_questions = Column(Integer, default=0, comment="总题目数")
    correct_count = Column(Integer, default=0, comment="正确数")
    wrong_count = Column(Integer, default=0, comment="错误数")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class PracticeQuestion(Base):
    """练习题"""
    __tablename__ = "practice_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True, comment="会话ID")
    question_type = Column(String(20), nullable=False, comment="题目类型：choice/fill")
    question = Column(Text, nullable=False, comment="题目内容")
    options = Column(JSON, nullable=True, comment="选项（选择题）")
    correct_answer = Column(String(500), nullable=False, comment="正确答案")
    explanation = Column(Text, nullable=True, comment="解析")
    encouragement = Column(Text, nullable=True, comment="鼓励语")
    order_index = Column(Integer, default=0, comment="排序索引")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class PracticeAnswer(Base):
    """练习答案记录"""
    __tablename__ = "practice_answers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id"), nullable=False, index=True, comment="会话ID")
    question_id = Column(Integer, ForeignKey("practice_questions.id"), nullable=False, index=True, comment="题目ID")
    user_answer = Column(String(500), nullable=False, comment="用户答案")
    is_correct = Column(Boolean, nullable=False, comment="是否正确")
    answered_at = Column(DateTime(timezone=True), server_default=func.now(), comment="答题时间")


class WrongQuestion(Base):
    """错题本"""
    __tablename__ = "wrong_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    question_id = Column(Integer, ForeignKey("practice_questions.id"), nullable=True, index=True, comment="题目ID（如果是练习题目）")
    question_type = Column(String(20), nullable=False, comment="题目类型：choice/fill")
    question = Column(Text, nullable=False, comment="题目内容")
    options = Column(JSON, nullable=True, comment="选项（选择题）")
    correct_answer = Column(String(500), nullable=False, comment="正确答案")
    user_answer = Column(String(500), nullable=False, comment="用户答案")
    explanation = Column(Text, nullable=True, comment="解析")
    grade = Column(String(20), nullable=True, comment="年级")
    version = Column(String(50), nullable=True, comment="教材版本")
    unit = Column(String(50), nullable=True, comment="单元")
    added_at = Column(DateTime(timezone=True), server_default=func.now(), comment="添加时间")
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment="复习时间")
    review_count = Column(Integer, default=0, comment="复习次数")


class WordBook(Base):
    """生词本"""
    __tablename__ = "word_book"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    word = Column(String(100), nullable=False, comment="单词")
    meaning = Column(String(500), nullable=True, comment="含义")
    example = Column(Text, nullable=True, comment="例句")
    added_at = Column(DateTime(timezone=True), server_default=func.now(), comment="添加时间")
    reviewed_at = Column(DateTime(timezone=True), nullable=True, comment="复习时间")
    review_count = Column(Integer, default=0, comment="复习次数")


class TestSession(Base):
    """国际学校模式测试会话"""
    __tablename__ = "test_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    status = Column(String(20), default="in_progress", comment="状态：in_progress/completed")
    level = Column(String(50), nullable=True, comment="测试结果等级")
    description = Column(Text, nullable=True, comment="等级描述")
    suggestions = Column(JSON, nullable=True, comment="建议项（数组）")
    started_at = Column(DateTime(timezone=True), server_default=func.now(), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class TestQuestion(Base):
    """测试题目（静态题目库）"""
    __tablename__ = "test_questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), nullable=False, comment="分类：词汇/语法/阅读")
    question = Column(Text, nullable=False, comment="题目内容")
    options = Column(JSON, nullable=False, comment="选项（数组）")
    correct_answer = Column(String(500), nullable=False, comment="正确答案")
    difficulty = Column(String(20), default="medium", comment="难度：easy/medium/hard")
    order_index = Column(Integer, default=0, comment="排序索引")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class TestAnswer(Base):
    """测试答案记录"""
    __tablename__ = "test_answers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("test_sessions.id"), nullable=False, index=True, comment="会话ID")
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False, index=True, comment="题目ID")
    user_answer = Column(String(500), nullable=False, comment="用户答案")
    is_correct = Column(Boolean, nullable=False, comment="是否正确")
    answered_at = Column(DateTime(timezone=True), server_default=func.now(), comment="答题时间")


class LearningModule(Base):
    """学习模块"""
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="模块名称")
    description = Column(Text, nullable=True, comment="模块描述")
    tag = Column(String(50), nullable=True, comment="标签：系统推荐/可选模块")
    tag_type = Column(String(20), default="optional", comment="标签类型：recommended/optional")
    target_level = Column(String(50), nullable=True, comment="目标等级")
    order_index = Column(Integer, default=0, comment="排序索引")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class UserLearningModule(Base):
    """用户学习模块关联"""
    __tablename__ = "user_learning_modules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False, index=True, comment="模块ID")
    is_added = Column(Boolean, default=True, comment="是否已加入计划")
    added_at = Column(DateTime(timezone=True), server_default=func.now(), comment="加入时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ChatMessage(Base):
    """AI对话记录"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    message_type = Column(String(20), nullable=False, comment="消息类型：user/ai")
    message = Column(Text, nullable=False, comment="消息内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class DailyPractice(Base):
    """每日练习记录（用于统计）"""
    __tablename__ = "daily_practice"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    practice_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="练习日期")
    question_count = Column(Integer, default=0, comment="题目数量")
    correct_count = Column(Integer, default=0, comment="正确数")
    practice_type = Column(String(20), default="public", comment="练习类型：public/international")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class Grade(Base):
    """年级表"""
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="年级名称")
    order_index = Column(Integer, default=0, comment="排序索引")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class TextbookVersion(Base):
    """教材版本表"""
    __tablename__ = "textbook_versions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="版本名称")
    order_index = Column(Integer, default=0, comment="排序索引")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class Unit(Base):
    """单元表"""
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, index=True, comment="年级ID")
    version_id = Column(Integer, ForeignKey("textbook_versions.id"), nullable=False, index=True, comment="版本ID")
    name = Column(String(50), nullable=False, comment="单元名称")
    order_index = Column(Integer, default=0, comment="排序索引")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 唯一约束：同一年级和版本下，单元名称不能重复
    __table_args__ = (
        {'mysql_engine': 'InnoDB'},
    )


class PracticeQuestionBank(Base):
    """练习题题库表"""
    __tablename__ = "practice_question_bank"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True, index=True, comment="年级ID（可选，为空表示通用）")
    version_id = Column(Integer, ForeignKey("textbook_versions.id"), nullable=True, index=True, comment="版本ID（可选，为空表示通用）")
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=True, index=True, comment="单元ID（可选，为空表示通用）")
    question_type = Column(String(20), nullable=False, comment="题目类型：choice/fill")
    question = Column(Text, nullable=False, comment="题目内容")
    options = Column(JSON, nullable=True, comment="选项（选择题）")
    correct_answer = Column(String(500), nullable=False, comment="正确答案")
    explanation = Column(Text, nullable=True, comment="解析")
    encouragement = Column(Text, nullable=True, comment="鼓励语")
    difficulty = Column(String(20), default="medium", comment="难度：easy/medium/hard")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class PathConfig(Base):
    """学习路径配置表"""
    __tablename__ = "path_config"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    config_key = Column(String(50), unique=True, nullable=False, index=True, comment="配置键")
    config_value = Column(JSON, nullable=False, comment="配置值（JSON格式）")
    description = Column(String(200), nullable=True, comment="配置描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

