from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import settings


class MouseControlError(Exception):
    pass


@dataclass
class MouseControl:
    enabled: bool = settings.ANNA_MOUSE_ENABLE

    def position(self) -> dict[str, Any]:
        if not self.enabled:
            raise MouseControlError("Mouse control is disabled. Set ANNA_MOUSE_ENABLE=1 to enable.")

        # Lazy import to avoid dependency until enabled
        try:
            import pyautogui
        except Exception as e:
            raise MouseControlError(f"pyautogui not installed: {e}")

        x, y = pyautogui.position()
        return {"x": int(x), "y": int(y)}


mouse_control = MouseControl()
