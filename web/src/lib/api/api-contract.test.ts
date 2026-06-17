import { apiRoutes } from "./routes";
import type {
  ChatRequest,
  ChatResponse,
  HealthResponse,
  IndexRebuildResponse,
  KnowledgeBaseStatusResponse,
  ManifestRegenerateResponse,
  StudioObjectsResponse,
} from "./types";

const backendRoutes: [
  "/health",
  "/objects",
  "/knowledge-base/status",
  "/knowledge-base/manifests/regenerate",
  "/knowledge-base/index/rebuild",
  "/chat",
] = [
  apiRoutes.health,
  apiRoutes.objects,
  apiRoutes.knowledgeBaseStatus,
  apiRoutes.knowledgeBaseManifestRegenerate,
  apiRoutes.knowledgeBaseIndexRebuild,
  apiRoutes.chat,
];

const chatRequest: ChatRequest = { question: "question", chat_id: "chat-1", object_id: "kk-advisor" };
const chatResponse: ChatResponse = {
  answer: "answer",
  object_id: "kk-advisor",
  citations: [
    {
      source: "qa.pdf",
      document_kind: "forum_post",
      item_id: "qa-p2-floor2",
      author: "kkndme",
      floor: 2,
      page_start: 2,
      page_end: 2,
    },
  ],
};
const healthResponse: HealthResponse = { status: "ok" };
const knowledgeBaseStatusResponse: KnowledgeBaseStatusResponse = {
  status: "needs_rebuild",
  has_db: false,
  object_id: "kk-advisor",
  knowledge_base_name: "KK 本地文档",
  document_count: 3,
  source_files: ["book1.pdf", "book2.pdf", "qa.pdf"],
  manifest_exists: true,
  index_exists: false,
  manifest_current: false,
};
const manifestRegenerateResponse: ManifestRegenerateResponse = {
  generated: [
    {
      source_file: "qa.pdf",
      source_type: "forum_qa",
      manifest_path: "data/processed/forum/qa.manifest.json",
      parse_status: "parsed",
      items: 846,
      pages: 1018,
      chapters: 0,
    },
  ],
};
const indexRebuildResponse: IndexRebuildResponse = {
  status: "rebuilt",
  chunks: 18420,
  elapsed_ms: 120000,
  error: null,
};
const objectsResponse: StudioObjectsResponse = {
  objects: [
    {
      id: "kk-advisor",
      name: "KK Advisor",
      type: "built object",
      domain: "investment research",
      status: "online",
      icon: "K",
      description: "Knowledge-backed conversation object.",
      knowledge_bases: ["KK source posts"],
      documents: 128,
      chunks: "18,420",
      updated_at: "today",
    },
  ],
};

void backendRoutes;
void chatRequest;
void chatResponse;
void healthResponse;
void knowledgeBaseStatusResponse;
void manifestRegenerateResponse;
void indexRebuildResponse;
void objectsResponse;
