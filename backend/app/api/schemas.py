from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ObjectId(str, Enum):
    book = "book"
    phone = "phone"
    puzzle = "puzzle"
    wallet = "wallet"
    coin = "coin"
    lamp = "lamp"
    folder = "folder"
    pen = "pen"
    headphones = "headphones"
    tulips = "tulips"


class Selection(BaseModel):
    objects: list[ObjectId] = Field(min_length=1, max_length=5)


class GenerateRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    mode: Literal["idea", "objects"] = "idea"
    format: Literal["horizontal", "square", "vertical"] = "horizontal"
    detail: Literal["S", "L"] = "L"
    seed: int = Field(default=0, ge=0, le=2147483647)
    background_objects: bool = True


class PaletteRequest(BaseModel):
    scheme: str = Field(min_length=1, max_length=64)
