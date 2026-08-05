from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from brain.memory import memory


@dataclass
class Learner:
    facts_key: str = "facts"
    todos_key: str = "todos"
    todo_next_id_key: str = "todo_next_id"

    # -------------------------
    # Facts
    # -------------------------
    def _load_facts(self) -> dict[str, Any]:
        data = memory.get(self.facts_key, {})
        return data if isinstance(data, dict) else {}

    def _save_facts(self, facts: dict[str, Any]) -> None:
        memory.set(self.facts_key, facts)

    def remember(self, key: str, value: Any) -> None:
        key = (key or "").strip()
        if not key:
            raise ValueError("Key is empty.")
        facts = self._load_facts()
        facts[key] = value
        self._save_facts(facts)

    def recall(self, key: str, default: Any = None) -> Any:
        key = (key or "").strip()
        if not key:
            raise ValueError("Key is empty.")
        facts = self._load_facts()
        return facts.get(key, default)

    def forget(self, key: str) -> bool:
        key = (key or "").strip()
        if not key:
            raise ValueError("Key is empty.")
        facts = self._load_facts()
        existed = key in facts
        if existed:
            del facts[key]
            self._save_facts(facts)
        return existed

    def list_keys(self) -> list[str]:
        facts = self._load_facts()
        return sorted([str(k) for k in facts.keys()], key=lambda x: x.lower())

    # -------------------------
    # TODOs
    # -------------------------
    def _now_utc(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_todos(self) -> list[dict[str, Any]]:
        data = memory.get(self.todos_key, [])
        return data if isinstance(data, list) else []

    def _save_todos(self, todos: list[dict[str, Any]]) -> None:
        memory.set(self.todos_key, todos)

    def _next_todo_id(self) -> int:
        cur = memory.get(self.todo_next_id_key, 1)
        try:
            cur_i = int(cur)
        except Exception:
            cur_i = 1
        memory.set(self.todo_next_id_key, cur_i + 1)
        return cur_i

    def todo_add(self, text: str) -> dict[str, Any]:
        t = (text or "").strip()
        if not t:
            raise ValueError("Todo text is empty.")
        todos = self._load_todos()
        item = {
            "id": self._next_todo_id(),
            "text": t,
            "done": False,
            "created_utc": self._now_utc(),
            "done_utc": None,
        }
        todos.append(item)
        self._save_todos(todos)
        return item

    def todo_list(self, include_done: bool = False) -> list[dict[str, Any]]:
        todos = self._load_todos()
        if include_done:
            return todos
        return [t for t in todos if not bool(t.get("done"))]

    def todo_done(self, todo_id: int) -> bool:
        todos = self._load_todos()
        changed = False
        for t in todos:
            if int(t.get("id", -1)) == int(todo_id):
                if not bool(t.get("done")):
                    t["done"] = True
                    t["done_utc"] = self._now_utc()
                    changed = True
                break
        if changed:
            self._save_todos(todos)
        return changed

    def todo_clear(self) -> None:
        self._save_todos([])


learner = Learner()
