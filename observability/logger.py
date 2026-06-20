"""Structured Logger — Records every agent call in JSONL format."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

# Ensure logs directory exists
_logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(_logs_dir, exist_ok=True)

_log_file = os.path.join(_logs_dir, "agent_activity.jsonl")

logging.basicConfig(
    filename=_log_file,
    level=logging.INFO,
    format="%(message)s",
)

_logger = logging.getLogger("hermes_dev_assistant")
_logger.setLevel(logging.INFO)

# Add file handler if not already present
if not _logger.handlers:
    handler = logging.FileHandler(_log_file)
    handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(handler)


def log_event(
    agent: str,
    skill: str,
    tool: str,
    model: str,
    input_msg: str,
    output: str,
    latency_ms: int,
) -> None:
    """Log a structured event for observability.

    Each call is recorded as a single JSON line in the JSONL log file.
    This enables easy analysis of agent performance, latency, and usage patterns.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "skill": skill,
        "tool": tool,
        "model": model,
        "input_length": len(input_msg),
        "output_length": len(output),
        "latency_ms": latency_ms,
    }
    _logger.info(json.dumps(record))
