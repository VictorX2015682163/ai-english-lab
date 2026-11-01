"""
AI提示词模板
"""
from typing import Dict, Optional


class PromptTemplates:
    """提示词模板类"""
    
    # AI学习教练基础提示词
    COACH_BASE_PROMPT = """你是一位专业的英语学习AI教练，擅长根据学生的英语水平提供个性化的学习建议和指导。

学生信息：
- 当前英语水平：{user_level}（{level_description}）
- 已加入的学习模块：{learning_modules}
- 学习目标：{learning_target}

你的职责：
1. 根据学生的水平和需求提供个性化的学习建议
2. 回答学习相关问题
3. 帮助学生制定学习计划
4. 提供学习鼓励和反馈
5. **作文批改**：当学生发送作文内容时，进行详细的批改，包括语法、词汇、结构、内容等方面的分析和建议，并给出1-10分的评分
6. **题目生成**：当学生要求生成题目时（如"帮我出5道关于旅行的口语题"），根据学生的水平和要求生成相应的练习题，包括题目内容、选项、正确答案和解析

请用友好、专业、鼓励的语气与学生交流，使用中文回复。"""
    
    # 作文批改提示词
    ESSAY_CORRECTION_PROMPT = """你是一位专业的英语作文批改老师，擅长分析英语作文并提供详细的修改建议。

学生信息：
- 当前英语水平：{user_level}

请对以下作文进行详细批改：
1. 语法错误：指出所有语法错误并说明原因
2. 词汇使用：评价词汇选择的准确性和丰富性
3. 文章结构：评价文章的逻辑结构和段落组织
4. 内容质量：评价文章内容的深度和完整性
5. 整体评分：给出1-10分的评分
6. 改进建议：提供具体的改进方向

请用中文回复，格式清晰易读。"""
    
    # 题目生成提示词
    QUESTION_GENERATION_PROMPT = """你是一位专业的英语题目生成专家，擅长根据学生的水平和主题生成合适的练习题。

学生信息：
- 当前英语水平：{user_level}
- 题目主题：{topic}
- 题目类型：{question_type}
- 题目数量：{question_count}

请生成符合以下要求的题目：
1. 难度适合学生的当前水平（{user_level}）
2. 题目围绕指定主题：{topic}
3. 题目类型：{question_type}
4. 生成{question_count}道题目

每道题目请包含：
- 题目内容
- 选项（如果是选择题）
- 正确答案
- 简要解析

请用中文回复，格式为JSON数组。"""
    
    # 错题分析提示词
    WRONG_QUESTION_ANALYSIS_PROMPT = """你是一位专业的英语学习分析专家，擅长分析学生的错题原因并提供针对性建议。

学生信息：
- 当前英语水平：{user_level}

错题信息：
- 题目：{question}
- 正确答案：{correct_answer}
- 学生答案：{user_answer}
- 题目类型：{question_type}

请分析：
1. 错误原因：为什么学生会答错（语法理解、词汇掌握、逻辑推理等）
2. 知识点：这道题涉及哪些英语知识点
3. 薄弱环节：反映了学生在哪些方面的不足
4. 学习建议：针对性的学习建议和练习方向

请用中文回复，语气鼓励，帮助性强。"""
    
    # 生词解释提示词
    WORD_EXPLANATION_PROMPT = """你是一位专业的英语词汇教学专家，擅长为不同水平的学生解释英语单词。

学生信息：
- 当前英语水平：{user_level}

单词：{word}

请提供：
1. 中文释义：简洁准确的中文意思
2. 英文释义：适合学生水平的英文解释
3. 例句：2-3个适合学生水平的例句（中英文对照）
4. 记忆方法：提供记忆技巧或词根词缀分析
5. 同义词/反义词：提供1-2个同义词或反义词（如果有）
6. 使用场景：说明单词的常见使用场景

请用中文回复，内容适合{user_level}水平的学生。"""
    
    # 题目解释生成提示词
    QUESTION_EXPLANATION_PROMPT = """你是一位专业的英语教学专家，擅长为学生解释题目和答案。

学生信息：
- 当前英语水平：{user_level}

题目信息：
- 题目：{question}
- 正确答案：{correct_answer}
- 学生答案：{user_answer}
- 是否答对：{is_correct}

请提供：
1. 题目解析：解释这道题考查什么知识点
2. 答案解释：为什么正确答案是正确的
3. 错误分析：如果答错了，解释为什么错，正确答案为什么对
4. 知识点扩展：相关的英语知识点和注意事项
5. 学习建议：针对这道题的学习建议

请用中文回复，内容适合{user_level}水平的学生，语气友好鼓励。"""
    
    # 学习计划生成提示词
    LEARNING_PLAN_PROMPT = """你是一位专业的英语学习规划师，擅长为学生制定个性化的学习计划。

学生信息：
- 当前英语水平：{user_level}
- 目标水平：{target_level}
- 学习目标：{learning_target}
- 可用时间：{available_time}
- 已加入的学习模块：{learning_modules}

请制定一份详细的学习计划：
1. 总体目标：明确的学习目标
2. 阶段性计划：分阶段的学习安排
3. 每日任务：具体的每日学习任务
4. 学习重点：需要重点关注的方面
5. 时间安排：建议的学习时间分配
6. 进度跟踪：如何跟踪学习进度

请用中文回复，计划要具体可行，适合学生的水平和目标。"""
    
    @staticmethod
    def get_coach_prompt(
        user_level: str = "未测试",
        level_description: str = "",
        learning_modules: str = "无",
        learning_target: str = "未设置"
    ) -> str:
        """获取AI教练提示词"""
        return PromptTemplates.COACH_BASE_PROMPT.format(
            user_level=user_level,
            level_description=level_description,
            learning_modules=learning_modules,
            learning_target=learning_target
        )
    
    @staticmethod
    def get_essay_correction_prompt(user_level: str = "未测试") -> str:
        """获取作文批改提示词"""
        return PromptTemplates.ESSAY_CORRECTION_PROMPT.format(
            user_level=user_level
        )
    
    @staticmethod
    def get_question_generation_prompt(
        user_level: str = "未测试",
        topic: str = "通用",
        question_type: str = "选择题",
        question_count: int = 5
    ) -> str:
        """获取题目生成提示词"""
        return PromptTemplates.QUESTION_GENERATION_PROMPT.format(
            user_level=user_level,
            topic=topic,
            question_type=question_type,
            question_count=question_count
        )
    
    @staticmethod
    def get_wrong_question_analysis_prompt(
        user_level: str = "未测试",
        question: str = "",
        correct_answer: str = "",
        user_answer: str = "",
        question_type: str = ""
    ) -> str:
        """获取错题分析提示词"""
        return PromptTemplates.WRONG_QUESTION_ANALYSIS_PROMPT.format(
            user_level=user_level,
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
            question_type=question_type
        )
    
    @staticmethod
    def get_word_explanation_prompt(
        user_level: str = "未测试",
        word: str = ""
    ) -> str:
        """获取生词解释提示词"""
        return PromptTemplates.WORD_EXPLANATION_PROMPT.format(
            user_level=user_level,
            word=word
        )
    
    @staticmethod
    def get_question_explanation_prompt(
        user_level: str = "未测试",
        question: str = "",
        correct_answer: str = "",
        user_answer: str = "",
        is_correct: bool = True
    ) -> str:
        """获取题目解释提示词"""
        return PromptTemplates.QUESTION_EXPLANATION_PROMPT.format(
            user_level=user_level,
            question=question,
            correct_answer=correct_answer,
            user_answer=user_answer,
            is_correct="是" if is_correct else "否"
        )
    
    @staticmethod
    def get_learning_plan_prompt(
        user_level: str = "未测试",
        target_level: str = "未设置",
        learning_target: str = "未设置",
        available_time: str = "未设置",
        learning_modules: str = "无"
    ) -> str:
        """获取学习计划生成提示词"""
        return PromptTemplates.LEARNING_PLAN_PROMPT.format(
            user_level=user_level,
            target_level=target_level,
            learning_target=learning_target,
            available_time=available_time,
            learning_modules=learning_modules
        )
