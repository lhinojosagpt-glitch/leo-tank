from __future__ import annotations

import asyncio
from typing import Any

import httpx2

from app.db import init_db

if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class ASGITestClient:
    """Small synchronous facade over httpx2's non-blocking ASGI transport."""

    def __init__(self, app: Any):
        self.app = app

    def __enter__(self):
        init_db()
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def request(self, method: str, url: str, **kwargs: Any):
        async def send():
            transport = httpx2.ASGITransport(app=self.app)
            async with httpx2.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, url, **kwargs)

        return asyncio.run(send())

    def get(self, url: str, **kwargs: Any):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any):
        return self.request("POST", url, **kwargs)
