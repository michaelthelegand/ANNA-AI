from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config import settings


class SpeechToTextError(Exception):
    pass


@dataclass
class SpeechToText:
    enabled: bool = settings.ANNA_STT_ENABLE
    timeout_sec: int = 8
    phrase_time_limit_sec: int = 10
    device_index: int | None = settings.ANNA_STT_DEVICE_INDEX
    last_wav_path: Path = settings.DATA_DIR / "stt_last.wav"

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

    def _save_wav(self, audio) -> None:
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        try:
            wav_bytes = audio.get_wav_data()
            self.last_wav_path.write_bytes(wav_bytes)
        except Exception as e:
            # Don't block STT if saving fails
            raise SpeechToTextError(f"Failed to save WAV ({type(e).__name__}): {e!r}")

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
                r.adjust_for_ambient_noise(source, duration=1.0)

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

        # Always save what we captured for debugging
        try:
            self._save_wav(audio)
        except SpeechToTextError as e:
            # Keep going, but preserve info
            save_err = str(e)
        else:
            save_err = ""

        # Online recognizer (desktop app still; this just calls a network service)
        try:
            text = r.recognize_google(audio, language="en-US")
            text = (text or "").strip()
            if not text:
                raise SpeechToTextError("Recognition returned empty text.")
            return text
        except sr.UnknownValueError:
            msg = "Could not understand audio (UnknownValueError)."
        except sr.RequestError as e:
            msg = f"Network/API error (RequestError): {e!r}"
        except SpeechToTextError:
            raise
        except Exception as e:
            msg = f"STT recognition failed ({type(e).__name__}): {e!r}"

        extra = f" Saved audio to: {self.last_wav_path}"
        if save_err:
            extra += f" (but save had issue: {save_err})"
        raise SpeechToTextError(msg + extra)


stt = SpeechToText()
