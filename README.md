# Состав

Веб-редактор векторных композиций по ТЗ Figma. Next.js + FastAPI + Gemini + MinIO + Nginx.

## Локальная разработка

Backend (из папки backend):

```powershell
.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Frontend (из папки frontend):

```powershell
npm ci
npm run dev
```

Открыть http://localhost:3000 . В локальной разработке без S3_ENDPOINT backend читает те же SVG с диска. Production Compose требует MinIO.

## Gemini

Ключ хранится только на сервере в переменной GEMINI_API_KEY. Название модели задаётся GEMINI_MODEL (по умолчанию gemini-3.5-flash-lite); доступность модели и квоты проверить с ключом пользователя. Без ключа доступен словарный подбор, и интерфейс явно сообщает об этом.

## Docker Compose

Скопировать .env.example в .env, задать GEMINI_API_KEY, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD (длинный случайный пароль). Запустить Docker Desktop с Linux engine.

```powershell
docker compose up --build -d
```

Работающий HTTPS-стенд: https://backgroundbuilder.duckdns.org/ . Для запуска текущего production-стенда использовать `docker compose -f compose.yaml -f compose.tls.yaml up -d --build` из ASCII-пути `C:/Users/artem/composition-build`. Только Nginx публикует порт. MinIO собирается из зафиксированного коммита официального репозитория; первая сборка требует времени и сети. Домен и HTTPS настроены; сертификат действует до 31 января 2027. Скрипт продления: infra/renew-certificate.ps1; автоматическое расписание пока не установлено.

## Палитры

Загрузка принимает JSON исходной схемы: {"scheme":"purple"}, {"scheme":"peach"} или {"scheme":"turquoise"}. Готовые файлы: frontend/public/palettes/. Произвольные цвета не разрешены.

## Архитектура

- audit/assets-manifest.json содержит классификацию исходников.
- frontend/app/catalog.json связывает идентификатор объекта, детализацию S/L, роль и файл.
- В production backend при старте загружает подготовленные SVG в приватный MinIO bucket и выдаёт разрешённые объекты через /media/. Административная консоль и S3-порт наружу не публикуются.
- Gemini возвращает только идентификаторы объектов по проверяемой схеме. Векторную геометрию модель не получает и не создаёт.
- FastAPI строит размещение с общим масштабом сцены. Относительные размеры объектов не меняются.
- Клиент хранит сцену в памяти вкладки. Холст — SVG; экспорт встраивает исходные векторные поддеревья, применяет палитру и переименовывает ID.
- PostgreSQL, аккаунтов и сохранения проектов нет: они не входят в согласованное ТЗ.

## Проверки

```powershell
# frontend
npm run build
# backend
.venv/Scripts/python.exe -m pytest -q
```

## Текущий статус

Работает контейнерный HTTPS-стенд с MinIO и настроенным Gemini. Пройдены 8 backend-тестов и браузерные проверки редактора/экспорта. Финальная приёмка, импорт SVG в Figma и материалы сдачи ещё не завершены.

## Организация кода и проверки

Структура описана в PROJECT.md, frontend/README.md и backend/README.md. Полный набор локальных проверок: `./tools/check.ps1`. Разовые генераторы каркаса находятся в архиве и не предназначены для повторного запуска. Поддерживаемая подготовка палитр: `python tools/prepare_palettes.py`.
