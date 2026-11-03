import type { EditorController } from "../hooks/use-editor";
import { catalog, labels } from "../lib/library";
export function CanvasPanel({ editor }: { editor: EditorController }) {
  const {
    items,
    setItems,
    selected,
    select,
    detail,
    setDetail,
    scheme,
    format,
    setFormat,
    status,
    setStatus,
    zoom,
    setZoom,
    svg,
    drag,
    w,
    h,
    current,
    objectUrl,
    dimensions,
    pointer,
  } = editor;
  return (
    <section className="stage">
      <div className="stage-toolbar">
        <select
          aria-label="Формат"
          value={format}
          onChange={(e) => {
            setFormat(e.target.value);
            setStatus("Формат изменён. Нажмите «Собрать», чтобы адаптировать расположение.");
          }}
        >
          <option value="horizontal">Горизонтальный</option>
          <option value="square">Квадратный</option>
          <option value="vertical">Вертикальный</option>
        </select>
        <span className="dimensions">
          {w} × {h}
        </span>
        <div className="detail">
          <span>Детализация</span>
          {["S", "L"].map((s) => (
            <button key={s} className={detail === s ? "active" : ""} onClick={() => setDetail(s)}>
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="canvas-area">
        <svg
          ref={svg}
          tabIndex={0}
          role="application"
          aria-label="Холст композиции. Стрелки — перемещение, Delete — удаление, Escape — снять выделение."
          viewBox={`0 0 ${w} ${h}`}
          style={
            {
              aspectRatio: `${w}/${h}`,
              "--canvas-ratio": w / h,
              "--canvas-zoom": zoom / 100,
            } as React.CSSProperties
          }
          onPointerDown={() => select(null)}
          onPointerMove={(e) => {
            if (drag.current) {
              const p = pointer(e),
                d = drag.current;
              setItems((all) =>
                all.map((i) =>
                  i.id === d.id ? { ...i, x: d.ox + p.x - d.x, y: d.oy + p.y - d.y } : i,
                ),
              );
            }
          }}
          onPointerUp={() => {
            drag.current = null;
          }}
          onPointerCancel={() => {
            drag.current = null;
          }}
          onLostPointerCapture={() => {
            drag.current = null;
          }}
        >
          <image
            href={
              catalog.find(
                (a) => a.kind === "background" && a.detail === detail && a.scheme === scheme,
              )!.url
            }
            width={w}
            height={h}
            preserveAspectRatio="none"
          />
          {items.map((i) => {
            const [width, height] = dimensions(i);
            return (
              <g
                key={i.id}
                data-object-id={i.id}
                aria-label={labels[i.object]}
                transform={`translate(${i.x} ${i.y}) rotate(${i.rotation} ${width / 2} ${height / 2})`}
                onPointerDown={(e) => {
                  e.stopPropagation();
                  select(i.id);
                  const p = pointer(e);
                  drag.current = { id: i.id, x: p.x, y: p.y, ox: i.x, oy: i.y };
                  svg.current!.focus();
                  svg.current!.setPointerCapture(e.pointerId);
                }}
              >
                <image href={objectUrl(i)} width={width} height={height} />
                {selected === i.id && (
                  <rect
                    x={-8}
                    y={-8}
                    width={width + 16}
                    height={height + 16}
                    fill="none"
                    stroke="#6852c5"
                    strokeWidth={2}
                    strokeDasharray="6 4"
                  />
                )}
              </g>
            );
          })}
        </svg>
      </div>
      <footer>
        <span role="status">{status}</span>
        <div>
          <button aria-label="Уменьшить" onClick={() => setZoom((z) => Math.max(40, z - 10))}>
            −
          </button>
          <span>{zoom}%</span>
          <button aria-label="Увеличить" onClick={() => setZoom((z) => Math.min(150, z + 10))}>
            +
          </button>
          <button onClick={() => setZoom(100)}>Вписать</button>
        </div>
      </footer>
    </section>
  );
}
