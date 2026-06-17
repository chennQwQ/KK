export const apiRoutes = {
  health: "/health",
  objects: "/objects",
  knowledgeBaseStatus: "/knowledge-base/status",
  knowledgeBaseManifestRegenerate: "/knowledge-base/manifests/regenerate",
  knowledgeBaseIndexRebuild: "/knowledge-base/index/rebuild",
  chat: "/chat",
} as const;

export type ApiRoute = (typeof apiRoutes)[keyof typeof apiRoutes];
