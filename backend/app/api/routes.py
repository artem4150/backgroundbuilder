"""HTTP endpoints; orchestration and algorithms live outside the router."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from app.api.schemas import GenerateRequest, PaletteRequest
from app.domain.catalog import CATALOG, COLORS, PALETTES
from app.domain.composition import build_composition
from app.infrastructure.storage import StorageUnavailableError, read_asset
from app.services.selection import select_objects

router = APIRouter()


@router.get("/api/health")
def health(request: Request):
    state = request.app.state
    return {
        "status": "ok",
        "ai_configured": state.ai is not None,
        "storage": "minio" if state.s3 else "local-development",
    }


@router.get("/api/catalog")
def catalog():
    return CATALOG


@router.get("/api/palettes")
def palettes():
    return PALETTES


@router.post("/api/palette")
def palette(request: PaletteRequest):
    if request.scheme not in COLORS:
        raise HTTPException(422, "Неизвестная исходная палитра")
    return {"scheme": request.scheme, "colors": COLORS[request.scheme]}


@router.get("/media/{name}")
def media(name: str, request: Request):
    try:
        data = read_asset(name, request.app.state.s3)
    except FileNotFoundError:
        raise HTTPException(404, "Объект не найден") from None
    except StorageUnavailableError:
        raise HTTPException(503, "Хранилище временно недоступно") from None
    return Response(
        data,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400", "X-Content-Type-Options": "nosniff"},
    )


@router.post("/api/compose")
async def compose(request: GenerateRequest, http_request: Request):
    try:
        objects, source, notice = await select_objects(request, http_request.app.state)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    result = build_composition(
        objects, CATALOG, request.detail, request.format, request.background_objects, request.seed
    )
    return {**result, "source": source, "notice": notice}
