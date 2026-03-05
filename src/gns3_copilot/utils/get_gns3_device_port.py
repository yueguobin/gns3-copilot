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
Public module for getting device port information from GNS3 topology
"""

from typing import Any

from gns3_copilot.log_config import setup_tool_logger

logger = setup_tool_logger("get_gns3_device_port")


def get_device_ports_from_topology(
    device_names: list[str],
    project_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Get device connection information from GNS3 topology

    Args:
        device_names: List of device names to look up
        project_id: UUID of the specific GNS3 project to retrieve topology from

    Returns:
        Dictionary mapping device names to their connection data:
        {
            "device_name": {
                "port": console_port,
                "groups": ["cisco_IOSv_telnet"]
            }
        }
        Devices that don't exist or missing console_port will not be included
    """
    # Log received parameters
    logger.info("Called with device_names=%s, project_id=%s", device_names, project_id)

    try:
        # Lazy import to avoid circular dependency
        from gns3_copilot.gns3_client import GNS3TopologyTool

        # Get topology information
        topo = GNS3TopologyTool()
        topology = topo._run(project_id=project_id)

        # Log topology data
        logger.debug("Topology data retrieved: %s", topology)
        logger.info("Retrieved topology with %d nodes", len(topology.get("nodes", {})))

        # Dynamically build hosts_data from topology
        hosts_data: dict[str, dict[str, Any]] = {}

        if not topology:
            logger.warning("Unable to get topology information")
            return hosts_data

        logger.debug("GNS3 topology: %s", topology)

        for device_name in device_names:
            logger.debug("Processing device: %s", device_name)
            # Check if device exists in topology
            if device_name not in topology.get("nodes", {}):
                logger.warning("Device '%s' not found in topology", device_name)
                continue

            node_info = topology["nodes"][device_name]
            if "console_port" not in node_info:
                logger.warning("Device '%s' missing console_port", device_name)
                continue

            # Add device to hosts_data
            hosts_data[device_name] = {
                "port": node_info["console_port"],
                "groups": ["cisco_IOSv_telnet"],
            }

        # Log final result
        logger.debug("Returning hosts_data: %s", hosts_data)
        logger.info("Returning %d device port mappings", len(hosts_data))

        return hosts_data

    except Exception as e:
        logger.error("Error getting device port information: %s", e)
        return {}
