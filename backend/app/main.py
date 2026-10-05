from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import ENGINE_VERSION
from app.api import router
from app.config import ROOT
from app.db import init_db

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="TANK650 ENGINE", version=ENGINE_VERSION, description="API 650 calculation and parametric tank design", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


dist = ROOT / "frontend" / "dist"
if dist.exists():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        candidate = dist / path
        return FileResponse(candidate if candidate.is_file() else dist / "index.html")
else:
    @app.get("/", include_in_schema=False)
    def api_root() -> dict:
        return {"name": "TANK650 ENGINE", "version": ENGINE_VERSION, "docs": "/docs", "frontend": "Run scripts/dev.bat or build frontend."}
