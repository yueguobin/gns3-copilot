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
GNS3 project lock/unlock tool for project management.

Provides functionality to lock, unlock, or check the lock status of GNS3 projects.
Locking a project prevents accidental modifications to drawings and nodes.
"""

from typing import Any

from langchain.tools import BaseTool

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_lock")


class GNS3ProjectLock(BaseTool):
    """
    Tool to lock, unlock, or check the lock status of a GNS3 project.

    This tool connects to GNS3 server and performs lock/unlock operations
    on the specified project, or retrieves the current lock status.

    IMPORTANT: Project lock/unlock operations are only supported in GNS3 API v3.
    Using this tool with GNS3 API v2 will result in an error.

    Supported operations:
    - "locked": Check if the project is currently locked
    - "lock": Lock all drawings and nodes in the project
    - "unlock": Unlock all drawings and nodes in the project
    """

    name: str = "gns3_project_lock"
    description: str = """
    Lock, unlock, or check the lock status of a GNS3 project.

    IMPORTANT: This tool only works with GNS3 API v3. It is not supported in API v2.

    Input parameters:
    - project_id: The unique UUID identifier of the project (required)
    - operation: The operation to perform - "locked", "lock", or "unlock" (required)

    Operations:
    - "locked": Returns the current lock status of the project
    - "lock": Locks all drawings and nodes in the project
    - "unlock": Unlocks all drawings and nodes in the project

    Returns: Dictionary with operation result including:
    - success: Whether the operation succeeded
    - operation: The operation performed
    - project_id: The project ID
    - locked_status: Current lock status (for "locked" operation)
    - message: Status message
    - error: Error message if operation failed

    Example output (check locked status):
        {
            "success": true,
            "operation": "locked",
            "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
            "locked_status": false,
            "message": "Project is currently unlocked"
        }

    Example output (lock project):
        {
            "success": true,
            "operation": "lock",
            "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
            "message": "Project locked successfully"
        }

    Example output (unlock project):
        {
            "success": true,
            "operation": "unlock",
            "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
            "message": "Project unlocked successfully"
        }

    Example output (API v2 not supported):
        {
            "success": false,
            "operation": "lock",
            "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
            "error": "Project lock/unlock operations are only supported in GNS3 API v3. Current API version: v2"
        }
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        """
        Execute the project lock/unlock operation.

        Args:
            tool_input: Dictionary containing project_id and operation
            run_manager: Run manager for tool execution (optional)

        Returns:
            Dictionary with operation result
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Validate input
            if not tool_input or "project_id" not in tool_input:
                return {
                    "success": False,
                    "error": "Missing required parameter: project_id",
                }

            if "operation" not in tool_input:
                return {
                    "success": False,
                    "error": "Missing required parameter: operation",
                }

            project_id = tool_input["project_id"]
            operation = tool_input["operation"]

            # Validate operation type
            valid_operations = ["locked", "lock", "unlock"]
            if operation not in valid_operations:
                return {
                    "success": False,
                    "error": f"Invalid operation '{operation}'. "
                    f"Must be one of: {', '.join(valid_operations)}",
                }

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            server = get_gns3_connector()

            if server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "success": False,
                    "error": "Failed to connect to GNS3 server. "
                    "Please check your configuration.",
                }

            # Create project instance and retrieve project details
            project = Project(project_id=project_id, connector=server)
            project.get(get_nodes=False, get_links=False, get_stats=False)

            # Check if project was found
            if not project.name:
                return {
                    "success": False,
                    "error": f"Project with ID '{project_id}' not found",
                }

            # Perform the requested operation
            result: dict[str, Any] = {
                "success": False,
                "operation": operation,
                "project_id": project_id,
            }

            if operation == "locked":
                # Get current lock status
                logger.info("Getting lock status for project %s", project_id)
                try:
                    locked_status = project.get_locked()
                    result.update(
                        {
                            "success": True,
                            "locked_status": locked_status,
                            "message": f"Project is currently {'locked' if locked_status else 'unlocked'}",
                        }
                    )
                    logger.info("Project lock status: %s", locked_status)
                except ValueError as e:
                    # Handle API version incompatibility
                    error_msg = str(e)
                    if "only supported in GNS3 API v3" in error_msg:
                        logger.error("API v2 not supported: %s", error_msg)
                        result.update(
                            {
                                "error": error_msg,
                                "message": "Project lock/unlock operations require GNS3 API v3. "
                                "Please upgrade your GNS3 server or use v3 API.",
                            }
                        )
                    else:
                        logger.error("Error getting lock status: %s", error_msg)
                        result.update(
                            {
                                "error": error_msg,
                                "message": f"Failed to get lock status: {error_msg}",
                            }
                        )

            elif operation == "lock":
                # Lock the project
                logger.info("Locking project %s", project_id)
                try:
                    project.lock_project()
                    result.update(
                        {
                            "success": True,
                            "message": f"Project '{project.name}' locked successfully",
                        }
                    )
                    logger.info("Project locked successfully")
                except ValueError as e:
                    # Handle API version incompatibility
                    error_msg = str(e)
                    if "only supported in GNS3 API v3" in error_msg:
                        logger.error("API v2 not supported: %s", error_msg)
                        result.update(
                            {
                                "error": error_msg,
                                "message": "Project lock/unlock operations require GNS3 API v3. "
                                "Please upgrade your GNS3 server or use v3 API.",
                            }
                        )
                    else:
                        logger.error("Error locking project: %s", error_msg)
                        result.update(
                            {
                                "error": error_msg,
                                "message": f"Failed to lock project: {error_msg}",
                            }
                        )

            elif operation == "unlock":
                # Unlock the project
                logger.info("Unlocking project %s", project_id)
                try:
                    project.unlock_project()
                    result.update(
                        {
                            "success": True,
                            "message": f"Project '{project.name}' unlocked successfully",
                        }
                    )
                    logger.info("Project unlocked successfully")
                except ValueError as e:
                    # Handle API version incompatibility
                    error_msg = str(e)
                    if "only supported in GNS3 API v3" in error_msg:
                        logger.error("API v2 not supported: %s", error_msg)
                        result.update(
                            {
                                "error": error_msg,
                                "message": "Project lock/unlock operations require GNS3 API v3. "
                                "Please upgrade your GNS3 server or use v3 API.",
                            }
                        )
                    else:
                        logger.error("Error unlocking project: %s", error_msg)
                        result.update(
                            {
                                "error": error_msg,
                                "message": f"Failed to unlock project: {error_msg}",
                            }
                        )

            # Log result
            logger.info("Project lock operation result: %s", result)

            return result

        except Exception as e:
            logger.error("Error performing lock operation on GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to perform lock operation on GNS3 project: {str(e)}",
            }


if __name__ == "__main__":
    # Test the tool locally
    print("=== Testing GNS3ProjectLock Tool ===")

    # Test 1: Check lock status
    print("\n--- Test 1: Check lock status ---")
    test_input_locked = {
        "project_id": "0c0fde25-6ead-4413-a283-ea8fd2324291",  # Replace with actual project UUID
        "operation": "locked",
    }
    tool = GNS3ProjectLock()
    result_locked = tool._run(test_input_locked)
    print(f"Result: {result_locked}")

    # Test 2: Lock project
    print("\n--- Test 2: Lock project ---")
    test_input_lock = {
        "project_id": "0c0fde25-6ead-4413-a283-ea8fd2324291",  # Replace with actual project UUID
        "operation": "lock",
    }
    result_lock = tool._run(test_input_lock)
    print(f"Result: {result_lock}")

    # Test 3: Unlock project
    print("\n--- Test 3: Unlock project ---")
    test_input_unlock = {
        "project_id": "0c0fde25-6ead-4413-a283-ea8fd2324291",  # Replace with actual project UUID
        "operation": "unlock",
    }
    result_unlock = tool._run(test_input_unlock)
    print(f"Result: {result_unlock}")
