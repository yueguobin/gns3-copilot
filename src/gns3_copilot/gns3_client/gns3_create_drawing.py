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
GNS3 drawing creation tool for adding graphical elements.

Provides functionality to create multiple drawings in a GNS3 project
using specified SVG content and coordinates through the GNS3 API.
"""

import json
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_create_drawing")


class GNS3CreateDrawingTool(BaseTool):
    """
    A LangChain tool to create multiple drawings in a GNS3 project
    using specified SVG content and coordinates.

    **Input:**
    A JSON object containing the project_id and an array of drawings with SVG content,
    coordinates, and optional properties.

    Example input:
        {
            "project_id": "uuid-of-project",
            "drawings": [
                {
                    "svg": "<svg>...</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": false,
                    "rotation": 0
                },
                {
                    "svg": "<svg>...</svg>",
                    "x": -200,
                    "y": 300,
                    "z": 1,
                    "locked": true,
                    "rotation": 90
                }
            ]
        }

    **Output:**
    A dictionary containing the creation results for all drawings.
    Example output:
        {
            "project_id": "uuid-of-project",
            "created_drawings": [
                {
                    "drawing_id": "uuid-of-drawing1",
                    "status": "success"
                },
                {
                    "drawing_id": "uuid-of-drawing2",
                    "status": "success"
                }
            ],
            "total_drawings": 2,
            "successful_drawings": 2,
            "failed_drawings": 0
        }
    If an error occurs during input validation, returns a dictionary with an error message.
    """

    name: str = "create_gns3_drawing"
    description: str = """
    Creates multiple drawings in a GNS3 project using specified SVG content and coordinates.
    Input is a JSON object with project_id and an array of drawings, each containing svg, x, y,
    and optional z, locked, and rotation parameters.
    Example input:
        {
            "project_id": "uuid-of-project",
            "drawings": [
                {
                    "svg": "<svg>...</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": false,
                    "rotation": 0
                }
            ]
        }
    Returns a dictionary with creation results for all drawings, including success/failure status.
    If the operation fails during input validation, returns a dictionary with an error message.
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Creates multiple drawings in a GNS3 project using the provided SVG content and coordinates.

        Args:
            tool_input (str): A JSON string containing project_id and an array of drawings.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary with creation results for all drawings or an error message.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            drawings = input_data.get("drawings", [])

            # Validate input
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return {"error": "Missing project_id."}

            if not isinstance(drawings, list) or len(drawings) == 0:
                logger.error("Invalid input: drawings must be a non-empty array.")
                return {"error": "drawings must be a non-empty array."}

            # Validate each drawing in the array
            for i, drawing_data in enumerate(drawings):
                if not isinstance(drawing_data, dict):
                    logger.error(
                        "Invalid input: Drawing %d must be a dictionary.", i + 1
                    )
                    return {"error": f"Drawing {i + 1} must be a dictionary."}

                svg = drawing_data.get("svg")
                x = drawing_data.get("x")
                y = drawing_data.get("y")

                if not all(
                    [svg, isinstance(x, (int, float)), isinstance(y, (int, float))]
                ):
                    logger.error(
                        "Invalid input: Drawing %d missing or invalid svg, x, or y.",
                        i + 1,
                    )
                    return {
                        "error": f"Drawing {i + 1} missing or invalid svg, x, or y."
                    }

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
                "Creating %d drawings in project %s...", len(drawings), project_id
            )
            project = Project(project_id=project_id, connector=gns3_server)

            # Create drawings
            results: list[dict[str, Any]] = []

            for i, drawing_data in enumerate(drawings):
                try:
                    svg = drawing_data.get("svg")
                    x = drawing_data.get("x")
                    y = drawing_data.get("y")
                    z = drawing_data.get("z", 0)
                    locked = drawing_data.get("locked", False)
                    rotation = drawing_data.get("rotation", 0)

                    logger.info(
                        "Creating drawing %d/%d at coordinates (%s, %s)...",
                        i + 1,
                        len(drawings),
                        x,
                        y,
                    )

                    # Create drawing using Project method
                    result = project.create_drawing(
                        svg=svg,
                        x=int(x),
                        y=int(y),
                        z=int(z),
                        locked=bool(locked),
                        rotation=int(rotation),
                    )

                    drawing_info = {
                        "drawing_id": result.get("drawing_id"),
                        "status": "success",
                    }

                    results.append(drawing_info)
                    logger.debug(
                        "Successfully created drawing %d: %s",
                        i + 1,
                        json.dumps(drawing_info, indent=2, ensure_ascii=False),
                    )

                except Exception as e:
                    error_info = {
                        "error": f"Drawing {i + 1} creation failed: {str(e)}",
                        "status": "failed",
                    }
                    results.append(error_info)
                    logger.error("Failed to create drawing %d: %s", i + 1, e)
                    # Continue with next drawing even if one fails

            # Calculate summary statistics
            successful_drawings = len(
                [r for r in results if r.get("status") == "success"]
            )
            failed_drawings = len([r for r in results if r.get("status") == "failed"])

            # Prepare final result
            final_result = {
                "project_id": project_id,
                "created_drawings": results,
                "total_drawings": len(drawings),
                "successful_drawings": successful_drawings,
                "failed_drawings": failed_drawings,
            }

            # Log the final result
            logger.info(
                "Drawing creation completed: %d successful, %d failed out of %d total drawings.",
                successful_drawings,
                failed_drawings,
                len(drawings),
            )
            logger.debug(
                "Final result: %s",
                json.dumps(final_result, indent=2, ensure_ascii=False),
            )

            # Return JSON-formatted result
            return final_result

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s", e)
            return {"error": f"Invalid JSON input: {e}"}
        except Exception as e:
            logger.error("Failed to process drawing creation request: %s", e)
            return {"error": f"Failed to process drawing creation request: {str(e)}"}


if __name__ == "__main__":
    # Test the tool locally with multiple drawings
    test_input = json.dumps(
        {
            "project_id": "0c0fde25-6ead-4413-a283-ea8fd2324291",  # Replace with actual project UUID
            "drawings": [
                {
                    "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"><text x="10" y="30" font-size="14">Label 1</text></svg>',
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": False,
                    "rotation": 0,
                },
                {
                    "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"><text x="10" y="30" font-size="14">Label 2</text></svg>',
                    "x": 200,
                    "y": -300,
                    "z": 1,
                    "locked": True,
                    "rotation": 90,
                },
            ],
        }
    )
    tool = GNS3CreateDrawingTool()
    result = tool._run(test_input)
    pprint(result)


"""
example output:
{'created_drawings': [{'drawing_id': '52045be2-d6d9-46f8-85af-c33bf7074b6a',
                       'status': 'success'},
                      {'drawing_id': '8f1838a7-1aa4-4613-acaa-b300b23e60d5',
                       'status': 'success'}],
 'failed_drawings': 0,
 'project_id': '2245149a-71c8-4387-9d1f-441a683ef7e7',
 'successful_drawings': 2,
 'total_drawings': 2}
"""
