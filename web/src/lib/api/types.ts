export interface ChatRequest {
  question: string;
  chat_id?: string;
  object_id?: string;
}

export interface ChatCitation {
  source: string;
  page?: string | null;
  quote?: string | null;
  document_kind?: string | null;
  item_id?: string | null;
  author?: string | null;
  floor?: number | null;
  page_start?: number | null;
  page_end?: number | null;
  topic?: string | null;
}

export interface ChatResponse {
  answer: string;
  object_id?: string | null;
  citations: ChatCitation[];
}

export interface HealthResponse {
  status: "ok" | string;
}

export interface KnowledgeBaseStatusResponse {
  status: "ready" | "missing" | string;
  has_db: boolean;
  object_id: string;
  knowledge_base_name: string;
  document_count: number;
  source_files: string[];
  manifest_exists: boolean;
  index_exists: boolean;
  manifest_current: boolean;
}

export interface ManifestRegenerateItem {
  source_file: string;
  source_type: string;
  manifest_path: string;
  parse_status: string;
  items: number;
  pages: number;
  chapters: number;
}

export interface ManifestRegenerateResponse {
  generated: ManifestRegenerateItem[];
}

export interface IndexRebuildResponse {
  status: string;
  chunks: number;
  elapsed_ms: number;
  error?: string | null;
}

export interface ApiStudioObject {
  id: string;
  name: string;
  type: string;
  domain: string;
  status: string;
  icon: string;
  description: string;
  knowledge_bases: string[];
  documents: number;
  chunks: string;
  updated_at: string;
}

export interface StudioObjectsResponse {
  objects: ApiStudioObject[];
}
