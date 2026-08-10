from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock

import pyttsx3

from brain.personality import current_persona


@dataclass
class TextToSpeech:
    engine: pyttsx3.Engine | None = field(default=None, init=False)
    voice_lock: Lock = field(default_factory=Lock, init=False)
    rate: int = 175
    volume: float = 0.9

    def _ensure_engine(self) -> pyttsx3.Engine:
        if self.engine is None:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)

            voices = self.engine.getProperty("voices")
            for voice in voices:
                if any(
                    word in voice.name.lower()
                    for word in ["female", "zira", "emma", "samantha"]
                ):
                    self.engine.setProperty("voice", voice.id)
                    break

        return self.engine

    def speak(self, text: str, wait: bool = True) -> None:
        if not text or not text.strip():
            return

        clean_text = text.strip()
        with self.voice_lock:
            engine = self._ensure_engine()
            engine.say(clean_text)
            engine.runAndWait()

    def stop(self) -> None:
        with self.voice_lock:
            if self.engine is None:
                return

            try:
                self.engine.stop()
            except Exception:
                pass


tts = TextToSpeech()
