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
Application Configuration Manager for GNS3 Copilot.

This module provides a unified interface for managing application configuration
stored in SQLite database. It includes default values for all configuration
items and helper functions for reading and saving configuration.

Functions:
    get_config(key, default=None): Retrieve a configuration value with default
    set_config(key, value): Save a configuration value to database
    get_all_config(): Retrieve all configuration values
    init_config(): Initialize database with default values

Constants:
    DEFAULT_CONFIG: Dictionary containing all configuration keys and their defaults
"""

from typing import Any

from gns3_copilot.log_config import setup_logger
from gns3_copilot.utils.config_db import (
    clear_all,
    get_all_values,
    get_value,
    init_db,
    set_value,
)

logger = setup_logger("app_config")

# Default configuration values for all application settings
DEFAULT_CONFIG: dict[str, str] = {
    # GNS3 Server Configuration
    "GNS3_SERVER_HOST": "",
    "GNS3_SERVER_URL": "http://127.0.0.1:3080/",
    "API_VERSION": "2",
    "GNS3_SERVER_USERNAME": "",
    "GNS3_SERVER_PASSWORD": "",
    # Model Configuration
    "MODE_PROVIDER": "openai",
    "MODEL_NAME": "gpt-4",
    "MODEL_API_KEY": "",
    "BASE_URL": "",
    "TEMPERATURE": "0.0",
    # Voice Configuration
    "VOICE": "False",
    # Voice TTS Configuration
    "TTS_API_KEY": "",
    "TTS_BASE_URL": "",
    "TTS_MODEL": "tts-1",
    "TTS_VOICE": "alloy",
    "TTS_SPEED": "1.0",
    # Voice STT Configuration
    "STT_API_KEY": "",
    "STT_BASE_URL": "",
    "STT_MODEL": "whisper-1",
    "STT_LANGUAGE": "en",
    "STT_TEMPERATURE": "0.0",
    "STT_RESPONSE_FORMAT": "json",
    # Linux Telnet Configuration
    "LINUX_TELNET_USERNAME": "",
    "LINUX_TELNET_PASSWORD": "",
    # Prompt Configuration
    "ENGLISH_LEVEL": "Normal Prompt",
    # Reading Page Configuration
    "CALIBRE_SERVER_URL": "",
    "READING_NOTES_DIR": "notes",
    # UI Configuration
    "CONTAINER_HEIGHT": "1200",
    "ZOOM_SCALE_TOPOLOGY": "0.8",
    # Other Settings
    "LANGUAGE": "zh",
    "TTS_HTTP_REFERER": "",
    "TTS_X_TITLE": "",
}


def _get_default(key: str) -> str | None:
    """Get the default value for a configuration key.

    Args:
        key: Configuration key

    Returns:
        Default value if key exists, None otherwise
    """
    return DEFAULT_CONFIG.get(key)


def get_config(key: str, default: str | None = None) -> str:
    """Retrieve a configuration value from the database.

    If the key doesn't exist in the database, it will use the default value
    from DEFAULT_CONFIG. If the key is not in DEFAULT_CONFIG either, it will
    use the provided default parameter.

    Args:
        key: The configuration key to retrieve
        default: Fallback default value if key not in DEFAULT_CONFIG

    Returns:
        The configuration value as a string

    Example:
        >>> get_config("GNS3_SERVER_URL")
        'http://127.0.0.1:3080/'

        >>> get_config("CUSTOM_KEY", "default_value")
        'default_value'
    """
    # Get default value from DEFAULT_CONFIG or use provided default
    default_value = default if default is not None else _get_default(key)

    # Retrieve value from database
    value = get_value(key, default_value)

    if value is None:
        logger.debug("Config key '%s' not found, using default: %s", key, default_value)
        return default_value if default_value is not None else ""

    # Ensure value is a string
    return str(value) if value else default_value if default_value else ""


def set_config(key: str, value: str) -> bool:
    """Save a configuration value to the database.

    Args:
        key: The configuration key to save
        value: The configuration value to store

    Returns:
        True if save was successful, False otherwise

    Example:
        >>> set_config("GNS3_SERVER_URL", "http://192.168.1.100:3080")
        True
    """
    return set_value(key, value)


def get_all_config() -> dict[str, str]:
    """Retrieve all configuration values from the database.

    Returns:
        Dictionary with all configuration key-value pairs

    Example:
        >>> config = get_all_config()
        >>> print(config["GNS3_SERVER_URL"])
        'http://127.0.0.1:3080/'
    """
    return get_all_values()


def init_config() -> None:
    """Initialize the configuration database with default values.

    This function initializes the database and populates it with default
    values for all configuration keys. If a key already exists in the
    database, its value will not be overwritten.

    This should be called once at application startup.

    Example:
        >>> init_config()
        # Database is now initialized with default values
    """
    try:
        # Initialize database and create tables
        init_db()

        # Set default values for all keys (only if not already set)
        for key, default_value in DEFAULT_CONFIG.items():
            existing_value = get_value(key)
            if existing_value is None:
                set_value(key, default_value)
                logger.debug("Initialized default config: %s = %s", key, default_value)
            else:
                logger.debug("Config key '%s' already exists, skipping", key)

        logger.info(
            "Configuration database initialized with %d keys", len(DEFAULT_CONFIG)
        )
    except Exception as e:
        logger.error("Failed to initialize configuration: %s", e)
        raise


def reset_config() -> None:
    """Reset all configuration to default values.

    This function clears all existing configuration values and
    restores them to defaults defined in DEFAULT_CONFIG.

    Example:
        >>> reset_config()
        # All configuration values are now set to defaults
    """
    try:
        # Clear all existing values
        clear_all()

        # Re-initialize with defaults
        init_config()

        logger.info("Configuration reset to defaults")
    except Exception as e:
        logger.error("Failed to reset configuration: %s", e)
        raise


def get_nornir_defaults() -> dict[str, Any]:
    """Get Nornir default configuration.

    Returns:
        Dictionary containing Nornir defaults

    Example:
        >>> defaults = get_nornir_defaults()
        >>> print(defaults)
        {'data': {'location': 'gns3'}}
    """
    return {"data": {"location": "gns3"}}


def get_nornir_all_groups_config() -> dict[str, dict[str, Any]]:
    """Get all Nornir groups configuration for network devices.

    Returns:
        Dictionary containing all Nornir group configurations

    Example:
        >>> groups = get_nornir_all_groups_config()
        >>> print(groups['linux_telnet'])
        {'platform': 'linux', 'hostname': '127.0.0.1', ...}
    """
    return {
        "cisco_IOSv_telnet": {
            "platform": "cisco_ios",
            "hostname": get_config("GNS3_SERVER_HOST"),
            "timeout": 120,
            "username": get_config("GNS3_SERVER_USERNAME"),
            "password": get_config("GNS3_SERVER_PASSWORD"),
            "connection_options": {
                "netmiko": {"extras": {"device_type": "cisco_ios_telnet"}}
            },
        },
        "linux_telnet": {
            "platform": "linux",
            "hostname": get_config("GNS3_SERVER_HOST"),
            "timeout": 120,
            "username": get_config("LINUX_TELNET_USERNAME"),
            "password": get_config("LINUX_TELNET_PASSWORD"),
            "connection_options": {
                "netmiko": {
                    "platform": "linux",
                    "extras": {
                        "device_type": "generic_telnet",
                        "global_delay_factor": 3,
                        "timeout": 120,
                        "fast_cli": False,
                    },
                }
            },
        },
    }


def get_nornir_groups_config(group_name: str = "cisco_IOSv_telnet") -> dict[str, Any]:
    """Get Nornir groups configuration for network devices.

    Args:
        group_name: Name of group configuration (default: "cisco_IOSv_telnet")

    Returns:
        Dictionary containing Nornir group configuration

    Example:
        >>> linux_config = get_nornir_groups_config("linux_telnet")
        >>> print(linux_config['platform'])
        'linux'
    """
    all_groups = get_nornir_all_groups_config()
    result = all_groups.get(group_name, {})
    return result
