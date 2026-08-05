from __future__ import annotations

import pyttsx3
from dataclasses import dataclass, field
from threading import Lock

from config import settings
from brain.personality import current_persona


@dataclass
class TextToSpeech:
    engine: pyttsx3.Engine = field(init=False)
    voice_lock: Lock = field(default_factory=Lock, init=False)
    rate: int = 175
    volume: float = 0.9

    def __post_init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)

        # Try to use a female voice if available (Windows)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if any(word in voice.name.lower() for word in ['female', 'zira', 'emma', 'samantha']):
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text: str, wait: bool = True) -> None:
        if not text or not text.strip():
            return

        clean_text = text.strip()
        with self.voice_lock:
            self.engine.say(clean_text)
            if wait:
                self.engine.runAndWait()

    def stop(self) -> None:
        with self.voice_lock:
            try:
                self.engine.stop()
            except Exception:
                pass


tts = TextToSpeech()
