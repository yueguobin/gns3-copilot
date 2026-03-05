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
GNS3 Project Read File Tool

Provides a LangChain tool for reading files in GNS3 projects.
This tool directly uses the Project.get_file() method from custom_gns3fy.
"""

import json
import re
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_read_file")


class GNS3ProjectReadFileTool(BaseTool):
    """
    A LangChain tool to read files from a GNS3 project.

    This tool reads the content of a file located in a GNS3 project directory.
    It uses the Project.get_file() method from custom_gns3fy.

    **Input:**
    A JSON object containing the project_id and the file path.

    Example input:
        {
            "project_id": "uuid-of-project",
            "path": "README.md"
        }

    **Output:**
    A dictionary containing the project_id, file path, content, and status.

    Example output:
        {
            "project_id": "uuid-of-project",
            "path": "README.md",
            "content": "This is the file content...",
            "status": "success"
        }

    If an error occurs, returns a dictionary with an error message.

    Example error output:
        {
            "project_id": "uuid-of-project",
            "path": "README.md",
            "status": "failed",
            "error": "File not found"
        }
    """

    name: str = "gns3_project_read_file"
    description: str = """
    Reads a file from a GNS3 project directory.
    Input is a JSON object with project_id and the file path.
    Example input:
        {
            "project_id": "uuid-of-project",
            "path": "README.md"
        }
    Returns a dictionary with the file content and status.
    If the operation fails, returns a dictionary with an error message.
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Reads a file from a GNS3 project.

        Args:
            tool_input (str): A JSON string containing project_id and file path.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary with the file content and status, or an error message.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            path = input_data.get("path")

            # Validate input
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return {"error": "Missing project_id."}

            if not path:
                logger.error("Invalid input: Missing path.")
                return {"error": "Missing path."}

            # Validate project_id format (UUID)
            if not self._validate_project_id(project_id):
                error_msg = (
                    f"Invalid project_id format: {project_id}. Expected UUID format."
                )
                logger.error(error_msg)
                return {"error": error_msg}

            # Get connector using factory function
            connector = get_gns3_connector()
            if connector is None:
                error_msg = "Failed to create GNS3 connector. Check configuration."
                logger.error(error_msg)
                return {"error": error_msg}

            logger.info("Connecting to GNS3 server...")

            # Create Project instance
            project = Project(project_id=project_id, connector=connector)

            # Read file content
            logger.info("Reading file '%s' from project '%s'...", path, project_id)
            content = project.get_file(path=path)

            # Prepare successful result
            result = {
                "project_id": project_id,
                "path": path,
                "content": content,
                "status": "success",
            }

            logger.info(
                "Successfully read file '%s' from project '%s'", path, project_id
            )
            logger.debug("File content preview: %s", content[:200] if content else "")

            return result

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s", e)
            return {"error": f"Invalid JSON input: {e}"}
        except ValueError as e:
            logger.error("Value error: %s", e)
            return {"error": f"Value error: {e}"}
        except Exception as e:
            logger.error("Failed to read file from project: %s", e)
            return {
                "project_id": project_id if "project_id" in locals() else None,
                "path": path if "path" in locals() else None,
                "status": "failed",
                "error": f"Failed to read file: {str(e)}",
            }

    def _validate_project_id(self, project_id: str) -> bool:
        """
        Validate project_id format (UUID).

        Args:
            project_id: The project ID to validate

        Returns:
            True if valid UUID format, False otherwise
        """
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(uuid_pattern, project_id, re.IGNORECASE))


if __name__ == "__main__":
    import pprint

    print("=" * 80)
    print("Testing GNS3ProjectReadFileTool")
    print("=" * 80)

    read_test_input = json.dumps(
        {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",  # Replace with actual project UUID
            "path": "test_write.txt",
        }
    )

    read_tool = GNS3ProjectReadFileTool()
    read_result = read_tool._run(read_test_input)
    print("\nRead Result:")
    pprint.pprint(read_result)
