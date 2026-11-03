import type { EditorController } from "../hooks/use-editor";
import { schemes, labels } from "../lib/library";
export function InspectorPanel({ editor }: { editor: EditorController }) {
  const {
    items,
    setItems,
    selected,
    select,
    scheme,
    setScheme,
    setStatus,
    groupScale,
    upload,
    palette,
    current,
    resizeGroup,
    removeSelected,
    duplicateSelected,
    update,
  } = editor;
  return (
    <aside className="right">
      <section>
        <h3>Оформление</h3>
        <label htmlFor="group-scale">
          Масштаб композиции <span>{groupScale}%</span>
        </label>
        <input
          id="group-scale"
          className="group-scale"
          type="range"
          min="60"
          max="180"
          step="5"
          value={groupScale}
          onChange={(e) => resizeGroup(Number(e.target.value))}
          disabled={!items.length}
        />
        <p className="scale-help">Все предметы вместе, относительно фона</p>
        <label>Цветовая схема</label>
        <div className="palettes">
          {schemes.map((s) => (
            <button
              title={s.name}
              aria-label={s.name}
              aria-pressed={scheme === s.id}
              className={scheme === s.id ? "chosen" : ""}
              key={s.id}
              onClick={() => setScheme(s.id)}
            >
              {s.colors.map((c) => (
                <span key={c} style={{ background: c }} />
              ))}
            </button>
          ))}
        </div>
        <p className="muted small">{palette.name} · исходная палитра</p>
        <input
          ref={upload}
          type="file"
          accept="application/json,.json"
          hidden
          onChange={async (e) => {
            const input = e.currentTarget;
            const file = input.files?.[0];
            if (!file) return;
            try {
              if (file.size > 4096) throw Error();
              const p = JSON.parse(await file.text());
              if (
                !p ||
                typeof p !== "object" ||
                Array.isArray(p) ||
                Object.keys(p).some((k) => k !== "scheme") ||
                !schemes.some((s) => s.id === p.scheme)
              )
                throw Error();
              setScheme(p.scheme);
              setStatus("Исходная палитра загружена");
            } catch {
              setStatus(
                "Ожидается JSON до 4 КБ только с полем scheme: purple, peach или turquoise",
              );
            } finally {
              input.value = "";
            }
          }}
        />
        <button className="secondary full" onClick={() => upload.current?.click()}>
          Загрузить палитру
        </button>
      </section>
      <section>
        <h3>{current ? labels[current.object] : "Объект"}</h3>
        {current ? (
          <>
            <label>Состояние</label>
            <div className="tabs">
              <button
                className={current.role === "main" ? "active" : ""}
                onClick={() => update({ role: "main" })}
              >
                Главный
              </button>
              <button
                className={current.role === "background" ? "active" : ""}
                onClick={() => update({ role: "background" })}
              >
                Фоновый
              </button>
            </div>
            <label htmlFor="angle">Поворот</label>
            <div className="angle">
              <input
                id="angle"
                type="number"
                min={-360}
                max={360}
                value={current.rotation}
                onChange={(e) => {
                  const angle = Number(e.target.value);
                  if (Number.isFinite(angle))
                    update({ rotation: Math.max(-360, Math.min(360, angle)) });
                }}
              />
              <span>°</span>
            </div>
            <button className="secondary full" onClick={duplicateSelected}>
              Дублировать
            </button>
            <button className="delete" onClick={removeSelected}>
              Удалить объект
            </button>
          </>
        ) : (
          <p className="muted">Выберите объект на холсте, чтобы изменить его свойства.</p>
        )}
      </section>
      <section className="layers">
        <h3>
          Слои <span>{items.length}</span>
        </h3>
        {[...items].reverse().map((i) => (
          <div className={"layer " + (i.id === selected ? "selected" : "")} key={i.id}>
            <button onClick={() => select(i.id)}>
              {labels[i.object]}
              <small>{i.role === "main" ? "Главный" : "Фоновый"}</small>
            </button>
            <button
              aria-label="На слой выше"
              disabled={items[items.length - 1]?.id === i.id}
              onClick={() =>
                setItems((a) => {
                  const n = [...a],
                    j = n.findIndex((x) => x.id === i.id);
                  if (j < n.length - 1) [n[j], n[j + 1]] = [n[j + 1], n[j]];
                  return n;
                })
              }
            >
              ↑
            </button>
            <button
              aria-label="На слой ниже"
              disabled={items[0]?.id === i.id}
              onClick={() =>
                setItems((a) => {
                  const n = [...a],
                    j = n.findIndex((x) => x.id === i.id);
                  if (j > 0) [n[j], n[j - 1]] = [n[j - 1], n[j]];
                  return n;
                })
              }
            >
              ↓
            </button>
          </div>
        ))}
      </section>
    </aside>
  );
}
