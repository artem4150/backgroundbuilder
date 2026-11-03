# Структура проекта

- `frontend/` — Next.js, компоненты редактора, модель сцены, экспорт и стили. Подробности: frontend/README.md.
- `backend/` — FastAPI, доменная компоновка, подбор, адаптеры Gemini/MinIO. Подробности: backend/README.md.
- `infra/` — Nginx, сборка MinIO, ручное продление сертификата.
- `tools/` — поддерживаемая подготовка ассетов; prepare_palettes.py читает оригиналы и единый каталог палитр.
- `audit/` — отчёты спринтов, результаты визуальных проверок и разовые миграции. Это не код приложения, в Docker-контекст не включается.
- `archive/bootstrap/` — архив первых генераторов каркаса. Не запускать поверх текущего проекта.
- `Тестовое _ иллюстрации/` и ZIP — оригиналы пользователя, сохранены без изменения.
- `.env` — локальные ключи, исключён из Git и Docker-контекста.
- `.env.example` — пример переменных без секретов.
- `compose.yaml`, `compose.tls.yaml` — контейнерный запуск.

Проверки перед сдачей:

```powershell
# frontend/
npm run check
npm run build
# backend/
.venv/Scripts/python.exe -m ruff check app main.py tests
.venv/Scripts/python.exe -m ruff format --check app main.py tests
.venv/Scripts/python.exe -m pytest -q
```

Развёртывание из ASCII-ссылки `C:/Users/artem/composition-build`:

```powershell
docker compose -f compose.yaml -f compose.tls.yaml up -d --build
docker compose -f compose.yaml -f compose.tls.yaml exec nginx nginx -s reload
```

Не выполнять `down -v`: тома содержат библиотеку MinIO и сертификаты. Автоматическое продление сертификата пока не настроено; доступен infra/renew-certificate.ps1.
