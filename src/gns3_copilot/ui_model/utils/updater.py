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
Core Update Logic Module for GNS3 Copilot.

This module provides the core functionality for checking and updating the
GNS3 Copilot application from PyPI. It includes version comparison,
update availability checking, and the update installation process.

This module is platform-agnostic and doesn't depend on Streamlit, making it
suitable for reuse in different contexts (CLI, web UI, automated scripts).

Key Functions:
    get_installed_version(): Retrieve the currently installed version
    get_latest_version(): Fetch the latest version from PyPI
    is_update_available(): Compare versions and check for updates
    run_update(): Execute the update process using pip

Constants:
    PYPI_URL: PyPI API endpoint for version information

Error Handling:
    - Network timeout: 5-second timeout for PyPI API requests
    - Invalid version: Handles version parsing errors gracefully
    - Subprocess timeout: 5-minute timeout for pip update process
    - Update failures: Returns descriptive error messages

Example:
    Check for updates programmatically:
        from gns3_copilot.ui_model.utils.updater import (
            is_update_available,
            run_update,
        )

        available, current, latest = is_update_available()
        if available:
            print(f"Update available: {current} -> {latest}")
            success, message = run_update()
            if success:
                print(message)
"""

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

from packaging.version import InvalidVersion, Version

PYPI_URL = "https://pypi.org/pypi/gns3-copilot/json"
SETTINGS_FILE = Path.home() / ".config" / "gns3-copilot" / "settings.json"


def get_installed_version() -> str:
    from gns3_copilot import __version__

    return __version__


def get_latest_version() -> str:
    with urllib.request.urlopen(PYPI_URL, timeout=5) as response:
        response_text = response.read().decode()
        data: dict = json.loads(response_text)
        info: dict = data["info"]
        version: str = info["version"]
        return version


def is_update_available() -> tuple[bool, str, str]:
    current = get_installed_version()
    latest = get_latest_version()

    try:
        if current == "unknown":
            return False, current, latest
        return Version(latest) > Version(current), current, latest
    except InvalidVersion:
        return False, current, latest


def save_skipped_version(version: str) -> None:
    """Save the skipped update version to settings file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if SETTINGS_FILE.exists():
            settings = json.loads(SETTINGS_FILE.read_text())
        else:
            settings = {}
        settings["skipped_update_version"] = version
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2))
    except Exception:
        pass


def load_skipped_version() -> str:
    """Load the skipped update version from settings file."""
    try:
        if SETTINGS_FILE.exists():
            settings: dict[str, str] = json.loads(SETTINGS_FILE.read_text())
            skipped = settings.get("skipped_update_version", "")
            return skipped if isinstance(skipped, str) else ""
    except Exception:
        pass
    return ""


def run_update() -> tuple[bool, str]:
    """Update gns3-copilot from PyPI"""
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "gns3-copilot",
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            # Check if anything was actually upgraded
            if (
                "Successfully installed" in result.stdout
                or "Requirement already satisfied" in result.stdout
            ):
                success_message: str = "Update completed successfully. Please restart GNS3 Copilot to use the new version."
                return True, success_message
            else:
                no_update_message: str = (
                    "No updates needed. You're already on the latest version."
                )
                return True, no_update_message
        else:
            error_message: str = f"Update failed:\n{result.stderr}"
            return False, error_message

    except subprocess.TimeoutExpired:
        timeout_message: str = "Update timed out after 5 minutes. Please try again."
        return False, timeout_message
    except Exception as e:
        exception_message: str = f"Unexpected error during update: {str(e)}"
        return False, exception_message
