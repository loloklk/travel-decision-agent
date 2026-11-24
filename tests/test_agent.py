import asyncio
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server


class StudyToolsTests(unittest.TestCase):
    def test_plan_preserves_budget_and_calendar(self):
        plan = server.core.create_study_plan(14, 65, "入门", "2026-12-25")
        self.assertEqual(len(plan["schedule"]), 14)
        self.assertEqual(plan["schedule"][-1]["date"], "2027-01-07")
        for day in plan["schedule"]:
            self.assertEqual(sum(day[k] for k in ("learn_minutes", "practice_minutes", "review_minutes")), 65)
        short = server.core.create_study_plan(1, 15)
        self.assertEqual(short["covered_stages"], 1)
        self.assertTrue(short["remaining_topics"])

    def test_invalid_input_is_reported(self):
        for args in ({"days": 0}, {"days": True}, {"daily_minutes": 3}, {"start_date": "tomorrow"}):
            self.assertIn("error", server.core.call_tool("create_study_plan", args))
        self.assertIn("error", server.core.call_tool("grade_quiz", {"answers": "DL01:B, DL01:A"}))
        self.assertIn("error", server.core.call_tool("grade_quiz", {"answers": "DL99:A"}))

    def test_quiz_does_not_leak_answers_and_grading_is_exact(self):
        quiz = server.core.generate_quiz("CNN", 10)
        self.assertEqual(quiz["actual_count"], 2)
        self.assertTrue(all("answer" not in q for q in quiz["questions"]))
        result = server.core.grade_quiz("DL03:C, DL04:A")
        self.assertEqual(result["score"], 50)
        self.assertEqual(result["weak_topics"], ["CNN"])

    def test_live_model_tool_round_trip(self):
        requests = []

        def respond(request):
            payload = json.loads(request.content)
            requests.append(payload)
            if len(requests) == 1:
                deltas = [
                    {"tool_calls": [{"index": 0, "id": "call_1", "function": {"name": "generate_quiz", "arguments": '{"topic":"CNN",'}}]},
                    {"tool_calls": [{"index": 0, "function": {"arguments": '"count":1}'}}]},
                ]
            else:
                self.assertEqual(payload["messages"][-1]["role"], "tool")
                result = json.loads(payload["messages"][-1]["content"])
                self.assertEqual(result["questions"][0]["id"], "DL03")
                deltas = [{"content": "以下是 CNN 测验。"}]
            text = "".join("data: " + json.dumps({"choices": [{"delta": d}]}) + "\n\n" for d in deltas)
            return httpx.Response(200, text=text + "data: [DONE]\n\n")

        original = httpx.AsyncClient
        def client(**kwargs):
            return original(**kwargs, transport=httpx.MockTransport(respond))

        async def collect():
            return [event async for event in server.live_events([{"role": "user", "content": "出一道 CNN 题"}], threading.Event())]

        with patch.dict(os.environ, {"AI_GATEWAY_API_KEY": "test-only", "AI_GATEWAY_BASE_URL": "https://mock.invalid/v1", "AI_GATEWAY_MODEL": "test"}), patch.object(server.httpx, "AsyncClient", client):
            events = asyncio.run(collect())
        self.assertEqual(len(requests), 2)
        self.assertIn(("tool_called", {"tool": "generate_quiz"}), events)
        self.assertEqual(events[-1], ("text_delta", {"delta": "以下是 CNN 测验。"}))

    def test_model_field_rejects_credentials_before_network_request(self):
        async def collect():
            return [event async for event in server.live_events([], threading.Event())]
        with patch.dict(os.environ, {"AI_GATEWAY_MODEL": "sk-test-only", "AI_GATEWAY_BASE_URL": "https://mock.invalid/v1"}), patch.object(server.httpx, "AsyncClient") as client:
            with self.assertRaisesRegex(ValueError, "应填写模型名称"):
                asyncio.run(collect())
            client.assert_not_called()

    def test_upstream_auth_error_explains_failure_without_echoing_body(self):
        original = httpx.AsyncClient
        def client(**kwargs):
            transport = httpx.MockTransport(lambda request: httpx.Response(401, text="sensitive-upstream-body"))
            return original(**kwargs, transport=transport)
        async def collect():
            return [event async for event in server.live_events([], threading.Event())]
        with patch.dict(os.environ, {"AI_GATEWAY_MODEL": "test-model", "AI_GATEWAY_BASE_URL": "https://mock.invalid/v1", "AI_GATEWAY_API_KEY": "test-only"}), patch.object(server.httpx, "AsyncClient", client):
            with self.assertRaises(ValueError) as raised:
                asyncio.run(collect())
        self.assertIn("HTTP 401", str(raised.exception))
        self.assertIn("Key 无效或已过期", str(raised.exception))
        self.assertNotIn("sensitive-upstream-body", str(raised.exception))


class LocalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db_patch = patch.object(server, "DB", Path(cls.tmp.name) / "test.db")
        cls.db_patch.start()
        cls.env_patch = patch.dict(os.environ, {"DEMO_MODE": "true"})
        cls.env_patch.start()
        cls.app = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=cls.app.serve_forever, daemon=True).start()
        cls.client = httpx.Client(base_url=f"http://127.0.0.1:{cls.app.server_port}", trust_env=False)

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.app.shutdown()
        cls.app.server_close()
        cls.env_patch.stop()
        cls.db_patch.stop()
        cls.tmp.cleanup()

    def test_full_demo_conversation_and_deletion(self):
        self.assertEqual(self.client.get("/health").json()["mode"], "demo")
        cid = "test-demo"
        for message, tool in [("入门14天计划，每天60分钟", "create_study_plan"), ("出3道综合题", "generate_quiz"), ("DL01:B, DL02:A, DL03:C", "grade_quiz")]:
            response = self.client.post("/chat", headers={"makers-conversation-id": cid}, json={"message": message})
            self.assertEqual(response.status_code, 200)
            self.assertIn(tool, response.text)
            self.assertIn("event: done", response.text)
            self.assertNotIn("event: error", response.text)
        self.assertEqual(len(self.client.post("/history", json={"conversation_id": cid}).json()["messages"]), 6)
        self.assertEqual(self.client.post("/conversations", json={}).json()["conversations"][0]["id"], cid)
        self.assertEqual(self.client.post("/delete-conversation", json={"conversation_id": cid}).status_code, 200)
        self.assertEqual(self.client.post("/history", json={"conversation_id": cid}).json()["messages"], [])


if __name__ == "__main__":
    unittest.main()
