import { requestJson } from "./client";
import { apiRoutes } from "./routes";
import type { IndexRebuildResponse, KnowledgeBaseStatusResponse, ManifestRegenerateResponse } from "./types";

export async function getKnowledgeBaseStatus(): Promise<KnowledgeBaseStatusResponse> {
  return requestJson<KnowledgeBaseStatusResponse>(apiRoutes.knowledgeBaseStatus);
}

export async function regenerateKnowledgeBaseManifests(): Promise<ManifestRegenerateResponse> {
  return requestJson<ManifestRegenerateResponse>(apiRoutes.knowledgeBaseManifestRegenerate, {
    method: "POST",
  });
}

export async function rebuildKnowledgeBaseIndex(): Promise<IndexRebuildResponse> {
  return requestJson<IndexRebuildResponse>(apiRoutes.knowledgeBaseIndexRebuild, {
    method: "POST",
  });
}
