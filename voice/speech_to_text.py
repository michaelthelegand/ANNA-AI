from __future__ import annotations

import audioop
from dataclasses import dataclass
from datetime import datetime
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

    def _device_default_sample_rate(self) -> int | None:
        if self.device_index is None:
            return None
        try:
            import pyaudio
        except Exception as e:
            raise SpeechToTextError(f"PyAudio not installed: {e!r}")

        pa = pyaudio.PyAudio()
        try:
            info = pa.get_device_info_by_index(int(self.device_index))
            rate = info.get("defaultSampleRate", None)
            return int(rate) if rate else None
        except Exception as e:
            raise SpeechToTextError(f"Failed to get device sample rate ({type(e).__name__}): {e!r}")
        finally:
            pa.terminate()

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

    # Backward-compat helper
    def list_microphones(self) -> list[str]:
        return [d["name"] for d in self.list_input_devices()]

    def _audio_stats(self, audio) -> tuple[int, int, bool]:
        raw = audio.get_raw_data()
        sw = getattr(audio, "sample_width", 2) or 2
        peak = audioop.max(raw, sw) if raw else 0
        rms = audioop.rms(raw, sw) if raw else 0
        clipped = peak >= 32000
        return rms, peak, clipped

    def _fallback_wav_path(self) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return settings.DATA_DIR / f"stt_last_{ts}.wav"

    def _save_wav_bytes(self, wav_bytes: bytes) -> Path:
        settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

        target = self.last_wav_path
        tmp = target.with_suffix(target.suffix + ".tmp")

        try:
            tmp.write_bytes(wav_bytes)
            tmp.replace(target)  # atomic replace
            return target
        except PermissionError:
            # If user is currently playing stt_last.wav, it can be locked.
            alt = self._fallback_wav_path()
            alt.write_bytes(wav_bytes)
            self.last_wav_path = alt
            return alt
        finally:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass

    def _save_wav(self, audio) -> Path:
        return self._save_wav_bytes(audio.get_wav_data())

    def probe(self) -> dict[str, Any]:
        """
        Captures a short chunk and saves WAV (no recognition).
        Returns a dict even if it times out (so it won't crash scripts).
        """
        if not self.enabled:
            raise SpeechToTextError("STT is disabled. Set ANNA_STT_ENABLE=1 to enable.")

        try:
            import speech_recognition as sr
        except Exception as e:
            raise SpeechToTextError(f"SpeechRecognition not installed: {e!r}")

        r = sr.Recognizer()
        sample_rate = self._device_default_sample_rate()

        try:
            with sr.Microphone(device_index=self.device_index, sample_rate=sample_rate) as source:
                r.adjust_for_ambient_noise(source, duration=0.6)
                try:
                    audio = r.listen(source, timeout=6, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    return {
                        "ok": False,
                        "error": "timeout_waiting_for_speech",
                        "device_index": self.device_index,
                        "sample_rate": sample_rate,
                    }
        except Exception as e:
            raise SpeechToTextError(f"Probe mic error ({type(e).__name__}): {e!r}")

        try:
            saved_path = self._save_wav(audio)
        except Exception as e:
            return {
                "ok": False,
                "error": f"wav_save_failed ({type(e).__name__}): {e!r}",
                "device_index": self.device_index,
                "sample_rate": sample_rate,
            }

        rms, peak, clipped = self._audio_stats(audio)
        return {
            "ok": True,
            "device_index": self.device_index,
            "sample_rate": sample_rate,
            "rms": rms,
            "peak": peak,
            "clipped": clipped,
            "wav": str(saved_path),
        }

    def listen_once(self) -> str:
        if not self.enabled:
            raise SpeechToTextError("STT is disabled. Set ANNA_STT_ENABLE=1 to enable.")

        try:
            import speech_recognition as sr
        except Exception as e:
            raise SpeechToTextError(f"SpeechRecognition not installed: {e!r}")

        r = sr.Recognizer()
        sample_rate = self._device_default_sample_rate()

        try:
            with sr.Microphone(device_index=self.device_index, sample_rate=sample_rate) as source:
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

        # Save capture for debugging (but don't block recognition if save fails)
        save_note = ""
        try:
            saved_path = self._save_wav(audio)
        except Exception as e:
            saved_path = None
            save_note = f" wav_save_failed={type(e).__name__}:{e!r}"

        rms, peak, clipped = self._audio_stats(audio)

        debug = f"device_index={self.device_index} sample_rate={sample_rate} lang={self.language} rms={rms} peak={peak}"
        if clipped:
            debug += " (CLIPPED: lower mic volume)"
        if saved_path:
            debug += f" wav={saved_path}"
        debug += save_note

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
