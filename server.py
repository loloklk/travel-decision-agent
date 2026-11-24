"""Local-only HTTP/SSE server. Run: python server.py (Python 3.10+)."""
import asyncio
import importlib.util
import json
import os
import re
import sqlite3
import threading
import time
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from contextlib import contextmanager

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
# 避免项目 agents/ 与第三方 openai-agents 包同名造成导入冲突。
spec = importlib.util.spec_from_file_location("study_core", ROOT / "agents" / "_study_core.py")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
DB = ROOT / "data" / "study.db"
ACTIVE = {}
LOCK = threading.Lock()


@contextmanager
def connect():
    DB.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        db.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, cid TEXT, role TEXT, content TEXT, timestamp INTEGER)")
        with db:
            yield db
    finally:
        db.close()


def history(cid):
    with connect() as db:
        return [dict(r) for r in db.execute("SELECT id,role,content,timestamp FROM messages WHERE cid=? ORDER BY timestamp,rowid", (cid,))]


def save(cid, role, content, message_id=None):
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?,?,?)", (message_id or str(uuid.uuid4()), cid, role, content, int(time.time() * 1000)))


def mode():
    configured = bool(os.getenv("AI_GATEWAY_API_KEY", "").strip())
    return "demo" if os.getenv("DEMO_MODE", "false").lower() == "true" or not configured else "live"


def demo(message):
    """规则演示模式，不调用模型；默认值均在回复中明示。"""
    if re.search(r"DL\d{2}\s*[:：=]", message, re.I):
        return "grade_quiz", {"answers": message.strip()}
    if any(word in message for word in ("题", "测验", "quiz")):
        topic = next((w for w in ("CNN", "梯度", "训练", "张量", "注意力") if w.lower() in message.lower()), "综合")
        count = re.search(r"(\d+)\s*(?:道|题)", message)
        return "generate_quiz", {"topic": topic, "count": int(count[1]) if count else 3}
    level = "零基础" if "零基础" in message else "进阶" if "进阶" in message else "入门"
    if any(word in message for word in ("计划", "天", "周", "plan")):
        days = re.search(r"(\d+)\s*天", message)
        weeks = re.search(r"(\d+)\s*周", message)
        minutes = re.search(r"(?:每天|每日)\s*(\d+)\s*分钟", message)
        hours = re.search(r"(?:每天|每日)\s*(\d+(?:\.\d+)?)\s*小时", message)
        return "create_study_plan", {"days": int(days[1]) if days else int(weeks[1]) * 7 if weeks else 14,
            "daily_minutes": int(minutes[1]) if minutes else int(float(hours[1]) * 60) if hours else 60, "level": level,
            "start_date": datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()}
    return "get_learning_path", {"level": level}


def render_demo(name, args, data):
    prefix = "**免 Key 演示模式** · 使用内置规则和教学数据，未调用大模型。\n\n"
    if "error" in data:
        return prefix + data["error"]
    if name == "get_learning_path":
        return prefix + f"当前按「{args['level']}」展示深度学习路线（未说明时默认入门）：\n\n" + "\n\n".join(
            f"**{s['stage']}. {s['topic']}**\n{s['knowledge']}\n\n验收：{s['deliverable']}" for s in data["stages"]) + "\n\n试试：我有 Python 基础，制定14天计划，每天60分钟。也可以发送“出3道综合题”。"
    if name == "create_study_plan":
        text = prefix + f"按「{args['level']}」、{data['days']} 天、每天 {data['daily_minutes']} 分钟安排，共 {data['total_hours']} 小时。未指定时默认入门、14天、60分钟，从今天开始。\n\n"
        text += "| 日期 | 主题 | 学习/练习/复习（分钟） | 当日任务 |\n|---|---|---|---|\n"
        text += "\n".join(f"| {s['date']} | {s['topic']} | {s['learn_minutes']}/{s['practice_minutes']}/{s['review_minutes']} | {s['task']} |" for s in data["schedule"])
        return text + "\n\n" + data["note"] + ("\n\n后续主题：" + "、".join(data["remaining_topics"]) if data["remaining_topics"] else "")
    if name == "generate_quiz":
        return prefix + f"**{data['topic']}测验 · {data['actual_count']} 题**（请求 {data['requested_count']} 题，受内置题库数量限制）\n\n" + "\n\n".join(
            f"**{q['id']} · {q['question']}**\n\n" + "\n\n".join(q["options"]) for q in data["questions"]) + "\n\n" + data["answer_format"]
    return prefix + f"**本次提交得分：{data['score']} / 100** · {data['correct']}/{data['total']} 题正确\n\n" + "\n\n".join(
        f"{'✅' if r['correct'] else '❌'} **{r['id']}**：你的答案 {r['submitted']}；正确答案 {r['correct_answer']}。{r['explanation']}" for r in data["results"]) + "\n\n建议复习：" + ("、".join(data["weak_topics"]) or "本次全部正确，可继续其他主题")


async def live_events(messages, cancelled):
    """OpenAI-compatible Chat Completions: stream tokens, execute tools, feed results back."""
    base = os.getenv("AI_GATEWAY_BASE_URL", "").strip().rstrip("/")
    model = os.getenv("AI_GATEWAY_MODEL", "").strip()
    if not base or not model:
        raise ValueError("请在 .env 填写 AI_GATEWAY_BASE_URL 和 AI_GATEWAY_MODEL，或设置 DEMO_MODE=true")
    if model.startswith(("sk-", "Bearer ", "ghp_")):
        raise ValueError("AI_GATEWAY_MODEL 应填写模型名称，不是 API Key。EdgeOne 内置模型可填写 @makers/deepseek-v4-flash")
    headers = {"Authorization": "Bearer " + os.environ["AI_GATEWAY_API_KEY"].strip()}
    prompt = core.SYSTEM_PROMPT + "\n当前上海日期：" + datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    conversation = [{"role": "system", "content": prompt}, *messages]
    async with httpx.AsyncClient(timeout=httpx.Timeout(90, connect=15)) as client:
        for _ in range(8):
            if cancelled.is_set():
                return
            calls, content = {}, ""
            async with client.stream("POST", base + "/chat/completions", headers=headers,
                    json={"model": model, "messages": conversation, "tools": core.TOOLS, "stream": True}) as response:
                if response.status_code != 200:
                    hints = {
                        400: "请检查模型名称、参数，以及模型是否支持工具调用",
                        401: "Key 无效或已过期，请确认 Key 来自当前接口地址对应的服务商",
                        403: "当前 Key 没有此模型的访问权限，请检查模型开通状态",
                        404: "接口地址或模型不存在；Base URL 应填写基础地址，不含 /chat/completions",
                        429: "请求过于频繁或额度不足，请检查服务商控制台的用量与配额",
                    }
                    raise ValueError(f"模型服务返回 HTTP {response.status_code}：" + hints.get(response.status_code, "模型服务暂时不可用，请稍后再试"))
                async for line in response.aiter_lines():
                    if cancelled.is_set():
                        return
                    if not line.startswith("data:") or line[5:].strip() == "[DONE]":
                        continue
                    event = json.loads(line[5:])
                    if event.get("error"):
                        raise ValueError("模型服务在流中返回错误，请检查模型及额度")
                    choices = event.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    if delta.get("content"):
                        content += delta["content"]
                        yield "text_delta", {"delta": delta["content"]}
                    for item in delta.get("tool_calls") or []:
                        call = calls.setdefault(item["index"], {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                        if item.get("id"):
                            call["id"] = item["id"]
                        for field in ("name", "arguments"):
                            call["function"][field] += (item.get("function") or {}).get(field) or ""
            if not calls:
                if not content:
                    raise ValueError("模型未返回文本或工具调用，请检查模型兼容性")
                return
            ordered = [calls[i] for i in sorted(calls)]
            conversation.append({"role": "assistant", "content": content or None, "tool_calls": ordered})
            for call in ordered:
                name = call["function"]["name"]
                yield "tool_called", {"tool": name}
                try:
                    arguments = json.loads(call["function"]["arguments"])
                    if not isinstance(arguments, dict):
                        raise ValueError("工具参数须为对象")
                    result = core.call_tool(name, arguments)
                except (ValueError, TypeError):
                    result = {"error": "工具参数不是有效 JSON 对象"}
                conversation.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result, ensure_ascii=False)})
        raise ValueError("已达到 8 轮工具调用上限，请简化请求后重试")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass  # 不把对话内容或凭证写进日志。

    def reply(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            return self.reply({"ok": True, "mode": mode()})
        # npm run build 后可直接用 Python 服务访问完整网站。
        target = (ROOT / "dist" / self.path.split("?")[0].lstrip("/")).resolve()
        dist = (ROOT / "dist").resolve()
        if not target.is_relative_to(dist):
            return self.reply({"error": "无效路径"}, 403)
        if not target.is_file():
            target = dist / "index.html"
        if not target.is_file():
            return self.reply({"message": "后端已启动，请运行 npm run dev 或先 npm run build"})
        import mimetypes
        payload = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                return self.reply({"error": "请求大小须为 1～65536 字节"}, 400)
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError()
        except (ValueError, TypeError):
            return self.reply({"error": "需要 JSON 对象"}, 400)
        cid = body.get("conversation_id") or self.headers.get("makers-conversation-id")
        if self.path == "/conversations":
            with connect() as db:
                rows = db.execute("SELECT cid, MIN(timestamp) createdAt, MAX(timestamp) lastMessageAt, COUNT(*) messageCount FROM messages GROUP BY cid ORDER BY lastMessageAt DESC,cid").fetchall()
            entries = []
            for row in rows:
                msgs = history(row["cid"])
                entries.append({"id": row["cid"], "title": msgs[0]["content"][:45], "preview": msgs[-1]["content"][:80],
                    "createdAt": row["createdAt"], "lastMessageAt": row["lastMessageAt"], "messageCount": row["messageCount"]})
            try:
                limit = max(1, min(int(body.get("limit", 20)), 100))
                offset = max(0, int(body.get("after") or 0))
            except (TypeError, ValueError):
                return self.reply({"error": "无效分页参数"}, 400)
            return self.reply({"conversations": entries[offset:offset + limit],
                "nextCursor": str(offset + limit) if len(entries) > offset + limit else None})
        if not isinstance(cid, str) or not cid.strip() or len(cid) > 200:
            return self.reply({"error": "需要有效 conversation_id"}, 400)
        if self.path == "/history":
            return self.reply({"messages": history(cid)})
        if self.path in ("/delete-conversation", "/clear-history"):
            with LOCK:
                if cid in ACTIVE:
                    return self.reply({"error": "请先停止当前生成"}, 409)
            with connect() as db:
                db.execute("DELETE FROM messages WHERE cid=?", (cid,))
            return self.reply({"ok": True})
        if self.path in ("/stop", "/chat/stop"):
            with LOCK:
                signal = ACTIVE.get(cid)
                if signal:
                    signal.set()
            return self.reply({"ok": True})
        if self.path != "/chat":
            return self.reply({"error": "未知接口"}, 404)
        message = body.get("message")
        if not isinstance(message, str) or not message.strip() or len(message) > 12000:
            return self.reply({"error": "message 需要 1～12000 字符"}, 400)
        signal = threading.Event()
        with LOCK:
            if cid in ACTIVE:
                return self.reply({"error": "本会话仍在生成中"}, 409)
            ACTIVE[cid] = signal
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
        output = []

        def emit(event, data):
            if event == "text_delta":
                output.append(data["delta"])
            payload = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
            self.wfile.write(payload.encode("utf-8"))
            self.wfile.flush()

        async def run():
            iterator = live_events([{"role": m["role"], "content": m["content"]} for m in history(cid)[-40:]], signal)
            try:
                while not signal.is_set():
                    pending = asyncio.create_task(anext(iterator))
                    while not pending.done() and not signal.is_set():
                        await asyncio.wait({pending}, timeout=0.1)
                    if signal.is_set():
                        pending.cancel()
                        await asyncio.gather(pending, return_exceptions=True)
                        break
                    try:
                        event, data = pending.result()
                    except StopAsyncIteration:
                        break
                    emit(event, data)
            finally:
                await iterator.aclose()

        try:
            save(cid, "user", message)
            if mode() == "demo":
                name, args = demo(message)
                emit("tool_called", {"tool": name})
                text = render_demo(name, args, core.call_tool(name, args))
                for offset in range(0, len(text), 80):
                    if signal.is_set():
                        break
                    emit("text_delta", {"delta": text[offset:offset + 80]})
            else:
                asyncio.run(run())
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            signal.set()
        except Exception as exc:
            # 不回传第三方异常文本，以免包含请求 URL、密钥或原始响应。
            safe = str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else "模型连接失败，请检查网络、接口配置和服务商的流式工具调用支持"
            try:
                emit("error", {"message": safe})
            except OSError:
                pass
        finally:
            if output:
                save(cid, "assistant", "".join(output) + ("\n\n*已停止生成*" if signal.is_set() else ""))
            with LOCK:
                ACTIVE.pop(cid, None)
            try:
                emit("done", {"stopped": signal.is_set()})
            except OSError:
                pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Study Coach: http://127.0.0.1:{port} · {mode()} mode", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
