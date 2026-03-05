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
GNS3 Copilot Public Model Package

This package provides reusable public models and utilities for GNS3 network automation tasks.
It contains common functionality that can be shared across different tools and modules.

Main modules:
- get_gns3_device_port: Device port information retrieval from GNS3 topology
- parse_tool_content: Tool execution result parsing and formatting utilities

Author: Guobin Yue
"""

# Import main utility functions
from .app_config import (
    DEFAULT_CONFIG,
    get_all_config,
    get_config,
    get_nornir_all_groups_config,
    get_nornir_defaults,
    get_nornir_groups_config,
    init_config,
    reset_config,
    set_config,
)
from .get_gns3_device_port import get_device_ports_from_topology
from .openai_stt import get_stt_config, speech_to_text
from .openai_tts import get_duration, get_tts_config, text_to_speech_wav
from .parse_tool_content import format_tool_response, parse_tool_content

# Dynamic version management
try:
    from importlib.metadata import version

    __version__ = version("gns3-copilot")
except Exception:
    __version__ = "unknown"

__author__ = "Guobin Yue"
__description__ = "AI-powered network automation assistant for GNS3"
__url__ = "https://github.com/yueguobin/gns3-copilot"


# Export main utility functions
__all__ = [
    "DEFAULT_CONFIG",
    "get_config",
    "set_config",
    "get_all_config",
    "get_nornir_all_groups_config",
    "get_nornir_defaults",
    "get_nornir_groups_config",
    "init_config",
    "reset_config",
    "get_device_ports_from_topology",
    "parse_tool_content",
    "format_tool_response",
    "text_to_speech_wav",
    "speech_to_text",
    "get_duration",
    "get_tts_config",
    "get_stt_config",
]
