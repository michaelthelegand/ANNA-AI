from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import settings


class SpeechToTextError(Exception):
    pass


@dataclass
class SpeechToText:
    enabled: bool = settings.ANNA_STT_ENABLE
    timeout_sec: int = 6
    phrase_time_limit_sec: int = 8
    device_index: int | None = None

    def list_microphones(self) -> list[str]:
        if not self.enabled:
            raise SpeechToTextError("STT is disabled. Set ANNA_STT_ENABLE=1 to enable.")

        try:
            import speech_recognition as sr
        except Exception as e:
            raise SpeechToTextError(f"SpeechRecognition not installed: {e!r}")

        try:
            return list(sr.Microphone.list_microphone_names())
        except Exception as e:
            raise SpeechToTextError(f"Failed to list microphones ({type(e).__name__}): {e!r}")

    def listen_once(self) -> str:
        if not self.enabled:
            raise SpeechToTextError("STT is disabled. Set ANNA_STT_ENABLE=1 to enable.")

        try:
            import speech_recognition as sr
        except Exception as e:
            raise SpeechToTextError(f"SpeechRecognition not installed: {e!r}")

        r = sr.Recognizer()

        try:
            with sr.Microphone(device_index=self.device_index) as source:
                # basic ambient noise adjustment
                r.adjust_for_ambient_noise(source, duration=0.6)
                try:
                    audio = r.listen(
                        source,
                        timeout=self.timeout_sec,
                        phrase_time_limit=self.phrase_time_limit_sec,
                    )
                except sr.WaitTimeoutError:
                    raise SpeechToTextError("No speech detected (timeout).")
        except SpeechToTextError:
            raise
        except Exception as e:
            raise SpeechToTextError(f"Microphone error ({type(e).__name__}): {e!r}")

        # Desktop app: uses Google Web Speech recognizer for now (online)
        try:
            text = r.recognize_google(audio)
            return (text or "").strip()
        except sr.UnknownValueError:
            raise SpeechToTextError("Could not understand audio (UnknownValueError).")
        except sr.RequestError as e:
            raise SpeechToTextError(f"Network/API error (RequestError): {e!r}")
        except Exception as e:
            raise SpeechToTextError(f"STT recognition failed ({type(e).__name__}): {e!r}")


stt = SpeechToText()
