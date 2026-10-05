from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("TANK650_DATABASE_URL", f"sqlite:///{(ROOT / 'data' / 'tank650.sqlite3').as_posix()}")
API_KEY = os.getenv("TANK650_API_KEY", "")
OPENSCAD_PATH = os.getenv("OPENSCAD_PATH", "")

