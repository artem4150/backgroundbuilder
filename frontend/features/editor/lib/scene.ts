import type { Item } from "./types";
/** Scale positions around the group center; callers apply the same ratio to object sizes. */
export function scaleScene(
  items: Item[],
  getDimensions: (item: Item) => number[],
  ratio: number,
): Item[] {
  if (!items.length) return [];
  const boxes = items.map((i) => {
    const [width, height] = getDimensions(i);
    const angle = (i.rotation * Math.PI) / 180;
    const bw = Math.abs(width * Math.cos(angle)) + Math.abs(height * Math.sin(angle));
    const bh = Math.abs(width * Math.sin(angle)) + Math.abs(height * Math.cos(angle));
    return {
      left: i.x + width / 2 - bw / 2,
      top: i.y + height / 2 - bh / 2,
      right: i.x + width / 2 + bw / 2,
      bottom: i.y + height / 2 + bh / 2,
    };
  });
  const cx = (Math.min(...boxes.map((b) => b.left)) + Math.max(...boxes.map((b) => b.right))) / 2;
  const cy = (Math.min(...boxes.map((b) => b.top)) + Math.max(...boxes.map((b) => b.bottom))) / 2;
  return items.map((i) => ({ ...i, x: cx + (i.x - cx) * ratio, y: cy + (i.y - cy) * ratio }));
}
