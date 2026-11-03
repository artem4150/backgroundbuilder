"""Application factory and HTTP router registration."""

from fastapi import FastAPI

from app.api.routes import router
from app.infrastructure.lifespan import lifespan


def create_app() -> FastAPI:
    application = FastAPI(title="Состав API", version="0.1.0", lifespan=lifespan)
    application.include_router(router)
    return application


app = create_app()
