# SPDX-License-Identifier: GPL-3.0-or-later
#
# GNS3-Copilot - AI-powered Network Lab Assistant for GNS3
#
# This file is part of GNS3-Copilot project.
#
# GNS3-Copilot is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# GNS3-Copilot is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNS3-Copilot. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (C) 2025 Guobin Yue
# Author: Guobin Yue
#
# Project Home: https://github.com/yueguobin/gns3-copilot
#

"""
Tests for checkpoint_utils module.
Contains test cases for LangGraph checkpoint utility functions.

Test Coverage:
1. TestListThreadIds
   - Basic thread ID listing functionality
   - Empty database handling
   - Thread ID ordering (most recent first)
   - Database error handling
   - Unique thread IDs only

2. TestEdgeCases
   - Non-existent checkpointer
   - Corrupted database
   - Missing checkpoints table

3. TestGenerateThreadId
   - UUID generation
   - Uniqueness

4. TestValidateCheckpointData
   - Valid checkpoint data
   - Missing required fields
   - Invalid data types
   - Missing channel_values
   - Missing messages

5. TestExportCheckpointToFile
   - Successful export
   - Non-existent thread
   - File write errors
   - Invalid checkpointer

6. TestImportCheckpointFromFile
   - Successful import
   - Invalid JSON format
   - Missing required fields
   - File not found
   - Custom thread_id

Total Test Cases: 30+
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.messages.tool import ToolCall

from gns3_copilot.agent.checkpoint_utils import (
    export_checkpoint_to_file,
    generate_thread_id,
    import_checkpoint_from_file,
    inspect_session,
    list_thread_ids,
    serialize_message,
    deserialize_message,
    validate_checkpoint_data,
    validate_messages_for_ui,
)


class TestListThreadIds:
    """Test list_thread_ids function."""
    
    def test_basic_thread_listing(self):
        """Test basic thread ID listing with multiple threads."""
        # Create mock checkpointer with database connection
        mock_checkpointer = Mock()
        
        # Create in-memory SQLite database for testing
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        
        # Insert test data
        test_threads = ["thread-1", "thread-2", "thread-3"]
        for i, thread_id in enumerate(test_threads, 1):
            conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", (thread_id,))
            # Add multiple checkpoints per thread
            conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", (thread_id,))
        
        conn.commit()
        mock_checkpointer.conn = conn
        
        # Test the function
        result = list_thread_ids(mock_checkpointer)
        
        # Should return unique thread IDs
        assert len(result) == 3
        assert set(result) == set(test_threads)
        
        # Should be ordered by most recent (descending rowid)
        # Last inserted should be first
        assert result[0] == "thread-3"
        
        conn.close()
    
    def test_empty_database(self):
        """Test with empty checkpoint database."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        conn.commit()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        assert result == []
        
        conn.close()
    
    def test_single_thread(self):
        """Test with single thread."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", ("single-thread",))
        conn.commit()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        assert len(result) == 1
        assert result[0] == "single-thread"
        
        conn.close()
    
    def test_duplicate_threads(self):
        """Test that duplicate thread IDs are filtered out."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        
        # Insert same thread multiple times
        thread_id = "duplicate-thread"
        for _ in range(5):
            conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", (thread_id,))
        
        conn.commit()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        # Should return only unique thread IDs
        assert len(result) == 1
        assert result[0] == thread_id
        
        conn.close()
    
    def test_uuid_thread_ids(self):
        """Test with UUID-format thread IDs."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        
        # Insert UUID-like thread IDs
        uuid_threads = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
        ]
        
        for thread_id in uuid_threads:
            conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", (thread_id,))
        
        conn.commit()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        assert len(result) == 3
        assert set(result) == set(uuid_threads)
        
        conn.close()


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_missing_table(self):
        """Test handling of missing checkpoints table."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        # Don't create the checkpoints table
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        # Should return empty list on error
        assert result == []
        
        conn.close()
    
    def test_database_error(self):
        """Test handling of database connection errors."""
        mock_checkpointer = Mock()
        
        # Mock a connection that raises error
        mock_conn = Mock()
        mock_conn.execute.side_effect = Exception("Database connection lost")
        mock_checkpointer.conn = mock_conn
        
        result = list_thread_ids(mock_checkpointer)
        
        # Should return empty list on error
        assert result == []
    
    def test_none_checkpointer(self):
        """Test with None checkpointer."""
        result = list_thread_ids(None)
        
        # Should return empty list on error
        assert result == []
    
    def test_missing_conn_attribute(self):
        """Test with checkpointer missing conn attribute."""
        mock_checkpointer = Mock(spec=[])  # Empty spec, no conn attribute
        
        result = list_thread_ids(mock_checkpointer)
        
        # Should return empty list on error
        assert result == []
    
    def test_corrupted_database(self):
        """Test with corrupted database."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        conn.commit()
        
        # Corrupt the database by closing it
        conn.close()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        # Should return empty list on error
        assert result == []


class TestOrdering:
    """Test thread ID ordering behavior."""
    
    def test_most_recent_first(self):
        """Test that most recent threads appear first."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        
        # Insert threads in order
        threads_order = ["first-thread", "second-thread", "third-thread"]
        for thread_id in threads_order:
            conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", (thread_id,))
        
        conn.commit()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        # Verify order: most recent (last inserted) should be first
        assert result[0] == "third-thread"
        assert result[1] == "second-thread"
        assert result[2] == "first-thread"
        
        conn.close()
    
    def test_mixed_activity_ordering(self):
        """Test ordering with mixed activity across threads."""
        mock_checkpointer = Mock()
        
        conn = sqlite3.connect(":memory:")
        conn.execute(
            "CREATE TABLE checkpoints (thread_id TEXT, rowid INTEGER PRIMARY KEY AUTOINCREMENT)"
        )
        
        # Simulate mixed activity: Thread A, then B, then A again
        activity = [
            ("thread-a", 1),
            ("thread-b", 2),
            ("thread-a", 3),
            ("thread-c", 4),
        ]
        
        for thread_id, _ in activity:
            conn.execute("INSERT INTO checkpoints (thread_id) VALUES (?)", (thread_id,))
        
        conn.commit()
        mock_checkpointer.conn = conn
        
        result = list_thread_ids(mock_checkpointer)
        
        # Verify order: unique threads ordered by most recent activity
        # Thread-c (most recent), thread-a, thread-b
        assert len(result) == 3
        assert result[0] == "thread-c"  # Most recent
        assert result[1] == "thread-a"  # Second most recent
        assert result[2] == "thread-b"  # Oldest
        
        conn.close()


class TestGenerateThreadId:
    """Test generate_thread_id function."""

    def test_generate_uuid_thread_id(self):
        """Test that generate_thread_id returns a valid UUID string."""
        thread_id = generate_thread_id()
        assert isinstance(thread_id, str)
        assert len(thread_id) == 36  # UUID format: 8-4-4-4-12

    def test_generate_unique_thread_ids(self):
        """Test that each generated thread_id is unique."""
        thread_ids = [generate_thread_id() for _ in range(100)]
        assert len(set(thread_ids)) == 100  # All unique


class TestValidateCheckpointData:
    """Test validate_checkpoint_data function."""

    def test_valid_checkpoint_data(self):
        """Test validation with valid checkpoint data."""
        valid_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "1f029ca3-1f5b-6704-8004-820c16b69a5a",
                "channel_values": {
                    "messages": [
                        {"role": "user", "content": "hi!"},
                        {"role": "assistant", "content": "Hello!"}
                    ],
                    "conversation_title": "GNS3 Session",
                    "llm_calls": 5
                },
                "channel_versions": {
                    "messages": "00000000000000000000000000000006.0.3205149138784782"
                },
                "versions_seen": {},
                "next": None
            }
        }

        is_valid, error_msg = validate_checkpoint_data(valid_data)
        assert is_valid is True
        assert error_msg == ""

    def test_missing_checkpoint_field(self):
        """Test validation when checkpoint field is missing."""
        invalid_data = {"other_field": "value"}
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "Missing required field: checkpoint" in error_msg

    def test_checkpoint_not_dict(self):
        """Test validation when checkpoint is not a dictionary."""
        invalid_data = {"checkpoint": "not_a_dict"}
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "checkpoint must be a dictionary" in error_msg

    def test_missing_top_level_checkpoint_fields(self):
        """Test validation when required top-level fields are missing."""
        invalid_data = {
            "checkpoint": {
                "v": 3,
                # Missing: ts, id, channel_values, channel_versions
            }
        }
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "Missing required checkpoint field" in error_msg

    def test_missing_channel_values(self):
        """Test validation when channel_values is missing."""
        invalid_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "1f029ca3-1f5b-6704-8004-820c16b69a5a",
                "channel_versions": {}
                # Missing: channel_values
            }
        }
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "Missing required checkpoint field: channel_values" in error_msg

    def test_channel_values_not_dict(self):
        """Test validation when channel_values is not a dictionary."""
        invalid_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "1f029ca3-1f5b-6704-8004-820c16b69a5a",
                "channel_values": "not_a_dict",
                "channel_versions": {}
            }
        }
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "channel_values must be a dictionary" in error_msg

    def test_missing_messages(self):
        """Test validation when messages field is missing."""
        invalid_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "1f029ca3-1f5b-6704-8004-820c16b69a5a",
                "channel_values": {
                    "conversation_title": "GNS3 Session"
                    # Missing: messages
                },
                "channel_versions": {}
            }
        }
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "Missing required field: channel_values.messages" in error_msg

    def test_messages_not_list(self):
        """Test validation when messages is not a list."""
        invalid_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "1f029ca3-1f5b-6704-8004-820c16b69a5a",
                "channel_values": {
                    "messages": "not_a_list"
                },
                "channel_versions": {}
            }
        }
        is_valid, error_msg = validate_checkpoint_data(invalid_data)
        assert is_valid is False
        assert "channel_values.messages must be a list" in error_msg

    def test_data_not_dict(self):
        """Test validation when input is not a dictionary."""
        is_valid, error_msg = validate_checkpoint_data("not_a_dict")
        assert is_valid is False
        assert "Data must be a dictionary" in error_msg


class TestExportCheckpointToFile:
    """Test export_checkpoint_to_file function."""

    def test_successful_export(self):
        """Test successful checkpoint export to file."""
        # Create mock checkpointer
        mock_checkpointer = Mock()
        mock_tuple = Mock()
        mock_tuple.checkpoint = {
            "v": 3,
            "ts": "2025-05-05T16:01:24.680462+00:00",
            "id": "test-id",
            "channel_values": {
                "messages": [{"role": "user", "content": "test"}]
            },
            "channel_versions": {}
        }
        mock_checkpointer.get_tuple.return_value = mock_tuple

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            from gns3_copilot.agent.checkpoint_utils import export_checkpoint_to_file

            result = export_checkpoint_to_file(
                mock_checkpointer, "test-thread-id", temp_file
            )
            assert result is True

            # Verify file was created and contains valid JSON
            with open(temp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "checkpoint" in data
            assert data["checkpoint"]["v"] == 3

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_export_nonexistent_thread(self):
        """Test export when thread doesn't exist."""
        mock_checkpointer = Mock()
        mock_checkpointer.get_tuple.return_value = None

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            from gns3_copilot.agent.checkpoint_utils import export_checkpoint_to_file

            result = export_checkpoint_to_file(
                mock_checkpointer, "nonexistent-thread", temp_file
            )
            assert result is False

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_export_with_unicode_content(self):
        """Test export with Chinese characters."""
        mock_checkpointer = Mock()
        mock_tuple = Mock()
        mock_tuple.checkpoint = {
            "v": 3,
            "ts": "2025-05-05T16:01:24.680462+00:00",
            "id": "test-id",
            "channel_values": {
                "messages": [{"role": "user", "content": "你好，世界！"}],
                "conversation_title": "GNS3 项目"
            },
            "channel_versions": {}
        }
        mock_checkpointer.get_tuple.return_value = mock_tuple

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            from gns3_copilot.agent.checkpoint_utils import export_checkpoint_to_file

            result = export_checkpoint_to_file(
                mock_checkpointer, "test-thread-id", temp_file
            )
            assert result is True

            # Verify Chinese characters are preserved
            with open(temp_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert "你好，世界！" in content
            assert "GNS3 项目" in content

        finally:
            Path(temp_file).unlink(missing_ok=True)


class TestMessageSerialization:
    """Test serialize_message and deserialize_message functions."""

    def test_serialize_human_message(self):
        """Test serialization of HumanMessage."""
        from langchain.messages import HumanMessage

        msg = HumanMessage(
            content="Hello, world!",
            additional_kwargs={"key": "value"},
            response_metadata={"meta": "data"},
            id="msg-123",
        )

        serialized = serialize_message(msg)

        assert serialized["type"] == "human"
        assert serialized["content"] == "Hello, world!"
        assert serialized["additional_kwargs"] == {"key": "value"}
        assert serialized["response_metadata"] == {"meta": "data"}
        assert serialized["id"] == "msg-123"

    def test_serialize_ai_message_with_tool_calls(self):
        """Test serialization of AIMessage with tool_calls."""
        from langchain.messages import AIMessage

        msg = AIMessage(
            content="I'll help you with that.",
            tool_calls=[
                {
                    "id": "call-1",
                    "name": "test_tool",
                    "args": {"param": "value"},
                    "type": "tool_call",
                }
            ],
            additional_kwargs={},
            response_metadata={},
            id="ai-msg-123",
        )

        serialized = serialize_message(msg)

        assert serialized["type"] == "ai"
        assert serialized["content"] == "I'll help you with that."
        assert len(serialized["tool_calls"]) == 1
        assert serialized["tool_calls"][0]["id"] == "call-1"
        assert serialized["tool_calls"][0]["name"] == "test_tool"
        assert serialized["tool_calls"][0]["args"] == {"param": "value"}

    def test_serialize_ai_message_gemini_format(self):
        """Test serialization of AIMessage with Gemini list format content."""
        from langchain.messages import AIMessage

        msg = AIMessage(
            content=[{"type": "text", "text": "Gemini response"}],
            tool_calls=[],
        )

        serialized = serialize_message(msg)

        assert serialized["type"] == "ai"
        assert serialized["content"] == [{"type": "text", "text": "Gemini response"}]

    def test_serialize_tool_message(self):
        """Test serialization of ToolMessage."""
        from langchain.messages import ToolMessage

        msg = ToolMessage(
            content="Tool execution result",
            tool_call_id="call-1",
            name="test_tool",
            additional_kwargs={},
            response_metadata={},
            id="tool-msg-123",
        )

        serialized = serialize_message(msg)

        assert serialized["type"] == "tool"
        assert serialized["content"] == "Tool execution result"
        assert serialized["tool_call_id"] == "call-1"
        assert serialized["name"] == "test_tool"
        assert serialized["id"] == "tool-msg-123"

    def test_deserialize_human_message(self):
        """Test deserialization of HumanMessage."""
        msg_dict = {
            "type": "human",
            "content": "Hello, world!",
            "additional_kwargs": {"key": "value"},
            "response_metadata": {"meta": "data"},
            "id": "msg-123",
        }

        deserialized = deserialize_message(msg_dict)

        assert isinstance(deserialized, HumanMessage)
        assert deserialized.content == "Hello, world!"
        assert deserialized.additional_kwargs == {"key": "value"}
        assert deserialized.response_metadata == {"meta": "data"}
        assert deserialized.id == "msg-123"

    def test_deserialize_ai_message_with_tool_calls(self):
        """Test deserialization of AIMessage with tool_calls."""
        msg_dict = {
            "type": "ai",
            "content": "I'll help you with that.",
            "tool_calls": [
                {
                    "id": "call-1",
                    "name": "test_tool",
                    "args": {"param": "value"},
                    "type": "tool_call",
                }
            ],
            "additional_kwargs": {},
            "response_metadata": {},
            "id": "ai-msg-123",
        }

        deserialized = deserialize_message(msg_dict)

        assert isinstance(deserialized, AIMessage)
        assert deserialized.content == "I'll help you with that."
        assert len(deserialized.tool_calls) == 1
        assert deserialized.tool_calls[0]["id"] == "call-1"
        assert deserialized.tool_calls[0]["name"] == "test_tool"
        assert deserialized.tool_calls[0]["args"] == {"param": "value"}

    def test_deserialize_tool_message(self):
        """Test deserialization of ToolMessage."""
        msg_dict = {
            "type": "tool",
            "content": "Tool execution result",
            "tool_call_id": "call-1",
            "name": "test_tool",
            "additional_kwargs": {},
            "response_metadata": {},
            "id": "tool-msg-123",
        }

        deserialized = deserialize_message(msg_dict)

        assert isinstance(deserialized, ToolMessage)
        assert deserialized.content == "Tool execution result"
        assert deserialized.tool_call_id == "call-1"
        assert deserialized.name == "test_tool"

    def test_serialize_deserialize_roundtrip(self):
        """Test that serialize/deserialize preserves message data."""
        from langchain.messages import HumanMessage, AIMessage, ToolMessage

        # Test HumanMessage
        original_human = HumanMessage(content="Test message", id="human-1")
        serialized_human = serialize_message(original_human)
        deserialized_human = deserialize_message(serialized_human)
        assert isinstance(deserialized_human, HumanMessage)
        assert deserialized_human.content == original_human.content

        # Test AIMessage
        original_ai = AIMessage(
            content="AI response",
            tool_calls=[{"id": "call-1", "name": "tool", "args": {}, "type": "tool_call"}],
            id="ai-1",
        )
        serialized_ai = serialize_message(original_ai)
        deserialized_ai = deserialize_message(serialized_ai)
        assert isinstance(deserialized_ai, AIMessage)
        assert deserialized_ai.content == original_ai.content
        assert len(deserialized_ai.tool_calls) == 1

        # Test ToolMessage
        original_tool = ToolMessage(
            content="Tool result",
            tool_call_id="call-1",
            name="tool",
            id="tool-1",
        )
        serialized_tool = serialize_message(original_tool)
        deserialized_tool = deserialize_message(serialized_tool)
        assert isinstance(deserialized_tool, ToolMessage)
        assert deserialized_tool.content == original_tool.content


class TestValidateMessagesForUI:
    """Test validate_messages_for_ui function."""

    def test_valid_messages(self):
        """Test validation with valid messages."""
        from langchain.messages import HumanMessage, AIMessage

        messages = [
            HumanMessage(content="Hello!"),
            AIMessage(content="Hi there!"),
        ]

        is_valid, error_msg, errors = validate_messages_for_ui(messages)

        assert is_valid is True
        assert error_msg == ""
        assert len(errors) == 0

    def test_missing_content_field(self):
        """Test validation when message is missing content field."""
        from langchain.messages import HumanMessage

        # Create a mock message without content
        msg = MagicMock(spec=HumanMessage)
        del msg.content  # Remove content attribute

        messages = [msg]
        is_valid, error_msg, errors = validate_messages_for_ui(messages)

        assert is_valid is False
        assert "Missing content field" in error_msg
        assert len(errors) > 0

    def test_ai_message_with_valid_tool_calls(self):
        """Test validation when AIMessage has valid tool_calls."""
        from langchain.messages import AIMessage

        msg = AIMessage(
            content="I'll use tools",
            tool_calls=[
                ToolCall(
                    id="call-1",
                    name="test_tool",
                    args={"param": "value"}
                )
            ],
        )

        messages = [msg]
        is_valid, error_msg, errors = validate_messages_for_ui(messages)

        assert is_valid is True
        assert error_msg == ""
        assert len(errors) == 0

    def test_tool_message_missing_fields(self):
        """Test validation when ToolMessage is missing required fields."""
        from langchain.messages import ToolMessage

        msg = ToolMessage(
            content="Result",
            tool_call_id="",  # Empty tool_call_id
            name="",  # Empty name
        )

        messages = [msg]
        is_valid, error_msg, errors = validate_messages_for_ui(messages)

        assert is_valid is False
        assert len(errors) > 0

    def test_unknown_message_type(self):
        """Test validation with unknown message type."""
        messages = [{"type": "unknown", "content": "data"}]

        is_valid, error_msg, errors = validate_messages_for_ui(messages)

        assert is_valid is False
        assert "Unknown message type" in error_msg

    def test_empty_messages(self):
        """Test validation with empty message list."""
        messages = []
        is_valid, error_msg, errors = validate_messages_for_ui(messages)

        assert is_valid is True
        assert error_msg == ""
        assert len(errors) == 0


class TestInspectSession:
    """Test inspect_session function."""

    def test_inspect_session_basic(self):
        """Test basic session inspection."""
        mock_graph = Mock()
        mock_snapshot = Mock()
        mock_snapshot.next = ["agent"]
        mock_snapshot.tasks = []
        mock_snapshot.interrupts = []
        mock_snapshot.metadata = {"step": 5}
        mock_snapshot.values = {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi"),
            ],
            "conversation_title": "Test Session",
            "selected_project": None,
        }
        mock_graph.get_state.return_value = mock_snapshot

        result = inspect_session("test-thread", mock_graph, verbose=False)

        assert result["thread_id"] == "test-thread"
        assert result["next"] == ["agent"]
        assert result["message_count"] == 2
        assert result["message_types"]["human"] == 1
        assert result["message_types"]["ai"] == 1
        assert result["step"] == 5
        assert result["ui_compatible"] is True
        assert result["conversation_title"] == "Test Session"

    def test_inspect_session_with_tool_calls(self):
        """Test session inspection with tool calls."""
        mock_graph = Mock()
        mock_snapshot = Mock()
        mock_snapshot.next = None
        mock_snapshot.tasks = []
        mock_snapshot.interrupts = []
        mock_snapshot.metadata = {}
        mock_snapshot.values = {
            "messages": [
                AIMessage(
                    content="I'll use tools",
                    tool_calls=[
                        {"id": "call-1", "name": "tool", "args": {}, "type": "tool_call"}
                    ],
                ),
                ToolMessage(content="Result", tool_call_id="call-1", name="tool"),
            ],
        }
        mock_graph.get_state.return_value = mock_snapshot

        result = inspect_session("test-thread", mock_graph, verbose=False)

        assert result["message_count"] == 2
        assert result["message_types"]["ai"] == 1
        assert result["message_types"]["tool"] == 1

    def test_inspect_session_verbose(self):
        """Test session inspection with verbose output."""
        mock_graph = Mock()
        mock_snapshot = Mock()
        mock_snapshot.next = None
        mock_snapshot.tasks = []
        mock_snapshot.interrupts = []
        mock_snapshot.metadata = {}
        mock_snapshot.values = {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi"),
            ],
        }
        mock_graph.get_state.return_value = mock_snapshot

        result = inspect_session("test-thread", mock_graph, verbose=True)

        assert "messages_preview" in result
        assert len(result["messages_preview"]) == 2
        assert result["messages_preview"][0]["type"] == "HumanMessage"
        assert result["messages_preview"][1]["type"] == "AIMessage"

    def test_inspect_session_error_handling(self):
        """Test error handling in session inspection."""
        mock_graph = Mock()
        mock_graph.get_state.side_effect = Exception("Database error")

        result = inspect_session("test-thread", mock_graph, verbose=False)

        assert "error" in result
        assert result["ui_compatible"] is False
        assert "Database error" in result["validation_error"]

    def test_inspect_session_gemini_format(self):
        """Test session inspection with Gemini format content."""
        mock_graph = Mock()
        mock_snapshot = Mock()
        mock_snapshot.next = None
        mock_snapshot.tasks = []
        mock_snapshot.interrupts = []
        mock_snapshot.metadata = {}
        mock_snapshot.values = {
            "messages": [
                AIMessage(content=[{"type": "text", "text": "Gemini response"}]),
            ],
        }
        mock_graph.get_state.return_value = mock_snapshot

        result = inspect_session("test-thread", mock_graph, verbose=False)

        assert result["message_count"] == 1
        assert "Gemini response" in result["latest_message"]


class TestExportImportRoundtrip:
    """Test complete export/import roundtrip."""

    def test_export_import_roundtrip(self):
        """Test that export and import preserve message data."""
        from langchain.messages import HumanMessage, AIMessage, ToolMessage

        # Create mock checkpointer
        mock_checkpointer = Mock()
        mock_tuple = Mock()
        
        # Create test messages
        test_messages = [
            HumanMessage(content="Hello!"),
            AIMessage(
                content="I'll help you",
                tool_calls=[
                    {"id": "call-1", "name": "tool", "args": {"param": "value"}, "type": "tool_call"}
                ],
            ),
            ToolMessage(content="Tool result", tool_call_id="call-1", name="tool"),
        ]
        
        mock_tuple.checkpoint = {
            "v": 3,
            "ts": "2025-05-05T16:01:24.680462+00:00",
            "id": "test-id",
            "channel_values": {
                "messages": test_messages,
                "conversation_title": "Test Session",
            },
            "channel_versions": {},
            "versions_seen": {},
            "next": None,
        }
        mock_tuple.config = {
            "configurable": {"thread_id": "original-thread"}
        }
        mock_tuple.metadata = {"source": "test"}
        mock_checkpointer.get_tuple.return_value = mock_tuple

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            # Export
            export_result = export_checkpoint_to_file(
                mock_checkpointer, "original-thread", temp_file
            )
            assert export_result is True

            # Read exported data
            with open(temp_file, "r", encoding="utf-8") as f:
                exported_data = json.load(f)

            # Verify exported structure
            assert "checkpoint" in exported_data
            assert "channel_values" in exported_data["checkpoint"]
            exported_messages = exported_data["checkpoint"]["channel_values"]["messages"]
            
            # Verify messages are serialized
            assert all("type" in msg for msg in exported_messages)

            # Import back
            mock_checkpointer.put = Mock()
            success, new_thread_id = import_checkpoint_from_file(
                mock_checkpointer, temp_file
            )
            
            assert success is True
            assert len(new_thread_id) == 36  # UUID format

            # Verify checkpointer.put was called with deserialized messages
            call_args = mock_checkpointer.put.call_args
            # Access checkpoint from kwargs or args
            imported_checkpoint = call_args.kwargs.get('checkpoint') or call_args.args[1]
            imported_messages = imported_checkpoint["channel_values"]["messages"]
            
            # Verify messages were deserialized to proper types
            from langchain.messages import HumanMessage, AIMessage, ToolMessage
            
            assert isinstance(imported_messages[0], HumanMessage)
            assert isinstance(imported_messages[1], AIMessage)
            assert isinstance(imported_messages[2], ToolMessage)
            
            # Verify content is preserved
            assert imported_messages[0].content == "Hello!"
            assert imported_messages[1].content == "I'll help you"
            assert imported_messages[2].content == "Tool result"
            
            # Verify tool_calls are preserved
            assert len(imported_messages[1].tool_calls) == 1
            assert imported_messages[1].tool_calls[0]["id"] == "call-1"
            assert imported_messages[1].tool_calls[0]["name"] == "tool"

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_export_import_with_chinese_content(self):
        """Test export/import roundtrip with Chinese characters."""
        from langchain.messages import HumanMessage

        mock_checkpointer = Mock()
        mock_tuple = Mock()
        
        test_messages = [
            HumanMessage(content="你好，世界！"),
            AIMessage(content="你好！我可以帮助你"),
        ]
        
        mock_tuple.checkpoint = {
            "v": 3,
            "ts": "2025-05-05T16:01:24.680462+00:00",
            "id": "test-id",
            "channel_values": {
                "messages": test_messages,
                "conversation_title": "GNS3 项目",
            },
            "channel_versions": {},
            "versions_seen": {},
            "next": None,
        }
        mock_tuple.config = {"configurable": {"thread_id": "original-thread"}}
        mock_tuple.metadata = {}
        mock_checkpointer.get_tuple.return_value = mock_tuple

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            temp_file = f.name

        try:
            # Export
            export_result = export_checkpoint_to_file(
                mock_checkpointer, "original-thread", temp_file
            )
            assert export_result is True

            # Import
            mock_checkpointer.put = Mock()
            success, new_thread_id = import_checkpoint_from_file(
                mock_checkpointer, temp_file
            )
            
            assert success is True

            # Verify Chinese content is preserved
            call_args = mock_checkpointer.put.call_args
            imported_checkpoint = call_args.kwargs.get('checkpoint') or call_args.args[1]
            imported_messages = imported_checkpoint["channel_values"]["messages"]
            
            assert imported_messages[0].content == "你好，世界！"
            assert imported_messages[1].content == "你好！我可以帮助你"
            assert imported_checkpoint["channel_values"]["conversation_title"] == "GNS3 项目"

        finally:
            Path(temp_file).unlink(missing_ok=True)


class TestImportCheckpointFromFile:
    """Test import_checkpoint_from_file function."""

    def test_successful_import(self):
        """Test successful checkpoint import from file."""
        # Create valid checkpoint file
        checkpoint_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "original-id",
                "channel_values": {
                    "messages": [{"role": "user", "content": "test"}],
                    "conversation_title": "Test Session",
                    "llm_calls": 1
                },
                "channel_versions": {
                    "messages": "00000000000000000000000000000001.0.1"
                },
                "versions_seen": {},
                "next": None
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            json.dump(checkpoint_data, f)
            temp_file = f.name

        try:
            # Mock checkpointer
            mock_checkpointer = Mock()
            mock_checkpointer.put.return_value = None

            success, result = import_checkpoint_from_file(
                mock_checkpointer, temp_file
            )
            assert success is True
            assert isinstance(result, str)
            assert len(result) == 36  # UUID format

            # Verify checkpointer.put was called
            mock_checkpointer.put.assert_called_once()
            call_args = mock_checkpointer.put.call_args
            # Access config from kwargs or args
            config = call_args.kwargs.get('config') or call_args.args[0]
            checkpoint = call_args.kwargs.get('checkpoint') or call_args.args[1]
            assert "configurable" in config
            # The second argument is the checkpoint dict itself, not wrapped
            assert checkpoint["channel_values"]["messages"][0]["content"] == "test"

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_import_with_custom_thread_id(self):
        """Test import with custom thread ID."""
        checkpoint_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "original-id",
                "channel_values": {
                    "messages": [{"role": "user", "content": "test"}]
                },
                "channel_versions": {},
                "versions_seen": {},
                "next": None
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            json.dump(checkpoint_data, f)
            temp_file = f.name

        try:
            mock_checkpointer = Mock()
            mock_checkpointer.put.return_value = None

            custom_thread_id = "custom-thread-123"
            success, result = import_checkpoint_from_file(
                mock_checkpointer, temp_file, custom_thread_id
            )
            assert success is True
            assert result == custom_thread_id

            # Verify correct thread_id was used
            call_args = mock_checkpointer.put.call_args
            # Access config from kwargs or args
            config = call_args.kwargs.get('config') or call_args.args[0]
            assert config["configurable"]["thread_id"] == custom_thread_id

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_import_file_not_found(self):
        """Test import when file doesn't exist."""
        mock_checkpointer = Mock()

        success, result = import_checkpoint_from_file(
            mock_checkpointer, "/nonexistent/file.txt"
        )
        assert success is False
        assert "File not found" in result

    def test_import_invalid_json(self):
        """Test import with invalid JSON format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("{ invalid json }")
            temp_file = f.name

        try:
            mock_checkpointer = Mock()

            success, result = import_checkpoint_from_file(
                mock_checkpointer, temp_file
            )
            assert success is False
            assert "Invalid JSON format" in result

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_import_missing_checkpoint_field(self):
        """Test import when checkpoint field is missing."""
        invalid_data = {"other_field": "value"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name

        try:
            mock_checkpointer = Mock()

            success, result = import_checkpoint_from_file(
                mock_checkpointer, temp_file
            )
            assert success is False
            assert "Missing required field: checkpoint" in result

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_import_with_chinese_content(self):
        """Test import with Chinese characters."""
        checkpoint_data = {
            "checkpoint": {
                "v": 3,
                "ts": "2025-05-05T16:01:24.680462+00:00",
                "id": "original-id",
                "channel_values": {
                    "messages": [{"role": "user", "content": "你好！"}],
                    "conversation_title": "GNS3 项目"
                },
                "channel_versions": {},
                "versions_seen": {},
                "next": None
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            json.dump(checkpoint_data, f, ensure_ascii=False)
            temp_file = f.name

        try:
            mock_checkpointer = Mock()
            mock_checkpointer.put.return_value = None

            success, result = import_checkpoint_from_file(
                mock_checkpointer, temp_file
            )
            assert success is True

            # Verify Chinese content is preserved
            call_args = mock_checkpointer.put.call_args
            imported_checkpoint = call_args.kwargs.get('checkpoint') or call_args.args[1]
            assert "你好！" in imported_checkpoint["channel_values"]["messages"][0]["content"]
            assert imported_checkpoint["channel_values"]["conversation_title"] == "GNS3 项目"

        finally:
            Path(temp_file).unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after tests."""
    yield
    # Any cleanup if needed
    pass
