"""Tests for the User Memory module."""

import os
import tempfile

import pytest

from memory.user_memory import UserMemory


class TestUserMemory:
    def setup_method(self):
        """Create a temporary database for each test."""
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.memory = UserMemory(db_path=self.tmp.name)

    def teardown_method(self):
        """Clean up temporary database."""
        self.memory.close()
        os.unlink(self.tmp.name)

    def test_set_and_get(self):
        self.memory.set("repo", "owner/my-repo")
        assert self.memory.get("repo") == "owner/my-repo"

    def test_get_nonexistent(self):
        assert self.memory.get("nonexistent") is None

    def test_overwrite(self):
        self.memory.set("key", "value1")
        self.memory.set("key", "value2")
        assert self.memory.get("key") == "value2"

    def test_delete(self):
        self.memory.set("key", "value")
        assert self.memory.delete("key") is True
        assert self.memory.get("key") is None

    def test_delete_nonexistent(self):
        assert self.memory.delete("nonexistent") is False

    def test_get_all(self):
        self.memory.set("a", "1")
        self.memory.set("b", "2")
        all_prefs = self.memory.get_all()
        assert all_prefs == {"a": "1", "b": "2"}
