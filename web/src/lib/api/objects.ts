import { requestJson } from "./client";
import { apiRoutes } from "./routes";
import type { ApiStudioObject, StudioObjectsResponse } from "./types";
import type { StudioObject } from "@/types/studio";

export async function getObjects(): Promise<StudioObject[]> {
  const response = await requestJson<StudioObjectsResponse>(apiRoutes.objects);
  return response.objects.map(toStudioObject);
}

function toStudioObject(item: ApiStudioObject): StudioObject {
  return {
    id: item.id,
    name: item.name,
    type: item.type,
    domain: item.domain,
    status: item.status,
    icon: item.icon,
    description: item.description,
    knowledgeBases: item.knowledge_bases,
    documents: item.documents,
    chunks: item.chunks,
    updatedAt: item.updated_at,
  };
}
