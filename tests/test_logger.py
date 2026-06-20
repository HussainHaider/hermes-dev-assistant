"""Tests for the observability logger."""

import json
import os
import tempfile

from observability.logger import log_event


class TestLogger:
    def test_log_event_creates_record(self):
        """Verify log_event produces valid JSONL output."""
        log_event(
            agent="test_agent",
            skill="test_skill",
            tool="test_tool",
            model="test-model",
            input_msg="hello",
            output="world",
            latency_ms=42,
        )
        # Verify the log file exists and has content
        log_file = os.path.join(
            os.path.dirname(__file__), "..", "logs", "agent_activity.jsonl"
        )
        assert os.path.exists(log_file)

        # Read last line and validate JSON structure
        with open(log_file) as f:
            lines = f.readlines()

        last_record = json.loads(lines[-1])
        assert last_record["agent"] == "test_agent"
        assert last_record["skill"] == "test_skill"
        assert last_record["tool"] == "test_tool"
        assert last_record["model"] == "test-model"
        assert last_record["input_length"] == 5
        assert last_record["output_length"] == 5
        assert last_record["latency_ms"] == 42
        assert "timestamp" in last_record
