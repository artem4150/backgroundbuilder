"""Prepared SVG library and original palette definitions."""

import json

from app.core.config import CATALOG_PATH, PALETTES_PATH

CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
PALETTES = json.loads(PALETTES_PATH.read_text(encoding="utf-8"))
COLORS = {palette["id"]: palette["colors"] for palette in PALETTES}
