import { historySections, studioObjects } from "./studio-data";

if (studioObjects.length !== 1 || studioObjects[0]?.id !== "kk-advisor") {
  throw new Error("Fallback studio data must expose only the real KK object.");
}

const invalidHistoryObjectIds = historySections
  .flatMap((section) => section.items.map((item) => item.objectId))
  .filter((id) => id !== "kk-advisor");

if (invalidHistoryObjectIds.length > 0) {
  throw new Error("Fallback history must not reference demo objects.");
}
