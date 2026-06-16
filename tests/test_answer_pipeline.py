import unittest
from unittest.mock import patch

from src.answer_pipeline import AnswerPipeline, RetrievedDocument, collect_sources


class FakeRetriever:
    def invoke(self, question):
        return [
            RetrievedDocument("alpha", {"source": "book1.pdf"}),
            RetrievedDocument("beta", {"source": "book1.pdf"}),
            RetrievedDocument("gamma", {"source": "qa.pdf"}),
        ]


class FakeDb:
    def as_retriever(self, search_kwargs):
        return FakeRetriever()


class FakeMemory:
    def load_memory_variables(self, values):
        return {"chat_history": []}

    def save_context(self, input_values, output_values):
        self.saved = (input_values, output_values)


class AnswerPipelineTests(unittest.TestCase):
    def test_collect_sources_deduplicates_source_file_names(self):
        docs = [
            RetrievedDocument("a", {"source": "C:/tmp/book1.pdf"}),
            RetrievedDocument("b", {"source": "C:/tmp/book1.pdf"}),
            RetrievedDocument("c", {"source": "qa.pdf"}),
        ]
        self.assertEqual(collect_sources(docs), ["book1.pdf", "qa.pdf"])

    def test_missing_api_key_returns_clear_error(self):
        pipeline = AnswerPipeline(api_key=None)
        result = pipeline.answer(FakeDb(), "问题", FakeMemory())
        self.assertIn("缺少 DEEPSEEK_API_KEY", result)

    def test_compatibility_answer_saves_memory_with_fake_llm(self):
        memory = FakeMemory()
        pipeline = AnswerPipeline(api_key="test-key", client_factory=lambda **kwargs: None)

        with patch.object(pipeline, "_generate_text", return_value=["回答"]):
            result = pipeline.answer(FakeDb(), "问题", memory)

        self.assertIn("回答", result)
        self.assertIn("book1.pdf", result)
        self.assertEqual(memory.saved[0], {"input": "问题"})


if __name__ == "__main__":
    unittest.main()
