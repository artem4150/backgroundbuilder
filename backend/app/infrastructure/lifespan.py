"""Own external resources for the lifetime of a FastAPI application."""

import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.gemini import create_gemini_client
from app.infrastructure.history import create_history_repository
from app.infrastructure.storage import initialize_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.history = await asyncio.to_thread(create_history_repository)
    app.state.s3 = None
    app.state.ai = None
    app.state.ai_slots = asyncio.Semaphore(1)
    app.state.ai_cache = {}
    app.state.ai_cooldown = 0
    try:
        if os.getenv("S3_ENDPOINT"):
            app.state.s3 = await initialize_storage()
        if os.getenv("GEMINI_API_KEY"):
            app.state.ai = create_gemini_client()
        yield
    finally:
        if app.state.ai:
            await app.state.ai.aio.aclose()
        if app.state.s3:
            app.state.s3.close()
