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
GNS3 File Index Manager

This module provides functionality to manage an index of files in GNS3 projects.
Since GNS3 API doesn't provide a way to list files, we maintain an index
file to track files written to each project.
"""

import json
from datetime import datetime
from typing import Any

from gns3_copilot.gns3_client import Project, get_gns3_connector
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_file_index")

# Load environment variables

# Index file name (stored in project directory)
INDEX_FILE_NAME = ".gns3_copilot_file_index.json"


def _get_index_path(project_id: str) -> str:
    """
    Get the path to the index file for a project.

    Args:
        project_id: The project ID

    Returns:
        The path to the index file (relative to project directory)
    """
    return INDEX_FILE_NAME


def load_file_index(project: Project) -> dict[str, Any]:
    """
    Load the file index for a project.

    Args:
        project: GNS3 Project instance

    Returns:
        A dictionary containing the index data, or an empty index if not found
    """
    if project.project_id is None:
        raise ValueError("Project ID must be set")

    index_path = _get_index_path(project.project_id)

    try:
        content = project.get_file(path=index_path)
        index_data = json.loads(content)

        # Validate index structure
        if not isinstance(index_data, dict):
            logger.warning("Invalid index structure, creating new index")
            return _create_empty_index(project.project_id)

        if "files" not in index_data:
            index_data["files"] = []

        logger.info(
            "Loaded file index for project %s with %d files",
            project.project_id,
            len(index_data["files"]),
        )
        return index_data

    except Exception as e:
        logger.info(
            "No existing file index found for project %s, creating new one: %s",
            project.project_id,
            e,
        )
        return _create_empty_index(project.project_id)


def save_file_index(project: Project, index_data: dict[str, Any]) -> None:
    """
    Save the file index for a project.

    Args:
        project: GNS3 Project instance
        index_data: The index data to save

    Raises:
        ValueError: If failed to save the index
    """
    if project.project_id is None:
        raise ValueError("Project ID must be set")

    index_path = _get_index_path(project.project_id)

    try:
        # Ensure project_id is in the index
        index_data["project_id"] = project.project_id

        # Save as JSON with indentation for readability
        content = json.dumps(index_data, indent=2, ensure_ascii=False)

        project.write_file(path=index_path, data=content)
        logger.info("Saved file index for project %s", project.project_id)

    except Exception as e:
        logger.error(
            "Failed to save file index for project %s: %s", project.project_id, e
        )
        raise ValueError(f"Failed to save file index: {str(e)}") from e


def _create_empty_index(project_id: str) -> dict[str, Any]:
    """
    Create an empty file index structure.

    Args:
        project_id: The project ID

    Returns:
        A dictionary with empty index structure
    """
    return {
        "project_id": project_id,
        "files": [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def add_file_to_index(
    project: Project,
    path: str,
    size: int | None = None,
) -> dict[str, Any]:
    """
    Add or update a file in the project index.

    Args:
        project: GNS3 Project instance
        path: The file path
        size: Optional file size in bytes

    Returns:
        The updated index data

    Raises:
        ValueError: If failed to update the index
    """
    try:
        # Load existing index
        index_data = load_file_index(project)

        # Check if file already exists
        file_entry = next((f for f in index_data["files"] if f["path"] == path), None)

        now = datetime.now().isoformat()

        if file_entry:
            # Update existing file
            file_entry["updated_at"] = now
            if size is not None:
                file_entry["size"] = size
            logger.info("Updated file in index: %s", path)
        else:
            # Add new file
            new_entry: dict[str, Any] = {
                "path": path,
                "created_at": now,
                "updated_at": None,
            }
            if size is not None:
                new_entry["size"] = size

            index_data["files"].append(new_entry)
            logger.info("Added file to index: %s", path)

        # Update index timestamp
        index_data["updated_at"] = now

        # Save index
        save_file_index(project, index_data)

        return index_data

    except Exception as e:
        logger.error("Failed to add file to index: %s", e)
        raise ValueError(f"Failed to add file to index: {str(e)}") from e


def get_file_list(project: Project) -> list[dict[str, Any]]:
    """
    Get the list of files from the project index.

    Args:
        project: GNS3 Project instance

    Returns:
        A list of file entries
    """
    try:
        index_data = load_file_index(project)
        files = index_data.get("files", [])
        return files if isinstance(files, list) else []
    except Exception as e:
        logger.error("Failed to get file list: %s", e)
        return []


if __name__ == "__main__":
    # Test the file index manager
    print("=" * 80)
    print("Testing GNS3 File Index Manager")
    print("=" * 80)

    try:
        # Create connector and project
        connector = get_gns3_connector()
        if connector is None:
            print("ERROR: Failed to create GNS3 connector")
            exit(1)

        # Replace with actual project ID for testing
        test_project_id = "your-project-uuid"
        print(f"\nTesting with project: {test_project_id}")
        print("NOTE: Replace 'your-project-uuid' with actual project ID")

        # Create project instance
        project = Project(project_id=test_project_id, connector=connector)

        # Load index
        print("\n1. Loading file index...")
        index_data = load_file_index(project)
        print(f"   Index loaded: {len(index_data.get('files', []))} files")

        # Add file to index
        print("\n2. Adding file to index...")
        updated_index = add_file_to_index(project, "test_file.txt", size=1024)
        print(f"   File added. Total files: {len(updated_index['files'])}")

        # Get file list
        print("\n3. Getting file list...")
        file_list = get_file_list(project)
        print("   Files in index:")
        for file_entry in file_list:
            print(f"   - {file_entry['path']}")

        print("\n" + "=" * 80)
        print("Test completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
