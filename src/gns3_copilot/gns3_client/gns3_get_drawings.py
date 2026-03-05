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
GNS3 drawings retrieval tool for managing graphical elements.

Provides functionality to retrieve all drawings from a GNS3 project,
including their coordinates, SVG content, and other properties.
"""

import json
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_get_drawings")


class GNS3GetDrawingsTool(BaseTool):
    """
    A LangChain tool to retrieve all drawings from a GNS3 project.

    **Input:**
    A JSON object containing the project_id.

    Example input:
        {
            "project_id": "uuid-of-project"
        }

    **Output:**
    A dictionary containing all drawings in the project.
    Example output:
        {
            "project_id": "uuid-of-project",
            "drawings": [
                {
                    "drawing_id": "uuid-of-drawing1",
                    "svg": "<svg>...</svg>",
                    "x": 100,
                    "y": 200,
                    "z": 0,
                    "locked": false,
                    "rotation": 0
                },
                {
                    "drawing_id": "uuid-of-drawing2",
                    "svg": "<svg>...</svg>",
                    "x": 300,
                    "y": 400,
                    "z": 1,
                    "locked": true,
                    "rotation": 90
                }
            ],
            "total_drawings": 2
        }
    If an error occurs during input validation, returns a dictionary with an error message.
    """

    name: str = "get_gns3_drawings"
    description: str = """
    Retrieves all drawings from a GNS3 project.
    Input is a JSON object with project_id.
    Example input:
        {
            "project_id": "uuid-of-project"
        }
    Returns a dictionary with all drawings in the project, including their drawing_id,
    svg content, coordinates (x, y), z-index, locked status, and rotation.
    If the operation fails, returns a dictionary with an error message.
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Retrieves all drawings from a GNS3 project.

        Args:
            tool_input (str): A JSON string containing project_id.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary with all drawings in the project or an error message.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")

            # Validate input
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return {"error": "Missing project_id."}

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Create project instance
            logger.info("Retrieving drawings from project %s...", project_id)
            project = Project(project_id=project_id, connector=gns3_server)

            # Get project drawings
            project.get_drawings()

            # Prepare drawing list
            drawings_list = []
            if project.drawings:
                for drawing in project.drawings:
                    drawing_info = {
                        "drawing_id": drawing.get("drawing_id"),
                        "svg": drawing.get("svg"),
                        "x": drawing.get("x"),
                        "y": drawing.get("y"),
                        "z": drawing.get("z"),
                        "locked": drawing.get("locked"),
                        "rotation": drawing.get("rotation", 0),
                    }
                    drawings_list.append(drawing_info)

            # Prepare final result
            final_result = {
                "project_id": project_id,
                "drawings": drawings_list,
                "total_drawings": len(drawings_list),
            }

            # Log the final result
            logger.info(
                "Retrieved %d drawings from project %s.",
                len(drawings_list),
                project_id,
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
            logger.error("Failed to retrieve drawings: %s", e)
            return {"error": f"Failed to retrieve drawings: {str(e)}"}


if __name__ == "__main__":
    # Test the tool locally
    test_input = json.dumps(
        {
            "project_id": "d7fc094c-685e-4db1-ac11-5e33a1b2e066"
        }  # Replace with actual project UUID
    )
    tool = GNS3GetDrawingsTool()
    result = tool._run(test_input)
    pprint(result)


"""
example output:
{'drawings': [{'drawing_id': 'e8202c5e-bd0a-447c-848c-15db2c9af2f0',
               'locked': False,
               'rotation': 0,
               'svg': '<svg height="131" width="391"><rect fill="#ffffff" '
                      'fill-opacity="1" height="131" width="391" '
                      'stroke="#000000" stroke-width="2" '
                      'stroke-dasharray="undefined" rx="0" ry="0" /></svg>',
               'x': -376,
               'y': -381,
               'z': 1},
              {'drawing_id': '7d2f2411-efe8-4f3a-9882-cc0ad7798ee0',
               'locked': False,
               'rotation': 0,
               'svg': '<svg height="100" width="100"><text fill="#000000" '
                      'fill-opacity="1.0" font-family="Noto Sans" '
                      'font-size="11" font-weight="bold"></text></svg>',
               'x': -394,
               'y': 4,
               'z': 1},
              {'drawing_id': '264be3ab-002c-4b1d-886d-b4c323de845a',
               'locked': False,
               'rotation': 0,
               'svg': '<svg height="100" width="100"><text fill="#000000" '
                      'fill-opacity="1.0" font-family="Noto Sans" '
                      'font-size="11" font-weight="bold">哈哈哈\n'
                      '哈和</text></svg>',
               'x': -596,
               'y': -43,
               'z': 1},
              {'drawing_id': '44210a41-0100-46a0-8962-a73c72171c47',
               'locked': False,
               'rotation': 0,
               'svg': '<svg height="100" width="100"><text fill="#000000" '
                      'fill-opacity="1.0" font-family="Noto Sans" '
                      'font-size="11" font-weight="bold">Area 0</text></svg>',
               'x': -573,
               'y': -272,
               'z': 1},
              {'drawing_id': 'efd1add9-a798-489d-af26-58b2d73c89dc',
               'locked': False,
               'rotation': 0,
               'svg': '<svg height="0" width="100"><line stroke="#000000" '
                      'stroke-width="2" x1="0" x2="200" y1="0" y2="0" '
                      'stroke-dasharray="none" /></svg>',
               'x': -636,
               'y': -152,
               'z': 1},
              {'drawing_id': '89913ef3-1041-4b11-94e1-c5d65c3a52d4',
               'locked': False,
               'rotation': 0,
               'svg': '<svg height="119" width="488"><ellipse fill="#ffffff" '
                      'fill-opacity="1" cx="244" cy="59.5" rx="244" ry="59.5" '
                      'stroke="#000000" stroke-width="2" '
                      'stroke-dasharray="undefined" /></svg>',
               'x': -891,
               'y': 66,
               'z': 1}],
 'project_id': '2245149a-71c8-4387-9d1f-441a683ef7e7',
 'total_drawings': 8}
"""
