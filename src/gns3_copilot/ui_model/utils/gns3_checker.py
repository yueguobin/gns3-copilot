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
GNS3 API Connectivity Checker Module.

This module provides functionality to verify the connectivity and accessibility
of the configured GNS3 server API. It validates configuration parameters and
tests the connection to ensure the application can communicate with the GNS3
server using the provided credentials.

Key Functions:
    check_gns3_api(): Test GNS3 server API connectivity with current configuration

Configuration Validation:
    - API Version (2 or 3): Determines required authentication fields
    - GNS3 Server Host: Server IP address or hostname
    - GNS3 Server URL: Full API endpoint URL
    - GNS3 Username/Password: Required for API v3 authentication

Error Handling:
    - Missing required fields: Displays clear error message listing missing fields
    - Connection timeout: Handles network timeout after 5 seconds
    - Authentication failure: Reports HTTP 401/403 errors
    - Network errors: Catches and displays RequestException details

Example:
    Test GNS3 API connectivity from settings page:
        from gns3_copilot.ui_model.utils import check_gns3_api

        if st.button("Check GNS3 API"):
            check_gns3_api()
            # Displays success or error message in UI
"""

import requests
import streamlit as st
from requests.exceptions import RequestException

from gns3_copilot.log_config import setup_logger

logger = setup_logger("gns3_checker")


def check_gns3_api() -> None:
    """
    Check whether the GNS3 API is reachable using the provided configuration.
    """
    logger.info("Starting GNS3 API check.")

    version: str = str(st.session_state.get("API_VERSION", "2"))

    required_fields = {
        "GNS3_SERVER_HOST": "GNS3 Server Host",
        "GNS3_SERVER_URL": "GNS3 Server URL",
        "API_VERSION": "API Version",
    }

    # Add auth fields for API v3
    if version == "3":
        required_fields.update(
            {
                "GNS3_SERVER_USERNAME": "GNS3 Server Username",
                "GNS3_SERVER_PASSWORD": "GNS3 Server Password",
            }
        )

    # Detect missing fields
    missing_fields = [
        label for key, label in required_fields.items() if not st.session_state.get(key)
    ]

    if missing_fields:
        message = "Please fill out the following fields:\n\n"
        message += "\n".join(f" - {field}" for field in missing_fields)
        logger.warning("Missing fields detected: %s", ", ".join(missing_fields))
        st.error(message)
        return

    # Extract validated values
    url: str = st.session_state.get("GNS3_SERVER_URL", "")
    auth: tuple[str, str] | None = None

    if version == "3":
        u = st.session_state.get("GNS3_SERVER_USERNAME", "")
        p = st.session_state.get("GNS3_SERVER_PASSWORD", "")
        if u and p:
            auth = (u, p)

    logger.debug(
        "Checking GNS3 API", extra={"url": url, "version": version, "auth": bool(auth)}
    )

    try:
        response = requests.get(url, auth=auth, timeout=5)
        response.raise_for_status()

        logger.info("Successfully connected to the GNS3 API at %s", url)
        st.success(f"Successfully connected to the GNS3 API at {url}")

    except RequestException as exc:
        logger.error(f"Failed to connect to the GNS3 API: {exc}")
        st.error(f"Failed to connect to the GNS3 API: {exc}")
