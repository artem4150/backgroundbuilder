"""Object selection with a bounded AI cache, quota cooldown and offline fallback."""

import logging
import time

from app.api.schemas import GenerateRequest
from app.domain.matching import match_objects
from app.infrastructure.gemini import select_with_gemini

log = logging.getLogger(__name__)


async def select_objects(request: GenerateRequest, state) -> tuple[list[str], str, str | None]:
    query = request.query.strip().lower()
    if not query:
        raise ValueError("Введите запрос")
    source = "names"
    notice = None
    if (
        request.mode == "idea"
        and query in state.ai_cache
        and state.ai_cache[query][0] > time.monotonic()
    ):
        objects = state.ai_cache[query][1]
        source = "gemini-cache"
    elif request.mode == "idea" and state.ai and time.monotonic() >= state.ai_cooldown:
        try:
            async with state.ai_slots:
                objects = await select_with_gemini(state.ai, request.query)
            source = "gemini"
            if len(state.ai_cache) >= 128:
                state.ai_cache.pop(next(iter(state.ai_cache)))
            state.ai_cache[query] = (time.monotonic() + 3600, objects)
        except Exception as error:
            if getattr(error, "code", None) == 429:
                state.ai_cooldown = time.monotonic() + 60
            log.warning("Gemini request failed; using catalog matching")
            objects = match_objects(query)
            source = "dictionary"
            notice = "AI временно недоступен. Объекты подобраны по словарю."
    else:
        objects = match_objects(query)
        if request.mode == "idea":
            source = "dictionary"
            notice = (
                "Пауза после ограничения AI. Объекты подобраны по словарю."
                if state.ai
                else "Gemini не настроен. Объекты подобраны по словарю."
            )
    objects = list(dict.fromkeys(objects))[:5]
    if not objects:
        raise ValueError("Не удалось подобрать объекты. Укажите названия из библиотеки.")
    return objects, source, notice
