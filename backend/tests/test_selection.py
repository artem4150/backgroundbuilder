"""Selection policy tests use a fake adapter and never consume Gemini quota."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.api.schemas import GenerateRequest
from app.services.selection import select_objects


def make_state():
    return SimpleNamespace(ai=object(), ai_slots=asyncio.Semaphore(1), ai_cache={}, ai_cooldown=0)


def test_repeated_metaphor_uses_cache(monkeypatch):
    adapter = AsyncMock(return_value=["book", "puzzle"])
    monkeypatch.setattr("app.services.selection.select_with_gemini", adapter)

    async def scenario():
        state = make_state()
        request = GenerateRequest(query="Систематизировать знания")
        first = await select_objects(request, state)
        second = await select_objects(request, state)
        assert first == (["book", "puzzle"], "gemini", None)
        assert second == (["book", "puzzle"], "gemini-cache", None)
        assert adapter.await_count == 1

    asyncio.run(scenario())


def test_quota_error_enters_cooldown_without_retry(monkeypatch):
    class QuotaError(Exception):
        code = 429

    adapter = AsyncMock(side_effect=QuotaError())
    monkeypatch.setattr("app.services.selection.select_with_gemini", adapter)

    async def scenario():
        state = make_state()
        request = GenerateRequest(query="книга")
        first = await select_objects(request, state)
        second = await select_objects(request, state)
        assert first[0] == second[0] == ["book"]
        assert first[1] == second[1] == "dictionary"
        assert state.ai_cooldown > 0
        assert adapter.await_count == 1

    asyncio.run(scenario())


def test_names_bypass_ai_and_preserve_order(monkeypatch):
    adapter = AsyncMock()
    monkeypatch.setattr("app.services.selection.select_with_gemini", adapter)

    async def scenario():
        result = await select_objects(
            GenerateRequest(query="монета, книга", mode="objects"), make_state()
        )
        assert result == (["coin", "book"], "names", None)
        adapter.assert_not_awaited()

    asyncio.run(scenario())
