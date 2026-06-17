import { requestJson } from "./client";
import { apiRoutes } from "./routes";
import type { HealthResponse } from "./types";

export async function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>(apiRoutes.health);
}
