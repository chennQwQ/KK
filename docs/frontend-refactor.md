# Frontend Refactor Plan

## Current Status

The repository now contains a Next.js App Router frontend in `web/` based on the selected Product Design direction, now reframed as **RAG Studio**.

RAG Studio is a studio for creating knowledge-backed conversation objects. KK is one object inside the studio, not the product boundary.

Current implementation boundary:

- Only `KK 投研助手` is connected as a real object.
- The object is backed by the existing local files in `data/`.
- Finance, legal, and newly-created objects are roadmap items until object persistence and upload flows exist.
- The frontend fallback data intentionally exposes only the KK object so the UI does not imply unimplemented databases or objects are connected.

Implemented in this slice:

- Product shell with primary navigation.
- Object list with selectable RAG objects.
- Object conversation panel with search and selectable conversations.
- Chat workspace with status metrics, model selector, answer area, feedback actions, and composer.
- Evidence side panel with citation ordering, relevance ordering, source cards, and metadata.
- Module switching from the primary navigation.
- Placeholder pages for undeveloped modules using `开发中...`.
- Responsive shell for desktop, medium-width, and narrow browser windows.
- Fixed viewport application shell: the page itself does not scroll horizontally or vertically.
- Chat thread body owns vertical scrolling; the composer stays pinned to the bottom of the conversation surface.
- Object conversation panel and evidence panel collapse into drawer panels when browser width is constrained.
- Below 1180px, side menus are removed from the normal layout instead of being compressed, preventing overlap and horizontal overflow.
- Container widths now use responsive `clamp()` and flexible grid tracks instead of fixed desktop-only sizing.
- Each object can own multiple conversations.
- A conversation can inherit context from an earlier conversation under the same object.
- API boundary for `POST /chat` through `askQuestion(question, chatId, objectId)`.
- Responsive layout for desktop, tablet, and small screens.

Initial object model:

- `KK 投研助手`: built object for KK-related investment research material.
- `金融研究员`: extensible object for research reports, announcements, and risk events.
- `法律顾问`: template object created by adding law articles, codes, and typical judgments.

Current frontend module status:

- Ready shell: 对象工作台, 新建对象, 对话记录, 知识库.
- Placeholder only: 数据源, 检索策略, 提示词, 评估中心, 模型管理, 设置.

The backend service layer:

- `src/api/app.py`: FastAPI service foundation for the product frontend.
- `web/`: Next.js frontend product shell.

Current frontend structure:

- `src/app`: App Router routes, root layout, global styles, placeholder auth routes, and API route examples.
- `src/components/layout`: RAG Studio shell, navigation, object sidebar, workspace, and module pages.
- `src/components/ui`: reserved for reusable primitive UI components.
- `src/hooks`: client-side state hooks such as `useStudioState`.
- `src/lib`: core data, API clients, and integration boundaries.
- `src/types`: shared TypeScript interfaces.
- `src/utils`: pure helper functions.
- `src/store`: reserved for future global state management.
- `public`: static assets.

## Recommended Product Stack

Target product stack:

- Frontend: Next.js + TypeScript.
- UI: componentized app shell, preferably using a small design system layer.
- Backend: FastAPI service boundary.
- Auth and tenancy: PostgreSQL-backed user, workspace, and membership model.
- Memory persistence: PostgreSQL for durable chat and memory records, Redis for short-lived streaming/task state.
- Vector search: Chroma for local-first stage, Qdrant for production deployment when multi-user indexing and operations matter.
- Graph retrieval: Neo4j for entity relationships, opinions, and concept chains.

## Migration Path

1. Create a Next.js app structure with `app/`, `components/`, `features/`, `lib/api`, and `lib/types`.
2. Port the Research Console into reusable components:
   - `AppShell`
   - `PrimaryNav`
   - `ResearchHistory`
   - `ChatThread`
   - `EvidencePanel`
   - `Composer`
3. Connect `/chat` to FastAPI.
5. Add SSE support through `/chat/stream`.
6. Replace JSON chat history with PostgreSQL.
7. Add knowledge-base upload and status pages.
8. Add virtual conversation objects.
9. Add graph retrieval and evidence fusion.

## Local Frontend Commands

From `web/`:

```powershell
npm.cmd install --legacy-peer-deps
npm.cmd test
npm.cmd run build
npm.cmd run dev
```

PowerShell may block `npm` because `npm.ps1` is disabled by execution policy. Use `npm.cmd` on Windows.

## API Contract Used By Prototype

The current prototype calls:

```http
POST /chat
Content-Type: application/json
```

Payload:

```json
{
  "question": "string",
  "chat_id": "string",
  "object_id": "string"
}
```

Current response:

```json
{
  "answer": "string",
  "object_id": "string",
  "citations": [
    {
      "source": "string",
      "page": "string",
      "quote": "string"
    }
  ]
}
```

The frontend also loads the object catalog from:

```http
GET /objects
```

The UI is intentionally tolerant of a missing API during visual preview. If FastAPI is not running, the UI marks the answer as local preview instead of failing the whole page.
