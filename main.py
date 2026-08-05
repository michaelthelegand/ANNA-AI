from __future__ import annotations

from datetime import datetime, timezone

from brain.memory import memory
from brain.personality import current_persona
from brain.reasoning import reasoner
from config import settings


def main() -> None:
    print(f"{settings.APP_NAME} v{settings.VERSION}")
    print(current_persona.get_intro())

    launch_count = int(memory.get("launch_count", 0)) + 1
    memory.set("launch_count", launch_count)
    memory.set("last_launch_utc", datetime.now(timezone.utc).isoformat())

    print(f"Launch count: {launch_count}")
    print("Type 'exit' to close ANNA.")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue

        if user_text.lower() in {"exit", "quit"}:
            break

        print(reasoner.respond(user_text))

    print("ANNA: Goodbye.")


if __name__ == "__main__":
    main()
