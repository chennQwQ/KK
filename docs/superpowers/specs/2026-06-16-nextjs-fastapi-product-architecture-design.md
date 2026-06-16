# Next.js + FastAPI 产品架构设计

日期：2026-06-16

## 目标

把当前 KK RAG 原型升级成一个支持登录的 Web 产品，并且以后可以持续加入新模块，而不是把所有新想法都塞进聊天页面。

确认采用双服务架构：

- Next.js 作为主产品应用。
- FastAPI 作为 Python RAG 服务。
- PostgreSQL 存储产品数据。
- Redis 加 worker 处理入库、索引、图谱抽取等长任务。
- Chroma 作为第一阶段向量库，后续保留切换到 Qdrant 或 pgvector 的空间。
- Neo4j 作为知识图谱存储，用于关系型检索。

## 第一阶段不做

- 不做计费、团队空间、公开模块市场。
- 不一次性迁移所有本地 JSON 聊天历史，除非新聊天链路需要。
- 不在入库和检索接口稳定前替换 Chroma。
- 不让 Neo4j 成为基础聊天的必需依赖；图谱检索失败时应自动降级为纯向量检索。

## 推荐技术栈

主应用：

- Next.js + TypeScript + App Router。
- Tailwind CSS + shadcn/ui。
- 认证使用 Clerk 或 Auth.js。默认建议 Clerk，开发更快；如果想减少托管服务依赖，再选 Auth.js。
- PostgreSQL 存用户、聊天、消息、知识库、文档、任务和模块配置。
- ORM 使用 Prisma 或 Drizzle。默认建议 Prisma，schema 和迁移更直观，适合快速迭代。

RAG 服务：

- FastAPI。
- 现有 Python RAG 代码重构到清晰的模块接口后复用。
- 使用 Server-Sent Events 输出流式回答。
- 入库和图谱抽取交给后台任务。

后台任务：

- Redis 作为任务队列和任务状态缓存。
- Celery 或 RQ。默认建议先用 RQ，因为第一阶段任务模型简单，运维负担更轻。

检索：

- Chroma 作为第一阶段向量检索 adapter。
- Neo4j 作为可选图谱检索 adapter。
- 混合检索模块负责合并向量片段和图谱事实，再交给回答模块。

## 产品模块

产品要按模块组织，而不是围绕一个巨大的聊天页堆功能。

- `chat`：会话、流式回答、引用来源、重新生成、导出。
- `knowledge-base`：上传文档、入库状态、重建索引、文档元数据。
- `retrieval`：向量搜索、原文搜索、混合检索调试。
- `graph`：实体关系浏览、图谱抽取状态。
- `prompts`：角色、人设、回答风格、prompt 版本。
- `evaluation`：固定问题集、期望来源、回答质量检查。
- `reports`：把聊天或研究过程整理成报告。
- `admin`：模型设置、provider key、系统健康、任务队列。

每个模块应拥有自己的页面、UI、产品数据和后端接口。共享代码只有在至少两个真实调用方出现后再抽出来。

## 数据模型

第一阶段 PostgreSQL 实体：

- `User`：登录用户。
- `KnowledgeBase`：用户拥有或共享的知识库。
- `Document`：上传文件元数据、来源类型、checksum、入库状态。
- `IngestionManifest`：文档哈希、解析器版本、chunk 参数、embedding 模型、创建时间。
- `Chat`：标题、所有者、关联知识库、创建时间。
- `Message`：角色、内容、模型信息、token 用量、创建时间。
- `Citation`：消息、文档、页码、chunk id、来源文本预览。
- `Job`：入库、重建、图谱抽取任务的状态、进度和错误摘要。
- `ModuleSetting`：用户级或知识库级配置。

第一阶段文件可以继续存在本地磁盘，但文件元数据和入库状态要进入 PostgreSQL。

## 后端接口

FastAPI 对外暴露产品语义接口，不把 Chroma、Neo4j、LangChain 细节泄露给前端。

聊天：

- `POST /chat/stream`
- `GET /chats`
- `GET /chats/{chat_id}`
- `POST /chats/{chat_id}/messages`

知识库：

- `POST /knowledge-bases`
- `GET /knowledge-bases`
- `POST /knowledge-bases/{id}/documents`
- `POST /knowledge-bases/{id}/rebuild`
- `GET /knowledge-bases/{id}/status`

检索：

- `POST /retrieval/search`
- `POST /retrieval/debug`

任务：

- `GET /jobs/{job_id}`
- `GET /jobs`

FastAPI 内部使用这些深模块：

- `IngestionModule`：解析、哈希、切分、manifest、重建计划。
- `RetrievalModule`：向量 adapter、图谱 adapter、重排、证据组装。
- `AnswerModule`：prompt、memory、流式 LLM 调用、引用来源。
- `ChatModule`：会话和消息持久化。
- `JobModule`：入队、进度、重试、错误报告。

## 请求流程

聊天流程：

1. 用户在 Next.js 里发送消息。
2. Next.js 校验登录态，并带上用户和会话上下文调用 FastAPI。
3. FastAPI 加载聊天、知识库和模块配置。
4. `RetrievalModule` 收集向量片段和可选图谱事实。
5. `AnswerModule` 流式输出 token 和引用来源元数据。
6. Next.js 渲染流式回答，并保存最终消息状态。

入库流程：

1. 用户在 Next.js 上传文档。
2. Next.js 把文件或已上传文件引用传给 FastAPI。
3. FastAPI 创建 `Job` 并立即返回。
4. worker 解析文件、计算 checksum、比较 manifest、切分内容、更新 Chroma，并按需安排图谱抽取。
5. UI 轮询或订阅任务状态。

## 错误处理

- 缺少 LLM key 时，回答生成应明确提示配置错误。
- Chroma 故障时，应标记检索不可用，但产品外壳不能崩。
- Neo4j 故障时，应关闭图谱证据，继续纯向量聊天。
- 入库失败时，要保留失败任务、源文件元数据和错误摘要。
- 流式回答失败时，如果已经输出 token，则保存部分 assistant 消息并显示失败状态。

## 测试策略

Python：

- 单元测试覆盖聊天历史迁移、文档哈希、manifest 比较、来源去重、缺少 API key。
- FastAPI 集成测试使用 fake retrieval 和 fake LLM adapter。
- 流式响应格式做 contract test。

Next.js：

- 组件测试覆盖聊天流式渲染、来源面板、上传状态、任务状态。
- API client 测试覆盖带登录态调用 FastAPI。
- E2E 覆盖登录、上传文档、重建索引、提问、查看引用来源。

检索质量：

- 为 KK 语料保存一组固定问题。
- 检查期望引用文档，以及证据不足时是否拒绝编造。

## 第一阶段范围

第一阶段目标是建立产品底座，而不是一次做完全部未来模块。

交付内容：

- FastAPI 服务化封装现有 RAG 代码。
- 入库 manifest，记录文档 checksum、chunk 参数、embedding 模型和入库时间。
- 流式回答接口。
- PostgreSQL schema：用户、知识库、文档、聊天、消息、引用、任务。
- Next.js 登录产品壳，包含聊天页、知识库页、索引状态页。
- 基础文档上传和重建流程。
- 覆盖入库 manifest、流式回答、聊天持久化的测试。

## 第二阶段范围

- 向量 + Neo4j 混合检索。
- 知识图谱浏览页。
- prompt 和角色管理。
- 问答评测问题集。
- 报告导出。
- 团队和共享知识库。

## 待定但有默认值的决策

- 认证：默认 Clerk；如果需要自托管优先，再改 Auth.js。
- ORM：默认 Prisma；如果以后需要更轻的 SQL 抽象，再考虑 Drizzle。
- worker：默认 RQ；任务复杂后再考虑 Celery。
- 文件存储：第一阶段本地磁盘；后续迁移对象存储。
