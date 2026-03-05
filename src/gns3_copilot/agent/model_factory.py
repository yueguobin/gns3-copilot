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
Model Factory for GNS3 Copilot Agent

This module provides factory functions to create fresh LLM model instances
on-demand from SQLite configuration. This allows configuration changes
to take effect without restarting the application.
"""

from typing import Any

from langchain.chat_models import init_chat_model

from gns3_copilot.log_config import setup_logger
from gns3_copilot.utils import get_config

logger = setup_logger("model_factory")


def _load_env_variables() -> dict[str, str]:
    """
    Load model configuration from SQLite database.

    Returns:
        Dictionary containing model configuration.
    """
    return {
        "model_name": get_config("MODEL_NAME", ""),
        "model_provider": get_config("MODE_PROVIDER", ""),
        "api_key": get_config("MODEL_API_KEY", ""),
        "base_url": get_config("BASE_URL", ""),
        "temperature": get_config("TEMPERATURE", "0"),
    }


def create_base_model() -> Any:
    """
    Create a fresh base LLM model instance from current environment variables.

    This function reads environment variables fresh every time it's called,
    allowing configuration changes to take effect immediately.

    Returns:
        Any: A new LLM model instance configured with current env vars.
              The actual type depends on the provider (e.g., ChatOpenAI, etc.).

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    env_vars = _load_env_variables()

    # Log the loaded configuration (mask sensitive data)
    logger.info(
        "Creating base model: name=%s, provider=%s, base_url=%s, temperature=%s",
        env_vars["model_name"],
        env_vars["model_provider"],
        env_vars["base_url"] if env_vars["base_url"] else "default",
        env_vars["temperature"],
    )

    # Validate required fields
    if not env_vars["model_name"]:
        raise ValueError("MODEL_NAME environment variable is required")

    if not env_vars["model_provider"]:
        raise ValueError("MODE_PROVIDER environment variable is required")

    try:
        model = init_chat_model(
            env_vars["model_name"],
            model_provider=env_vars["model_provider"],
            api_key=env_vars["api_key"],
            base_url=env_vars["base_url"],
            temperature=env_vars["temperature"],
            configurable_fields="any",
            config_prefix="foo",
        )

        logger.info("Base model created successfully")
        return model

    except Exception as e:
        logger.error("Failed to create base model: %s", e)
        raise RuntimeError(f"Failed to create base model: {e}") from e


def create_title_model() -> Any:
    """
    Create a fresh title generation model instance.

    This creates a model instance suitable for generating conversation titles.
    It uses the same configuration as the base model but with a higher temperature
    for more creative output.

    Returns:
        Any: A new LLM model instance for title generation.
              The actual type depends on the provider.

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    env_vars = _load_env_variables()

    logger.info(
        "Creating title model: name=%s, provider=%s, base_url=%s, temperature=1.0",
        env_vars["model_name"],
        env_vars["model_provider"],
        env_vars["base_url"] if env_vars["base_url"] else "default",
    )

    # Validate required fields
    if not env_vars["model_name"]:
        raise ValueError("MODEL_NAME environment variable is required")

    if not env_vars["model_provider"]:
        raise ValueError("MODE_PROVIDER environment variable is required")

    try:
        model = init_chat_model(
            env_vars["model_name"],
            model_provider=env_vars["model_provider"],
            api_key=env_vars["api_key"],
            base_url=env_vars["base_url"],
            temperature="1.0",  # Higher temperature for more creative titles
            configurable_fields="any",
            config_prefix="foo",
        )

        logger.info("Title model created successfully")
        return model

    except Exception as e:
        logger.error("Failed to create title model: %s", e)
        raise RuntimeError(f"Failed to create title model: {e}") from e


def create_model_with_tools(
    model: Any,
    tools: list[Any],
) -> Any:
    """
    Bind tools to a model instance.

    Args:
        model: The base model instance.
        tools: List of tools to bind to the model.

    Returns:
        Any: A model instance with tools bound (type varies by provider).

    Raises:
        RuntimeError: If tool binding fails.
    """
    try:
        model_with_tools = model.bind_tools(tools)
        logger.info("Model bound with %d tools successfully", len(tools))
        return model_with_tools
    except Exception as e:
        logger.error("Failed to bind tools to model: %s", e)
        raise RuntimeError(f"Failed to bind tools to model: {e}") from e


def create_note_organizer_model() -> Any:
    """
    Create a fresh model instance for note organization.

    This creates a model instance suitable for organizing and formatting notes.
    It uses the same configuration as the base model but with a lower temperature
    for more consistent and predictable output.

    Returns:
        Any: A new LLM model instance for note organization.
              The actual type depends on the provider.

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    env_vars = _load_env_variables()

    logger.info(
        "Creating note organizer model: name=%s, provider=%s, base_url=%s, temperature=0.3",
        env_vars["model_name"],
        env_vars["model_provider"],
        env_vars["base_url"] if env_vars["base_url"] else "default",
    )

    # Validate required fields
    if not env_vars["model_name"]:
        raise ValueError("MODEL_NAME environment variable is required")

    if not env_vars["model_provider"]:
        raise ValueError("MODE_PROVIDER environment variable is required")

    try:
        model = init_chat_model(
            env_vars["model_name"],
            model_provider=env_vars["model_provider"],
            api_key=env_vars["api_key"],
            base_url=env_vars["base_url"],
            temperature="0.3",  # Lower temperature for more consistent note organization
            configurable_fields="any",
            config_prefix="foo",
        )

        logger.info("Note organizer model created successfully")
        return model

    except Exception as e:
        logger.error("Failed to create note organizer model: %s", e)
        raise RuntimeError(f"Failed to create note organizer model: {e}") from e


def create_base_model_with_tools(tools: list[Any]) -> Any:
    """
    Create a fresh base model instance with tools bound.

    This is a convenience function that combines creating the base model
    and binding tools to it.

    Args:
        tools: List of tools to bind to the model.

    Returns:
        Any: A new model instance with tools bound (type varies by provider).

    Raises:
        ValueError: If required environment variables are missing.
        RuntimeError: If model creation or tool binding fails.
    """
    base_model = create_base_model()
    return create_model_with_tools(base_model, tools)
