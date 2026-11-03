# Backend

Структура:

```text
backend/
  main.py                    # совместимая точка запуска Uvicorn
  app/
    main.py                  # фабрика FastAPI и подключение router
    api/
      routes.py              # HTTP, коды ответов, обработка ошибок
      schemas.py             # валидация запросов и структурированного ответа AI
    core/
      config.py              # пути и загрузка окружения
    domain/
      catalog.py             # библиотека и палитры
      matching.py            # локальный подбор по названиям
      composition.py         # геометрия и компоновка, без HTTP и SDK
    services/
      selection.py           # сценарий подбора, кэш, cooldown, fallback
    infrastructure/
      gemini.py              # адаптер Google GenAI
      storage.py             # чтение SVG и инициализация MinIO
      lifespan.py            # создание и закрытие внешних клиентов
  tests/                     # API, библиотека, композиции, подбор
  pyproject.toml             # правила Ruff и pytest
  requirements.lock.txt      # зависимости контейнера
  requirements-dev.txt       # инструменты разработки
```

Маршрут валидирует HTTP-запрос, вызывает сервис подбора и чистый алгоритм композиции. Сервис вызывает Gemini через адаптер и управляет кэшем/квотой. Хранилище выдаёт только разрешённые SVG. Внешние клиенты создаются и закрываются в lifespan. Формат ответов API сохранён.

Из папки backend:

```powershell
.venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m ruff check app main.py tests
.venv/Scripts/python.exe -m ruff format --check app main.py tests
```

13 тестов используют подмену Gemini при проверке ошибок, кэша и локального поиска; реальные API-вызовы и бесплатная квота при запуске тестов не расходуются.
