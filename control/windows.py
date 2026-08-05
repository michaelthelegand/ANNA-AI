from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import BASE_DIR
from config import settings


class WindowsControlError(Exception):
    pass


@dataclass
class WindowsControl:
    base_dir: Path = BASE_DIR
    enabled: bool = settings.ANNA_WINDOWS_CONTROL_ENABLE

    def _resolve(self, user_path: str | Path) -> Path:
        p = Path(user_path)
        if not p.is_absolute():
            p = (self.base_dir / p)
        p = p.resolve()

        base = self.base_dir.resolve()
        if p != base and base not in p.parents:
            raise WindowsControlError(f"Path is outside project folder: {p}")

        return p

    def open_path(self, user_path: str | Path) -> dict[str, Any]:
        if not self.enabled:
            raise WindowsControlError(
                "Windows control is disabled. Set ANNA_WINDOWS_CONTROL_ENABLE=1 to enable."
            )

        p = self._resolve(user_path)
        if not p.exists():
            raise WindowsControlError(f"Not found: {p}")

        # Open file/folder with default handler
        os.startfile(str(p))  # Windows only
        return {"opened": True, "path": str(p)}

    def reveal_in_explorer(self, user_path: str | Path) -> dict[str, Any]:
        if not self.enabled:
            raise WindowsControlError(
                "Windows control is disabled. Set ANNA_WINDOWS_CONTROL_ENABLE=1 to enable."
            )

        p = self._resolve(user_path)
        if not p.exists():
            raise WindowsControlError(f"Not found: {p}")

        # Reveal file in Explorer (select it) or open folder
        if p.is_file():
            subprocess.Popen(["explorer.exe", "/select,", str(p)], shell=False)
        else:
            os.startfile(str(p))
        return {"revealed": True, "path": str(p)}


windows_control = WindowsControl()
