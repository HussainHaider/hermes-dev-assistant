"""Planning Agent — Organizes tasks into structured daily/weekly plans."""

from __future__ import annotations

import time
from typing import Any, Optional

from observability.logger import log_event
from tools.llm_client import get_llm


class PlanningAgent:
    """Agent responsible for converting raw task lists into structured plans.

    Creates daily/weekly plans with priorities (P1/P2/P3) and generates
    actionable standup notes.
    """

    name = "planning_agent"
    description = "Organizes tasks into structured plans and standup reports"

    def __init__(self) -> None:
        self.llm = get_llm()

    def run(self, task: str, context: dict[str, Any]) -> str:
        """Generate a structured plan from the provided task items."""
        start = time.time()
        items = context.get("task_items", [])

        prompt = (
            "You are a planning assistant for a software engineer.\n"
            f"Given these items: {items}\n"
            "Create a structured daily plan with priorities (P1/P2/P3).\n"
            "Format: bullet points, concise, actionable.\n"
            "Group by priority level. Include estimated time for each task."
        )

        model_name = self.llm.model_name
        result = self.llm.complete(prompt)

        latency = int((time.time() - start) * 1000)
        log_event(
            agent=self.name,
            skill="task_planning",
            tool="llm",
            model=model_name,
            input_msg=task,
            output=result,
            latency_ms=latency,
        )
        return result
