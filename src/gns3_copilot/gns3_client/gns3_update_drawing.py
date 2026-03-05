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
GNS3 drawing update tool for modifying graphical elements.

Provides functionality to update drawing properties in a GNS3 project,
including coordinates, SVG content, locked status, z-index, and rotation.
"""

import json
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_update_drawing")


class GNS3UpdateDrawingTool(BaseTool):
    """
    A LangChain tool to update drawing properties in a GNS3 project.

    **Input:**
    A JSON object containing the project_id, drawing_id, and the properties to update.
    All properties are optional; only provided properties will be updated.

    Example input:
        {
            "project_id": "uuid-of-project",
            "drawing_id": "uuid-of-drawing",
            "svg": "<svg>...</svg>",
            "x": 150,
            "y": -250,
            "z": 1,
            "locked": true,
            "rotation": 45
        }

    **Output:**
    A dictionary containing the updated drawing information.
    Example output:
        {
            "project_id": "uuid-of-project",
            "drawing_id": "uuid-of-drawing",
            "updated_properties": {
                "x": 150,
                "y": -250,
                "z": 1,
                "locked": true,
                "rotation": 45
            },
            "status": "success"
        }
    If an error occurs during input validation, returns a dictionary with an error message.
    """

    name: str = "update_gns3_drawing"
    description: str = """
    Updates drawing properties in a GNS3 project. All properties are optional; only provided properties will be updated.
    Input is a JSON object with project_id, drawing_id, and optional properties to update (svg, x, y, z, locked, rotation).
    Example input:
        {
            "project_id": "uuid-of-project",
            "drawing_id": "uuid-of-drawing",
            "x": 150,
            "y": -250,
            "z": 1,
            "locked": true,
            "rotation": 45
        }
    Returns a dictionary with the updated drawing information and status.
    If the operation fails, returns a dictionary with an error message.
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Updates drawing properties in a GNS3 project.

        Args:
            tool_input (str): A JSON string containing project_id, drawing_id, and optional properties to update.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary with the updated drawing information and status or an error message.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            drawing_id = input_data.get("drawing_id")

            # Validate required fields
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return {"error": "Missing project_id."}

            if not drawing_id:
                logger.error("Invalid input: Missing drawing_id.")
                return {"error": "Missing drawing_id."}

            # Extract optional properties to update
            update_properties = {}
            if "svg" in input_data:
                update_properties["svg"] = input_data["svg"]
            if "x" in input_data:
                if not isinstance(input_data["x"], (int, float)):
                    logger.error("Invalid input: x must be a number.")
                    return {"error": "x must be a number."}
                update_properties["x"] = int(input_data["x"])
            if "y" in input_data:
                if not isinstance(input_data["y"], (int, float)):
                    logger.error("Invalid input: y must be a number.")
                    return {"error": "y must be a number."}
                update_properties["y"] = int(input_data["y"])
            if "z" in input_data:
                if not isinstance(input_data["z"], (int, float)):
                    logger.error("Invalid input: z must be a number.")
                    return {"error": "z must be a number."}
                update_properties["z"] = int(input_data["z"])
            if "locked" in input_data:
                if not isinstance(input_data["locked"], bool):
                    logger.error("Invalid input: locked must be a boolean.")
                    return {"error": "locked must be a boolean."}
                update_properties["locked"] = input_data["locked"]
            if "rotation" in input_data:
                if not isinstance(input_data["rotation"], (int, float)):
                    logger.error("Invalid input: rotation must be a number.")
                    return {"error": "rotation must be a number."}
                update_properties["rotation"] = int(input_data["rotation"])

            # Check if there are properties to update
            if not update_properties:
                logger.error("Invalid input: No properties to update.")
                return {"error": "No properties to update."}

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Create project instance
            logger.info("Updating drawing %s in project %s...", drawing_id, project_id)
            project = Project(project_id=project_id, connector=gns3_server)

            # Update the drawing
            logger.debug(
                "Update properties: %s",
                json.dumps(update_properties, indent=2, ensure_ascii=False),
            )
            project.update_drawing(
                drawing_id=drawing_id,
                svg=update_properties.get("svg"),
                locked=update_properties.get("locked"),
                x=update_properties.get("x"),
                y=update_properties.get("y"),
                z=update_properties.get("z"),
            )

            # Note: rotation is not directly supported by update_drawing method in custom_gns3fy.py
            # but it's included in the input for future compatibility
            if "rotation" in update_properties:
                logger.warning(
                    "Rotation parameter provided but not supported by update_drawing method in current version."
                )

            # Prepare final result
            final_result = {
                "project_id": project_id,
                "drawing_id": drawing_id,
                "updated_properties": update_properties,
                "status": "success",
            }

            # Log the final result
            logger.info("Drawing update completed successfully.")
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
            logger.error("Failed to update drawing: %s", e)
            return {"error": f"Failed to update drawing: {str(e)}"}


if __name__ == "__main__":
    # Test the tool locally
    test_input = json.dumps(
        {
            "project_id": "0c0fde25-6ead-4413-a283-ea8fd2324291",  # Replace with actual project UUID
            "drawing_id": "3f375126-bb44-43e9-a934-8d135b79fd6c",  # Replace with actual drawing UUID
            "x": 150,
            "y": -250,
            "z": 1,
            "locked": True,
        }
    )
    tool = GNS3UpdateDrawingTool()
    result = tool._run(test_input)
    pprint(result)


"""
example output:
{'drawing_id': 'daf3385a-86f0-458d-8563-6e1fbd87af77',
 'project_id': '2245149a-71c8-4387-9d1f-441a683ef7e7',
 'status': 'success',
 'updated_properties': {'locked': True, 'x': 150, 'y': -250, 'z': 1}}
"""
