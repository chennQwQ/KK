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

请直接、简洁地回答：
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
            sources_text = "\n\n**参考来源：**\n" + "\n".join(
                f"- {source}" for source in sources
            )
            full_response += sources_text
            yield sources_text

        memory.save_context({"input": question}, {"output": full_response})

    def answer(self, db: Any, question: str, memory: Any) -> str:
        return "".join(self.stream_answer(db, question, memory))

    def _generate_text(self, messages: list[dict[str, str]]) -> Iterable[str]:
        client_factory = self.client_factory
        if client_factory is None:
            from openai import OpenAI

            client_factory = OpenAI
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
