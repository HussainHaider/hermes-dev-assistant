"""Tests for skills modules."""

import pytest


class MockLLM:
    """Mock LLM client for testing."""

    model_name = "test-model"

    def complete(self, prompt: str, **kwargs) -> str:
        if "standup" in prompt.lower() or "yesterday" in prompt.lower():
            return (
                "**Yesterday:** Reviewed PR #42, fixed auth bug\n"
                "**Today:** Implement caching layer, code review\n"
                "**Blockers:** Waiting on API key from DevOps"
            )
        elif "summarize" in prompt.lower():
            return "3 critical bugs, 2 feature requests, 5 minor improvements"
        elif "extract" in prompt.lower():
            return "1. Update documentation\n2. Fix login bug\n3. Deploy to staging"
        elif "plan" in prompt.lower() or "priorit" in prompt.lower():
            return (
                "**P1 (Critical):**\n- Fix auth bug (2h)\n"
                "**P2 (Important):**\n- Code review (1h)\n"
                "**P3 (Nice to have):**\n- Update docs (30m)"
            )
        return "Generic response"


class TestGitHubSummarySkill:
    def test_execute_with_issues(self):
        from skills.github_summary_skill import GitHubSummarySkill

        skill = GitHubSummarySkill()
        issues = [
            {"number": 1, "title": "Login broken", "labels": ["bug", "critical"]},
            {"number": 2, "title": "Add dark mode", "labels": ["feature"]},
            {"number": 3, "title": "Typo in docs", "labels": ["docs"]},
        ]
        result = skill.execute(issues, MockLLM())
        assert result  # LLM produces a summary
        assert len(result) > 0

    def test_execute_with_empty_issues(self):
        from skills.github_summary_skill import GitHubSummarySkill

        skill = GitHubSummarySkill()
        result = skill.execute([], MockLLM())
        assert result == "No open issues found."


class TestStandupSkill:
    def test_execute_with_data(self):
        from skills.standup_skill import StandupSkill

        skill = StandupSkill()
        data = {
            "issues": [{"number": 1, "title": "Bug fix"}],
            "tasks": [{"title": "Deploy", "status": "In Progress"}],
            "commits": [{"sha": "abc1234", "message": "Fix auth"}],
        }
        result = skill.execute(data, MockLLM())
        assert "Yesterday" in result
        assert "Today" in result
        assert "Blockers" in result

    def test_execute_with_empty_data(self):
        from skills.standup_skill import StandupSkill

        skill = StandupSkill()
        result = skill.execute({}, MockLLM())
        assert result  # Should still produce output


class TestTaskExtractionSkill:
    def test_execute_with_text(self):
        from skills.task_extraction_skill import TaskExtractionSkill

        skill = TaskExtractionSkill()
        text = "We need to update docs, fix the login bug, and deploy to staging."
        result = skill.execute(text, MockLLM())
        assert isinstance(result, list)
        assert len(result) == 3

    def test_execute_with_empty_text(self):
        from skills.task_extraction_skill import TaskExtractionSkill

        skill = TaskExtractionSkill()
        result = skill.execute("", MockLLM())
        assert result == []
