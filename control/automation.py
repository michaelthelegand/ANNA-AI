from __future__ import annotations

from typing import Any

from config import settings


class Automation:
    """Read-only automation capability status.

    Action execution will be added later with explicit safety checks.
    """

    def status(self) -> dict[str, Any]:
        return {
            "automation_enabled": bool(settings.ANNA_AUTOMATION_ENABLE),
            "keyboard_enabled": bool(settings.ANNA_KEYBOARD_ENABLE),
            "mouse_enabled": bool(settings.ANNA_MOUSE_ENABLE),
            "windows_enabled": bool(settings.ANNA_WINDOWS_CONTROL_ENABLE),
            "supported_actions": [],
        }


automation = Automation()
