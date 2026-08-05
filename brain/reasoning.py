from __future__ import annotations

from dataclasses import dataclass

from brain.personality import current_persona
from brain.memory import memory


@dataclass
class Reasoner:
    # Placeholder: later we will plug in an LLM + tools + RAG here.
    name: str = current_persona.name

    def respond(self, user_text: str) -> str:
        memory.set("last_user_text", user_text)
        return (
            f"{self.name}: I heard: '{user_text}'. "
            "Reasoning is placeholder right now (LLM not connected yet)."
        )


reasoner = Reasoner()
