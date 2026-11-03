export function LoadingOverlay({ busy, exporting }: { busy: boolean; exporting: boolean }) {
  return (
    <>
      {(busy || exporting) && (
        <div className="loading-overlay" role="status" aria-live="polite">
          <div className="loading-card">
            <div className="assembly-loader" aria-hidden="true">
              <span />
              <span />
              <span />
            </div>
            <strong>{busy ? "Собираем композицию" : "Готовим SVG"}</strong>
            <p>
              {busy
                ? "Подбираем объекты и находим им место"
                : "Сохраняем векторные объекты и цвета"}
            </p>
            <span className="loading-caption">
              {busy ? "Это может занять несколько секунд" : "Файл скоро будет готов"}
            </span>
          </div>
        </div>
      )}
    </>
  );
}
