from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    user_task: str

    plan: list[str] = field(default_factory=list)

    current_step: int = 0

    observations: list[dict[str, Any]] = field(
        default_factory=list
    )

    tool_history: list[dict[str, Any]] = field(
        default_factory=list
    )

    final_answer: str = ""

    status: str = "planning"