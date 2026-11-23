const en = {
  // Header
  "app.title": "Deep Learning Study Coach",
  "app.subtitle": "Turn learning goals into daily practice and feedback",

  // Empty state
  "empty.title": "Learn something new today",
  "empty.hint": "Share your experience, goals and daily time budget. Build a roadmap, practice with quizzes and review mistakes.",
  "empty.features": "Roadmap · Daily plan · Quiz · Review",

  // Chat input
  "chat.placeholder": "Type a message...  ⏎ Send · Shift+⏎ Newline",
  "chat.hint": "Plan, practice, and check your understanding",

  // Preset questions
  "preset.1": "我有 Python 基础，请按入门水平制定14天深度学习计划，每天60分钟。",
  "preset.2": "出3道深度学习综合选择题，先不要告诉我答案。",

  // Tool indicators
  "tool.geocode": "Roadmap",
  "tool.malls": "Study plan",
  "tool.brand": "Quiz",
  "tool.distance": "Review",

  // Status & errors
  "status.error": "Request failed. Please check if the backend service is running.",
  "status.stopped": "⏹ *Generation stopped*",
  "status.backendError": "Backend abort request failed. The server may still be running.",

  // Debug panel
  "debug.title": "Trace",
  "debug.events": "events",
  "debug.clear": "Clear",
  "debug.empty": "Waiting for SSE events...",
  "debug.emptyHint": "After sending a message, all raw backend data will be displayed here.",

  // Conversation sidebar
  "sidebar.label": "Conversation list",
  "sidebar.title": "Chats",
  "sidebar.newChat": "New chat",
  "sidebar.loading": "Loading conversations...",
  "sidebar.loadMore": "Load more",
  "sidebar.loadingMore": "Loading...",
  "sidebar.emptyTitle": "No conversations yet",
  "sidebar.emptyHint": "Click \"New chat\" to start your first conversation.",
  "sidebar.delete": "Delete conversation",
  "sidebar.deleteConfirm": "Permanently delete this conversation? This cannot be undone.",

  // Aria labels (button hover/screen-reader)
  "aria.send": "Send",
  "aria.clearHistory": "Clear history",
  "aria.stopGeneration": "Stop generation",

  // Language toggle
  "lang.switch": "中文",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "Deploy",
  "floatingLink.github": "GitHub",
} as const;

export default en;
