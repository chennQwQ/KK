import unittest


class ApiSchemaTests(unittest.TestCase):
    def test_schema_models_validate_payloads(self):
        from src.api.schemas import (
            ChatRequest,
            ChatResponse,
            HealthResponse,
            KnowledgeBaseStatusResponse,
        )

        self.assertEqual(ChatRequest(question="你好").question, "你好")
        self.assertIsNone(ChatRequest(question="你好").chat_id)
        self.assertEqual(ChatResponse(answer="回答").answer, "回答")
        self.assertEqual(HealthResponse(status="ok").status, "ok")
        self.assertTrue(KnowledgeBaseStatusResponse(status="ready", has_db=True).has_db)


class ApiRouteTests(unittest.TestCase):
    def test_health_route_returns_ok(self):
        from fastapi.testclient import TestClient
        from src.api.app import create_app

        client = TestClient(create_app())

        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_knowledge_base_status_uses_injected_db_provider(self):
        from fastapi.testclient import TestClient
        from src.api.app import create_app

        client = TestClient(create_app(db_provider=lambda: object()))

        response = client.get("/knowledge-base/status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ready", "has_db": True})

    def test_chat_route_uses_injected_pipeline(self):
        from fastapi.testclient import TestClient
        from src.api.app import create_app

        class FakePipeline:
            def answer(self, db, question, memory):
                self.seen = (db, question, memory)
                return f"answer:{question}"

        pipeline = FakePipeline()
        db = object()
        memory = object()
        client = TestClient(
            create_app(
                db_provider=lambda: db,
                pipeline_provider=lambda: pipeline,
                memory_provider=lambda: memory,
            )
        )

        response = client.post("/chat", json={"question": "问题", "chat_id": "c1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"answer": "answer:问题"})
        self.assertEqual(pipeline.seen, (db, "问题", memory))


if __name__ == "__main__":
    unittest.main()
