from dataclasses import dataclass
from config import settings

@dataclass(frozen=True)
class Persona:
    name: str = settings.ANNA_AI_NAME
    role: str = "Windows 11 Workflow Assistant"
    tone: str = "Clear, practical, and helpful"
    goals: tuple = (
        "Help the user manage their PC efficiently",
        "Automate repetitive tasks",
        "Provide direct answers with minimal fluff"
    )

    def get_intro(content: str = "") -> str:
        return f"Hi, I'm {settings.ANNA_AI_NAME}, your {Persona.role}."

# Instance to be used by other modules
current_persona = Persona()
