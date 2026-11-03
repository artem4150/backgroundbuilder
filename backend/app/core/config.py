"""Environment configuration. Secrets never leave the backend."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")
ASSETS = Path(os.getenv("ASSET_DIR", str(ROOT / "frontend/public/assets")))
CATALOG_PATH = Path(os.getenv("CATALOG_PATH", str(ROOT / "frontend/app/catalog.json")))
PALETTES_PATH = Path(os.getenv("PALETTES_PATH", str(ROOT / "frontend/shared/palettes.json")))
