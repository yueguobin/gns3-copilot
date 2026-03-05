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
Dynamic prompt loader for GNS3 Network Automation Assistant

This module provides functionality to dynamically load system prompts based on English proficiency levels.
It supports loading different prompts for A1, A2, B1, B2, C1, and C2 English levels from environment variables.
Additionally, it can append voice-optimized prompts when VOICE mode is enabled.
"""

import importlib
import os
from typing import cast

from gns3_copilot.log_config import setup_logger

logger = setup_logger("prompt_loader")

# Mapping of English levels to their corresponding prompt modules
ENGLISH_LEVEL_PROMPT_MAP = {
    "NORMAL PROMPT": "base_prompt",
    "A1": "english_level_prompt_a1",
    "A2": "english_level_prompt_a2",
    "B1": "english_level_prompt_b1",
    "B2": "english_level_prompt_b2",
    "C1": "english_level_prompt_c1",
    "C2": "english_level_prompt_c2",
}

# Mapping of English levels to their corresponding voice prompt modules
VOICE_LEVEL_PROMPT_MAP = {
    "A1": "voice_prompt_english_level_a1",
    "A2": "voice_prompt_english_level_a2",
    "B1": "voice_prompt_english_level_b1",
    "B2": "voice_prompt_english_level_b2",
    "C1": "voice_prompt_english_level_c1",
    "C2": "voice_prompt_english_level_c2",
}


def _load_base_prompt() -> str:
    """
    Load the base_prompt system prompt.

    Returns:
        str: The base_prompt system prompt content.

    Raises:
        ImportError: If there's an error importing the base_prompt module.
        AttributeError: If the SYSTEM_PROMPT is not found in the base_prompt module.
    """
    try:
        # Import the base_prompt module
        base_prompt_module = importlib.import_module("gns3_copilot.prompts.base_prompt")

        # Get the SYSTEM_PROMPT from the module
        if hasattr(base_prompt_module, "SYSTEM_PROMPT"):
            system_prompt = cast(str, base_prompt_module.SYSTEM_PROMPT)
            logger.info("Successfully loaded base_prompt")
            return system_prompt
        else:
            raise AttributeError("SYSTEM_PROMPT not found in base_prompt module")

    except ImportError as e:
        logger.error("Failed to import base_prompt module: %s", e)
        raise ImportError(f"Failed to import base_prompt module: {e}") from e

    except AttributeError as e:
        logger.error("Error accessing SYSTEM_PROMPT in base_prompt module: %s", e)
        raise AttributeError(
            f"Error accessing SYSTEM_PROMPT in base_prompt module: {e}"
        ) from e


def _load_regular_level_prompt(level: str | None = None) -> str:
    """
    Load regular prompt based on English proficiency level.

    Args:
        level (str, optional): English proficiency level (A1, A2, B1, B2, C1, C2).
                              If not provided, will use base_prompt.

    Returns:
        str: The regular system prompt content for the specified English level.
    """
    # Normalize level to uppercase if provided
    if level:
        level = level.upper().strip()

    # If no valid English level is specified, use base_prompt
    if not level or level not in ENGLISH_LEVEL_PROMPT_MAP:
        logger.info(
            "No valid English level specified (got '%s'), using base_prompt", level
        )
        return _load_base_prompt()

    # Get the module name for the level
    module_name = ENGLISH_LEVEL_PROMPT_MAP[level]

    try:
        # Import the module dynamically
        prompt_module = importlib.import_module(f"gns3_copilot.prompts.{module_name}")

        # Get the SYSTEM_PROMPT from the module
        if hasattr(prompt_module, "SYSTEM_PROMPT"):
            base_prompt = cast(str, prompt_module.SYSTEM_PROMPT)
            logger.info(
                "Successfully loaded regular system prompt for English level: %s", level
            )
            return base_prompt
        else:
            raise AttributeError(f"SYSTEM_PROMPT not found in module {module_name}")

    except ImportError as e:
        logger.error("Failed to import regular prompt module '%s': %s", module_name, e)
        # Fallback to base_prompt
        logger.info("Falling back to base_prompt due to import error")
        return _load_base_prompt()

    except AttributeError as e:
        logger.error(
            "Error accessing SYSTEM_PROMPT in regular prompt module '%s': %s",
            module_name,
            e,
        )
        # Fallback to base_prompt
        logger.info("Falling back to base_prompt due to attribute error")
        return _load_base_prompt()


def _load_voice_level_prompt(level: str | None = None) -> str:
    """
    Load voice prompt based on English proficiency level.

    Args:
        level (str, optional): English proficiency level (A1, A2, B1, B2, C1, C2).
                              If not provided, will use generic voice_prompt.

    Returns:
        str: The voice system prompt content for the specified English level.
    """
    # Normalize level to uppercase if provided
    if level:
        level = level.upper().strip()

    # Try to load level-specific voice prompt first
    if level and level in VOICE_LEVEL_PROMPT_MAP:
        module_name = VOICE_LEVEL_PROMPT_MAP[level]
        try:
            # Import the level-specific voice prompt module
            voice_prompt_module = importlib.import_module(
                f"gns3_copilot.prompts.{module_name}"
            )

            # Get the SYSTEM_PROMPT from the module
            if hasattr(voice_prompt_module, "SYSTEM_PROMPT"):
                voice_prompt = cast(str, voice_prompt_module.SYSTEM_PROMPT)
                logger.info(
                    "Successfully loaded voice prompt for English level: %s", level
                )
                return voice_prompt
            else:
                raise AttributeError(
                    f"SYSTEM_PROMPT not found in voice prompt module {module_name}"
                )

        except ImportError as e:
            logger.error(
                "Failed to import level-specific voice prompt module '%s': %s",
                module_name,
                e,
            )
            logger.info("Falling back to generic voice prompt")
        except AttributeError as e:
            logger.error(
                "Error accessing SYSTEM_PROMPT in level-specific voice prompt module '%s': %s",
                module_name,
                e,
            )
            logger.info("Falling back to generic voice prompt")

    # Fallback to generic voice prompt
    try:
        # Import the generic voice prompt module
        voice_prompt_module = importlib.import_module(
            "gns3_copilot.prompts.voice_prompt"
        )

        # Get the SYSTEM_PROMPT from the module
        if hasattr(voice_prompt_module, "SYSTEM_PROMPT"):
            voice_prompt = cast(str, voice_prompt_module.SYSTEM_PROMPT)
            logger.info("Successfully loaded generic voice prompt")
            return voice_prompt
        else:
            raise AttributeError(
                "SYSTEM_PROMPT not found in generic voice prompt module"
            )

    except ImportError as e:
        logger.error("Failed to import generic voice prompt module: %s", e)
        # Return base_prompt as ultimate fallback
        logger.warning("Voice prompt not available, falling back to base_prompt")
        return _load_base_prompt()

    except AttributeError as e:
        logger.error(
            "Error accessing SYSTEM_PROMPT in generic voice prompt module: %s", e
        )
        # Return base_prompt as ultimate fallback
        logger.warning("Voice prompt not found, falling back to base_prompt")
        return _load_base_prompt()


def _is_voice_enabled() -> bool:
    """
    Check if voice mode is enabled in environment variables.

    Returns:
        bool: True if voice mode is enabled, False otherwise.
    """
    voice_value = os.getenv("VOICE", "False").lower().strip()
    return voice_value in ("true", "1", "yes", "on")


def load_system_prompt(level: str | None = None) -> str:
    """
    Load system prompt based on English proficiency level and voice mode settings.

    This function uses a replacement strategy rather than concatenation:
    - If voice mode is disabled: uses ENGLISH_LEVEL_PROMPT_MAP
    - If voice mode is enabled: uses VOICE_LEVEL_PROMPT_MAP

    Args:
        level (str, optional): English proficiency level (A1, A2, B1, B2, C1, C2).
                              If not provided, will read from ENGLISH_LEVEL environment variable.

    Returns:
        str: The system prompt content for the specified English level and mode.

    Raises:
        ImportError: If there's an error importing the prompt module.
        AttributeError: If the SYSTEM_PROMPT is not found in the module.
    """
    # Determine the English level to use
    if not level:
        level = os.getenv("ENGLISH_LEVEL", "")

    # Normalize level to uppercase
    level = level.upper().strip()

    # Check if voice mode is enabled and choose the appropriate prompt set
    if _is_voice_enabled():
        logger.info("Voice mode is enabled, using voice prompts")
        return _load_voice_level_prompt(level)
    else:
        logger.info("Voice mode is disabled, using regular prompts")
        return _load_regular_level_prompt(level)
