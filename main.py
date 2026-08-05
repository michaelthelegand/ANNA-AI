from __future__ import annotations

from datetime import datetime, timezone

from brain.memory import memory
from brain.personality import current_persona
from brain.reasoning import reasoner
from config import settings

try:
    from voice.text_to_speech import tts
except Exception:
    tts = None


def _speak(text: str) -> None:
    if not settings.ANNA_TTS_ENABLE:
        return
    if not tts:
        return

    # Keep speech short so it doesn't read huge file outputs.
    short = (text or "").strip()
    if len(short) > 300:
        short = short[:300] + " ..."

    try:
        tts.speak(short, wait=False)
    except Exception:
        pass


def main() -> None:
    print(f"{settings.APP_NAME} v{settings.VERSION}")
    print(current_persona.get_intro())

    launch_count = int(memory.get("launch_count", 0)) + 1
    memory.set("launch_count", launch_count)
    memory.set("last_launch_utc", datetime.now(timezone.utc).isoformat())

    print(f"Launch count: {launch_count}")
    print(f"TTS enabled: {settings.ANNA_TTS_ENABLE}")
    print("Type 'exit' to close ANNA.")

    _speak(current_persona.get_intro())

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

        response = reasoner.respond(user_text)
        print(response)
        _speak(response)

    print("ANNA: Goodbye.")
    _speak("Goodbye.")


if __name__ == "__main__":
    main()
