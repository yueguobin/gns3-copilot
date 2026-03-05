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
GNS3 Project List Files Tool

This module provides a LangChain tool to list files in a GNS3 project.
It uses a file index stored in the project directory to track files.
"""

import json
import re

import requests
from langchain.tools import BaseTool

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.gns3_client.gns3_file_index import load_file_index
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_list_files")

# Load environment variables


class GNS3ProjectListFilesTool(BaseTool):
    """
    Tool to list files in a GNS3 project.

    This tool reads a file index maintained in the project directory
    and returns a list of all tracked files.

    Input format (JSON string):
    {
        "project_id": "uuid-of-project",
        "pattern": "*.cfg"  # Optional: filter by file pattern
    }

    Returns:
        JSON string with file list:
        {
            "project_id": "uuid-of-project",
            "files": [
                {
                    "path": "README.md",
                    "created_at": "2026-01-01T10:00:00",
                    "updated_at": "2026-01-01T10:05:00",
                    "size": 1024
                }
            ],
            "total_count": 1,
            "status": "success"
        }
    """

    name: str = "gns3_project_list_files"
    description: str = """List files in a GNS3 project using a file index.

    This tool reads a file index (.gns3_copilot_file_index.json) that tracks
    all files written to the project. It returns a list of file paths and metadata.

    Args:
        project_id (required): The UUID of the GNS3 project
        pattern (optional): A glob pattern to filter files (e.g., "*.cfg", "configs/*")

    Returns:
        A list of files with their metadata
    """

    def _run(self, tool_input: str) -> str:
        """
        Execute the tool to list files in a project.

        Args:
            tool_input: JSON string containing project_id and optional pattern

        Returns:
            JSON string containing the file list
        """
        try:
            # Parse input JSON
            input_data = json.loads(tool_input)
            project_id = input_data.get("project_id")
            pattern = input_data.get("pattern")

            # Validate input
            if not project_id:
                logger.error("Invalid input: Missing project_id.")
                return json.dumps({"error": "Missing project_id."})

            # Validate UUID format (basic check)
            uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
            if not re.match(uuid_pattern, project_id):
                logger.error("Invalid project_id format: %s", project_id)
                return json.dumps({"error": f"Invalid project_id format: {project_id}"})

            # Create connector
            connector = get_gns3_connector()
            if connector is None:
                logger.error("Failed to create GNS3 connector")
                return json.dumps(
                    {
                        "project_id": project_id,
                        "status": "failed",
                        "error": "Failed to create GNS3 connector. Check server configuration.",
                    }
                )

            # Create project instance
            project = Project(project_id=project_id, connector=connector)

            # Load file index
            logger.info("Loading file index for project: %s", project_id)
            index_data = load_file_index(project)

            # Get file list
            files = index_data.get("files", [])

            # Apply pattern filter if provided
            if pattern:
                filtered_files = []
                for file_entry in files:
                    if self._matches_pattern(file_entry["path"], pattern):
                        filtered_files.append(file_entry)
                files = filtered_files
                logger.info(
                    "Filtered %d files matching pattern: %s", len(files), pattern
                )

            # Prepare result
            result = {
                "project_id": project_id,
                "files": files,
                "total_count": len(files),
                "status": "success",
            }

            logger.info(
                "Successfully listed %d files for project: %s", len(files), project_id
            )

            return json.dumps(result, indent=2)

        except requests.HTTPError as e:
            logger.error("HTTP error listing files: %s", e)
            return json.dumps(
                {
                    "project_id": project_id if project_id else "unknown",
                    "status": "failed",
                    "error": f"HTTP error: {str(e)}",
                }
            )
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON input: %s", e)
            return json.dumps({"error": f"Invalid JSON input: {str(e)}"})
        except Exception as e:
            logger.error("Unexpected error listing files: %s", e)
            return json.dumps(
                {
                    "project_id": project_id if project_id else "unknown",
                    "status": "failed",
                    "error": f"Failed to list files: {str(e)}",
                }
            )

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a file path matches a glob pattern.

        Args:
            path: The file path to check
            pattern: The glob pattern (e.g., "*.cfg", "configs/*")

        Returns:
            True if the path matches the pattern
        """
        # Convert glob pattern to regex
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
        return bool(re.match(regex_pattern, path))


if __name__ == "__main__":
    # Test the tool
    print("=" * 80)
    print("Testing GNS3ProjectListFilesTool")
    print("=" * 80)

    try:
        tool = GNS3ProjectListFilesTool()

        # Replace with actual project ID for testing
        test_project_id = (
            "1445a4ba-4635-430b-a332-bef438f65932"  # Replace with actual project UUID
        )
        print(f"\nTesting with project: {test_project_id}")
        print("NOTE: Replace 'your-project-uuid' with actual project ID")

        # Test 1: List all files
        print("\n1. Listing all files...")
        result1 = tool._run(
            json.dumps(
                {
                    "project_id": test_project_id,
                }
            )
        )
        result_data1 = json.loads(result1)
        print(f"   Status: {result_data1.get('status')}")
        print(f"   Total files: {result_data1.get('total_count', 0)}")
        if result_data1.get("files"):
            print("   Files:")
            for file_entry in result_data1["files"]:
                print(f"     - {file_entry['path']}")

        # Test 2: List files with pattern
        print("\n2. Listing files matching pattern '*.cfg'...")
        result2 = tool._run(
            json.dumps({"project_id": test_project_id, "pattern": "*.cfg"})
        )
        result_data2 = json.loads(result2)
        print(f"   Status: {result_data2.get('status')}")
        print(f"   Matching files: {result_data2.get('total_count', 0)}")
        if result_data2.get("files"):
            print("   Files:")
            for file_entry in result_data2["files"]:
                print(f"     - {file_entry['path']}")

        # Test 3: Missing project_id
        print("\n3. Testing with missing project_id...")
        result3 = tool._run(json.dumps({}))
        print(f"   Result: {result3}")

        print("\n" + "=" * 80)
        print("Test completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
