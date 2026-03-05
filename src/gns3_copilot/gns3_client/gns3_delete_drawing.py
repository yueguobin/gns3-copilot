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
GNS3 drawing deletion tool for removing graphical elements.

Provides functionality to delete drawings from a GNS3 project.
"""

import json
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_delete_drawing")


class GNS3DeleteDrawingTool(BaseTool):
    """
    A LangChain tool to delete a drawing from a GNS3 project.

    **Input:**
    A JSON object containing the project_id and drawing_id.

    Example input:
        {
            "project_id": "uuid-of-project",
            "drawing_id": "uuid-of-drawing"
        }

    **Output:**
    A dictionary containing the deletion result.
    Example output:
        {
            "project_id": "uuid-of-project",
            "drawing_id": "uuid-of-drawing",
            "status": "success"
        }
    If an error occurs during input validation, returns a dictionary with an error message.
    """

    name: str = "delete_gns3_drawing"
    description: str = """
    Deletes a drawing from a GNS3 project.
    Input is a JSON object with project_id and drawing_id.
    Example input:
        {
            "project_id": "uuid-of-project",
            "drawing_id": "uuid-of-drawing"
        }
    Returns a dictionary with deletion result and status.
    If the operation fails, returns a dictionary with an error message.
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Deletes a drawing from a GNS3 project.

        Args:
            tool_input (str): A JSON string containing project_id and drawing_id.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary with the deletion result and status or an error message.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            drawing_id = input_data.get("drawing_id")

            # Validate input
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return {"error": "Missing project_id."}

            if not drawing_id:
                logger.error("Invalid input: Missing drawing_id.")
                return {"error": "Missing drawing_id."}

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Create project instance
            logger.info(
                "Deleting drawing %s from project %s...", drawing_id, project_id
            )
            project = Project(project_id=project_id, connector=gns3_server)

            # Delete the drawing
            project.delete_drawing(drawing_id=drawing_id)

            # Prepare final result
            final_result = {
                "project_id": project_id,
                "drawing_id": drawing_id,
                "status": "success",
            }

            # Log the final result
            logger.info("Drawing deletion completed successfully.")
            logger.debug(
                "Final result: %s",
                json.dumps(final_result, indent=2, ensure_ascii=False),
            )

            # Return JSON-formatted result
            return final_result

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s", e)
            return {"error": f"Invalid JSON input: {e}"}
        except ValueError as e:
            logger.error("Value error: %s", e)
            return {"error": str(e)}
        except Exception as e:
            logger.error("Failed to delete drawing: %s", e)
            return {"error": f"Failed to delete drawing: {str(e)}"}


if __name__ == "__main__":
    # Test the tool locally
    test_input = json.dumps(
        {
            "project_id": "0c0fde25-6ead-4413-a283-ea8fd2324291",  # Replace with actual project UUID
            "drawing_id": "0728feaf-defd-40e3-ae02-1f97734810e2",  # Replace with actual drawing UUID
        }
    )
    tool = GNS3DeleteDrawingTool()
    result = tool._run(test_input)
    pprint(result)


"""
example output:

error output when drawing is locked:
{'error': 'Failed to delete drawing: Unknown Status: Drawing ID '
          'daf3385a-86f0-458d-8563-6e1fbd87af77 cannot be deleted because it '
          'is locked (Original 409 Error)'}

successful output:
{'drawing_id': 'daf3385a-86f0-458d-8563-6e1fbd87af77',
 'project_id': '2245149a-71c8-4387-9d1f-441a683ef7e7',
 'status': 'success'}
"""
