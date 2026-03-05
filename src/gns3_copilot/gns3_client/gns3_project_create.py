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

from typing import Any

from langchain.tools import BaseTool

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_create")


class GNS3ProjectCreate(BaseTool):
    """
    Tool to create a new GNS3 project.

    This tool connects to GNS3 server and creates a new project with the specified
    name and optional configuration parameters.
    """

    name: str = "create_gns3_project"
    description: str = """
    Creates a new GNS3 project with the specified name and optional parameters.

    Input parameters:
    - name: The name of the project to create (required)
    - auto_start: Automatically start the project when opened (optional, default: False)
    - auto_close: Automatically close the project when client disconnects (optional, default: False)
    - auto_open: Automatically open the project when GNS3 starts (optional, default: False)
    - scene_width: Width of the drawing area in pixels (optional)
    - scene_height: Height of the drawing area in pixels (optional)

    Returns: Project creation status and detailed information including:
    - success: Whether the operation succeeded
    - project: Project details (name, project_id, status, etc.)
    - message: Status message

    Example output:
        {
            "success": true,
            "project": {
                "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
                "name": "my_new_project",
                "status": "opened"
            },
            "message": "Project 'my_new_project' created successfully"
        }
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        """
        Execute the project creation operation.

        Args:
            tool_input: Dictionary containing project parameters
            run_manager: Run manager for tool execution (optional)

        Returns:
            Dictionary with operation result and project details
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Validate input
            if not tool_input or "name" not in tool_input:
                return {
                    "success": False,
                    "error": "Missing required parameter: name",
                }

            name = tool_input["name"]

            # Validate project name is not empty
            if not name or not isinstance(name, str) or not name.strip():
                return {
                    "success": False,
                    "error": "Project name must be a non-empty string",
                }

            # Get optional parameters
            auto_start = tool_input.get("auto_start", False)
            auto_close = tool_input.get("auto_close", False)
            auto_open = tool_input.get("auto_open", False)
            scene_width = tool_input.get("scene_width")
            scene_height = tool_input.get("scene_height")

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            server = get_gns3_connector()

            if server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "success": False,
                    "error": "Failed to connect to GNS3 server. Please check your configuration.",
                }

            # Create project instance with specified parameters
            project_params = {
                "name": name,
                "auto_start": auto_start,
                "auto_close": auto_close,
                "auto_open": auto_open,
            }

            # Add optional scene parameters if provided
            if scene_width is not None:
                project_params["scene_width"] = scene_width
            if scene_height is not None:
                project_params["scene_height"] = scene_height

            project = Project(connector=server, **project_params)

            # Create the project
            project.create()

            # Verify project was created successfully
            if not project.project_id:
                return {
                    "success": False,
                    "error": "Failed to create project: project_id not returned",
                }

            logger.info(
                "Project created successfully: %s (ID: %s)",
                project.name,
                project.project_id,
            )

            # Prepare result
            result = {
                "success": True,
                "project": {
                    "project_id": project.project_id,
                    "name": project.name,
                    "status": project.status,
                    "path": project.path,
                },
                "message": f"Project '{project.name}' created successfully",
            }

            # Log result
            logger.info("Project creation result: %s", result)

            # Return success with project details
            return result

        except ValueError as e:
            logger.error("Validation error creating GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
            }
        except Exception as e:
            logger.error("Error creating GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to create GNS3 project: {str(e)}",
            }
