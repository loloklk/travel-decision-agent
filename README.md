# 深度学习学习规划助手 · Study Coach Agent

基于 `travel-decision-agent-main` 改造的全栈 Agent，主题已由出行决策改为深度学习辅学。原项目保留在相邻目录。

支持学习路线、每日计划、随堂测验、自动批改和错题复盘。前端为 React + TypeScript；本地后端为 Python，使用 OpenAI 兼容的 Chat Completions 流式工具调用协议。另保留 EdgeOne Makers 的 Python Agents SDK 部署入口。

## 立即运行（Windows，无需 Key）

环境：Node.js 22.12+、Python 3.10+。

在本目录打开 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt
npm.cmd install
npm.cmd run build
Copy-Item .env.example .env
.\.venv\Scripts\python.exe server.py
```

打开 http://127.0.0.1:8000 即可使用。不填 Key 时自动进入演示模式。

之后可用 `powershell -ExecutionPolicy Bypass -File .\start.ps1` 启动，脚本优先使用 `.venv`。若已存在 `.env`，无需重复复制。端口占用时在 `.env` 修改 `PORT`。

开发时，另开一个 PowerShell 运行 `npm.cmd run dev`，访问终端显示的 Vite 地址；后端仍需运行。开发代理默认转发至 8000，如改变后端端口，请同步修改 `vite.config.ts`。

## 后续填写 Key

编辑项目根目录的 `.env`，填这三项：

```dotenv
AI_GATEWAY_API_KEY=在这里填写服务商的Key
AI_GATEWAY_BASE_URL=在这里填写以/v1结尾的OpenAI兼容地址
AI_GATEWAY_MODEL=在这里填写服务商提供的模型ID
DEMO_MODE=false
PORT=8000
```

`BASE_URL` 填基础地址，不要填完整 `/chat/completions` 路径。模型必须支持 Chat Completions 的 `tools` 和流式 `tool_calls`。三项必须来自同一服务商的兼容配置。

保存后重启 Python 后端，再刷新网页，标题旁会显示 `LIVE`。Key 只由后端读取，不进入前端构建，不需要地图 Key、搜索 Key 或其他 Key。不要给 Key 使用 `VITE_` 前缀。

- 无 Key：自动进入 **DEMO**，规则匹配用户意图并调用真实的本地学习工具。
- 有 Key：进入 **LIVE**，模型自主选择工具，后端执行并回传结果，再由模型生成回答；最多 8 轮调用。
- 强制演示：设置 `DEMO_MODE=true`。
- 模型配置错误：明确报错，不会偷偷回退为演示。

## 可以这样体验

1. `我是零基础，给我一份深度学习路线。`
2. `我有 Python 基础，请按入门水平制定14天深度学习计划，每天60分钟。`
3. `出3道深度学习综合选择题，先不要告诉我答案。`
4. `DL01:B, DL02:A, DL03:A` → 得分 67/100，提示复习 CNN，并展示计算解析。

演示模式仅支持中文路线、计划、出题和题号答案格式，不具备自由对话或自动理解上下文的能力。省略条件时，明确使用入门、14 天、每日 60 分钟；日期按上海时区计算。真实模型模式会先询问缺失的计划条件，并可使用历史对话。

## 四个 Agent 工具

| 工具 | 作用 | 输入 |
|---|---|---|
| `get_learning_path` | 查询 7 阶段深度学习路线 | `level`：零基础、入门、进阶 |
| `create_study_plan` | 按时间预算排期，区分学习/练习/复习 | `days` 1～90、`daily_minutes` 15～480、`level`、可选 `start_date` |
| `generate_quiz` | 从内置题库取题，不返回答案 | `topic`、`count` 1～10 |
| `grade_quiz` | 确定性批改，提供解析与薄弱主题 | `answers`，例如 `DL01:B, DL02:A` |

内置 10 道基础选择题，支持综合、梯度、CNN、训练、张量、注意力；题量不足时返回实际数量，不编造补题。题目按固定顺序抽取，不是随机题库。只支持内置题号的客观题批改，不支持任意作业自动评分。

计划以每阶段约 120 分钟作基础预算，不足时只安排前面的阶段并列出剩余主题。连续同主题日用于迭代练习，不保证短期内完成整个课程。路线与题库是项目内置教学数据，无联网检索。

## 文件结构

```text
study-coach-agent/
├── server.py                   # 本地 API、模型工具循环、SSE、SQLite、静态网页
├── start.ps1                   # Windows 启动脚本
├── requirements-local.txt      # 本地 Python 依赖
├── .env.example                # Key 配置模板（无真实凭证）
├── agents/
│   ├── _study_core.py          # 课程、题库、工具实现、JSON schemas 和系统提示词
│   ├── _tools.py               # EdgeOne Agents SDK 工具包装
│   └── chat/                  # EdgeOne 聊天与停止入口
├── cloud-functions/            # EdgeOne 会话相关接口
├── src/                        # 聊天界面、工具状态、会话栏与中英文文本
├── tests/test_agent.py         # 工具、API 和模拟模型回归测试
└── data/study.db               # 首次聊天后自动创建的本地会话数据库（Git 忽略）
```

本地是个人使用模式，只绑定 `127.0.0.1`，没有账号登录。同一后端的所有本地浏览器共享 SQLite 会话列表；不要直接公开为多人网站。学习对话和答案保存在本地数据库；LIVE 模式会把最近最多 40 条对话和工具结果发给你配置的模型服务商。工具中间调用在当前轮用于模型推理，长期仅保存用户消息和助手回复。

## 验证

```powershell
python -m unittest discover -s tests -v
npm.cmd run build
npm.cmd audit
```

测试覆盖时间预算与跨年日期、参数校验、测验隐藏答案、确定性批改、模拟模型的分片工具调用和工具结果回传，以及本地演示聊天/历史/会话/删除接口。无需真实 Key。真实服务商的联网调用需要填写 Key 后验证。

协议参考：[OpenAI Function calling 官方文档](https://developers.openai.com/api/docs/guides/function-calling)。

## 可选：EdgeOne Makers

保留原模板的 `edgeone.json`、`agents/` 和 `cloud-functions/`。部署环境安装根目录 `requirements.txt`，配置上述三项 `AI_GATEWAY_*` 变量，使用平台的 Agents SDK 入口；`server.py` 仅用于本地。

EdgeOne 入口需要真实 Key，不支持本地演示模式，历史会话使用平台 store。本次已验证本地版本与构建，未实际部署 EdgeOne。不要使用旧模板的一键部署链接，它指向原示例项目。

原模板 MIT 许可证保留于 `LICENSE`。

## 知序 UI 更新

采用冰蓝白、海军蓝与天蓝色的学习工作台风格，加入 Pexels 的蓝色桌面笔记本实拍图片、四个可直接执行的快捷任务、可收起的学习指南/工具记录面板，以及移动端会话抽屉。长计划表格在聊天气泡内横向滚动，支持键盘焦点样式和减少动态效果偏好。字体使用本地系统字体，避免额外字体网络请求。

当前网络图片的作者、来源和许可，以及历史生成素材的提示词见 `public/assets/ASSETS.md`。桌面和手机预览见 `preview-ui-v2.jpg` 与 `preview-mobile-v2.jpg`。
