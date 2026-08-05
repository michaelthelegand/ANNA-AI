from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from brain.learning import learner
from brain.personality import current_persona
from brain.memory import memory
from control.keyboard import KeyboardControlError, keyboard_control
from control.mouse import MouseControlError, mouse_control
from control.windows import WindowsControlError, windows_control
from tools.browser import BrowserToolError, browser_tool
from tools.files import FileToolError, files_tool
from tools.terminal import TerminalToolError, terminal_tool


@dataclass
class Reasoner:
    name: str = current_persona.name
    history_key: str = "chat_history"
    max_history_items: int = 100

    def _now_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_history(self) -> list[dict]:
        h = memory.get(self.history_key, [])
        return h if isinstance(h, list) else []

    def _save_history(self, h: list[dict]) -> None:
        if len(h) > self.max_history_items:
            h = h[-self.max_history_items :]
        memory.set(self.history_key, h)

    def _append_history(self, role: str, text: str) -> None:
        h = self._load_history()
        h.append({"ts_utc": self._now_utc(), "role": role, "text": text})
        self._save_history(h)

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
            "  openpath <path>              Open a file/folder (DISABLED by default)\n"
            "  mousepos                     Get mouse position (DISABLED by default)\n"
            "  type <text>                  Type text (DISABLED by default)\n"
            "  press <key>                  Press a key (DISABLED by default)\n"
            "  hotkey <k1>+<k2>+...         Press a hotkey combo (DISABLED by default)\n"
            "\n"
            "Learning (saved in data/memory.json):\n"
            "  remember <key> = <value>     Save a fact\n"
            "  recall <key>                 Read a fact\n"
            "  forget <key>                 Delete a fact\n"
            "  facts                        List saved fact keys\n"
            "\n"
            "TODOs (saved in data/memory.json):\n"
            "  todo add <text>              Add a todo\n"
            "  todo list [all]              List todos (default hides done)\n"
            "  todo done <id>               Mark todo as done by id\n"
            "  todo clear                   Clear all todos\n"
            "\n"
            "History (saved in data/memory.json):\n"
            "  history [n]                  Show last n messages (default: 20)\n"
            "  clearhistory                 Clear chat history\n"
            "\n"
            "Notes:\n"
            "  - Paths are restricted to the ANNA-AI project folder for safety.\n"
            "  - Terminal needs ANNA_TERMINAL_ENABLE=1.\n"
            "  - Browser needs ANNA_BROWSER_ENABLE=1.\n"
            "  - Windows control needs ANNA_WINDOWS_CONTROL_ENABLE=1.\n"
            "  - Mouse needs ANNA_MOUSE_ENABLE=1.\n"
            "  - Keyboard needs ANNA_KEYBOARD_ENABLE=1.\n"
        )

    def respond(self, user_text: str) -> str:
        text = (user_text or "").strip()
        memory.set("last_user_text", text)

        if not text:
            return f"{self.name}: Say something or type 'help'."

        self._append_history("user", text)

        cmd, *rest = text.split(maxsplit=1)
        cmd_l = cmd.lower()
        arg = rest[0].strip() if rest else ""

        try:
            if cmd_l in {"help", "?"}:
                reply = f"{self.name}:\n{self._help_text()}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l in {"ls", "dir"}:
                path = arg if arg else "."
                items = files_tool.list_dir(path)
                if not items:
                    reply = f"{self.name}: (empty) {path}"
                    self._append_history("assistant", reply)
                    return reply

                lines = []
                for it in items:
                    if it["is_dir"]:
                        lines.append(f"{it['name']}/")
                    else:
                        size = it.get("size")
                        lines.append(f"{it['name']} ({size} bytes)" if size is not None else it["name"])
                reply = f"{self.name}: Listing {path}\n" + "\n".join(lines)
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "exists":
                if not arg:
                    reply = f"{self.name}: Usage: exists <path>"
                    self._append_history("assistant", reply)
                    return reply
                reply = f"{self.name}: {arg} -> {files_tool.exists(arg)}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "read":
                if not arg:
                    reply = f"{self.name}: Usage: read <path>"
                    self._append_history("assistant", reply)
                    return reply
                content = files_tool.read_text(arg)
                max_chars = 4000
                out = content[:max_chars]
                if len(content) > max_chars:
                    out += "\n...[truncated]..."
                reply = f"{self.name}: Contents of {arg}\n{out}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "write":
                if not arg or "::" not in arg:
                    reply = f"{self.name}: Usage: write <path> :: <text>"
                    self._append_history("assistant", reply)
                    return reply
                target, content = arg.split("::", 1)
                target = target.strip()
                content = content.lstrip()
                p = files_tool.write_text(target, content, overwrite=False)
                rel = p.relative_to(files_tool.base_dir)
                reply = f"{self.name}: Wrote {len(content)} chars -> {rel}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "run":
                if not arg:
                    reply = f"{self.name}: Usage: run <command>"
                    self._append_history("assistant", reply)
                    return reply
                r = terminal_tool.run(arg)
                stdout = (r.get("stdout") or "").strip()
                stderr = (r.get("stderr") or "").strip()
                parts = [f"{self.name}: returncode={r.get('returncode')}"]
                if stdout:
                    parts.append("stdout:\n" + stdout)
                if stderr:
                    parts.append("stderr:\n" + stderr)
                reply = "\n".join(parts)
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "search":
                if not arg:
                    reply = f"{self.name}: Usage: search <query>"
                    self._append_history("assistant", reply)
                    return reply
                r = browser_tool.search(arg)
                reply = f"{self.name}: Opened search for '{r.get('query')}'."
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "openurl":
                if not arg:
                    reply = f"{self.name}: Usage: openurl <https://...>"
                    self._append_history("assistant", reply)
                    return reply
                browser_tool.open_url(arg)
                reply = f"{self.name}: Opened URL."
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "openpath":
                if not arg:
                    reply = f"{self.name}: Usage: openpath <path>"
                    self._append_history("assistant", reply)
                    return reply
                windows_control.open_path(arg)
                reply = f"{self.name}: Opened path: {arg}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "mousepos":
                pos = mouse_control.position()
                reply = f"{self.name}: Mouse position x={pos.get('x')} y={pos.get('y')}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "type":
                if not arg:
                    reply = f"{self.name}: Usage: type <text>"
                    self._append_history("assistant", reply)
                    return reply
                r = keyboard_control.type_text(arg)
                reply = f"{self.name}: Typed {r.get('chars')} chars."
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "press":
                if not arg:
                    reply = f"{self.name}: Usage: press <key>"
                    self._append_history("assistant", reply)
                    return reply
                r = keyboard_control.press(arg)
                reply = f"{self.name}: Pressed {r.get('key')}."
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "hotkey":
                if not arg:
                    reply = f"{self.name}: Usage: hotkey <k1>+<k2>+..."
                    self._append_history("assistant", reply)
                    return reply
                keys = [k.strip() for k in arg.split("+") if k.strip()]
                if len(keys) < 2:
                    reply = f"{self.name}: Usage: hotkey <k1>+<k2>+..."
                    self._append_history("assistant", reply)
                    return reply
                keyboard_control.hotkey(*keys)
                reply = f"{self.name}: Hotkey pressed: {'+'.join(keys)}."
                self._append_history("assistant", reply)
                return reply

            # Learning: facts
            if cmd_l == "remember":
                if not arg:
                    reply = f"{self.name}: Usage: remember <key> = <value>"
                    self._append_history("assistant", reply)
                    return reply
                if ("=" not in arg) and ("::" not in arg):
                    reply = f"{self.name}: Usage: remember <key> = <value>"
                    self._append_history("assistant", reply)
                    return reply
                if "::" in arg:
                    key, value = arg.split("::", 1)
                else:
                    key, value = arg.split("=", 1)
                key = key.strip()
                value = value.strip()
                learner.remember(key, value)
                reply = f"{self.name}: Remembered {key}."
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "recall":
                if not arg:
                    reply = f"{self.name}: Usage: recall <key>"
                    self._append_history("assistant", reply)
                    return reply
                val = learner.recall(arg, default=None)
                if val is None:
                    reply = f"{self.name}: I don't have '{arg}' saved."
                    self._append_history("assistant", reply)
                    return reply
                reply = f"{self.name}: {arg} = {val}"
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "forget":
                if not arg:
                    reply = f"{self.name}: Usage: forget <key>"
                    self._append_history("assistant", reply)
                    return reply
                existed = learner.forget(arg)
                reply = f"{self.name}: Deleted {arg}." if existed else f"{self.name}: Nothing to delete for {arg}."
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "facts":
                keys = learner.list_keys()
                reply = f"{self.name}: No facts saved." if not keys else (f"{self.name}: Facts keys:\n" + "\n".join(keys))
                self._append_history("assistant", reply)
                return reply

            # TODO commands
            if cmd_l == "todo":
                if not arg:
                    reply = f"{self.name}: Usage: todo add <text> | todo list [all] | todo done <id> | todo clear"
                    self._append_history("assistant", reply)
                    return reply

                sub, *rest2 = arg.split(maxsplit=1)
                sub_l = sub.lower()
                sub_arg = rest2[0].strip() if rest2 else ""

                if sub_l == "add":
                    item = learner.todo_add(sub_arg)
                    reply = f"{self.name}: Added TODO #{item.get('id')}: {item.get('text')}"
                    self._append_history("assistant", reply)
                    return reply

                if sub_l == "list":
                    include_done = sub_arg.strip().lower() == "all"
                    todos = learner.todo_list(include_done=include_done)
                    if not todos:
                        reply = f"{self.name}: No todos."
                        self._append_history("assistant", reply)
                        return reply
                    lines = []
                    for t in todos:
                        mark = "✓" if t.get("done") else " "
                        lines.append(f"[{mark}] #{t.get('id')}: {t.get('text')}")
                    reply = f"{self.name}: TODOs:\n" + "\n".join(lines)
                    self._append_history("assistant", reply)
                    return reply

                if sub_l == "done":
                    if not sub_arg:
                        reply = f"{self.name}: Usage: todo done <id>"
                        self._append_history("assistant", reply)
                        return reply
                    try:
                        todo_id = int(sub_arg)
                    except Exception:
                        reply = f"{self.name}: Invalid id: {sub_arg}"
                        self._append_history("assistant", reply)
                        return reply
                    ok = learner.todo_done(todo_id)
                    reply = f"{self.name}: Marked TODO #{todo_id} done." if ok else f"{self.name}: TODO #{todo_id} not found (or already done)."
                    self._append_history("assistant", reply)
                    return reply

                if sub_l == "clear":
                    learner.todo_clear()
                    reply = f"{self.name}: Cleared all todos."
                    self._append_history("assistant", reply)
                    return reply

                reply = f"{self.name}: Usage: todo add <text> | todo list [all] | todo done <id> | todo clear"
                self._append_history("assistant", reply)
                return reply

            # History
            if cmd_l == "history":
                n = 20
                if arg:
                    try:
                        n = int(arg)
                    except Exception:
                        n = 20
                h = self._load_history()[-max(1, n) :]
                if not h:
                    reply = f"{self.name}: History is empty."
                    self._append_history("assistant", reply)
                    return reply
                lines = []
                for item in h:
                    role = item.get("role", "?")
                    t = item.get("text", "")
                    prefix = "You" if role == "user" else self.name
                    lines.append(t if (role != "user" and t.startswith(f"{self.name}:")) else f"{prefix}: {t}")
                reply = f"{self.name}: Last {len(h)} messages:\n" + "\n".join(lines)
                self._append_history("assistant", reply)
                return reply

            if cmd_l == "clearhistory":
                self._save_history([])
                reply = f"{self.name}: History cleared."
                self._append_history("assistant", reply)
                return reply

        except (
            FileToolError,
            TerminalToolError,
            BrowserToolError,
            WindowsControlError,
            MouseControlError,
            KeyboardControlError,
        ) as e:
            reply = f"{self.name}: Tool error: {e}"
            self._append_history("assistant", reply)
            return reply
        except Exception as e:
            reply = f"{self.name}: Error: {e}"
            self._append_history("assistant", reply)
            return reply

        reply = (
            f"{self.name}: I heard: '{text}'. "
            "Reasoning is still placeholder (LLM not connected yet). Type 'help' for commands."
        )
        self._append_history("assistant", reply)
        return reply


reasoner = Reasoner()
