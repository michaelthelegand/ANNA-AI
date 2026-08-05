from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import BASE_DIR


class FileToolError(Exception):
    pass


@dataclass
class FilesTool:
    base_dir: Path = BASE_DIR
    max_read_bytes: int = 200_000
    max_list_entries: int = 200

    def _resolve(self, user_path: str | Path) -> Path:
        p = Path(user_path)

        # Treat relative paths as relative to project base_dir
        if not p.is_absolute():
            p = (self.base_dir / p)

        p = p.resolve()

        # Safety: restrict to project folder
        base = self.base_dir.resolve()
        if p != base and base not in p.parents:
            raise FileToolError(f"Path is outside project folder: {p}")

        return p

    def exists(self, user_path: str | Path) -> bool:
        return self._resolve(user_path).exists()

    def list_dir(self, user_path: str | Path = ".") -> list[dict[str, Any]]:
        p = self._resolve(user_path)
        if not p.exists():
            raise FileToolError(f"Not found: {p}")
        if not p.is_dir():
            raise FileToolError(f"Not a directory: {p}")

        items = []
        for i, child in enumerate(sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))):
            if i >= self.max_list_entries:
                break
            try:
                size = child.stat().st_size if child.is_file() else None
            except Exception:
                size = None
            items.append(
                {
                    "name": child.name,
                    "is_dir": child.is_dir(),
                    "size": size,
                }
            )
        return items

    def read_text(self, user_path: str | Path, encoding: str = "utf-8") -> str:
        p = self._resolve(user_path)
        if not p.exists():
            raise FileToolError(f"Not found: {p}")
        if not p.is_file():
            raise FileToolError(f"Not a file: {p}")

        data = p.read_bytes()
        if len(data) > self.max_read_bytes:
            raise FileToolError(f"File too large to read ({len(data)} bytes): {p}")

        return data.decode(encoding, errors="replace")

    def write_text(self, user_path: str | Path, content: str, overwrite: bool = False, encoding: str = "utf-8") -> Path:
        p = self._resolve(user_path)

        if p.exists() and (not overwrite):
            raise FileToolError(f"Refusing to overwrite existing file: {p}")

        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding=encoding)
        return p


files_tool = FilesTool()
