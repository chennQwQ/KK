# RAG Studio Object Model Design

## Decision

Use **RAG Studio** as the product name.

The product is no longer framed as a single KK-specific RAG app. It is a studio for creating and operating knowledge-backed conversation objects.

## Product Model

- Product: RAG Studio.
- Workspace: a user's product workspace.
- Object: a virtual conversation object built from knowledge bases, prompts, memory, retrieval settings, and model settings.
- Knowledge Base: versioned source material attached to one or more objects.
- Conversation: chat history scoped to one object.
- Evidence: retrieved source snippets used by an answer.

## Initial Objects

The first object remains **KK 投研助手**. It is an already built object using KK-related documents and investment research material.

The interface should also show that new objects can be created from knowledge bases. Example: **法律顾问** can be created by adding:

- 现行法条
- 基础法典
- 典型判决案例

## UI Changes

- Brand: `RAG Studio`.
- Subtitle: `Object Console`.
- Navigation:
  - 对象工作台
  - 新建对象
  - 对话记录
  - 知识库
  - 数据源
  - 检索策略
  - 提示词
  - 评估中心
  - 设置
- Left panel: object list plus object conversation history.
- Top status bar: current object, domain, document count, chunk count, index update, model selector.
- Main thread: answer identity is the selected object, not a fixed KK assistant.
- Evidence panel: remains object-scoped.

## API Direction

The frontend should send `object_id` with chat requests:

```json
{
  "question": "string",
  "chat_id": "string",
  "object_id": "string"
}
```

Backend persistence should eventually scope conversations, memory, citations, and retrieval settings by object.

