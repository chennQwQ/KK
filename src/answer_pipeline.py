import os
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, LLM_MODEL, STYLE_PROMPT


@dataclass(frozen=True)
class RetrievedDocument:
    page_content: str
    metadata: dict[str, Any]


def collect_sources(docs: Iterable[Any]) -> list[str]:
    sources: list[str] = []
    for doc in docs:
        source = getattr(doc, "metadata", {}).get("source")
        if not source:
            continue
        source_name = os.path.basename(source)
        if source_name not in sources:
            sources.append(source_name)
    return sources


def collect_citations(docs: Iterable[Any]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()

    for doc in docs:
        metadata = getattr(doc, "metadata", {})
        source = metadata.get("source")
        if not source:
            continue

        citation = {
            "source": os.path.basename(source),
            "document_kind": metadata.get("document_kind"),
            "item_id": metadata.get("item_id"),
            "author": metadata.get("author"),
            "floor": metadata.get("floor"),
            "page_start": metadata.get("page_start"),
            "page_end": metadata.get("page_end"),
            "topic": metadata.get("topic"),
        }
        citation = {key: value for key, value in citation.items() if value is not None}
        key = (
            citation.get("source"),
            citation.get("item_id"),
            citation.get("page_start"),
            citation.get("page_end"),
            citation.get("floor"),
        )
        if key in seen or _has_more_specific_citation(citations, citation):
            continue

        seen.add(key)
        citations.append(citation)

    return citations


def _has_more_specific_citation(
    citations: list[dict[str, Any]],
    citation: dict[str, Any],
) -> bool:
    if citation.get("item_id") or citation.get("floor"):
        return False

    for existing in citations:
        if existing.get("source") != citation.get("source"):
            continue
        if existing.get("page_start") != citation.get("page_start"):
            continue
        if existing.get("item_id") or existing.get("floor"):
            return True

    return False


class AnswerPipeline:
    def __init__(
        self,
        api_key: str | None = DEEPSEEK_API_KEY,
        base_url: str = DEEPSEEK_BASE_URL,
        model: str = LLM_MODEL,
        client_factory: Callable[..., Any] | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client_factory = client_factory

    def retrieve(self, db: Any, question: str) -> list[Any]:
        retriever = db.as_retriever(search_kwargs={"k": 4})
        return list(retriever.invoke(question))

    def build_messages(self, docs: list[Any], question: str, memory: Any) -> list[dict[str, str]]:
        context = "\n\n".join(getattr(doc, "page_content", "") for doc in docs)
        current_user_message = f"""
【参考内容】
{context}

【问题】
{question}

请直接、简洁地回答。
"""
        messages = [{"role": "system", "content": STYLE_PROMPT}]
        for msg in memory.load_memory_variables({})["chat_history"]:
            role = _message_role(msg)
            if role:
                messages.append({"role": role, "content": msg.content})
        messages.append({"role": "user", "content": current_user_message})
        return messages

    def stream_answer(self, db: Any, question: str, memory: Any) -> Iterable[str]:
        if not self.api_key:
            yield "调用 API 时出错：缺少 DEEPSEEK_API_KEY，请先配置环境变量。"
            return

        docs = self.retrieve(db, question)
        messages = self.build_messages(docs, question, memory)
        full_response = ""
        for content in self._generate_text(messages):
            full_response += content
            yield content

        sources = collect_sources(docs)
        if sources:
            sources_text = "\n\n**参考来源：**\n" + "\n".join(f"- {source}" for source in sources)
            full_response += sources_text
            yield sources_text

        memory.save_context({"input": question}, {"output": full_response})

    def answer(self, db: Any, question: str, memory: Any) -> str:
        return "".join(self.stream_answer(db, question, memory))

    def answer_for_object(self, db: Any, question: str, memory: Any, studio_object: Any) -> dict[str, Any]:
        object_question = _object_question(question, studio_object)

        if not self.api_key:
            return {
                "answer": self.answer(db, object_question, memory),
                "citations": [],
            }

        docs = self.retrieve(db, object_question)
        messages = self.build_messages(docs, object_question, memory)
        answer = "".join(self._generate_text(messages))
        memory.save_context({"input": question}, {"output": answer})

        return {
            "answer": answer,
            "citations": collect_citations(docs),
        }

    def _generate_text(self, messages: list[dict[str, str]]) -> Iterable[str]:
        client_factory = self.client_factory
        if client_factory is None:
            try:
                from openai import OpenAI
            except ImportError:
                yield "调用 API 时出错：缺少 openai Python 包，请先安装项目依赖。"
                return

            client_factory = OpenAI

        try:
            client = client_factory(api_key=self.api_key, base_url=self.base_url)
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as exc:
            yield f"调用 API 时出错：{exc}"


def _message_role(msg: Any) -> str | None:
    message_type = getattr(msg, "type", None)
    if message_type == "human":
        return "user"
    if message_type == "ai":
        return "assistant"

    class_name = msg.__class__.__name__
    if class_name == "HumanMessage":
        return "user"
    if class_name == "AIMessage":
        return "assistant"
    return None


def _object_question(question: str, studio_object: Any) -> str:
    knowledge_bases = getattr(studio_object, "knowledge_bases", None)
    if knowledge_bases is None:
        knowledge_bases = getattr(studio_object, "knowledgeBases", [])

    return "\n".join(
        [
            f"Object ID: {getattr(studio_object, 'id', '')}",
            f"Object name: {getattr(studio_object, 'name', '')}",
            f"Domain: {getattr(studio_object, 'domain', '')}",
            f"Description: {getattr(studio_object, 'description', '')}",
            f"Knowledge bases: {', '.join(knowledge_bases)}",
            f"Question: {question}",
        ]
    )
