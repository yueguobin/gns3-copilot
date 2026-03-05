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

from typing import Any

from langchain.tools import BaseTool

from gns3_copilot.gns3_client import get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_list")

"""
example output:

[('mylab', 'ff8e059c-c33d-47f4-bc11-c7dda8a1d500', 0, 0, 'closed'),
 ('q-learning-traffic-management', '69d49a6a-ff7f-45dd-af1e-dc14aff600cc', 0, 0, 'closed'),
 ('network_ai', 'f2f7ed27-7aa3-4b11-a64c-da947a2c7210', 6, 8, 'opened'),
 ('test', '365dd3ff-cda9-447a-94da-3a6cef75fe77', 0, 0, 'closed'),
 ('Soft-RoCE learning', 'd1e4509e-64bd-4109-b954-266223959ee9', 0, 0, 'closed')]

"""


class GNS3ProjectList(BaseTool):
    name: str = "list_gns3_projects"
    description: str = """
    Retrieves a list of all GNS3 projects with their details.
    Returns a dictionary containing a list of project information including name,
    project_name, project_id, nodes count, links count, and status.
    Example output:
        {
            "projects": [
                ("mylab", "ff8e059c-c33d-47f4-bc11-c7dda8a1d500", 0, 0, "closed"),
                ("network_ai", "f2f7ed27-7aa3-4b11-a64c-da947a2c7210", 6, 8, "opened")
            ]
        }
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Initialize Gns3Connector using factory function
            logger.info("Connecting to GNS3 server...")
            server = get_gns3_connector()

            if server is None:
                logger.error("Failed to create GNS3 connector")
                return {
                    "error": "Failed to connect to GNS3 server. Please check your configuration."
                }

            # Return the projects data in a structured format
            projects = server.projects_summary(is_print=False)

            # Prepare result
            result = {"projects": projects}

            # Log result
            logger.info("Projects list result: %s", result)

            return result

        except Exception as e:
            logger.error("Error retrieving GNS3 project list: %s", str(e))
            return {"error": f"Failed to retrieve GNS3 project list: {str(e)}"}


if __name__ == "__main__":
    from pprint import pprint

    # Test the tool
    tool = GNS3ProjectList()

    print("Testing GNS3ProjectList - retrieving all projects...")
    result = tool._run()
    pprint(result)
