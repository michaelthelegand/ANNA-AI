# ANNA-AI settings (stage 4: add windows control flag)

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"


def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _load_env() -> None:
    if load_dotenv and ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=False)


_load_env()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "ANNA-AI")
    version: str = os.getenv("ANNA_AI_VERSION", "0.0.1")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    anna_ai_name: str = os.getenv("ANNA_AI_NAME", "ANNA")
    data_dir: Path = BASE_DIR / "data"

    # Feature flags
    tts_enable: bool = _env_flag("ANNA_TTS_ENABLE", "0")
    browser_enable: bool = _env_flag("ANNA_BROWSER_ENABLE", "0")
    windows_control_enable: bool = _env_flag("ANNA_WINDOWS_CONTROL_ENABLE", "0")


settings = Settings()

# Backwards-compatible module-level exports
APP_NAME = settings.app_name
VERSION = settings.version
LOG_LEVEL = settings.log_level
ANNA_AI_NAME = settings.anna_ai_name
DATA_DIR = settings.data_dir

ANNA_TTS_ENABLE = settings.tts_enable
ANNA_BROWSER_ENABLE = settings.browser_enable
ANNA_WINDOWS_CONTROL_ENABLE = settings.windows_control_enable
