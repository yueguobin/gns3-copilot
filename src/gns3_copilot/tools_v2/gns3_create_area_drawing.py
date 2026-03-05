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
GNS3 area annotation drawing tool for creating visual area markers.

This tool creates visual annotations (ellipses) for network devices to represent
groupings such as OSPF areas, EIGRP AS numbers, or other protocol-defined regions.
Currently supports two-node ellipse annotations.
"""

import json
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import (
    GNS3GetNodesTool,
    Project,
    get_gns3_connector,
)
from gns3_copilot.log_config import setup_tool_logger
from gns3_copilot.utils.gns3_drawing_utils import (
    calculate_two_node_ellipse,
    calculate_two_node_rectangle,
)

# Configure logging
logger = setup_tool_logger("gns3_create_area_drawing")


class GNS3CreateAreaDrawingTool(BaseTool):
    """
    A LangChain tool to create visual area annotations for network devices.

    Creates ellipse annotations that connect two network devices,
    automatically calculating optimal position, size, and rotation based on node coordinates.

    **Input:**
    A JSON object containing the project_id, area_name, and node_names.

    Example input:
        {
            "project_id": "uuid-of-project",
            "area_name": "Area 0",
            "node_names": ["R-1", "R-2"]
        }

    **Output:**
    A dictionary containing the creation results:
        {
            "project_id": "uuid-of-project",
            "area_name": "Area 0",
            "node_count": 2,
            "shape_type": "ellipse",
            "created_drawings": [
                {
                    "drawing_id": "uuid-of-drawing1",
                    "type": "ellipse",
                    "status": "success"
                },
                {
                    "drawing_id": "uuid-of-drawing2",
                    "type": "text",
                    "status": "success"
                }
            ],
            "total_drawings": 2,
            "successful_drawings": 2,
            "failed_drawings": 0
        }

    **Use Cases:**
    - Protocol Domains: OSPF areas, BGP AS, IS-IS levels
    - Logical Isolation: VRF, VLAN, MSTP
    - High Availability: VRRP, HSRP, Stack, M-LAG
    - External Boundaries: Internet, DMZ
    - Management Networks: OOB, Management

    **Semantic Color Coding:**
    The tool automatically applies business-professional colors based on area_name keywords:

    | Category               | Colors              | Keywords in area_name        | Border Style |
    |------------------------|---------------------|------------------------------|--------------|
    | Primary Routing        | Blue (#2196F3)      | BGP, AS, Area 0, Backbone    | Solid        |
    | Secondary Routing      | Light Blue (#64B5F6)| Area, Level                 | Solid        |
    | Logical Isolation      | Purple (#9C27B0)    | VRF, VLAN, MSTP             | Dashed       |
    | High Availability      | Amber (#FFC107)     | VRRP, HSRP, HA, Stack       | Solid        |
    | External/Boundary      | Red (#EF5350)       | INET, OUT, External, DMZ     | Solid        |
    | Management             | Gray (#757575)      | MGMT, OOB                    | Dashed       |

    **Implementation Details:**
    - Retrieves node coordinates from the GNS3 project topology
    - Calculates rotated ellipse parameters (center, radius, rotation angle)
    - Generates professional SVG graphics with semantic colors
    - Creates two drawings: ellipse shape and text label
    - All coordinates are integers as required by GNS3 API

    **Example Usage:**
    User: "Configure OSPF area 0 on R-1 and R-2"
    → Call: create_gns3_area_drawing(project_id="xxx", area_name="Area 0", node_names=["R-1", "R-2"])

    User: "Create VLAN 10 for SW-1 and SW-2"
    → Call: create_gns3_area_drawing(project_id="xxx", area_name="VLAN 10", node_names=["SW-1", "SW-2"])

    User: "Configure VRRP group 1 on R-1 and R-2"
    → Call: create_gns3_area_drawing(project_id="xxx", area_name="VRRP Group 1", node_names=["R-1", "R-2"])
    """

    name: str = "create_gns3_area_drawing"
    description: str = """
    Creates a visual annotation (ellipse or rectangle) to mark logical groupings between two network devices.

    Use for protocol domains (OSPF areas, BGP AS, IS-IS levels), logical isolation (VRF, VLAN),
    or high availability groups (VRRP, HSRP). Automatically calculates optimal position,
    size, rotation, and applies semantic colors.

    Parameters:
    - project_id: GNS3 project UUID
    - area_name: Logical group name (e.g., "Area 0", "VLAN 10", "VRRP Group 1")
    - node_names: List of exactly 2 node names (e.g., ["R-1", "R-2"])
    - shape_type: Shape type, either "ellipse" (default) or "rectangle"
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Creates a visual area annotation for network devices.

        Args:
            tool_input: A JSON string containing project_id, area_name, and node_names.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary with creation results or an error message.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            area_name = input_data.get("area_name")
            node_names = input_data.get("node_names", [])
            shape_type = input_data.get("shape_type", "ellipse")

            # Validate input
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return {"error": "Missing project_id."}

            if not area_name:
                logger.error("Invalid input: Missing area_name.")
                return {"error": "Missing area_name."}

            if not isinstance(node_names, list) or len(node_names) == 0:
                logger.error("Invalid input: node_names must be a non-empty array.")
                return {"error": "node_names must be a non-empty array."}

            # Validate: requires exactly 2 nodes
            if len(node_names) != 2:
                logger.error(
                    "Invalid input: Exactly 2 nodes are required, got %d.",
                    len(node_names),
                )
                return {
                    "error": f"Exactly 2 nodes are required, got {len(node_names)}. "
                    "Please provide exactly 2 node names."
                }

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Initialize Project object for drawing creation
            logger.info("Initializing project for drawing creation...")
            project = Project(project_id=project_id, connector=gns3_server)
            project.get()  # Load project details

            # Get node information using GNS3GetNodesTool to retrieve complete node data
            # including height, width, coordinates, etc.
            logger.info(
                "Retrieving node information for project %s...",
                project_id,
            )
            get_nodes_tool = GNS3GetNodesTool()
            nodes_result = get_nodes_tool._run(json.dumps({"project_id": project_id}))

            # Check if node retrieval was successful
            if "error" in nodes_result:
                logger.error("Failed to retrieve nodes: %s", nodes_result["error"])
                return {"error": f"Failed to retrieve nodes: {nodes_result['error']}"}

            # Build a dictionary mapping node names to their complete information
            nodes_dict = {node["name"]: node for node in nodes_result.get("nodes", [])}

            # Validate all requested nodes exist
            for node_name in node_names:
                if node_name not in nodes_dict:
                    logger.error("Node %s not found in project", node_name)
                    return {
                        "error": f"Node '{node_name}' not found in project topology."
                    }

            # Retrieve all requested nodes
            nodes = [nodes_dict[node_name] for node_name in node_names]

            # Log node information
            node_info_list = [
                f"{node_name} at ({node['x']}, {node['y']}, size: {node.get('width', 'N/A')}x{node.get('height', 'N/A')})"
                for node_name, node in zip(node_names, nodes, strict=True)
            ]
            logger.info("Found nodes: %s", ", ".join(node_info_list))

            # Validate shape_type
            if shape_type not in ["ellipse", "rectangle"]:
                logger.error("Invalid shape_type: %s", shape_type)
                return {
                    "error": f"Invalid shape_type '{shape_type}'. Must be 'ellipse' or 'rectangle'."
                }

            # Calculate shape parameters for 2 nodes
            logger.info("Calculating %s parameters for 2 nodes...", shape_type)

            # Use the appropriate calculation function based on shape_type
            if shape_type == "ellipse":
                shape_result = calculate_two_node_ellipse(nodes[0], nodes[1], area_name)
                shape_key = "ellipse"
            else:  # rectangle
                shape_result = calculate_two_node_rectangle(
                    nodes[0], nodes[1], area_name
                )
                shape_key = "rectangle"

            metadata = shape_result["metadata"]
            logger.info(
                "Two-node %s: center=(%.2f, %.2f), distance=%.2f, angle=%.2f°",
                shape_type,
                metadata["center_x"],
                metadata["center_y"],
                metadata["distance"],
                metadata["angle_deg"],
            )

            # Prepare drawings for creation
            # Ensure all coordinates are integers as required by GNS3 API
            drawings = [
                {
                    "svg": shape_result[shape_key]["svg"],
                    "x": int(shape_result[shape_key]["x"]),
                    "y": int(shape_result[shape_key]["y"]),
                    "z": shape_result[shape_key]["z"],
                    "locked": False,
                    "rotation": int(shape_result[shape_key]["rotation"]),
                },
                {
                    "svg": shape_result["text"]["svg"],
                    "x": int(shape_result["text"]["x"]),
                    "y": int(shape_result["text"]["y"]),
                    "z": shape_result["text"]["z"],
                    "locked": False,
                    "rotation": int(shape_result["text"]["rotation"]),
                },
            ]

            # Create drawings using Project method
            logger.info(
                "Creating %d drawings in project %s...", len(drawings), project_id
            )
            results: list[dict[str, Any]] = []

            for i, drawing_data in enumerate(drawings):
                try:
                    drawing_type = shape_type if i == 0 else "text"
                    logger.info(
                        "Creating drawing %d/%d: %s at (%d, %d) with rotation %d°...",
                        i + 1,
                        len(drawings),
                        drawing_type,
                        drawing_data["x"],
                        drawing_data["y"],
                        drawing_data["rotation"],
                    )

                    result = project.create_drawing(
                        svg=drawing_data["svg"],
                        x=drawing_data["x"],
                        y=drawing_data["y"],
                        z=drawing_data["z"],
                        locked=drawing_data["locked"],
                        rotation=drawing_data["rotation"],
                    )

                    drawing_info = {
                        "drawing_id": result.get("drawing_id"),
                        "type": drawing_type,
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
                        "type": "ellipse" if i == 0 else "text",
                        "error": f"Drawing {i + 1} creation failed: {str(e)}",
                        "status": "failed",
                    }
                    results.append(error_info)
                    logger.error("Failed to create drawing %d: %s", i + 1, e)

            # Calculate summary statistics
            successful_drawings = len(
                [r for r in results if r.get("status") == "success"]
            )
            failed_drawings = len([r for r in results if r.get("status") == "failed"])

            # Prepare final result
            final_result = {
                "project_id": project_id,
                "area_name": area_name,
                "node_count": len(node_names),
                "nodes": node_names,
                "shape_type": shape_type,
                "created_drawings": results,
                "total_drawings": len(drawings),
                "successful_drawings": successful_drawings,
                "failed_drawings": failed_drawings,
            }

            # Log the final result
            logger.info(
                "Area annotation creation completed: %d successful, %d failed out of %d total drawings.",
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
            logger.error("Failed to process area annotation request: %s", e)
            return {"error": f"Failed to process area annotation request: {str(e)}"}


if __name__ == "__main__":
    # Test the tool locally
    from pprint import pprint

    # Test with ellipse (default)
    test_input_ellipse = json.dumps(
        {
            "project_id": "d7fc094c-685e-4db1-ac11-5e33a1b2e066",  # Replace with actual project UUID
            "area_name": "Core Area",
            "node_names": ["R-6", "R-4"],  # Replace with actual node names
            "shape_type": "ellipse",
        }
    )

    # Test with rectangle
    test_input_rectangle = json.dumps(
        {
            "project_id": "d7fc094c-685e-4db1-ac11-5e33a1b2e066",  # Replace with actual project UUID
            "area_name": "VLAN 10",
            "node_names": ["SW-1", "SW-2"],  # Replace with actual node names
            "shape_type": "rectangle",
        }
    )

    tool = GNS3CreateAreaDrawingTool()
    result = tool._run(test_input_ellipse)
    pprint(result)


"""
example output:
{
    'area_name': 'Area 0',
    'created_drawings': [
        {'drawing_id': 'uuid-of-drawing1', 'status': 'success', 'type': 'ellipse'},
        {'drawing_id': 'uuid-of-drawing2', 'status': 'success', 'type': 'text'}
    ],
    'failed_drawings': 0,
    'node_count': 2,
    'nodes': ['R-1', 'R-2'],
    'project_id': '2245149a-71c8-4387-9d1f-441a683ef7e7',
    'shape_type': 'ellipse',
    'successful_drawings': 2,
    'total_drawings': 2
}
"""
