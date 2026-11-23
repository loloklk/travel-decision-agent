"""Deterministic learning tools, shared by the local server and EdgeOne agent."""
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


CURRICULUM = [
    ("Python 与张量", "变量、函数、NumPy 广播和张量形状", "实现矩阵乘法并打印每一步 shape"),
    ("梯度与自动求导", "链式法则、梯度下降和 autograd", "用 PyTorch 拟合 y=2x+1，记录损失"),
    ("神经网络训练", "MLP、损失函数、训练集与验证集", "训练 MNIST 分类器并比较训练与验证准确率"),
    ("卷积神经网络", "卷积、池化、通道和参数量", "搭建小型 CNN 并计算各层输出尺寸"),
    ("泛化与迁移学习", "过拟合、正则化和冻结参数", "对比数据增强前后的验证集指标"),
    ("序列与注意力", "RNN、LSTM、注意力与 Transformer", "画出注意力计算流程并检查 Q/K/V 形状"),
    ("项目与复盘", "推理、指标、误差分析和复现", "整理一个可复现项目：代码、指标、失败样例和 README"),
]

# id, topic, question, options, answer, explanation
BANK = [
    ("DL01", "梯度", "训练时 backward() 的主要作用是什么？", ["A. 更新参数", "B. 计算梯度", "C. 清空梯度", "D. 切换推理模式"], "B", "backward() 计算梯度；optimizer.step() 才会更新参数。"),
    ("DL02", "梯度", "PyTorch 训练循环中为何通常先 zero_grad()？", ["A. 避免梯度意外累加", "B. 随机初始化参数", "C. 增大 batch", "D. 保存模型"], "A", "梯度默认累加；通常每个 batch 开始时清零，梯度累积训练除外。"),
    ("DL03", "CNN", "输入宽度 32，卷积核 3、padding=1、stride=1，输出宽度是多少？", ["A. 30", "B. 31", "C. 32", "D. 34"], "C", "floor((32+2×1−3)/1)+1=32。"),
    ("DL04", "CNN", "卷积层参数量通常与下列哪项无关？", ["A. 卷积核大小", "B. 输入通道数", "C. 输出通道数", "D. 输入图像宽高"], "D", "标准卷积参数量为 Cout×Cin×Kh×Kw，加上可选偏置 Cout。"),
    ("DL05", "训练", "训练损失下降，验证损失持续上升，通常提示什么？", ["A. 欠拟合", "B. 过拟合", "C. 无梯度", "D. 数据一定正确"], "B", "模型可能开始记忆训练数据，可检查正则化、数据增强、早停与数据划分。"),
    ("DL06", "训练", "测试集最合适的用途是什么？", ["A. 每轮调参", "B. 参与反向传播", "C. 最终独立评估", "D. 生成训练标签"], "C", "频繁根据测试集调整模型会造成评估信息泄漏。"),
    ("DL07", "张量", "形状 (16,3,32,32) 的 NCHW 张量中，3 表示什么？", ["A. batch 大小", "B. 通道数", "C. 宽度", "D. 高度"], "B", "NCHW 依次表示批量、通道、高度、宽度。"),
    ("DL08", "注意力", "标准缩放点积注意力使用什么计算权重？", ["A. softmax(QKᵀ/√dk)", "B. Q+K+V", "C. sigmoid(V)", "D. argmax(Q)"], "A", "用查询与键的相似度经缩放和 softmax 得到权重，再对 V 加权。"),
    ("DL09", "训练", "model.eval() 会自动禁用梯度计算吗？", ["A. 会", "B. 不会", "C. 仅在 CPU 上会", "D. 仅在 CNN 中会"], "B", "eval() 切换 Dropout/BatchNorm 等的行为；禁用梯度需 no_grad() 或 inference_mode()。"),
    ("DL10", "注意力", "Transformer 中位置编码主要补充什么信息？", ["A. 标签", "B. 学习率", "C. 序列顺序", "D. batch 数量"], "C", "自注意力本身需要额外的位置机制来表达 token 的顺序。"),
]


def _integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} 必须是 {low}～{high} 的整数")
    return value


def get_learning_path(level: str = "入门") -> dict:
    """查询深度学习路线。level 为零基础、入门或进阶。"""
    if level not in ("零基础", "入门", "进阶"):
        raise ValueError("level 请选择零基础、入门或进阶")
    start = 0 if level != "进阶" else 3
    return {"level": level, "prerequisites": "Python 基础、矩阵乘法与导数；缺失时先补基础", "stages": [
        {"stage": i + 1, "topic": topic, "knowledge": knowledge, "deliverable": task}
        for i, (topic, knowledge, task) in enumerate(CURRICULUM[start:])
    ], "source": "项目内置教学路线，可按课程要求调整"}


def create_study_plan(days: int = 14, daily_minutes: int = 60, level: str = "入门", start_date: str = "") -> dict:
    """按可用时间分配学习任务和复习。日期可用 YYYY-MM-DD；空则从今天起。"""
    _integer(days, "days", 1, 90)
    _integer(daily_minutes, "daily_minutes", 15, 480)
    start = date.fromisoformat(start_date) if start_date else datetime.now(ZoneInfo("Asia/Shanghai")).date()
    stages = get_learning_path(level)["stages"]
    # 每阶段至少约 120 分钟；时间不足时只覆盖前面的阶段，不承诺速成。
    count = min(len(stages), max(1, days * daily_minutes // 120), days)
    selected = stages[:count]
    schedule = []
    for d in range(days):
        index = min(count - 1, d * count // days)
        stage = selected[index]
        review = daily_minutes // 5
        practice = daily_minutes // 2
        schedule.append({"day": d + 1, "date": (start + timedelta(days=d)).isoformat(),
                         "topic": stage["topic"], "learn_minutes": daily_minutes - review - practice,
                         "practice_minutes": practice, "review_minutes": review,
                         "task": stage["deliverable"],
                         "checkpoint": "解释原理、提交运行结果、记录一个问题；后续同主题日迭代实验"})
    return {"days": days, "daily_minutes": daily_minutes, "total_hours": round(days * daily_minutes / 60, 1),
            "covered_stages": count, "remaining_topics": [s["topic"] for s in stages[count:]],
            "note": "这是按时间预算分配的学习建议，不代表掌握保证；同主题连续日用于练习和复盘。",
            "schedule": schedule}


def generate_quiz(topic: str = "综合", count: int = 3) -> dict:
    """从固定题库抽取不含答案的测验，供后续按题号批改。"""
    _integer(count, "count", 1, 10)
    aliases = {"cnn": "CNN", "卷积": "CNN", "反向传播": "梯度", "transformer": "注意力", "过拟合": "训练"}
    topic = aliases.get(topic.lower(), topic)
    pool = BANK if topic in ("综合", "深度学习") else [q for q in BANK if q[1] == topic]
    if not pool:
        raise ValueError("支持的主题：综合、梯度、CNN、训练、张量、注意力")
    return {"topic": topic, "requested_count": count, "actual_count": min(count, len(pool)),
            "questions": [{"id": q[0], "question": q[2], "options": q[3]} for q in pool[:count]],
            "answer_format": "按题号提交，例如 DL01:B, DL02:A；题库不足时返回实际题数。"}


def grade_quiz(answers: str) -> dict:
    """批改题库选择题。answers 格式 DL01:B, DL02:A；只批改用户提交的题。"""
    parts = [p.strip() for p in re.split(r"[,，;；\n]+", answers.strip()) if p.strip()]
    if not parts:
        raise ValueError("请提交答案，例如 DL01:B, DL02:A")
    bank = {q[0]: q for q in BANK}
    results, seen = [], set()
    for part in parts:
        match = re.fullmatch(r"(DL\d{2})\s*[:：=]\s*([A-D])", part.upper())
        if not match or match[1] not in bank:
            raise ValueError(f"无法识别答案：{part}，请使用有效题号和 A/B/C/D")
        qid, answer = match.groups()
        if qid in seen:
            raise ValueError(f"重复题号：{qid}")
        seen.add(qid)
        q = bank[qid]
        results.append({"id": qid, "submitted": answer, "correct_answer": q[4], "correct": answer == q[4],
                        "topic": q[1], "explanation": q[5]})
    correct = sum(r["correct"] for r in results)
    return {"total": len(results), "correct": correct, "score": round(correct / len(results) * 100),
            "weak_topics": sorted({r["topic"] for r in results if not r["correct"]}), "results": results}


FUNCTIONS = {f.__name__: f for f in (get_learning_path, create_study_plan, generate_quiz, grade_quiz)}


def call_tool(name: str, arguments: dict) -> dict:
    if name not in FUNCTIONS:
        return {"error": "未知工具"}
    try:
        return FUNCTIONS[name](**arguments)
    except (ValueError, TypeError, OverflowError) as exc:
        return {"error": str(exc)}


def _schema(name, properties):
    return {"type": "function", "function": {"name": name, "description": FUNCTIONS[name].__doc__,
            "parameters": {"type": "object", "properties": properties, "additionalProperties": False}}}


TOOLS = [
    _schema("get_learning_path", {"level": {"type": "string", "enum": ["零基础", "入门", "进阶"]}}),
    _schema("create_study_plan", {"days": {"type": "integer", "minimum": 1, "maximum": 90},
        "daily_minutes": {"type": "integer", "minimum": 15, "maximum": 480},
        "level": {"type": "string", "enum": ["零基础", "入门", "进阶"]}, "start_date": {"type": "string"}}),
    _schema("generate_quiz", {"topic": {"type": "string"}, "count": {"type": "integer", "minimum": 1, "maximum": 10}}),
    _schema("grade_quiz", {"answers": {"type": "string"}}),
]

SYSTEM_PROMPT = """你是深度学习学习规划助手，帮助用户完成路线→计划→测验→错题复盘。
用用户使用的语言回答。根据意图自主选择工具，不要求每次调用全部工具。
制定计划前确认学习基础、天数和每日时间；缺失时先询问，用户接受默认方案后再生成。
路线、日期、分钟数、题目、分数以工具结果为准；出题时不泄露答案，用户作答后调用 grade_quiz。
只批改内置题号的选择题，缺少答案时追问；不虚构已完成任务或掌握程度。
工具失败时解释原因并请用户修正参数。无法联网查证，不声称检索了实时资料。
范围为深度学习；其他学科明确说明内置路线和题库不支持。回答清晰，优先给可执行的任务。
"""
