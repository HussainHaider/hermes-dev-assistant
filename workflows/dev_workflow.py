"""Dev Workflow — Main router that ties agents, skills, and tools together."""

from __future__ import annotations

import logging
from typing import Any

from agents.github_agent import GitHubAgent
from agents.planning_agent import PlanningAgent
from agents.report_agent import ReportAgent
from memory.user_memory import UserMemory
from skills.github_summary_skill import GitHubSummarySkill
from skills.standup_skill import StandupSkill
from skills.task_extraction_skill import TaskExtractionSkill
from tools.llm_client import get_llm
from tools.notion_tool import NotionTool

logger = logging.getLogger(__name__)


class DevWorkflow:
    """Main workflow router for the Developer Productivity Assistant.

    Routes incoming messages to the appropriate agent + skill combination
    based on keyword matching and intent detection.
    """

    def __init__(self) -> None:
        self.github_agent = GitHubAgent()
        self.planning_agent = PlanningAgent()
        self.report_agent = ReportAgent()
        self.notion_tool = NotionTool()
        self.memory = UserMemory()
        self.llm = get_llm()

        # Skills
        self.github_summary_skill = GitHubSummarySkill()
        self.standup_skill = StandupSkill()
        self.task_extraction_skill = TaskExtractionSkill()

    def _get_repo(self) -> str:
        """Get the default repo from memory or environment."""
        saved_repo = self.memory.get("default_repo")
        if saved_repo:
            return saved_repo
        return self.github_agent.default_repo

    def handle(self, user_message: str) -> str:
        """Route user message to the appropriate agent/skill pipeline."""
        msg = user_message.lower().strip()

        try:
            if any(kw in msg for kw in ["standup", "daily report", "morning update"]):
                return self._handle_standup()

            elif any(kw in msg for kw in ["issues", "github", "open issues"]):
                return self._handle_github(user_message)

            elif any(kw in msg for kw in ["plan", "prioritize", "organize"]):
                return self._handle_planning(user_message)

            elif any(kw in msg for kw in ["extract tasks", "action items", "meeting notes"]):
                return self._handle_task_extraction(user_message)

            elif any(kw in msg for kw in ["weekly", "weekly summary", "week report"]):
                return self._handle_weekly_report()

            elif msg.startswith("set repo "):
                repo = user_message[9:].strip()
                self.memory.set("default_repo", repo)
                return f"Default repository set to: {repo}"

            elif any(kw in msg for kw in ["add task", "create task", "new task"]):
                return self._handle_add_task(user_message)

            elif any(kw in msg for kw in ["my tasks", "notion tasks", "task list"]):
                return self._handle_list_tasks()

            else:
                return self._handle_fallback(user_message)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return f"Sorry, I encountered an error: {str(e)}"

    def _handle_standup(self) -> str:
        """Full standup workflow: fetch GitHub + Notion data, generate report."""
        repo = self._get_repo()
        issues = self.github_agent.get_open_issues(repo)
        commits = self.github_agent.get_recent_commits(repo)
        tasks = self.notion_tool.get_tasks()

        data = {"issues": issues, "tasks": tasks, "commits": commits}
        report = self.standup_skill.execute(data, self.llm)

        # Also save via report agent
        context: dict[str, Any] = {"summary": data}
        self.report_agent.run("standup", context)

        return report

    def _handle_github(self, user_message: str) -> str:
        """Handle GitHub-related queries."""
        repo = self._get_repo()
        issues = self.github_agent.get_open_issues(repo)
        return self.github_summary_skill.execute(issues, self.llm)

    def _handle_planning(self, user_message: str) -> str:
        """Handle planning/prioritization requests."""
        tasks = self.notion_tool.get_tasks()
        return self.planning_agent.run(user_message, {"task_items": tasks})

    def _handle_task_extraction(self, user_message: str) -> str:
        """Extract tasks from free-form text."""
        # Remove the trigger phrase to get the actual content
        for phrase in ["extract tasks from", "action items from", "extract tasks"]:
            if phrase in user_message.lower():
                text = user_message[user_message.lower().index(phrase) + len(phrase):].strip()
                break
        else:
            text = user_message

        tasks = self.task_extraction_skill.execute(text, self.llm)
        return "\n".join(tasks) if tasks else "No actionable tasks found."

    def _handle_weekly_report(self) -> str:
        """Generate a weekly summary report."""
        repo = self._get_repo()
        issues = self.github_agent.get_open_issues(repo)
        tasks = self.notion_tool.get_tasks()
        context: dict[str, Any] = {"summary": {"issues": issues, "tasks": tasks}}
        return self.report_agent.run("weekly summary", context)

    def _handle_add_task(self, user_message: str) -> str:
        """Add a new task to Notion."""
        # Extract task title from message
        for prefix in ["add task ", "create task ", "new task "]:
            if prefix in user_message.lower():
                title = user_message[user_message.lower().index(prefix) + len(prefix):].strip()
                break
        else:
            title = user_message

        result = self.notion_tool.add_task(title)
        return f"Task created: '{title}'\nNotion link: {result['url']}"

    def _handle_list_tasks(self) -> str:
        """List current tasks from Notion."""
        tasks = self.notion_tool.get_tasks()
        if not tasks:
            return "No tasks found in your Notion database."

        lines = ["**Your Tasks:**\n"]
        for task in tasks:
            status_emoji = {"To Do": "⬜", "In Progress": "🔄", "Done": "✅"}.get(
                task["status"], "❓"
            )
            lines.append(f"{status_emoji} {task['title']} — *{task['status']}*")
        return "\n".join(lines)

    def _handle_fallback(self, user_message: str) -> str:
        """Fallback: use LLM to answer directly."""
        system = (
            "You are a helpful developer productivity assistant. "
            "You help software engineers with their daily workflow, "
            "task management, and code-related questions. "
            "Keep responses concise and actionable."
        )
        return self.llm.complete_with_system(system, user_message)
