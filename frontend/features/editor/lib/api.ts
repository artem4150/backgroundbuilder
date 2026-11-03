import type { Item } from "./types";
export type CompositionRequest = {
  query: string;
  mode: string;
  format: string;
  detail: string;
  background_objects: boolean;
  seed: number;
};
export type CompositionResponse = {
  items: Omit<Item, "id">[];
  commonScale: number;
  notice: string | null;
  source: string;
};
export async function requestComposition(
  request: CompositionRequest,
): Promise<CompositionResponse> {
  const response = await fetch("/api/compose", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (response.status === 429) throw Error("Слишком много запросов. Подождите минуту.");
  if (!response.headers.get("content-type")?.includes("application/json"))
    throw Error("Сервис временно недоступен. Попробуйте ещё раз.");
  const result = await response.json();
  if (!response.ok)
    throw Error(typeof result.detail === "string" ? result.detail : "Проверьте запрос");
  if (
    !Array.isArray(result.items) ||
    !Number.isFinite(result.commonScale) ||
    result.commonScale <= 0
  )
    throw Error("Сервис вернул некорректную композицию. Попробуйте ещё раз.");
  return result;
}
