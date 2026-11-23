"""SDK wrappers around deterministic study tools."""
import json
from agents import function_tool
from . import _study_core as core

@function_tool
def get_learning_path(level: str = "入门") -> str:
    """查询深度学习路线；level 为零基础、入门或进阶。"""
    return json.dumps(core.call_tool("get_learning_path", {"level": level}), ensure_ascii=False)

@function_tool
def create_study_plan(days: int = 14, daily_minutes: int = 60, level: str = "入门", start_date: str = "") -> str:
    """按天数、每日分钟数生成计划；日期可用 YYYY-MM-DD。"""
    return json.dumps(core.call_tool("create_study_plan", dict(days=days, daily_minutes=daily_minutes, level=level, start_date=start_date)), ensure_ascii=False)

@function_tool
def generate_quiz(topic: str = "综合", count: int = 3) -> str:
    """生成不含答案的测验，支持综合、CNN、梯度、训练、张量、注意力。"""
    return json.dumps(core.call_tool("generate_quiz", dict(topic=topic, count=count)), ensure_ascii=False)

@function_tool
def grade_quiz(answers: str) -> str:
    """批改题库选择题答案，例如 DL01:B, DL02:A，并分析错题。"""
    return json.dumps(core.call_tool("grade_quiz", {"answers": answers}), ensure_ascii=False)
