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
GNS3 node startup tool for network device activation.

Provides functionality to start one or multiple nodes in GNS3 projects
with progress tracking and status monitoring.
"""

import json
import time
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import Node, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_start_node")


def show_progress_bar(
    duration: int = 120, interval: int = 1, node_count: int = 1
) -> None:
    """
    Display a simple text progress bar for node startup.

    Args:
        duration: Total duration of the progress bar in seconds
        interval: Update interval in seconds
        node_count: Number of nodes being started
    """
    print(f"Starting {node_count} node(s), please wait...")
    for elapsed in range(duration):
        # Calculate progress percentage
        progress = (elapsed + 1) / duration * 100

        # Create progress bar display
        bar_length = 30
        filled_length = int(bar_length * elapsed // duration)
        progress_string = (
            "=" * filled_length + ">" + " " * (bar_length - filled_length - 1)
        )

        # Print progress bar with node count
        print(f"\r[{progress_string}] {progress:.1f}%", end="", flush=True)
        time.sleep(interval)

    print(f"\n{node_count} node(s) startup completed!")


class GNS3StartNodeTool(BaseTool):
    """
    A LangChain tool to start one or multiple nodes in a GNS3 project.

    **Input**:
    A JSON object with project_id and node_ids (list of node IDs).
    Example:
        {
            "project_id": "uuid-of-project",
            "node_ids": ["uuid-of-node-1", "uuid-of-node-2"]
        }

    **Output**:
    A dictionary with all nodes' details:
    {
        "project_id": "...",
        "total_nodes": 2,
        "successful": 2,
        "failed": 0,
        "nodes": [
            {"node_id": "...", "name": "...", "status": "..."},
            {"node_id": "...", "name": "...", "status": "..."}
        ]
    }
    """

    name: str = "start_gns3_node"
    description: str = """
    Starts one or multiple nodes in a GNS3 project.
    Input: JSON with project_id and node_ids (list of node IDs).
    Returns: A dictionary with all nodes' details including success/failure status.
    """

    def _run(
        self, tool_input: str, run_manager: CallbackManagerForToolRun | None = None
    ) -> dict[str, Any]:
        logger.debug("Received input: %s", tool_input)
        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            node_ids = input_data.get("node_ids")

            # Validate input
            if not project_id or not node_ids:
                logger.error("Missing required fields: project_id or node_ids.")
                return {"error": "Missing required fields: project_id and node_ids."}

            if not isinstance(node_ids, list):
                logger.error("node_ids must be a list.")
                return {"error": "node_ids must be a list."}

            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # First loop: Send start commands for all nodes
            logger.info(
                "Sending start commands for %d nodes in project %s...",
                len(node_ids),
                project_id,
            )
            for node_id in node_ids:
                try:
                    node = Node(
                        project_id=project_id, node_id=node_id, connector=gns3_server
                    )
                    # Verify node exists
                    node.get()
                    if node.node_id:
                        node.start()
                        logger.info("Start command sent for node %s", node_id)
                    else:
                        logger.error(
                            "Node %s not found in project %s", node_id, project_id
                        )
                except Exception as e:
                    logger.error(
                        "Failed to send start command for node %s: %s", node_id, e
                    )

            # Calculate progress bar duration: 140s base + 10s per additional node
            base_duration = 140
            extra_duration = max(0, len(node_ids) - 1) * 10
            total_duration = base_duration + extra_duration

            # Show progress bar
            show_progress_bar(
                duration=total_duration, interval=1, node_count=len(node_ids)
            )

            # Second loop: Get status for all nodes
            results = []
            logger.info("Retrieving status for %d nodes...", len(node_ids))
            for node_id in node_ids:
                try:
                    node = Node(
                        project_id=project_id, node_id=node_id, connector=gns3_server
                    )
                    node.get()  # Get latest status
                    node_info = {
                        "node_id": node.node_id,
                        "name": node.name or "N/A",
                        "status": node.status or "unknown",
                    }
                    results.append(node_info)
                    logger.debug("Node %s status: %s", node_id, node_info["status"])
                except Exception as e:
                    logger.error("Failed to get status for node %s: %s", node_id, e)
                    results.append(
                        {
                            "node_id": node_id,
                            "name": "N/A",
                            "status": "error",
                            "error": str(e),
                        }
                    )

            # Analyze results
            successful_nodes = [r for r in results if r.get("status") != "error"]
            failed_nodes = [r for r in results if r.get("status") == "error"]

            # Construct final response
            response = {
                "project_id": project_id,
                "total_nodes": len(node_ids),
                "successful": len(successful_nodes),
                "failed": len(failed_nodes),
                "nodes": results,
            }

            logger.info(
                "Start operation completed: %d successful, %d failed",
                len(successful_nodes),
                len(failed_nodes),
            )
            logger.debug(
                "Final result: %s", json.dumps(response, indent=2, ensure_ascii=False)
            )

            return response

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s", e)
            return {"error": f"Invalid JSON input: {e}"}
        except Exception as e:
            logger.error("Failed to start nodes: %s", e)
            return {"error": f"Failed to start nodes: {str(e)}"}


if __name__ == "__main__":
    # Test with single node
    print("=== Testing single node startup ===")
    test_input_single = json.dumps(
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",  # Replace with actual project UUID
            "node_ids": [
                "fbeda109-9a74-4d8c-a749-cc3847911a90"
            ],  # Replace with actual node UUID
        }
    )
    tool = GNS3StartNodeTool()
    result_single = tool._run(test_input_single)
    pprint(result_single)

    # Test with multiple nodes
    print("\n=== Testing multiple nodes startup ===")
    test_input_multiple = json.dumps(
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",  # Replace with actual project UUID
            "node_ids": [
                "fbeda109-9a74-4d8c-a749-cc3847911a90",  # Replace with actual node UUIDs
                "another-node-uuid-here",
                "third-node-uuid-here",
            ],
        }
    )
    result_multiple = tool._run(test_input_multiple)
    pprint(result_multiple)
