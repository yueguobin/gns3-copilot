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
GNS3 Project Path Tool.

This module provides a LangChain tool for retrieving GNS3 project paths.
These paths are needed for features like Notes to store markdown files
in the project directory.

Usage:
    from gns3_copilot.gns3_client.gns3_project_path import GNS3ProjectPath
    tool = GNS3ProjectPath()
    result = tool._run({"project_name": "mylab", "project_id": "uuid"})
"""

from typing import Any

from langchain.tools import BaseTool

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_path")


class GNS3ProjectPath(BaseTool):
    """
    Tool to retrieve the local filesystem path of a GNS3 project.

    This tool connects to GNS3 server and retrieves the local path where
    project files are stored on the server. Useful for features that need to
    access project-specific files such as Notes.

    Input parameters:
    - project_name: Name of the GNS3 project (required)
    - project_id: The unique UUID identifier of project (required)

    Returns: Project path information including:
    - success: Whether the operation succeeded
    - project_path: Full path to the project directory on the server
    - project_name: Name of the project
    - project_id: UUID of the project
    - message: Status message

    Example output (success):
        {
            "success": true,
            "project_path": "/home/user/GNS3/projects/mylab",
            "project_name": "mylab",
            "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
            "message": "Successfully retrieved project path"
        }

    Example output (error):
        {
            "success": false,
            "error": "Project with ID 'xxx' not found"
        }
    """

    name: str = "get_gns3_project_path"
    description: str = """
    Retrieves the local filesystem path for a GNS3 project.

    Input parameters:
    - project_name: Name of the GNS3 project (required)
    - project_id: The unique UUID identifier of project (required)

    This tool is useful for accessing project-specific files and directories
    on the GNS3 server, such as storing notes or configuration files.

    Returns: Project path information including success status, path,
    project details, and status message.
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        """
        Execute the project path retrieval operation.

        Args:
            tool_input: Dictionary containing project_name and project_id
            run_manager: Run manager for tool execution (optional)

        Returns:
            Dictionary with operation result and project path details
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Validate input
            if not tool_input:
                return {
                    "success": False,
                    "error": "Missing required parameters: project_name and project_id",
                }

            project_name = tool_input.get("project_name")
            project_id = tool_input.get("project_id")

            if not project_name or not project_id:
                return {
                    "success": False,
                    "error": "Both project_name and project_id are required parameters",
                }

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            server = get_gns3_connector()

            if server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "success": False,
                    "error": "Failed to connect to GNS3 server. Please check your configuration.",
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

            # Verify project name matches
            if project.name != project_name:
                logger.warning(
                    "Project name mismatch: expected '%s', got '%s'",
                    project_name,
                    project.name,
                )
                # Continue anyway as project_id is more authoritative

            # Return project path if available
            if project.path:
                result = {
                    "success": True,
                    "project_path": project.path,
                    "project_name": project.name,
                    "project_id": project.project_id,
                    "message": f"Successfully retrieved project path for '{project.name}'",
                }
                # Log result
                logger.info("Project path retrieval result: %s", result)
                return result
            else:
                return {
                    "success": False,
                    "error": f"Project '{project_name}' exists but has no path attribute",
                }

        except Exception as e:
            logger.error("Error retrieving project path: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to retrieve project path: {str(e)}",
            }
