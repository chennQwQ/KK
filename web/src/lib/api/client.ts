import type { ApiRoute } from "./routes";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiRequestError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiRequestError";
  }
}

export async function requestJson<TResponse>(
  route: ApiRoute,
  init: RequestInit = {},
): Promise<TResponse> {
  const headers = new Headers(init.headers);

  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${route}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    throw new ApiRequestError(`API request failed: ${response.status}`, response.status);
  }

  return response.json() as Promise<TResponse>;
}
