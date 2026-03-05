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
GNS3 template retrieval tool for device discovery.

Provides functionality to retrieve all available device templates
from a GNS3 server, including template names, IDs, and types.
"""

import json
from pprint import pprint
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from gns3_copilot.gns3_client import get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_get_node_temp")


class GNS3TemplateTool(BaseTool):
    """
    A LangChain tool to retrieve all available device templates from a GNS3 server.
    The tool connects to the GNS3 server and extracts the name, template_id, and template_type
    for each template.

    **Input:**
    No input is required for this tool. It connects to the GNS3 server at the default URL
    (http://localhost:3080) and retrieves all templates.

    **Output:**
    A dictionary containing a list of dictionaries, each with the name, template_id, and
    template_type of a template. Example output:
        {
            "templates": [
                {"name": "Router1", "template_id": "uuid1", "template_type": "qemu"},
                {"name": "Switch1", "template_id": "uuid2", "template_type": "ethernet_switch"}
            ]
        }
    If an error occurs, returns a dictionary with an error message.
    """

    name: str = "get_gns3_templates"
    description: str = """
    Retrieves all available device templates from a GNS3 server.
    Returns a dictionary containing a list of dictionaries, each with the name, template_id,
    and template_type of a template. No input is required.
    Example output:
        {
            "templates": [
                {"name": "Router1", "template_id": "uuid1", "template_type": "qemu"},
                {"name": "Switch1", "template_id": "uuid2", "template_type": "ethernet_switch"}
            ]
        }
    If the connection fails, returns a dictionary with an error message.
    """

    def _run(
        self,
        tool_input: str = "",
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> dict[str, Any]:
        """
        Connects to the GNS3 server and retrieves a list of all available device templates.

        Args:
            tool_input (str): Optional input (not used in this tool).
            run_manager: LangChain run manager (unused).

        Returns:
            dict: A dictionary containing the list of templates or an error message.
        """
        try:
            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            gns3_server = get_gns3_connector()

            if gns3_server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Retrieve all available templates
            templates = gns3_server.get_templates()
            # Extract name, template_id, and template_type
            template_info = [
                {
                    "name": template.get("name", "N/A"),
                    "template_id": template.get("template_id", "N/A"),
                    "template_type": template.get("template_type", "N/A"),
                }
                for template in templates
            ]

            # Log the retrieved templates
            logger.debug(
                "Retrieved templates: %s",
                json.dumps(template_info, indent=2, ensure_ascii=False),
            )

            # Return JSON-formatted result with full logging
            result = {"templates": template_info}
            logger.info(
                "Template retrieval completed. Total templates: %d. Result: %s",
                len(template_info),
                json.dumps(result, indent=2, ensure_ascii=False),
            )
            return result

        except Exception as e:
            logger.error(
                "Failed to connect to GNS3 server or retrieve templates: %s", e
            )
            return {"error": f"Failed to retrieve templates: {str(e)}"}


if __name__ == "__main__":
    # Test's tool locally
    tool = GNS3TemplateTool()
    result = tool._run("")
    pprint(result)
