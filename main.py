from __future__ import annotations

from datetime import datetime, timezone

from config import settings
from brain.personality import current_persona
from brain.memory import memory


def main():
    print(f"{settings.APP_NAME} v{settings.VERSION} (scaffold; placeholders only).")
    print(current_persona.get_intro())

    launch_count = int(memory.get("launch_count", 0)) + 1
    memory.set("launch_count", launch_count)
    memory.set("last_launch_utc", datetime.now(timezone.utc).isoformat())

    print(f"Launch count: {launch_count}")


if __name__ == "__main__":
    main()
