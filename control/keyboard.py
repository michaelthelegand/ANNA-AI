from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import settings


class KeyboardControlError(Exception):
    pass


@dataclass
class KeyboardControl:
    enabled: bool = settings.ANNA_KEYBOARD_ENABLE

    def _require_enabled(self) -> None:
        if not self.enabled:
            raise KeyboardControlError(
                "Keyboard control is disabled. Set ANNA_KEYBOARD_ENABLE=1 to enable."
            )

    def type_text(self, text: str, interval: float = 0.02) -> dict[str, Any]:
        self._require_enabled()

        try:
            import pyautogui
        except Exception as e:
            raise KeyboardControlError(f"pyautogui not installed: {e}")

        pyautogui.write(text, interval=interval)
        return {"typed": True, "chars": len(text)}

    def press(self, key: str) -> dict[str, Any]:
        self._require_enabled()

        try:
            import pyautogui
        except Exception as e:
            raise KeyboardControlError(f"pyautogui not installed: {e}")

        pyautogui.press(key)
        return {"pressed": True, "key": key}

    def hotkey(self, *keys: str) -> dict[str, Any]:
        self._require_enabled()

        try:
            import pyautogui
        except Exception as e:
            raise KeyboardControlError(f"pyautogui not installed: {e}")

        pyautogui.hotkey(*keys)
        return {"hotkey": True, "keys": list(keys)}


keyboard_control = KeyboardControl()
