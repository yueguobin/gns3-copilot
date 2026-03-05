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
Configuration Management Module for GNS3 Copilot.

This module handles loading, saving, and validating application configuration
settings for the GNS3 Copilot application. It uses SQLite database for
persistent configuration storage, including GNS3 server settings, LLM model
configurations, voice settings (TTS/STT), and other application preferences.

Key Functions:
    init_config(): Initialize configuration database with default values
    load_config(): Load configuration from database into session state
    save_config(): Save current session state configuration to database

Configuration Categories:
    - GNS3 Server: Host, URL, API version, authentication credentials
    - LLM Model: Provider, model name, API key, base URL, temperature
    - Voice (TTS): API key, model, voice, base URL, speed settings
    - Voice (STT): API key, model, language, base URL, temperature, response format
    - Other: Linux console credentials, English proficiency level
    - UI Settings: Container height, zoom scale for topology view

Constants:
    CONFIG_MAP: Mapping between Streamlit widget keys and config keys
    MODEL_PROVIDERS: List of supported LLM model providers
    TTS_MODELS: Supported text-to-speech models
    TTS_VOICES: Available voice options for TTS
    STT_MODELS: Supported speech-to-text models
    STT_RESPONSE_FORMATS: Available output formats for STT

Example:
    Initialize configuration at application startup:
        from gns3_copilot.ui_model.utils import init_config

        init_config()  # Initializes config database

    Load configuration for use in UI:
        from gns3_copilot.ui_model.utils import load_config

        load_config()  # Loads config into st.session_state

    Save configuration after user modifies settings:
        from gns3_copilot.ui_model.utils import save_config

        save_config()  # Persists session state to database
"""

import streamlit as st

from gns3_copilot.log_config import setup_logger
from gns3_copilot.utils import get_config, init_config, set_config

logger = setup_logger("config_manager")

# Defines the configuration keys used in the application.
# Format: {Streamlit_Session_State_Key: Config_Database_Key}
CONFIG_MAP = {
    # GNS3 Server Configuration
    "GNS3_SERVER_HOST": "GNS3_SERVER_HOST",
    "GNS3_SERVER_URL": "GNS3_SERVER_URL",
    "API_VERSION": "API_VERSION",
    "GNS3_SERVER_USERNAME": "GNS3_SERVER_USERNAME",
    "GNS3_SERVER_PASSWORD": "GNS3_SERVER_PASSWORD",
    # Model Configuration
    "MODE_PROVIDER": "MODE_PROVIDER",
    "MODEL_NAME": "MODEL_NAME",
    "MODEL_API_KEY": "MODEL_API_KEY",
    "BASE_URL": "BASE_URL",
    "TEMPERATURE": "TEMPERATURE",
    # Voice Configuration
    "VOICE": "VOICE",
    # Voice TTS Configuration
    "TTS_API_KEY": "TTS_API_KEY",
    "TTS_BASE_URL": "TTS_BASE_URL",
    "TTS_MODEL": "TTS_MODEL",
    "TTS_VOICE": "TTS_VOICE",
    "TTS_SPEED": "TTS_SPEED",
    # Voice STT Configuration
    "STT_API_KEY": "STT_API_KEY",
    "STT_BASE_URL": "STT_BASE_URL",
    "STT_MODEL": "STT_MODEL",
    "STT_LANGUAGE": "STT_LANGUAGE",
    "STT_TEMPERATURE": "STT_TEMPERATURE",
    # Other Settings
    "LINUX_TELNET_USERNAME": "LINUX_TELNET_USERNAME",
    "LINUX_TELNET_PASSWORD": "LINUX_TELNET_PASSWORD",
    # Prompt Configuration
    "ENGLISH_LEVEL": "ENGLISH_LEVEL",
    # Reading Page Configuration
    "CALIBRE_SERVER_URL": "CALIBRE_SERVER_URL",
    "READING_NOTES_DIR": "READING_NOTES_DIR",
    # UI Configuration
    "CONTAINER_HEIGHT": "CONTAINER_HEIGHT",
    "zoom_scale_topology": "ZOOM_SCALE_TOPOLOGY",
    # Other Settings
    "LANGUAGE": "LANGUAGE",
    "TTS_HTTP_REFERER": "TTS_HTTP_REFERER",
    "TTS_X_TITLE": "TTS_X_TITLE",
}


def init_app_config() -> None:
    """Initialize the application configuration database.

    This function should be called once at application startup to initialize
    the SQLite database with default configuration values. It will not
    overwrite existing values.

    This replaces the old .env file initialization.
    """
    try:
        logger.info("Initializing application configuration database")
        init_config()
        logger.info("Application configuration database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize configuration database: %s", e)
        st.error(
            f"Failed to initialize configuration database: {e}. "
            "Please check the application logs."
        )


def load_config() -> None:
    """Load configuration from database and initialize st.session_state.

    This function loads configuration items from SQLite database into
    Streamlit's session state for use in UI components. It applies
    type conversion and validation to ensure proper data types.

    The function uses a marker `_config_loaded` in session_state to track
    whether configuration has been initialized.
    """
    # Check if configuration has already been loaded
    if st.session_state.get("_config_loaded", False):
        logger.debug("Configuration already loaded, skipping reload")
        return

    logger.info("Starting to load configuration from database")

    # Load configuration values from database into session_state
    for st_key, config_key in CONFIG_MAP.items():
        # Get value from database
        config_value = get_config(config_key, "")

        # Special handling for GNS3 Server settings
        if st_key in ("GNS3_SERVER_HOST", "GNS3_SERVER_URL"):
            st.session_state[st_key] = config_value
            logger.debug("Loaded config: %s = %s", st_key, config_value)
            continue

        # Special handling for API_VERSION
        if st_key == "API_VERSION":
            # Ensure value is either "2" or "3"
            if config_value not in ("2", "3"):
                config_value = "2"
            st.session_state[st_key] = config_value
            logger.debug("Loaded config: %s = %s", st_key, config_value)
            continue

        # Special handling for TEMPERATURE
        if st_key == "TEMPERATURE":
            if not config_value.replace(".", "", 1).isdigit():
                logger.debug(
                    "Invalid TEMPERATURE value: %s, setting to default '0.0'",
                    config_value,
                )
                config_value = "0.0"
            st.session_state[st_key] = config_value
            continue

        # Special handling for VOICE (boolean)
        if st_key == "VOICE":
            voice_str = str(config_value).lower().strip()
            if voice_str not in (
                "true",
                "false",
                "1",
                "0",
                "yes",
                "no",
                "on",
                "off",
                "",
            ):
                logger.debug(
                    "Invalid VOICE value: %s, setting to default 'false'", config_value
                )
                voice_str = "false"
            is_enabled: bool = voice_str in ("true", "1", "yes", "on")
            st.session_state[st_key] = is_enabled
            logger.debug("Loaded config: %s = %s", st_key, is_enabled)
            continue

        # Special handling for TTS_SPEED
        if st_key == "TTS_SPEED":
            try:
                speed_float = float(config_value) if config_value else 1.0
                if not (0.25 <= speed_float <= 4.0):
                    logger.debug(
                        "Invalid TTS_SPEED value: %s, setting to default '1.0'",
                        config_value,
                    )
                    speed_float = 1.0
                st.session_state[st_key] = speed_float
                logger.debug("Loaded config: %s = %s", st_key, speed_float)
            except ValueError:
                logger.debug(
                    "Invalid TTS_SPEED value: %s, setting to default '1.0'",
                    config_value,
                )
                st.session_state[st_key] = 1.0
            continue

        # Special handling for STT_TEMPERATURE
        if st_key == "STT_TEMPERATURE":
            try:
                temp_float = float(config_value) if config_value else 0.0
                if not (0.0 <= temp_float <= 1.0):
                    logger.debug(
                        "Invalid STT_TEMPERATURE value: %s, setting to default '0.0'",
                        config_value,
                    )
                    temp_float = 0.0
                st.session_state[st_key] = temp_float
                logger.debug("Loaded config: %s = %s", st_key, temp_float)
            except ValueError:
                logger.debug(
                    "Invalid STT_TEMPERATURE value: %s, setting to default '0.0'",
                    config_value,
                )
                st.session_state[st_key] = 0.0
            continue

        # Special handling for CONTAINER_HEIGHT (UI setting)
        if st_key == "CONTAINER_HEIGHT":
            try:
                height_int = int(config_value) if config_value else 1200
                if not (300 <= height_int <= 1500):
                    logger.debug(
                        "Invalid CONTAINER_HEIGHT value: %s, setting to default 1200",
                        config_value,
                    )
                    height_int = 1200
                st.session_state[st_key] = height_int
                logger.debug("Loaded config: %s = %s", st_key, height_int)
            except ValueError:
                logger.debug(
                    "Invalid CONTAINER_HEIGHT value: %s, setting to default 1200",
                    config_value,
                )
                st.session_state[st_key] = 1200
            continue

        # Special handling for zoom_scale_topology (UI setting)
        if st_key == "zoom_scale_topology":
            try:
                zoom_float = float(config_value) if config_value else 0.8
                if not (0.5 <= zoom_float <= 1.2):
                    logger.debug(
                        "Invalid zoom_scale_topology value: %s, setting to default 0.8",
                        config_value,
                    )
                    zoom_float = 0.8
                st.session_state[st_key] = zoom_float
                logger.debug("Loaded config: %s = %s", st_key, zoom_float)
            except ValueError:
                logger.debug(
                    "Invalid zoom_scale_topology value: %s, setting to default 0.8",
                    config_value,
                )
                st.session_state[st_key] = 0.8
            continue

        # Default handling for string values
        st.session_state[st_key] = config_value
        logger.debug(
            "Loaded config: %s = %s",
            st_key,
            "[HIDDEN]" if "PASSWORD" in st_key or "KEY" in st_key else config_value,
        )

    # Mark configuration as loaded
    st.session_state["_config_loaded"] = True
    logger.info("Configuration loading completed")


def save_config() -> None:
    """Save current session state to configuration database.

    This function persists all configuration values from Streamlit's
    session_state to the SQLite database.
    """
    logger.info("Starting to save configuration to database")

    saved_count = 0

    for st_key, config_key in CONFIG_MAP.items():
        current_value = st.session_state.get(st_key)

        if current_value is not None:
            str_value = str(current_value)

            try:
                # Save value to database
                set_config(config_key, str_value)

                saved_count += 1
                logger.debug(
                    "Saved config: %s = %s",
                    st_key,
                    "[HIDDEN]"
                    if "PASSWORD" in st_key or "KEY" in st_key
                    else str_value,
                )
            except Exception as e:
                logger.error("Failed to save %s: %s", st_key, e)

    logger.info(
        "Configuration save completed. Saved %d configuration items", saved_count
    )
    st.success("Configuration successfully saved!")

    # Mark config as loaded so it will be reloaded on next page
    st.session_state["_config_loaded"] = False
