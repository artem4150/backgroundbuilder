"use client";
import { useState, useRef } from "react";
import { catalog, schemes } from "../lib/library";
import type { Item } from "../lib/types";
import { scaleScene } from "../lib/scene";
import { requestComposition } from "../lib/api";
import { downloadSvg } from "../lib/export-svg";
export function useEditor() {
  const [items, setItems] = useState<Item[]>([
    { id: 1, object: "book", x: 150, y: 200, rotation: 0, role: "background" },
    { id: 2, object: "phone", x: 650, y: 410, rotation: 0, role: "main" },
  ]);
  const [selected, select] = useState<number | null>(null);
  const [detail, setDetail] = useState("L");
  const [scheme, setScheme] = useState("purple");
  const [format, setFormat] = useState("horizontal");
  const [tab, setTab] = useState("idea");
  const [query, setQuery] = useState("Обучение и новые идеи");
  const [status, setStatus] = useState("Готово к работе");
  const [zoom, setZoom] = useState(100);
  const [busy, setBusy] = useState(false);
  const [commonScale, setCommonScale] = useState(1);
  const [backgroundObjects, setBackgroundObjects] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [groupScale, setGroupScale] = useState(100);
  const svg = useRef<SVGSVGElement>(null);
  const drag = useRef<{ id: number; x: number; y: number; ox: number; oy: number } | null>(null);
  const seq = useRef(3);
  const upload = useRef<HTMLInputElement>(null);
  const [w, h] =
    format === "square" ? [1000, 1000] : format === "vertical" ? [750, 1200] : [1200, 750];
  const palette = schemes.find((s) => s.id === scheme)!;
  const current = items.find((i) => i.id === selected);
  function asset(i: Item) {
    return catalog.find(
      (a) =>
        a.kind === "component" && a.object === i.object && a.detail === detail && a.role === i.role,
    )!;
  }
  function objectUrl(i: Item) {
    const url = asset(i).url;
    return (scheme === "purple" ? url : url.replace(".svg", `-${scheme}.svg`)) + "?v=palette-2";
  }
  function dimensions(i: Item) {
    const a = asset(i);
    const factor = (detail === "L" ? 0.55 : 1.1) * commonScale;
    return [
      ("sceneWidth" in a ? (a.sceneWidth ?? +a.width) : +a.width) * factor,
      ("sceneHeight" in a ? (a.sceneHeight ?? +a.height) : +a.height) * factor,
    ];
  }
  function resizeGroup(value: number) {
    if (!items.length) return;
    const ratio = value / groupScale;
    setItems(scaleScene(items, dimensions, ratio));
    setCommonScale((v) => v * ratio);
    setGroupScale(value);
    setStatus("Масштаб всех объектов изменён. Края могут выходить за холст.");
  }
  function removeSelected() {
    setItems((a) => a.filter((i) => i.id !== selected));
    select(null);
    setStatus("Объект удалён");
  }
  function duplicateSelected() {
    if (!current) return;
    const copy = { ...current, id: seq.current++, x: current.x + 35, y: current.y + 35 };
    setItems((a) => [...a, copy]);
    select(copy.id);
    setStatus("Объект продублирован");
  }
  function keyboard(e: React.KeyboardEvent) {
    if ((e.target as HTMLElement).closest("input,textarea,select,button") || busy || exporting)
      return;
    if (e.key === "Escape") {
      select(null);
      return;
    }
    if (!current) return;
    if (e.key === "Delete" || e.key === "Backspace") {
      e.preventDefault();
      removeSelected();
    } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "d") {
      e.preventDefault();
      duplicateSelected();
    } else {
      const step = e.shiftKey ? 10 : 1;
      const delta: Record<string, [number, number]> = {
        ArrowLeft: [-step, 0],
        ArrowRight: [step, 0],
        ArrowUp: [0, -step],
        ArrowDown: [0, step],
      };
      if (delta[e.key]) {
        e.preventDefault();
        update({ x: current.x + delta[e.key][0], y: current.y + delta[e.key][1] });
      }
    }
  }
  function update(values: Partial<Item>) {
    setItems((all) => all.map((i) => (i.id === selected ? { ...i, ...values } : i)));
  }
  function add(object: string) {
    const id = seq.current++;
    setItems((all) => [
      ...all,
      { id, object, x: w * 0.25, y: h * 0.25, rotation: 0, role: "main" },
    ]);
    select(id);
  }
  async function assemble() {
    if (busy) return;
    setBusy(true);
    setStatus("Собираем композицию…");
    try {
      const result = await requestComposition({
        query,
        mode: tab,
        format,
        detail,
        background_objects: backgroundObjects,
        seed: Math.floor(Math.random() * 1000000),
      });
      setItems(result.items.map((i: Omit<Item, "id">) => ({ ...i, id: seq.current++ })));
      setCommonScale(result.commonScale);
      setGroupScale(100);
      select(null);
      setStatus(result.notice || "Композиция собрана");
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Сервис недоступен");
    } finally {
      setBusy(false);
    }
  }
  async function exportSvg() {
    if (exporting || busy) return;
    setExporting(true);
    setStatus("Подготавливаем SVG…");
    try {
      const bg = catalog.find(
        (a) => a.kind === "background" && a.detail === detail && a.scheme === scheme,
      )!;
      const specs = [
        { url: bg.url, x: 0, y: 0, width: w, height: h, angle: 0, id: "background" },
        ...items.map((i) => {
          const [width, height] = dimensions(i);
          return {
            url: objectUrl(i),
            x: i.x,
            y: i.y,
            width,
            height,
            angle: i.rotation,
            id: "object-" + i.id,
          };
        }),
      ];
      await downloadSvg(specs, w, h);
      setStatus("SVG скачан");
    } catch {
      setStatus("Не удалось экспортировать SVG. Попробуйте ещё раз.");
    } finally {
      setExporting(false);
    }
  }
  function pointer(e: React.PointerEvent) {
    const p = svg.current!.createSVGPoint();
    p.x = e.clientX;
    p.y = e.clientY;
    return p.matrixTransform(svg.current!.getScreenCTM()!.inverse());
  }

  return {
    items,
    setItems,
    selected,
    select,
    detail,
    setDetail,
    scheme,
    setScheme,
    format,
    setFormat,
    tab,
    setTab,
    query,
    setQuery,
    status,
    setStatus,
    zoom,
    setZoom,
    busy,
    backgroundObjects,
    setBackgroundObjects,
    exporting,
    groupScale,
    svg,
    drag,
    upload,
    w,
    h,
    palette,
    current,
    asset,
    objectUrl,
    dimensions,
    resizeGroup,
    removeSelected,
    duplicateSelected,
    keyboard,
    update,
    add,
    assemble,
    exportSvg,
    pointer,
  };
}
export type EditorController = ReturnType<typeof useEditor>;
