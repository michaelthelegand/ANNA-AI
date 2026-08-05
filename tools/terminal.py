from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config.settings import BASE_DIR


class TerminalToolError(Exception):
    pass


def _env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass
class TerminalTool:
    base_dir: Path = BASE_DIR
    enabled: bool = _env_flag("ANNA_TERMINAL_ENABLE", "0")  # disabled by default
    timeout_sec: int = 15
    max_output_chars: int = 6000

    # Safety: allowlist executables (no shells).
    allowlist: tuple[str, ...] = ("python", "git")

    def run(self, command: str) -> dict[str, Any]:
        if not self.enabled:
            raise TerminalToolError(
                "Terminal tool is disabled. Set ANNA_TERMINAL_ENABLE=1 to enable."
            )

        if not command or not command.strip():
            raise TerminalToolError("Empty command.")

        # Parse without invoking a shell.
        parts = shlex.split(command, posix=False)
        if not parts:
            raise TerminalToolError("Empty command after parsing.")

        exe = Path(parts[0]).name.lower()
        if exe not in {x.lower() for x in self.allowlist}:
            raise TerminalToolError(f"Executable not allowed: {exe}")

        p = subprocess.run(
            parts,
            cwd=str(self.base_dir),
            capture_output=True,
            text=True,
            timeout=self.timeout_sec,
            shell=False,
        )

        stdout = (p.stdout or "")
        stderr = (p.stderr or "")

        if len(stdout) > self.max_output_chars:
            stdout = stdout[: self.max_output_chars] + "\n...[truncated]..."
        if len(stderr) > self.max_output_chars:
            stderr = stderr[: self.max_output_chars] + "\n...[truncated]..."

        return {"returncode": p.returncode, "stdout": stdout, "stderr": stderr}


terminal_tool = TerminalTool()
