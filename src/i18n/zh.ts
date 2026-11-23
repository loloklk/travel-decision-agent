const zh = {
  // Header
  "app.title": "深度学习学习规划助手",
  "app.subtitle": "从学习路线到每日行动，让每一次练习都有反馈",

  // Empty state
  "empty.title": "今天，学会一点新东西",
  "empty.hint": "告诉我你的基础、学习目标和每天可用的时间。我会规划路线、安排练习，并通过测验帮你找到薄弱环节。",
  "empty.features": "学习路线 · 每日计划 · 随堂测验 · 错题复盘",

  // Chat input
  "chat.placeholder": "今天想学什么？说说你的目标，或提交测验答案…",
  "chat.hint": "Enter 发送 · Shift + Enter 换行  /  让练习成为理解的一部分",

  // Preset questions
  "preset.1": "我有 Python 基础，请按入门水平制定14天深度学习计划，每天60分钟。",
  "preset.2": "出3道深度学习综合选择题，先不要告诉我答案。",

  // Tool indicators
  "tool.geocode": "学习路线",
  "tool.malls": "每日计划",
  "tool.brand": "随堂测验",
  "tool.distance": "错题复盘",

  // Status & errors
  "status.error": "⚠️ 请求失败，请检查后端服务是否启动。",
  "status.stopped": "⏹ *已停止生成*",
  "status.backendError": "⚠️ 后端中断请求失败，服务端可能仍在运行。",

  // Debug panel
  "debug.title": "传输流",
  "debug.events": "事件",
  "debug.clear": "清除",
  "debug.empty": "等待 SSE 事件...",
  "debug.emptyHint": "发送消息后，所有原始后端数据将在此处显示。",

  // Conversation sidebar
  "sidebar.label": "会话列表",
  "sidebar.title": "会话",
  "sidebar.newChat": "新建聊天",
  "sidebar.loading": "正在加载会话...",
  "sidebar.loadMore": "加载更多",
  "sidebar.loadingMore": "加载中...",
  "sidebar.emptyTitle": "暂无会话",
  "sidebar.emptyHint": "点击「新建聊天」开始第一段对话。",
  "sidebar.delete": "删除会话",
  "sidebar.deleteConfirm": "确定要永久删除这个会话吗？此操作不可恢复。",

  // Aria labels (button hover/screen-reader)
  "aria.send": "发送",
  "aria.clearHistory": "清除历史",
  "aria.stopGeneration": "停止生成",

  // Language toggle
  "lang.switch": "English",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "一键部署",
  "floatingLink.github": "GitHub",
} as const;

export default zh;
