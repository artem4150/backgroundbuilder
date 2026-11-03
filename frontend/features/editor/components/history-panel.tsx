import type { EditorController } from "../hooks/use-editor";
import type { Snapshot } from "../lib/history";
import { catalog, schemes } from "../lib/library";
function Preview({ scene }: { scene: Snapshot }) {
  const [w, h] =
    scene.format === "square"
      ? [1000, 1000]
      : scene.format === "vertical"
        ? [750, 1200]
        : [1200, 750];
  const palette = schemes.find((p) => p.id === scene.scheme)!;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} aria-hidden="true">
      <rect width={w} height={h} fill={palette.colors[0]} />
      {scene.items.map((i) => {
        const a = catalog.find(
          (a) =>
            a.kind === "component" &&
            a.object === i.object &&
            a.detail === scene.detail &&
            a.role === i.role,
        )!;
        const factor = (scene.detail === "L" ? 0.55 : 1.1) * scene.commonScale;
        const width = (a.sceneWidth ?? +a.width) * factor,
          height = (a.sceneHeight ?? +a.height) * factor;
        const url =
          (scene.scheme === "purple" ? a.url : a.url.replace(".svg", `-${scene.scheme}.svg`)) +
          "?v=palette-2";
        return (
          <image
            key={i.id}
            href={url}
            width={width}
            height={height}
            transform={`translate(${i.x} ${i.y}) rotate(${i.rotation} ${width / 2} ${height / 2})`}
          />
        );
      })}
    </svg>
  );
}
export function HistoryPanel({ editor }: { editor: EditorController }) {
  const {
    historyLoading,
    historyError,
    history,
    restoreHistory,
    reloadHistory,
    busy,
    exporting,
    removeHistory,
    deletingHistory,
  } = editor;
  return (
    <section className="history-panel" aria-label="История генераций">
      <h3>
        История <span>{history.length}</span>
      </h3>
      {historyLoading ? (
        <p className="muted" role="status">
          Загружаем…
        </p>
      ) : historyError ? (
        <div>
          <p className="muted" role="alert">
            {historyError}
          </p>
          <button className="secondary full" onClick={reloadHistory}>
            Повторить
          </button>
        </div>
      ) : history.length === 0 ? (
        <p className="muted history-empty">Здесь появятся ваши генерации</p>
      ) : (
        <div className="history-list">
          {history.map((entry) => (
            <article key={entry.id} className="history-card">
              <button
                className="history-entry"
                disabled={busy || exporting}
                onClick={() => restoreHistory(entry)}
                title="Восстановить эту композицию"
              >
                <Preview scene={entry.snapshot} />
                <span>
                  <strong>{entry.snapshot.query}</strong>
                  <small>
                    {new Date(entry.created_at).toLocaleString("ru-RU", {
                      day: "2-digit",
                      month: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}{" "}
                    · {entry.snapshot.detail}
                  </small>
                </span>
              </button>
              <button
                className="history-delete"
                aria-label={`Удалить из истории: ${entry.snapshot.query}`}
                title="Удалить из истории"
                disabled={busy || exporting || deletingHistory !== null}
                onClick={() => removeHistory(entry.id)}
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  aria-hidden="true"
                >
                  <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v5M14 11v5" />
                </svg>
              </button>
            </article>
          ))}
        </div>
      )}
      <p className="history-note">
        Нажмите на превью, чтобы восстановить. Сохраняются результаты генерации.
      </p>
    </section>
  );
}
