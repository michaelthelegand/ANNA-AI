from __future__ import annotations

from dataclasses import dataclass

from brain.learning import learner
from brain.personality import current_persona
from brain.memory import memory
from tools.browser import BrowserToolError, browser_tool
from tools.files import FileToolError, files_tool
from tools.terminal import TerminalToolError, terminal_tool


@dataclass
class Reasoner:
    # Placeholder: later we will plug in an LLM + tools + RAG here.
    name: str = current_persona.name

    def _help_text(self) -> str:
        return (
            "Commands:\n"
            "  help                         Show this help\n"
            "  ls [path]                    List a folder (default: .)\n"
            "  read <path>                  Read a text file\n"
            "  exists <path>                Check if a path exists\n"
            "  write <path> :: <text>       Create a new text file (no overwrite)\n"
            "  run <command>                Run an allowlisted command (DISABLED by default)\n"
            "  search <query>               Open a web search (DISABLED by default)\n"
            "  openurl <https://...>        Open a URL in default browser (DISABLED by default)\n"
            "\n"
            "Learning (saved in data/memory.json):\n"
            "  remember <key> = <value>     Save a fact\n"
            "  recall <key>                 Read a fact\n"
            "  forget <key>                 Delete a fact\n"
            "  facts                        List saved fact keys\n"
            "\n"
            "Notes:\n"
            "  - Paths are restricted to the ANNA-AI project folder for safety.\n"
            "  - Terminal needs ANNA_TERMINAL_ENABLE=1.\n"
            "  - Browser needs ANNA_BROWSER_ENABLE=1.\n"
        )

    def respond(self, user_text: str) -> str:
        text = (user_text or "").strip()
        memory.set("last_user_text", text)

        if not text:
            return f"{self.name}: Say something or type 'help'."

        cmd, *rest = text.split(maxsplit=1)
        cmd_l = cmd.lower()
        arg = rest[0].strip() if rest else ""

        try:
            if cmd_l in {"help", "?"}:
                return f"{self.name}:\n{self._help_text()}"

            if cmd_l in {"ls", "dir"}:
                path = arg if arg else "."
                items = files_tool.list_dir(path)
                if not items:
                    return f"{self.name}: (empty) {path}"

                lines = []
                for it in items:
                    if it["is_dir"]:
                        lines.append(f"{it['name']}/")
                    else:
                        size = it.get("size")
                        lines.append(f"{it['name']} ({size} bytes)" if size is not None else it["name"])
                return f"{self.name}: Listing {path}\n" + "\n".join(lines)

            if cmd_l == "exists":
                if not arg:
                    return f"{self.name}: Usage: exists <path>"
                return f"{self.name}: {arg} -> {files_tool.exists(arg)}"

            if cmd_l == "read":
                if not arg:
                    return f"{self.name}: Usage: read <path>"
                content = files_tool.read_text(arg)
                max_chars = 4000
                out = content[:max_chars]
                if len(content) > max_chars:
                    out += "\n...[truncated]..."
                return f"{self.name}: Contents of {arg}\n{out}"

            if cmd_l == "write":
                if not arg or "::" not in arg:
                    return f"{self.name}: Usage: write <path> :: <text>"
                target, content = arg.split("::", 1)
                target = target.strip()
                content = content.lstrip()
                p = files_tool.write_text(target, content, overwrite=False)
                rel = p.relative_to(files_tool.base_dir)
                return f"{self.name}: Wrote {len(content)} chars -> {rel}"

            if cmd_l == "run":
                if not arg:
                    return f"{self.name}: Usage: run <command>"
                r = terminal_tool.run(arg)
                stdout = (r.get("stdout") or "").strip()
                stderr = (r.get("stderr") or "").strip()
                parts = [f"{self.name}: returncode={r.get('returncode')}"]
                if stdout:
                    parts.append("stdout:\n" + stdout)
                if stderr:
                    parts.append("stderr:\n" + stderr)
                return "\n".join(parts)

            if cmd_l == "search":
                if not arg:
                    return f"{self.name}: Usage: search <query>"
                r = browser_tool.search(arg)
                return f"{self.name}: Opened search for '{r.get('query')}'."

            if cmd_l == "openurl":
                if not arg:
                    return f"{self.name}: Usage: openurl <https://...>"
                r = browser_tool.open_url(arg)
                return f"{self.name}: Opened URL."

            # Learning commands
            if cmd_l == "remember":
                if not arg:
                    return f"{self.name}: Usage: remember <key> = <value>"
                if ("=" not in arg) and ("::" not in arg):
                    return f"{self.name}: Usage: remember <key> = <value>"
                if "::" in arg:
                    key, value = arg.split("::", 1)
                else:
                    key, value = arg.split("=", 1)
                key = key.strip()
                value = value.strip()
                learner.remember(key, value)
                return f"{self.name}: Remembered {key}."

            if cmd_l == "recall":
                if not arg:
                    return f"{self.name}: Usage: recall <key>"
                val = learner.recall(arg, default=None)
                if val is None:
                    return f"{self.name}: I don't have '{arg}' saved."
                return f"{self.name}: {arg} = {val}"

            if cmd_l == "forget":
                if not arg:
                    return f"{self.name}: Usage: forget <key>"
                existed = learner.forget(arg)
                return f"{self.name}: Deleted {arg}." if existed else f"{self.name}: Nothing to delete for {arg}."

            if cmd_l == "facts":
                keys = learner.list_keys()
                if not keys:
                    return f"{self.name}: No facts saved."
                return f"{self.name}: Facts keys:\n" + "\n".join(keys)

        except (FileToolError, TerminalToolError, BrowserToolError) as e:
            return f"{self.name}: Tool error: {e}"
        except Exception as e:
            return f"{self.name}: Error: {e}"

        return (
            f"{self.name}: I heard: '{text}'. "
            "Reasoning is still placeholder (LLM not connected yet). Type 'help' for commands."
        )


reasoner = Reasoner()
