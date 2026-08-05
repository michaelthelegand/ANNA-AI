from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from brain.memory import memory


@dataclass
class Learner:
    facts_key: str = "facts"

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


learner = Learner()
