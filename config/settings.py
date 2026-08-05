# ANNA-AI settings (stage 1: .env loader)

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


def _load_env() -> None:
    # Load .env if present (we keep .env out of git).
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


settings = Settings()

# Backwards-compatible module-level exports (so main.py stays simple)
APP_NAME = settings.app_name
VERSION = settings.version
LOG_LEVEL = settings.log_level
ANNA_AI_NAME = settings.anna_ai_name
DATA_DIR = settings.data_dir
