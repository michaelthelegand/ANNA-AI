from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from config import settings


class SpeechToTextError(Exception):
    pass


@dataclass
class SpeechToText:
    enabled: bool = settings.ANNA_STT_ENABLE
    timeout_sec: int = 6
    phrase_time_limit_sec: int = 8

    def listen_once(self) -> str:
        if not self.enabled:
            raise SpeechToTextError("STT is disabled. Set ANNA_STT_ENABLE=1 to enable.")

        try:
            import speech_recognition as sr
        except Exception as e:
            raise SpeechToTextError(f"SpeechRecognition not installed: {e}")

        r = sr.Recognizer()

        with sr.Microphone() as source:
            # basic ambient noise adjustment
            r.adjust_for_ambient_noise(source, duration=0.6)
            audio = r.listen(source, timeout=self.timeout_sec, phrase_time_limit=self.phrase_time_limit_sec)

        # Offline engines are more complex; for now use Google Web Speech API
        # (still a desktop app; just uses an online recognizer)
        try:
            return r.recognize_google(audio)
        except Exception as e:
            raise SpeechToTextError(f"STT recognition failed: {e}")


stt = SpeechToText()
