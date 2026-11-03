import type { EditorController } from "../hooks/use-editor";
import { catalog, labels } from "../lib/library";
export function LibraryPanel({ editor }: { editor: EditorController }) {
  const {
    detail,
    tab,
    setTab,
    query,
    setQuery,
    busy,
    backgroundObjects,
    setBackgroundObjects,
    palette,
    add,
    assemble,
  } = editor;
  return (
    <aside className="left">
      <div className="tabs">
        <button className={tab === "idea" ? "active" : ""} onClick={() => setTab("idea")}>
          По идее
        </button>
        <button className={tab === "objects" ? "active" : ""} onClick={() => setTab("objects")}>
          Объекты
        </button>
      </div>
      <div className="panel-content">
        <h2>{tab === "idea" ? "С чего начнём?" : "Соберите свою сцену"}</h2>
        <p className="muted">
          {tab === "idea"
            ? "Опишите тему иллюстрации — подберём объекты из библиотеки."
            : "Введите названия или добавьте объекты из библиотеки."}
        </p>
        <label htmlFor="query">
          {tab === "idea" ? "Метафора или заголовок" : "Названия объектов"}
        </label>
        <textarea id="query" value={query} onChange={(e) => setQuery(e.target.value)} />
        <label className="background-toggle">
          <input
            type="checkbox"
            checked={backgroundObjects}
            onChange={(e) => setBackgroundObjects(e.target.checked)}
          />{" "}
          Использовать фоновые объекты
        </label>
        <button className="primary full" disabled={busy} onClick={assemble}>
          {busy ? "Собираем…" : "Собрать композицию"}
        </button>
        <div className="divider" />
        <div className="section-title">
          Библиотека <span>10 объектов</span>
        </div>
        <div className="library">
          {Object.entries(labels).map(([key, label]) => {
            const a = catalog.find(
              (a) =>
                a.kind === "component" &&
                a.object === key &&
                a.detail === detail &&
                a.role === "main",
            )!;
            return (
              <button key={key} onClick={() => add(key)} title={`Добавить: ${label}`}>
                <img src={a.url + "?v=palette-2"} alt="" />
                <span>{label}</span>
                <b>+</b>
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
