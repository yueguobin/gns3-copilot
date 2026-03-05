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
logger = setup_tool_logger("gns3_project_delete")


class GNS3ProjectDelete(BaseTool):
    """
    Tool to delete a GNS3 project.

    This tool connects to GNS3 server and deletes an existing project,
    optionally retrieving project details before deletion.
    """

    name: str = "delete_gns3_project"
    description: str = """
    Deletes an existing GNS3 project.

    Input parameters:
    Required:
    - project_id: The UUID of the project to delete OR
    - name: The name of the project to delete (one must be provided)

    Returns: Project deletion status and detailed information including:
    - success: Whether the operation succeeded
    - project: Deleted project details (name, project_id, status, etc.)
    - message: Status message

    Example output:
        {
            "success": true,
            "project": {
                "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
                "name": "my_project",
                "status": "closed"
            },
            "message": "Project 'my_project' deleted successfully"
        }
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        """
        Execute the project deletion operation.

        Args:
            tool_input: Dictionary containing project identifier
            run_manager: Run manager for tool execution (optional)

        Returns:
            Dictionary with operation result and deleted project details
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Validate input
            if not tool_input:
                return {
                    "success": False,
                    "error": "No input provided",
                }

            # Check for project identifier
            project_id = tool_input.get("project_id")
            project_name = tool_input.get("name")

            if not project_id and not project_name:
                return {
                    "success": False,
                    "error": "Missing required parameter: either 'project_id' or 'name' must be provided",
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

            # Create project instance
            if project_id:
                project = Project(project_id=project_id, connector=server)
            else:
                project = Project(name=project_name, connector=server)

            # Get project information before deletion
            project.get(get_nodes=False, get_links=False, get_stats=False)

            # Verify project was found
            if not project.project_id:
                if project_name:
                    return {
                        "success": False,
                        "error": f"Project with name '{project_name}' not found",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Project with ID '{project_id}' not found",
                    }

            # Store project details for response
            project_details = {
                "project_id": project.project_id,
                "name": project.name,
                "status": project.status,
                "path": project.path,
            }

            # Delete the project
            project.delete()

            logger.info(
                "Project deleted successfully: %s (ID: %s)",
                project.name,
                project.project_id,
            )

            # Prepare result
            result = {
                "success": True,
                "project": project_details,
                "message": f"Project '{project.name}' deleted successfully",
            }

            # Log result
            logger.info("Project deletion result: %s", result)

            # Return success with project details
            return result

        except ValueError as e:
            logger.error("Validation error deleting GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
            }
        except Exception as e:
            logger.error("Error deleting GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to delete GNS3 project: {str(e)}",
            }
