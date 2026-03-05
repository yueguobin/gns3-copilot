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
GNS3 Connector Factory Module

This module provides factory functions for creating Gns3Connector instances
based on environment configuration. It encapsulates the logic for reading
GNS3 server settings and creating appropriately configured connectors.

Main Functions:
    get_gns3_connector: Create a Gns3Connector from environment variables

Example:
    from gns3_copilot.gns3_client import get_gns3_connector

    connector = get_gns3_connector()
    if connector:
        # Use connector to interact with GNS3 server
        projects = connector.projects
"""

from gns3_copilot.gns3_client.custom_gns3fy import Gns3Connector
from gns3_copilot.log_config import setup_logger
from gns3_copilot.utils import get_config

logger = setup_logger("connector_factory")


def get_gns3_connector() -> Gns3Connector | None:
    """Create and return a Gns3Connector instance from environment variables.

    This factory function reads GNS3 server configuration from environment
    variables and creates an appropriate Gns3Connector instance based on
    the API version. It handles both API v2 (no authentication) and
    API v3 (with username/password authentication).

    The function reads the following environment variables:
        - API_VERSION: GNS3 API version ("2" or "3")
        - GNS3_SERVER_URL: GNS3 server URL
        - GNS3_SERVER_USERNAME: Username for API v3 authentication
        - GNS3_SERVER_PASSWORD: Password for API v3 authentication

    Returns:
        Gns3Connector instance if configuration is valid, None otherwise

    Example:
        # Create connector from environment
        connector = get_gns3_connector()
        if connector:
            projects = connector.projects
        else:
            logger.error("Failed to create GNS3 connector")
    """
    try:
        # Get GNS3 server configuration from SQLite database
        api_version_str = get_config("API_VERSION")
        server_url = get_config("GNS3_SERVER_URL")

        if not api_version_str:
            logger.error("API_VERSION not configured")
            return None

        if not server_url:
            logger.error("GNS3_SERVER_URL not configured")
            return None

        # Create connector based on API version
        if api_version_str == "2":
            # API v2 does not require authentication
            connector = Gns3Connector(
                url=server_url,
                api_version=int(api_version_str),
            )
            logger.debug("Created Gns3Connector for API v2")
        elif api_version_str == "3":
            # API v3 requires username and password
            username = get_config("GNS3_SERVER_USERNAME")
            password = get_config("GNS3_SERVER_PASSWORD")

            connector = Gns3Connector(
                url=server_url,
                user=username,
                cred=password,
                api_version=int(api_version_str),
            )
            logger.debug("Created Gns3Connector for API v3")
        else:
            logger.error("Unsupported API_VERSION: %s", api_version_str)
            return None

        logger.info("Successfully created Gns3Connector")
        return connector

    except Exception as e:
        logger.error("Failed to create Gns3Connector: %s", str(e))
        return None
