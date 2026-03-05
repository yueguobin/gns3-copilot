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
Unified logging configuration module.

Provides centralized logging configuration for GNS3 Copilot tools package,
eliminating duplicate logging setup code across modules.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

# Module path mapping: maps module names to their log subdirectories
MODULE_PATH_MAPPING: dict[str, str] = {
    # Agent modules
    "gns3_copilot": "agent",
    "checkpoint_utils": "agent",
    # GNS3 client modules
    "connector_factory": "gns3_client",
    "custom_gns3fy": "gns3_client",
    "gns3_file_index": "gns3_client",
    "gns3_create_drawing": "gns3_client",
    "gns3_delete_drawing": "gns3_client",
    "gns3_get_drawings": "gns3_client",
    "gns3_get_nodes": "gns3_client",
    "gns3_project_create": "gns3_client",
    "gns3_project_delete": "gns3_client",
    "gns3_project_list_files": "gns3_client",
    "gns3_project_lock": "gns3_client",
    "gns3_project_open": "gns3_client",
    "gns3_project_path": "gns3_client",
    "gns3_project_read_file": "gns3_client",
    "gns3_project_update": "gns3_client",
    "gns3_project_write_file": "gns3_client",
    "gns3_projects_list": "gns3_client",
    "gns3_topology_reader": "gns3_client",
    "gns3_update_drawing": "gns3_client",
    # Public model modules
    "gns3_drawing_utils": "public_model",
    "get_gns3_device_port": "public_model",
    "openai_stt": "public_model",
    "openai_tts": "public_model",
    "parse_tool_content": "public_model",
    # Prompts modules
    "base_prompt": "prompts",
    "drawing_prompt": "prompts",
    "english_level_prompt_a1": "prompts",
    "english_level_prompt_a2": "prompts",
    "english_level_prompt_b1": "prompts",
    "english_level_prompt_b2": "prompts",
    "english_level_prompt_c1": "prompts",
    "english_level_prompt_c2": "prompts",
    "prompt_loader": "prompts",
    "title_prompt": "prompts",
    "voice_prompt_english_level_a1": "prompts",
    "voice_prompt_english_level_a2": "prompts",
    "voice_prompt_english_level_b1": "prompts",
    "voice_prompt_english_level_b2": "prompts",
    "voice_prompt_english_level_c1": "prompts",
    "voice_prompt_english_level_c2": "prompts",
    "vocie_prompt": "prompts",
    # Tools v2 modules
    "config_tools_nornir": "tools_v2",
    "display_tools_nornir": "tools_v2",
    "gns3_create_area_drawing": "tools_v2",
    "gns3_create_link": "tools_v2",
    "gns3_create_node": "tools_v2",
    "gns3_get_node_temp": "tools_v2",
    "gns3_start_node": "tools_v2",
    "linux_tools_nornir": "tools_v2",
    "vpcs_tools_telnetlib3": "tools_v2",
    # UI model modules
    "app_ui": "ui_model",
    "chat": "ui_model",
    "chat_helpers": "ui_model",
    "config_manager": "ui_model",
    "gns3_checker": "ui_model",
    "help": "ui_model",
    "llm_providers": "ui_model",
    "notes": "ui_model",
    "project_manager_ui": "ui_model",
    "settings": "ui_model",
    "sidebar": "ui_model",
    "update_ui": "ui_model",
    "updater": "ui_model",
}


def _get_log_path(name: str) -> str:
    """
    Get the log file path based on module name mapping.

    Args:
        name (str): Module name

    Returns:
        str: Log file path
    """
    # Check if the module name is in the mapping
    subdirectory = MODULE_PATH_MAPPING.get(name)

    if subdirectory:
        # Use subdirectory-based path
        return f"log/{subdirectory}/{name}.log"
    else:
        # Use default flat structure
        return f"log/{name}.log"


def setup_logger(
    name: str,
    log_file: str | None = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Set up unified logging configuration.

    Args:
        name (str): Logger name, typically the module name
        log_file (str, optional): Log file path, defaults to log/{name}.log
        console_level (int, optional): Console log level, defaults to INFO
        file_level (int, optional): File log level, defaults to DEBUG

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set logger level to DEBUG for maximum detail

    # Prevent duplicate handlers
    if not logger.handlers:
        # Create unified formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Configure file handler
        if log_file is None:
            log_file = _get_log_path(name)

        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configure file handler with timed rotation (every 7 days)
        file_handler = TimedRotatingFileHandler(
            log_file,
            when="D",  # Rotate daily
            interval=7,  # Every 7 days
            backupCount=5,  # Keep 5 backup files
            encoding="utf-8",
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger to avoid duplicate logging
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger, use default configuration if not configured.

    Args:
        name (str): Logger name

    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, use default configuration
    if not logger.handlers:
        return setup_logger(name)

    return logger


def configure_package_logging(level: int = logging.INFO) -> None:
    """
    Configure root log level for the entire package.

    Args:
        level (int): Log level
    """
    # Set package root logger
    package_logger = logging.getLogger("tools")
    package_logger.setLevel(level)

    # If no handlers, add a simple console handler
    if not package_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter("GNS3 Tools: %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        package_logger.addHandler(console_handler)


# Default logger configuration for all modules
DEFAULT_LOGGER_CONFIG = {
    "console_level": logging.ERROR,
    "file_level": logging.DEBUG,
}

# Predefined logging configurations for modules that need special settings
# Most modules will use DEFAULT_LOGGER_CONFIG, so only list exceptions here
LOGGER_CONFIGS: dict[str, dict[str, int]] = {
    # Add modules with special configurations here
    # Example:
    # "special_module": {"console_level": logging.INFO, "file_level": logging.DEBUG},
}


def setup_tool_logger(tool_name: str, config_name: str | None = None) -> logging.Logger:
    """
    Set up logger for specific tool using predefined configuration.

    Args:
        tool_name (str): Tool name (used for log file name)
        config_name (str, optional): Configuration name to look up in LOGGER_CONFIGS,
                                     defaults to tool_name. If not found, uses DEFAULT_LOGGER_CONFIG.

    Returns:
        logging.Logger: Configured logger instance
    """
    if config_name is None:
        config_name = tool_name

    # Get configuration, fall back to default if not found
    config = LOGGER_CONFIGS.get(config_name, DEFAULT_LOGGER_CONFIG)

    return setup_logger(
        name=tool_name,
        log_file=_get_log_path(tool_name),
        console_level=config.get(
            "console_level", DEFAULT_LOGGER_CONFIG["console_level"]
        ),
        file_level=config.get("file_level", DEFAULT_LOGGER_CONFIG["file_level"]),
    )
