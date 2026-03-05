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
GNS3 Copilot Checkpoint Utilities

This module provides utility functions for interacting with LangGraph checkpoint
database, including thread ID listing, checkpoint export, import, validation,
and session inspection.
"""

import json
import uuid
from typing import Any

from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.pregel import Pregel
from langgraph.types import RunnableConfig

from gns3_copilot.log_config import setup_logger

logger = setup_logger("checkpoint_utils")


def list_thread_ids(checkpointer: Any) -> list[str]:
    """
    Get all unique thread IDs from LangGraph checkpoint database.

    Args:
        checkpointer: LangGraph checkpointer instance.

    Returns:
        list: List of unique thread IDs ordered by most recent activity.
              Returns empty list on error or if table doesn't exist.
    """
    try:
        res = checkpointer.conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints ORDER BY rowid DESC"
        ).fetchall()
        return [r[0] for r in res]
    except Exception as e:
        # Table might not exist yet, return empty list
        logger.debug("Error listing thread IDs (table may not exist): %s", e)
        return []


def generate_thread_id() -> str:
    """
    Generate a new unique thread ID.

    Returns:
        str: A UUID-based thread ID.
    """
    return str(uuid.uuid4())


def validate_checkpoint_data(data: Any) -> tuple[bool, str]:
    """
    Validate checkpoint data structure.

    Ensures the imported checkpoint data has the required structure for
    importing into LangGraph checkpointer.

    Args:
        data: Dictionary containing checkpoint data.

    Returns:
        tuple: (is_valid, error_message)
               - is_valid: True if data is valid, False otherwise
               - error_message: Empty string if valid, error description if invalid
    """
    # Check if data is a dictionary
    if not isinstance(data, dict):
        return False, "Data must be a dictionary"

    # Check if checkpoint field exists
    if "checkpoint" not in data:
        return False, "Missing required field: checkpoint"

    checkpoint = data["checkpoint"]

    # Check if checkpoint is a dictionary
    if not isinstance(checkpoint, dict):
        return False, "checkpoint must be a dictionary"

    # Check required top-level fields in checkpoint
    required_fields = ["v", "ts", "id", "channel_values", "channel_versions"]
    if not all(field in checkpoint for field in required_fields):
        missing = [f for f in required_fields if f not in checkpoint]
        return False, f"Missing required checkpoint field: {missing[0]}"

    # Check if channel_values is a dictionary
    channel_values = checkpoint["channel_values"]
    if not isinstance(channel_values, dict):
        return False, "channel_values must be a dictionary"

    # Check if messages field exists in channel_values
    if "messages" not in channel_values:
        return False, "Missing required field: channel_values.messages"

    # Check if messages is a list
    if not isinstance(channel_values["messages"], list):
        return False, "channel_values.messages must be a list"

    # All validations passed
    return True, ""


def parse_message_string(msg_str: str) -> dict:
    """
    Parse a message string representation back to a dictionary.

    Handles the format: "content='xxx' additional_kwargs={} response_metadata={}"

    Args:
        msg_str: String representation of a LangChain message.

    Returns:
        dict: Parsed message data with type and content.
    """
    import re

    # Try to determine message type from string content
    msg_type = "unknown"

    # Check for ToolMessage pattern (has tool_call_id or tool_name)
    if "tool_call_id=" in msg_str or "name=" in msg_str:
        msg_type = "tool"
    # Check for AIMessage pattern (has tool_calls or is an AI response)
    elif "tool_calls=" in msg_str:
        msg_type = "ai"
    else:
        # Default to human if no other indicators
        msg_type = "human"

    # Extract content using regex
    content_match = re.search(r"content='([^']*)'|content=\"([^\"]*)\"", msg_str)
    content = (
        content_match.group(1)
        if content_match and content_match.group(1)
        else (
            content_match.group(2) if content_match and content_match.group(2) else ""
        )
    )

    return {"type": msg_type, "content": content, "original_string": msg_str}


def serialize_message(msg: Any) -> dict:
    """
    Serialize a LangChain message to a dictionary for JSON storage.

    Ensures all message fields are properly serialized for UI compatibility,
    including tool_calls structure for AIMessage and all metadata fields.

    Args:
        msg: LangChain message object (HumanMessage, AIMessage, or ToolMessage)
             or a string representation of a message.

    Returns:
        dict: Serialized message with type, content, and all metadata.
    """
    # If it's already a string (stored in database), parse it
    if isinstance(msg, str):
        return parse_message_string(msg)

    if isinstance(msg, HumanMessage):
        return {
            "type": "human",
            "content": msg.content,
            "additional_kwargs": msg.additional_kwargs,
            "response_metadata": msg.response_metadata,
            "id": msg.id,
        }
    elif isinstance(msg, AIMessage):
        # Serialize tool_calls with complete structure
        tool_calls = []
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_calls.append(
                    {
                        "id": tool_call.get("id", ""),
                        "name": tool_call.get("name", ""),
                        "args": tool_call.get("args", {}),
                        "type": tool_call.get("type", "tool_call"),
                    }
                )

        return {
            "type": "ai",
            "content": msg.content,
            "additional_kwargs": msg.additional_kwargs,
            "response_metadata": msg.response_metadata,
            "tool_calls": tool_calls,
            "id": msg.id,
        }
    elif isinstance(msg, ToolMessage):
        return {
            "type": "tool",
            "content": msg.content,
            "tool_call_id": msg.tool_call_id,
            "name": msg.name,
            "additional_kwargs": msg.additional_kwargs,
            "response_metadata": msg.response_metadata,
            "id": msg.id,
        }
    else:
        # For any other message types, try to serialize as dict
        return {"type": "unknown", "content": str(msg)}


def deserialize_message(msg_dict: dict) -> Any:
    """
    Deserialize a dictionary back to a LangChain message object.

    Ensures proper reconstruction of message objects with all required fields
    for UI compatibility, including tool_calls structure for AIMessage.

    Args:
        msg_dict: Dictionary containing serialized message data.

    Returns:
        LangChain message object (HumanMessage, AIMessage, or ToolMessage).

    Raises:
        ValueError: If message type is unknown or required fields are missing.
    """
    msg_type = msg_dict.get("type", "unknown")

    if msg_type == "human":
        return HumanMessage(
            content=msg_dict.get("content", ""),
            additional_kwargs=msg_dict.get("additional_kwargs", {}),
            response_metadata=msg_dict.get("response_metadata", {}),
            id=msg_dict.get("id"),
        )
    elif msg_type == "ai":
        # Reconstruct tool_calls with proper structure
        tool_calls = []
        serialized_tool_calls = msg_dict.get("tool_calls", [])

        if serialized_tool_calls:
            for tool_call in serialized_tool_calls:
                # Handle both dict and list formats
                if isinstance(tool_call, dict):
                    tool_calls.append(
                        {
                            "id": tool_call.get("id", ""),
                            "name": tool_call.get("name", ""),
                            "args": tool_call.get("args", {}),
                            "type": tool_call.get("type", "tool_call"),
                        }
                    )

        return AIMessage(
            content=msg_dict.get("content", ""),
            additional_kwargs=msg_dict.get("additional_kwargs", {}),
            response_metadata=msg_dict.get("response_metadata", {}),
            tool_calls=tool_calls,
            id=msg_dict.get("id"),
        )
    elif msg_type == "tool":
        return ToolMessage(
            content=msg_dict.get("content", ""),
            tool_call_id=msg_dict.get("tool_call_id", ""),
            name=msg_dict.get("name", ""),
            additional_kwargs=msg_dict.get("additional_kwargs", {}),
            response_metadata=msg_dict.get("response_metadata", {}),
            id=msg_dict.get("id"),
        )
    else:
        # Return as dict for unknown types
        logger.warning("Unknown message type: %s, returning dict", msg_type)
        return msg_dict


def export_checkpoint_to_file(
    checkpointer: Any, thread_id: str, file_path: str
) -> bool:
    """
    Export checkpoint data to a .txt file in JSON format.

    Exports the checkpoint data for a specific thread to a text file.
    The exported data includes the complete checkpoint state with messages,
    conversation title, config, and metadata. Messages are properly serialized
    to ensure they can be correctly deserialized on import.

    Args:
        checkpointer: LangGraph checkpointer instance.
        thread_id: The thread ID to export.
        file_path: Path to the output .txt file.

    Returns:
        bool: True if export succeeded, False otherwise.
    """
    try:
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        checkpoint_tuple = checkpointer.get_tuple(config)

        if checkpoint_tuple is None:
            logger.error("Checkpoint not found for thread_id: %s", thread_id)
            return False

        # Create a copy of checkpoint data to avoid modifying the original
        checkpoint_data = dict(checkpoint_tuple.checkpoint)

        # Serialize messages for proper JSON export
        if (
            "channel_values" in checkpoint_data
            and "messages" in checkpoint_data["channel_values"]
        ):
            messages = checkpoint_data["channel_values"]["messages"]
            serialized_messages = [serialize_message(msg) for msg in messages]
            checkpoint_data["channel_values"]["messages"] = serialized_messages

        # Save complete checkpoint data including config and metadata
        export_data = {
            "checkpoint": checkpoint_data,
            "config": checkpoint_tuple.config,
            "metadata": checkpoint_tuple.metadata,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

        logger.info("Checkpoint exported to %s for thread_id: %s", file_path, thread_id)
        return True

    except Exception as e:
        logger.error("Failed to export checkpoint: %s", e)
        return False


def validate_messages_for_ui(messages: list) -> tuple[bool, str, list[str]]:
    """
    Validate that messages can be correctly rendered by the UI.

    Checks that all messages are proper LangChain message objects with
    required fields for UI rendering (chat.py compatibility).

    Args:
        messages: List of message objects to validate.

    Returns:
        tuple: (is_valid, error_message, validation_errors)
               - is_valid: True if all messages are valid for UI
               - error_message: Summary error message
               - validation_errors: List of specific validation errors per message
    """
    validation_errors = []

    if not messages:
        return True, "", []

    for idx, msg in enumerate(messages):
        msg_error = f"Message {idx}: "

        # Check if message is a recognized type
        if isinstance(msg, HumanMessage):
            # HumanMessage requires content
            if not hasattr(msg, "content") or msg.content is None:
                validation_errors.append(msg_error + "Missing content field")
            continue
        elif isinstance(msg, AIMessage):
            # AIMessage should have content and tool_calls
            if not hasattr(msg, "content"):
                validation_errors.append(msg_error + "Missing content field")

            # Validate tool_calls if present
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_idx, tool_call in enumerate(msg.tool_calls):
                    required_fields = ["id", "name", "args"]
                    missing = [f for f in required_fields if f not in tool_call]
                    if missing:
                        validation_errors.append(
                            f"{msg_error} Tool call {tool_idx} missing: {', '.join(missing)}"
                        )
            continue
        elif isinstance(msg, ToolMessage):
            # ToolMessage requires content, tool_call_id, and name
            if not hasattr(msg, "content"):
                validation_errors.append(msg_error + "Missing content field")
            if not hasattr(msg, "tool_call_id") or not msg.tool_call_id:
                validation_errors.append(msg_error + "Missing or empty tool_call_id")
            if not hasattr(msg, "name") or not msg.name:
                validation_errors.append(msg_error + "Missing or empty name")
            continue
        else:
            validation_errors.append(
                f"{msg_error} Unknown message type: {type(msg).__name__}"
            )
            continue

    is_valid = len(validation_errors) == 0
    error_message = "; ".join(validation_errors) if validation_errors else ""

    return is_valid, error_message, validation_errors


def inspect_session(
    thread_id: str, graph: Pregel, verbose: bool = False
) -> dict[str, Any]:
    """
    Inspect and return human-readable session state using graph.get_state().

    Provides detailed information about a session including message statistics,
    UI compatibility, and current execution state.

    Args:
        thread_id: Thread ID to inspect.
        graph: Compiled LangGraph agent instance.
        verbose: If True, include detailed message contents in output.

    Returns:
        dict: Human-readable session information including:
            - next: Next action to be executed
            - message_count: Number of messages
            - message_types: Dictionary counting message types
            - latest_message: Content of latest message
            - step: Current step number
            - pending_tasks: Number of pending tasks
            - has_interrupts: Whether there are interrupts
            - conversation_title: Session title
            - selected_project: Currently selected GNS3 project
            - ui_compatible: Whether messages are compatible with UI
            - validation_errors: List of validation errors (if any)
            - messages_preview: Preview of messages (if verbose=True)
    """
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    try:
        snapshot = graph.get_state(config)

        # Extract message information
        messages = snapshot.values.get("messages", [])
        message_count = len(messages)

        # Count message types
        message_types = {"human": 0, "ai": 0, "tool": 0, "unknown": 0}
        for msg in messages:
            if isinstance(msg, HumanMessage):
                message_types["human"] += 1
            elif isinstance(msg, AIMessage):
                message_types["ai"] += 1
            elif isinstance(msg, ToolMessage):
                message_types["tool"] += 1
            else:
                message_types["unknown"] += 1

        # Get latest message content
        latest_message = None
        if messages:
            latest_msg = messages[-1]
            if hasattr(latest_msg, "content"):
                if isinstance(latest_msg.content, str):
                    latest_message = latest_msg.content
                elif isinstance(latest_msg.content, list) and latest_msg.content:
                    # Handle Gemini format (list with text field)
                    if isinstance(latest_msg.content[0], dict):
                        latest_message = latest_msg.content[0].get(
                            "text", str(latest_msg.content)
                        )
                    else:
                        latest_message = str(latest_msg.content)
                else:
                    latest_message = str(latest_msg.content)

        # Validate UI compatibility
        is_valid, error_msg, validation_errors = validate_messages_for_ui(messages)

        # Build result dictionary
        result = {
            "thread_id": thread_id,
            "next": snapshot.next,
            "message_count": message_count,
            "message_types": message_types,
            "latest_message": latest_message,
            "step": snapshot.metadata.get("step", "N/A")
            if snapshot.metadata
            else "N/A",
            "pending_tasks": len(snapshot.tasks),
            "has_interrupts": len(snapshot.interrupts) > 0,
            "conversation_title": snapshot.values.get("conversation_title"),
            "selected_project": snapshot.values.get("selected_project"),
            "ui_compatible": is_valid,
            "validation_error": error_msg,
            "validation_errors": validation_errors,
        }

        # Add verbose details if requested
        if verbose:
            messages_preview = []
            for idx, msg in enumerate(messages):
                msg_preview = {
                    "index": idx,
                    "type": type(msg).__name__,
                }
                if hasattr(msg, "content"):
                    msg_preview["content"] = str(msg.content)[
                        :200
                    ]  # Truncate long content
                if (
                    isinstance(msg, AIMessage)
                    and hasattr(msg, "tool_calls")
                    and msg.tool_calls
                ):
                    msg_preview["tool_calls_count"] = len(msg.tool_calls)
                messages_preview.append(msg_preview)
            result["messages_preview"] = messages_preview

        return result

    except Exception as e:
        logger.error("Failed to inspect session %s: %s", thread_id, e)
        return {
            "thread_id": thread_id,
            "error": str(e),
            "message_count": 0,
            "message_types": {"human": 0, "ai": 0, "tool": 0, "unknown": 0},
            "ui_compatible": False,
            "validation_error": f"Failed to get state: {e}",
        }


def import_checkpoint_from_file(
    checkpointer: Any, file_path: str, new_thread_id: str | None = None
) -> tuple[bool, str]:
    """
    Import checkpoint data from a .txt file to a new thread.

    Reads checkpoint data from a JSON-formatted .txt file and imports it
    into a new thread in the LangGraph checkpointer. The imported data is
    validated and messages are deserialized before insertion.

    Args:
        checkpointer: LangGraph checkpointer instance.
        file_path: Path to .txt file containing checkpoint data.
        new_thread_id: Optional thread ID for the new thread.
                      If None, a new UUID will be generated.

    Returns:
        tuple: (success, result)
               - success: True if import succeeded, False otherwise
               - result: New thread ID if success, error message if failed
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Validate checkpoint data structure
        is_valid, error_msg = validate_checkpoint_data(data)
        if not is_valid:
            logger.error("Invalid checkpoint data: %s", error_msg)
            return False, error_msg

        # Generate new thread ID if not provided
        if new_thread_id is None:
            new_thread_id = generate_thread_id()

        # Create a copy of checkpoint data to avoid modifying original
        checkpoint_data = dict(data["checkpoint"])

        # Deserialize messages if they are in serialized format
        if (
            "channel_values" in checkpoint_data
            and "messages" in checkpoint_data["channel_values"]
        ):
            messages = checkpoint_data["channel_values"]["messages"]

            # Check if messages are in serialized format (have 'type' field)
            if messages and isinstance(messages[0], dict) and "type" in messages[0]:
                deserialized_messages = []
                for msg_dict in messages:
                    try:
                        deserialized_msg = deserialize_message(msg_dict)
                        deserialized_messages.append(deserialized_msg)
                    except Exception as e:
                        logger.error(
                            "Failed to deserialize message: %s. Error: %s",
                            msg_dict.get("type", "unknown"),
                            e,
                        )
                        # Skip invalid messages or add as dict
                        deserialized_messages.append(msg_dict)
                checkpoint_data["channel_values"]["messages"] = deserialized_messages

        # Rebuild complete config with all required keys
        saved_config = data.get("config", {})
        new_config = {
            **saved_config,
            "configurable": {
                **saved_config.get("configurable", {}),
                "thread_id": new_thread_id,
                "checkpoint_ns": "",  # Required: checkpoint namespace (empty string)
                "checkpoint_id": str(uuid.uuid4()),  # Required: new checkpoint ID
            },
        }

        # Use saved metadata if available, otherwise create new
        metadata = data.get("metadata", {"source": "import"})
        if "source" not in metadata:
            metadata["source"] = "import"

        new_versions = checkpoint_data["channel_versions"]

        checkpointer.put(
            config=new_config,
            checkpoint=checkpoint_data,
            metadata=metadata,
            new_versions=new_versions,
        )

        logger.info(
            "Checkpoint imported from %s to new thread_id: %s", file_path, new_thread_id
        )
        return True, new_thread_id

    except FileNotFoundError:
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        return False, error_msg
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in file: {e}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to import checkpoint: {e}"
        logger.error(error_msg)
        return False, error_msg
