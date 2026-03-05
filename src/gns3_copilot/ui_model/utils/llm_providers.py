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
Predefined LLM provider configurations for GNS3 Copilot.

This module provides a centralized configuration of supported LLM providers,
including their base URLs, available models, and other metadata. This enables
a streamlined user experience through predefined configurations while
maintaining flexibility for custom configurations.

Provider Categories:
    - aggregator: Third-party aggregators (OpenRouter, etc.)
    - first_party: Official provider APIs (OpenAI, DeepSeek, etc.)
    - local: Local/self-hosted models (Ollama, LM Studio, etc.)
"""


class ProviderConfig:
    """Configuration class for a single LLM provider."""

    def __init__(
        self,
        provider: str,
        base_url: str,
        models: list[str],
        requires_api_key: bool,
        category: str,
    ):
        self.provider = provider
        self.base_url = base_url
        self.models = models
        self.requires_api_key = requires_api_key
        self.category = category


# Predefined LLM provider configurations
LLM_PROVIDERS: dict[str, ProviderConfig] = {
    "OpenRouter": ProviderConfig(
        provider="openai",
        base_url="https://openrouter.ai/api/v1",
        models=[
            "deepseek/deepseek-v3.2",
            "x-ai/grok-3",
            "anthropic/claude-sonnet-4",
            "z-ai/glm-4.7",
        ],
        requires_api_key=True,
        category="aggregator",
    ),
    "DeepSeek": ProviderConfig(
        provider="deepseek",
        base_url="https://api.deepseek.com/v1",
        models=[
            "deepseek-chat",
        ],
        requires_api_key=True,
        category="first_party",
    ),
}


def get_provider_config(provider_name: str) -> ProviderConfig | None:
    """Get provider configuration by name.

    Args:
        provider_name: Name of the provider (e.g., "OpenRouter", "OpenAI")

    Returns:
        ProviderConfig object if found, None otherwise
    """
    return LLM_PROVIDERS.get(provider_name)


def get_all_providers() -> list[str]:
    """Get list of all available provider names.

    Returns:
        List of provider names sorted by category and name
    """
    # Sort by category (local first, then aggregator, then first_party)
    category_order = {"local": 0, "aggregator": 1, "first_party": 2}

    sorted_providers = sorted(
        LLM_PROVIDERS.keys(),
        key=lambda p: (category_order.get(LLM_PROVIDERS[p].category, 99), p),
    )

    return sorted_providers
