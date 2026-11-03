"""History is scoped to a high-entropy anonymous browser cookie."""

import hashlib
import re
import secrets
from typing import Literal
from urllib.parse import urlparse
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas import ObjectId
from app.domain.catalog import COLORS

router = APIRouter(prefix="/api/history", tags=["history"])


class SceneItem(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    id: int = Field(ge=1)
    object: ObjectId
    x: float = Field(ge=-100000, le=100000)
    y: float = Field(ge=-100000, le=100000)
    rotation: float = Field(ge=-360, le=360)
    role: Literal["main", "background"]


class Snapshot(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    mode: Literal["idea", "objects"]
    format: Literal["horizontal", "square", "vertical"]
    detail: Literal["S", "L"]
    scheme: str = Field(max_length=64)
    backgroundObjects: bool
    commonScale: float = Field(gt=0, le=100, allow_inf_nan=False)
    items: list[SceneItem] = Field(min_length=1, max_length=50)


def context(request: Request, response: Response):
    origin = request.headers.get("origin")
    if origin and urlparse(origin).netloc != request.headers.get("host"):
        raise HTTPException(403, "История доступна только с этого сайта")
    repository = request.app.state.history
    if repository is None:
        raise HTTPException(503, "История временно недоступна")
    token = request.cookies.get("composition_session", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        token = secrets.token_urlsafe(32)
        response.set_cookie(
            "composition_session",
            token,
            max_age=60 * 60 * 24 * 180,
            httponly=True,
            secure=request.url.scheme == "https"
            or request.headers.get("x-forwarded-proto") == "https",
            samesite="lax",
        )
    response.headers["Cache-Control"] = "no-store"
    return repository, hashlib.sha256(token.encode()).hexdigest()


@router.get("")
def list_history(request: Request, response: Response):
    repository, owner = context(request, response)
    return repository.list(owner)


@router.post("")
def save_history(snapshot: Snapshot, request: Request, response: Response):
    if snapshot.scheme not in COLORS or len({item.id for item in snapshot.items}) != len(
        snapshot.items
    ):
        raise HTTPException(422, "Некорректная сцена")
    repository, owner = context(request, response)
    return repository.save(owner, str(uuid4()), snapshot.model_dump(mode="json"))


@router.delete("/{identifier}")
def delete_history(identifier: UUID, request: Request, response: Response):
    repository, owner = context(request, response)
    if not repository.delete(owner, str(identifier)):
        raise HTTPException(404, "Запись не найдена")
    return {"deleted": True}
