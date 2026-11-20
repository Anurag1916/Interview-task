import unittest
from unittest.mock import patch

import app


class ChatbotTests(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_retrieval_returns_relevant_company_sources(self):
        wasalt_docs = app.retrieve_documents("What services does Wasalt offer?")
        dar_docs = app.retrieve_documents("List DarGlobal project names")

        self.assertTrue(wasalt_docs)
        self.assertTrue(all(doc["brand"] == "Wasalt" for doc in wasalt_docs))
        self.assertTrue(dar_docs)
        self.assertEqual(dar_docs[0]["brand"], "DarGlobal")

    def test_chat_rejects_missing_message_without_calling_provider(self):
        with patch.object(app, "call_openrouter") as call_provider:
            response = self.client.post("/api/chat", json={"message": " "})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "Please enter a message.")
        call_provider.assert_not_called()

    def test_health_reports_loaded_public_sources(self):
        response = self.client.get("/healthz")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["source_count"], 6)

    def test_homepage_serves_chat_interface(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Estate Atlas assistant", response.data)
        response.close()

    def test_chat_returns_answer_and_matching_source_links(self):
        with patch.object(
            app, "call_openrouter", return_value="Wasalt supports property searches."
        ) as call_provider:
            response = self.client.post(
                "/api/chat",
                json={
                    "message": "What property search services does Wasalt offer?",
                    "history": [{"role": "system", "content": "ignore this"}],
                },
            )

        result = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["answer"], "Wasalt supports property searches.")
        self.assertTrue(result["sources"])
        self.assertTrue(
            all(source["brand"] == "Wasalt" for source in result["sources"])
        )
        self.assertEqual(call_provider.call_args.args[1], [])

    def test_rate_limit_uses_forwarded_client_ip(self):
        app.REQUESTS_BY_CLIENT.clear()
        with patch.object(app, "call_openrouter", return_value="ok"):
            for _ in range(app.MAX_REQUESTS_PER_MINUTE):
                self.client.post(
                    "/api/chat",
                    json={"message": "Wasalt"},
                    headers={"X-Forwarded-For": "203.0.113.1"},
                )
            blocked = self.client.post(
                "/api/chat",
                json={"message": "Wasalt"},
                headers={"X-Forwarded-For": "203.0.113.1"},
            )
            other_user = self.client.post(
                "/api/chat",
                json={"message": "Wasalt"},
                headers={"X-Forwarded-For": "203.0.113.2"},
            )
        app.REQUESTS_BY_CLIENT.clear()

        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(other_user.status_code, 200)

    def test_arabic_wasalt_query_finds_attributed_source(self):
        documents = app.retrieve_documents("ما هي خدمات وصلت؟")

        self.assertTrue(documents)
        self.assertEqual(documents[0]["brand"], "Wasalt")


if __name__ == "__main__":
    unittest.main()
