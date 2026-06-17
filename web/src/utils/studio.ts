import { historySections, studioObjects } from "@/lib/studio-data";
import type { HistoryItem, StudioObject } from "@/types/studio";

export function findHistoryItem(id: string): HistoryItem | undefined {
  return historySections.flatMap((section) => section.items).find((item) => item.id === id);
}

export function findStudioObject(id: string): StudioObject | undefined {
  return studioObjects.find((item) => item.id === id);
}

export function getObjectQuestionPlaceholder(objectName: string): string {
  return `向 ${objectName} 提问...`;
}

export function getObjectThreads(objectId: string): HistoryItem[] {
  return historySections.flatMap((section) => section.items).filter((item) => item.objectId === objectId);
}
