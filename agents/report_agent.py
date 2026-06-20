"""Report Agent — Drafts standup reports and weekly summaries."""

from __future__ import annotations

import datetime
import os
import time
from typing import Any, Optional

from observability.logger import log_event
from tools.llm_client import get_llm


class ReportAgent:
    """Agent responsible for drafting standup and summary reports.

    Generates formatted standup reports (Yesterday/Today/Blockers) and
    saves them to local markdown files.
    """

    name = "report_agent"
    description = "Drafts standup and weekly summary reports"

    def __init__(self) -> None:
        self.llm = get_llm()
        self.reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def run(self, task: str, context: dict[str, Any]) -> str:
        """Generate a standup or summary report from provided data."""
        start = time.time()
        summary_data = context.get("summary", "")

        if "weekly" in task.lower():
            prompt = (
                "Write a professional weekly summary report for a software engineer.\n"
                f"Data: {summary_data}\n"
                "Format: Key Accomplishments / In Progress / Next Week / Risks\n"
                "Keep it under 250 words."
            )
            filename = f"weekly_{datetime.date.today()}.md"
        else:
            prompt = (
                "Write a professional standup report for a software engineer.\n"
                f"Data: {summary_data}\n"
                "Format: Yesterday / Today / Blockers\n"
                "Keep it under 150 words."
            )
            filename = f"standup_{datetime.date.today()}.md"

        model_name = self.llm.model_name
        report = self.llm.complete(prompt)

        # Save report to file
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, "w") as f:
            f.write(f"# {filename.replace('.md', '').replace('_', ' ').title()}\n\n")
            f.write(report)

        latency = int((time.time() - start) * 1000)
        log_event(
            agent=self.name,
            skill="report_generation",
            tool="llm",
            model=model_name,
            input_msg=task,
            output=report,
            latency_ms=latency,
        )
        return report
