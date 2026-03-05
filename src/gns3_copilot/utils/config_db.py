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
Configuration Database Module for GNS3 Copilot.

This module provides SQLite database operations for persisting application
configuration. All configuration values are stored in a single database
file, eliminating reliance on session_state or .env files.

Functions:
    init_db(): Initialize the configuration database and create tables
    get_value(key, default=None): Retrieve a configuration value
    set_value(key, value): Save a configuration value
    get_all_values(): Retrieve all configuration values as a dictionary
    delete_key(key): Delete a configuration key
    clear_all(): Clear all configuration values

Constants:
    DB_PATH: Path to the configuration database file
"""

import os
import sqlite3
from typing import Any

from gns3_copilot.log_config import setup_logger

logger = setup_logger("config_db")

# Database file path
DB_PATH = os.path.join(os.getcwd(), "data", "app_config.db")


def _get_connection() -> sqlite3.Connection:
    """Get a database connection with proper configuration."""
    # Ensure the data directory exists before opening the database
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.debug("Created database directory: %s", db_dir)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the configuration database and create necessary tables.

    This function creates the app_config table if it doesn't exist.
    The table structure includes:
    - key: Configuration key (primary key)
    - value: Configuration value (text)
    - updated_at: Timestamp of last update
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()
        logger.debug("Configuration database initialized at: %s", DB_PATH)
    except Exception as e:
        logger.error("Failed to initialize configuration database: %s", e)
        raise


def get_value(key: str, default: Any = None) -> Any:
    """Retrieve a configuration value from the database.

    Args:
        key: The configuration key to retrieve
        default: Default value to return if key doesn't exist

    Returns:
        The configuration value, or default if not found
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM app_config WHERE key = ?", (key,))
        result = cursor.fetchone()

        conn.close()

        if result:
            logger.debug("Retrieved config: %s = %s", key, result["value"])
            return result["value"]
        else:
            logger.debug(
                "Config key '%s' not found, returning default: %s", key, default
            )
            return default
    except Exception as e:
        logger.error("Failed to retrieve config key '%s': %s", key, e)
        return default


def set_value(key: str, value: Any) -> bool:
    """Save or update a configuration value in the database.

    Args:
        key: The configuration key to save
        value: The configuration value to store

    Returns:
        True if save was successful, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        # Convert value to string for storage
        str_value = str(value)

        # Use UPSERT (INSERT OR REPLACE) to handle both new and existing keys
        cursor.execute(
            """
            INSERT OR REPLACE INTO app_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (key, str_value),
        )

        conn.commit()
        conn.close()
        logger.debug("Saved config: %s = %s", key, str_value)
        return True
    except Exception as e:
        logger.error("Failed to save config key '%s': %s", key, e)
        return False


def get_all_values() -> dict[str, str]:
    """Retrieve all configuration values from the database.

    Returns:
        Dictionary with all configuration key-value pairs
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT key, value FROM app_config")
        results = cursor.fetchall()

        config_dict = {row["key"]: row["value"] for row in results}

        conn.close()
        logger.debug("Retrieved %d configuration items", len(config_dict))
        return config_dict
    except Exception as e:
        logger.error("Failed to retrieve all config values: %s", e)
        return {}


def delete_key(key: str) -> bool:
    """Delete a configuration key from the database.

    Args:
        key: The configuration key to delete

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM app_config WHERE key = ?", (key,))

        conn.commit()
        conn.close()
        logger.debug("Deleted config key: %s", key)
        return True
    except Exception as e:
        logger.error("Failed to delete config key '%s': %s", key, e)
        return False


def clear_all() -> bool:
    """Clear all configuration values from the database.

    Returns:
        True if clear was successful, False otherwise
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM app_config")

        conn.commit()
        conn.close()
        logger.debug("Cleared all configuration values")
        return True
    except Exception as e:
        logger.error("Failed to clear all config values: %s", e)
        return False
