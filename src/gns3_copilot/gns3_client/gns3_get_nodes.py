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
GNS3 node retrieval tool for device information.

Provides functionality to retrieve all node instances from a project,
including node dimensions, symbol, and other attributes.
"""

import json
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_get_nodes")


class GNS3GetNodesTool(BaseTool):
    """
    A LangChain tool to retrieve all node instances from a GNS3 project.
    The tool connects to the GNS3 server and extracts comprehensive node information
    including dimensions, symbol, coordinates, and other attributes.

    **Input:**
    A JSON string with project_id parameter.
    Example: '{"project_id": "uuid-of-project"}'

    **Output:**
    A dictionary containing a list of dictionaries, each with comprehensive node information.
    Example output:
        {
            "nodes": [
                {
                    "name": "R-1",
                    "node_id": "uuid1",
                    "node_type": "iou",
                    "height": 50,
                    "width": 50,
                    "symbol": ":/symbols/router.svg",
                    "x": -180,
                    "y": -30,
                    "z": 1,
                    "status": "started",
                    "ports": [
                        {"name": "Ethernet0/0", "short_name": "e0/0", "adapter_number": 0, "port_number": 0},
                        {"name": "Ethernet0/1", "short_name": "e0/1", "adapter_number": 0, "port_number": 1}
                    ]
                }
            ]
        }
    If an error occurs, returns a dictionary with an error message.
    """

    name: str = "get_gns3_nodes"
    description: str = """
    Retrieves all node instances from a GNS3 project.
    Requires a JSON string input with 'project_id' parameter.
    Returns comprehensive node information including name, node_id, node_type,
    height, width, symbol, coordinates (x, y, z), status, and simplified port information.
    Example input: '{"project_id": "uuid-of-project"}'
    Example output:
        {
            "nodes": [
                {
                    "name": "R-1",
                    "node_id": "uuid1",
                    "node_type": "iou",
                    "height": 50,
                    "width": 50,
                    "symbol": ":/symbols/router.svg",
                    "x": -180,
                    "y": -30,
                    "z": 1,
                    "status": "started",
                    "ports": [
                        {"name": "Ethernet0/0", "short_name": "e0/0", "adapter_number": 0, "port_number": 0}
                    ]
                }
            ]
        }
    """

    def _run(
        self,
        tool_input: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> dict[str, Any]:
        """
        Connects to the GNS3 server and retrieves all nodes from the specified project.

        Args:
            tool_input (str): JSON string containing project_id parameter.
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary containing the list of nodes or an error message.
        """
        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")

            if not project_id:
                logger.error("Missing project_id in input")
                return {"error": "Missing required parameter: project_id"}

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Retrieve all nodes from the project
            logger.info(f"Retrieving nodes from project: {project_id}")
            nodes = gns3_server.get_nodes(project_id)

            # Simplify and organize node information
            node_info = []
            for node in nodes:
                # Simplify ports - keep essential information only
                simplified_ports = []
                if node.get("ports"):
                    for port in node["ports"]:
                        simplified_ports.append(
                            {
                                "name": port.get("name", "N/A"),
                                "short_name": port.get("short_name", "N/A"),
                                "adapter_number": port.get("adapter_number", 0),
                                "port_number": port.get("port_number", 0),
                            }
                        )

                # Extract node information
                node_data = {
                    "name": node.get("name", "N/A"),
                    "node_id": node.get("node_id", "N/A"),
                    "node_type": node.get("node_type", "N/A"),
                    "height": node.get("height"),  # Node height (read-only)
                    "width": node.get("width"),  # Node width (read-only)
                    "symbol": node.get("symbol", "N/A"),
                    "x": node.get("x"),
                    "y": node.get("y"),
                    "z": node.get("z"),
                    "status": node.get("status", "N/A"),
                    "console": node.get("console"),
                    "console_type": node.get("console_type", "N/A"),
                    "ports": simplified_ports,
                }
                node_info.append(node_data)

            # Log the retrieved nodes
            logger.debug(
                "Retrieved nodes: %s",
                json.dumps(node_info, indent=2, ensure_ascii=False),
            )

            # Return JSON-formatted result
            result = {"nodes": node_info}
            logger.info(
                "Node retrieval completed. Total nodes: %d.",
                len(node_info),
            )
            return result

        except json.JSONDecodeError as e:
            logger.error("Failed to parse input JSON: %s", e)
            return {"error": f"Invalid JSON input: {str(e)}"}
        except Exception as e:
            logger.error("Failed to connect to GNS3 server or retrieve nodes: %s", e)
            return {"error": f"Failed to retrieve nodes: {str(e)}"}


if __name__ == "__main__":
    # Test the tool locally
    tool = GNS3GetNodesTool()

    # Example: Replace with your actual project_id
    test_project_id = "d7fc094c-685e-4db1-ac11-5e33a1b2e066"
    result = tool._run(f'{{"project_id": "{test_project_id}"}}')
    pprint(result)
