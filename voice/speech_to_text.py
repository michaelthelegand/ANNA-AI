from __future__ import annotations

import audioop
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import settings


class SpeechToTextError(Exception):
    pass


@dataclass
class SpeechToText:
    enabled: bool = settings.ANNA_STT_ENABLE
    timeout_sec: int = 8
    phrase_time_limit_sec: int = 10
    device_index: int | None = settings.ANNA_STT_DEVICE_INDEX
    language: str = "en-US"
    last_wav_path: Path = settings.DATA_DIR / "stt_last.wav"

    def list_input_devices(self) -> list[dict[str, Any]]:
        if not self.enabled:
            raise SpeechToTextError("STT is disabled. Set ANNA_STT_ENABLE=1 to enable.")

        try:
            import pyaudio
        except Exception as e:
            raise SpeechToTextError(f"PyAudio not installed: {e!r}")

        pa = pyaudio.PyAudio()
        out: list[dict[str, Any]] = []
        try:
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                max_in = int(info.get("maxInputChannels") or 0)
                if max_in <= 0:
                    continue
                out.append(
                    {
                        "index": int(i),
                        "name": str(info.get("name") or ""),
                        "max_input_channels": max_in,
                        "default_sample_rate": int(info.get("defaultSampleRate") or 0),
                    }
                )
        finally:
            pa.terminate()

        return out

    # Backward-compat helper (older Reasoner code used this)
    def list_microphones(self) -> list[str]:
        return [d["name"] for d in self.list_input_devices()]

    def _save_wav(self, audio) -> None:
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.last_wav_path.write_bytes(audio.get_wav_data())

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

        # Save capture for debugging
        try:
            self._save_wav(audio)
            saved = True
        except Exception as e:
            saved = False
            save_err = f"{type(e).__name__}: {e!r}"

        # Compute signal stats
        raw = audio.get_raw_data()
        sw = getattr(audio, "sample_width", 2) or 2
        peak = audioop.max(raw, sw) if raw else 0
        rms = audioop.rms(raw, sw) if raw else 0
        clipped = peak >= 32000

        debug = f"device_index={self.device_index} lang={self.language} rms={rms} peak={peak}"
        if clipped:
            debug += " (CLIPPED: lower mic volume)"

        if saved:
            debug += f" wav={self.last_wav_path}"
        else:
            debug += f" wav_save_error={save_err}"

        # Recognize (online)
        try:
            result = r.recognize_google(audio, language=self.language, show_all=True)
        except sr.UnknownValueError:
            raise SpeechToTextError(f"Could not understand audio (UnknownValueError). {debug}")
        except sr.RequestError as e:
            raise SpeechToTextError(f"Network/API error (RequestError): {e!r}. {debug}")
        except Exception as e:
            raise SpeechToTextError(f"STT recognition failed ({type(e).__name__}): {e!r}. {debug}")

        transcript = ""
        if isinstance(result, dict):
            alts = result.get("alternative") or []
            if alts and isinstance(alts[0], dict):
                transcript = (alts[0].get("transcript") or "").strip()
        elif isinstance(result, str):
            transcript = result.strip()

        if not transcript:
            raise SpeechToTextError(f"No transcription alternatives returned. {debug}")

        return transcript


stt = SpeechToText()
