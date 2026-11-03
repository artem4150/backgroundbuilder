import type { EditorController } from "../hooks/use-editor";

export function EditorHeader({ editor }: { editor: EditorController }) {
  const { busy, exporting, exportSvg } = editor;
  return (
    <header>
      <div className="brand">
        <span className="mark">◒</span> состав
        <span className="subtitle">Конструктор иллюстраций</span>
      </div>
      <button className="primary" disabled={exporting || busy} onClick={exportSvg}>
        {exporting ? "Подготовка…" : "Скачать SVG"} <span>↗</span>
      </button>
    </header>
  );
}
