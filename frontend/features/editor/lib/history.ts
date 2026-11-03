import type { Item } from "./types";
export type Snapshot = {
  query: string;
  mode: string;
  format: string;
  detail: string;
  scheme: string;
  backgroundObjects: boolean;
  commonScale: number;
  items: Item[];
};
export type HistoryEntry = { id: string; created_at: string; snapshot: Snapshot };
export async function loadHistory(): Promise<HistoryEntry[]> {
  const r = await fetch("/api/history", { cache: "no-store" });
  if (!r.ok) throw Error("Не удалось загрузить историю");
  return r.json();
}
export async function saveHistory(snapshot: Snapshot): Promise<HistoryEntry> {
  const r = await fetch("/api/history", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(snapshot),
  });
  if (!r.ok) throw Error("Композиция готова, но сохранить её в историю не удалось");
  return r.json();
}

export async function deleteHistory(id: string): Promise<void> {
  const response = await fetch(`/api/history/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!response.ok) throw Error("Не удалось удалить запись. Попробуйте ещё раз.");
}
