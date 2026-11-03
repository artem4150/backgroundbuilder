"""Local Uvicorn entrypoint: uvicorn main:app."""

from app.main import app

__all__ = ["app"]
