from __future__ import annotations

import os
import webbrowser
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus, urlparse

from config import settings


class BrowserToolError(Exception):
    pass


def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class BrowserTool:
    enabled: bool = settings.ANNA_BROWSER_ENABLE
    default_search_base: str = "https://www.bing.com/search?q="

    def _check_enabled(self) -> None:
        if not self.enabled:
            raise BrowserToolError("Browser tool is disabled. Set ANNA_BROWSER_ENABLE=1 to enable.")

    def open_url(self, url: str) -> dict[str, Any]:
        self._check_enabled()

        url = (url or "").strip()
        if not url:
            raise BrowserToolError("Empty URL.")

        parsed = urlparse(url)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise BrowserToolError("Only http/https URLs are allowed.")

        ok = webbrowser.open(url, new=2, autoraise=True)
        return {"opened": bool(ok), "url": url}

    def search(self, query: str) -> dict[str, Any]:
        self._check_enabled()

        q = (query or "").strip()
        if not q:
            raise BrowserToolError("Empty search query.")

        url = self.default_search_base + quote_plus(q)
        ok = webbrowser.open(url, new=2, autoraise=True)
        return {"opened": bool(ok), "url": url, "query": q}


browser_tool = BrowserTool()
