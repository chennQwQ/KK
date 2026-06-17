import { requestJson } from "./client";
import { apiRoutes } from "./routes";
import type { ChatRequest, ChatResponse } from "./types";

export interface AskQuestionPayload {
  question: string;
  chatId: string;
  objectId: string;
}

export async function askQuestion({ question, chatId, objectId }: AskQuestionPayload): Promise<ChatResponse> {
  const payload: ChatRequest = {
    question,
    chat_id: chatId,
    object_id: objectId,
  };

  return requestJson<ChatResponse>(apiRoutes.chat, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
