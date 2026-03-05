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
Streamlit-based settings management module for GNS3 Copilot application.

This module provides a comprehensive configuration interface for managing GNS3 server
connections, LLM model settings, and application preferences. It handles loading and
saving configuration to/from SQLite database, validates input parameters, and maintains
session state for persistent settings across the Streamlit application.

Key Features:
- GNS3 server configuration (host, URL, API version, authentication)
- LLM model provider setup with support for multiple providers
- SQLite database persistence for configuration
- Input validation and error handling
- Streamlit UI components for interactive configuration
"""

import streamlit as st

from gns3_copilot.log_config import setup_logger
from gns3_copilot.ui_model.utils import (
    check_gns3_api,
    get_all_providers,
    get_provider_config,
    render_update_settings,
    save_config,
)

logger = setup_logger("settings")


# Streamlit UI
st.markdown(
    """
    <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>Settings</h3>
    """,
    unsafe_allow_html=True,
)

with st.container(width=800, horizontal_alignment="center", vertical_alignment="top"):
    st.info("Configuration is stored in SQLite database (data/app_config.db)")

    with st.expander("GNS3 Copilot Updates", expanded=True):
        render_update_settings()

    with st.expander("GNS3 API Settings", expanded=True):
        # GNS3 Server address/API point
        col1, col2 = st.columns([1, 2])
        with col1:
            st.text_input(
                "GNS3 Server Host *",
                key="GNS3_SERVER_HOST",
                value=st.session_state.get("GNS3_SERVER_HOST", ""),
                type="default",
                placeholder="E.g., 127.0.0.1",
            )
        with col2:
            st.text_input(
                "GNS3 Server URL *",
                key="GNS3_SERVER_URL",
                value=st.session_state.get("GNS3_SERVER_URL", ""),
                type="default",
                placeholder="E.g., http://127.0.0.1:3080 or http://127.0.0.1:8000",
            )

        # GNS3 API version select
        col1, col2, col3 = st.columns([1, 2, 2])
        with col1:
            st.selectbox(
                "GNS3 API Version",
                ["2", "3"],
                index=0 if st.session_state.get("API_VERSION", "2") == "2" else 1,
                key="API_VERSION",
            )

        if st.session_state.get("API_VERSION") == "3":
            with col2:
                st.text_input(
                    "GNS3 User *",
                    key="GNS3_SERVER_USERNAME",
                    value=st.session_state.get("GNS3_SERVER_USERNAME", ""),
                    type="default",
                    placeholder="E.g., admin",
                )
            with col3:
                st.text_input(
                    "GNS3 Password *",
                    key="GNS3_SERVER_PASSWORD",
                    value=st.session_state.get("GNS3_SERVER_PASSWORD", ""),
                    type="password",
                    placeholder="E.g., admin",
                )
        else:
            pass

        # Button to manually check if GNS3 API is reachable
        if st.button("Check GNS3 API"):
            check_gns3_api()

    with st.expander("LLM Model Configuration", expanded=True):
        # Recommended models information
        st.success(
            """
            **🌟 Recommended Models:**
            - **Best:** `deepseek-chat` or `deepseek/deepseek-v3.2` (via OpenRouter)
            - Other recommended: `x-ai/grok-3`, `anthropic/claude-sonnet-4`, `z-ai/glm-4.7`
            """
        )

        # Provider selector and model selector side-by-side
        col1, col2 = st.columns([1, 2])

        with col1:
            # Provider selector with custom option
            all_providers = get_all_providers()
            selected_provider_preset = st.selectbox(
                "Select LLM Provider",
                ["Custom"] + all_providers,
                help="Choose a predefined provider for automatic configuration",
            )

        with col2:
            # Model selector - only show when provider is not Custom
            if selected_provider_preset != "Custom":
                provider_config = get_provider_config(selected_provider_preset)
                if provider_config:
                    model_options = provider_config.models + ["Custom model name..."]

                    selected_model = st.selectbox(
                        "Model Name *",
                        model_options,
                        help="Select a predefined model or choose custom to enter manually",
                    )

                    if selected_model == "Custom model name...":
                        # Show custom input field
                        custom_model = st.text_input(
                            "Enter Custom Model Name",
                            key="CUSTOM_MODEL_NAME",
                            value=st.session_state.get("MODEL_NAME", ""),
                            placeholder="e.g., custom-model-name",
                            help="Enter exact model name as required by the provider",
                        )
                        st.session_state["MODEL_NAME"] = custom_model
                    else:
                        # Set it to selected model
                        st.session_state["MODEL_NAME"] = selected_model

        # Apply preset configuration only when provider is not Custom
        if selected_provider_preset != "Custom":
            provider_config = get_provider_config(selected_provider_preset)
            if provider_config:
                # Auto-fill provider type
                st.session_state["MODE_PROVIDER"] = provider_config.provider
                # Auto-fill base URL
                st.session_state["BASE_URL"] = provider_config.base_url
        st.markdown("---")
        # Manual Configuration Section (always available)
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            # LLM Model Provider
            st.text_input(
                "Model Provider *",
                key="MODE_PROVIDER",
                value=st.session_state.get("MODE_PROVIDER", ""),
                type="default",
                help="""
        Supported model_provider values and the corresponding integration package are:

        openai,
        anthropic,
        ollama,
        deepseek,
        xai...

        If using "OpenRouter" platform, please enter "openai" here.
                """,
                placeholder="e.g. 'deepseek', 'openai'",
            )

        with col2:
            # LLM Model Name
            st.text_input(
                "Model Name *",
                key="MODEL_NAME",
                value=st.session_state.get("MODEL_NAME", ""),
                type="default",
                help="""
    The name or ID of the model, e.g. "o3-mini", "claude-sonnet-4-5-20250929", "deepseek-chat".

    If using the OpenRouter platform,
    please enter the model name in the OpenRouter format,
    e.g.: "openai/gpt-4o-mini", "x-ai/grok-4-fast".
                """,
                placeholder="e.g. 'o3-mini', 'claude-sonnet-4-5-20250929', 'deepseek-chat'",
            )

        with col3:
            # LLM model temperature
            st.text_input(
                "Model Temperature",
                key="TEMPERATURE",
                value=st.session_state.get("TEMPERATURE", ""),
                type="default",
                help="""
    Controls randomness: higher values mean more random output. Typical range is 0.0 to 1.0.
                """,
            )

        # LLM model provider base url
        st.text_input(
            "Base Url",
            key="BASE_URL",
            value=st.session_state.get("BASE_URL", ""),
            type="default",
            help="""
    To use OpenRouter, Base Url must be entered, e.g., https://openrouter.ai/api/v1.
            """,
            placeholder="e.g., OpenRouter https://openrouter.ai/api/v1",
        )

        # LLM API KEY
        st.text_input(
            "Model API Key *",
            key="MODEL_API_KEY",
            value=st.session_state.get("MODEL_API_KEY", ""),
            type="password",
            help="""
    The key required for authenticating with the model's provider.
    This is usually issued when you sign up for access to a model.
            """,
        )

    with st.expander("Voice Settings (TTS/STT)", expanded=True):
        # Voice Enable/Disable Toggle
        st.caption("Voice Control")
        voice_enabled = st.checkbox(
            "Enable Voice Features (TTS/STT)",
            value=st.session_state.get("VOICE", False),
            help="""
    Enable or disable voice features including:
    - **Text-to-Speech (TTS)**: Convert AI responses to speech
    - **Speech-to-Text (STT)**: Convert voice input to text

    When disabled, all voice-related settings below will be hidden.
            """,
        )

        # Update session state with boolean value
        st.session_state["VOICE"] = voice_enabled

        # Show voice settings only when voice is enabled
        if voice_enabled:
            st.markdown("---")  # Separator

            # TTS Configuration Section
            st.caption("Text-to-Speech (TTS) Configuration")

            # TTS First row: API Key, Model, Voice
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.text_input(
                    "TTS API Key",
                    key="TTS_API_KEY",
                    value=st.session_state.get("TTS_API_KEY", ""),
                    type="password",
                    help="""
    API key for TTS service authentication.
    Leave empty for local/dummy services.
                    """,
                    placeholder="Enter your TTS API key",
                )
            with col2:
                st.text_input(
                    "TTS Model",
                    key="TTS_MODEL",
                    value=st.session_state.get("TTS_MODEL", ""),
                    type="default",
                    help="""
    Enter the TTS model to use (e.g., tts-1, tts-1-hd, gpt-4o-mini-tts).
    - **tts-1**: Standard quality, faster
    - **tts-1-hd**: High quality, slower
    - **gpt-4o-mini-tts**: Latest model with voice instructions support
                    """,
                    placeholder="e.g., tts-1, tts-1-hd, gpt-4o-mini-tts",
                )
            with col3:
                st.text_input(
                    "TTS Voice",
                    key="TTS_VOICE",
                    value=st.session_state.get("TTS_VOICE", ""),
                    type="default",
                    help="""
    Enter the voice persona for TTS output.
    Different voices have different tones and characteristics.
                    """,
                    placeholder="e.g., alloy, echo, nova, shimmer",
                )

            # TTS Second row: Base URL and Speed
            col1, col2 = st.columns([2, 1])
            with col1:
                st.text_input(
                    "TTS Base URL",
                    key="TTS_BASE_URL",
                    value=st.session_state.get("TTS_BASE_URL", ""),
                    type="default",
                    help="""
    Base URL for the TTS API endpoint.
    Use local TTS service endpoints like http://localhost:4123/v1
                    """,
                    placeholder="e.g., http://localhost:4123/v1",
                )
            with col2:
                tts_speed = st.session_state.get("TTS_SPEED", 1.0)
                try:
                    tts_speed = float(tts_speed)
                except (ValueError, TypeError):
                    tts_speed = 1.0
                tts_speed = max(0.25, min(4.0, tts_speed))
                st.slider(
                    "TTS Speed",
                    min_value=0.25,
                    max_value=4.0,
                    value=tts_speed,
                    step=0.25,
                    key="TTS_SPEED",
                    help="""
    Controls the speed of speech synthesis:
    - 0.25: Very slow
    - 1.0: Normal speed
    - 4.0: Very fast
                    """,
                )

            # STT Configuration Section
            st.markdown("---")  # Separator
            st.caption("Speech-to-Text (STT) Configuration")

            # STT First row: API Key, Model, Language
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.text_input(
                    "STT API Key",
                    key="STT_API_KEY",
                    value=st.session_state.get("STT_API_KEY", ""),
                    type="password",
                    help="""
    API key for STT service authentication.
    Leave empty for local/dummy services.
                    """,
                    placeholder="Enter your STT API key",
                )
            with col2:
                st.text_input(
                    "STT Model",
                    key="STT_MODEL",
                    value=st.session_state.get("STT_MODEL", ""),
                    type="default",
                    help="""
    Enter the STT model to use (e.g., whisper-1, gpt-4o-transcribe).
    - **whisper-1**: Standard Whisper model
    - **gpt-4o-transcribe**: GPT-4 based transcription
    - **gpt-4o-transcribe-diarize**: With speaker diarization
                    """,
                    placeholder="e.g., whisper-1, gpt-4o-transcribe",
                )
            with col3:
                st.text_input(
                    "STT Language",
                    key="STT_LANGUAGE",
                    value=st.session_state.get("STT_LANGUAGE", ""),
                    type="default",
                    help="""
    ISO 639-1 language code (e.g., 'en', 'zh', 'ja').
    Leave empty for auto-detection.
                    """,
                    placeholder="e.g., en, zh, ja (optional)",
                )

            # STT Second row: Base URL, Temperature
            col1, col2 = st.columns([2, 1])
            with col1:
                st.text_input(
                    "STT Base URL",
                    key="STT_BASE_URL",
                    value=st.session_state.get("STT_BASE_URL", ""),
                    type="default",
                    help="""
    Base URL for the STT API endpoint.
    Use local STT service endpoints like http://127.0.0.1:8001/v1
                    """,
                    placeholder="e.g., http://127.0.0.1:8001/v1",
                )
            with col2:
                stt_temp = st.session_state.get("STT_TEMPERATURE", 0.0)
                try:
                    stt_temp = float(stt_temp)
                except (ValueError, TypeError):
                    stt_temp = 0.0
                stt_temp = max(0.0, min(1.0, stt_temp))
                st.slider(
                    "STT Temperature",
                    min_value=0.0,
                    max_value=1.0,
                    value=stt_temp,
                    step=0.1,
                    key="STT_TEMPERATURE",
                    help="""
    Controls randomness in transcription:
    - 0.0: Deterministic, most accurate
    - 1.0: More creative, less accurate
                    """,
                )
        else:
            st.caption(
                "💡 Voice features are currently disabled. Enable toggle above to configure TTS/STT settings. (Experimental Test Feature)"
            )

    with st.expander("Calibre & Reading Settings", expanded=True):
        # st.caption("Calibre E-book Server Configuration")
        (col1,) = st.columns([1])
        with col1:
            st.text_input(
                "Calibre Server URL",
                key="CALIBRE_SERVER_URL",
                value=st.session_state.get(
                    "CALIBRE_SERVER_URL",
                ),
                type="default",
                placeholder="e.g., http://localhost:8080",
                help="""
    Enter the URL of your Calibre Content Server.
    Make sure the Calibre server is running and accessible.
                """,
            )

        # st.caption("Reading Notes Directory")

        notes_dir_value = st.session_state.get("READING_NOTES_DIR", "notes")
        st.text_input(
            "Notes Directory Path",
            key="READING_NOTES_DIR",
            value=notes_dir_value,
            type="default",
            placeholder="e.g., notes",
            help="""
    Directory where reading notes will be stored.
    Notes are saved as Markdown (.md) files.
                """,
        )

        # Show warning if the value is empty or contains only whitespace
        if not notes_dir_value or not notes_dir_value.strip():
            st.info(
                "💡 Empty path detected. The default directory **'notes'** will be used."
            )

    with st.expander("Other Settings", expanded=True):
        english_levels = ["Normal Prompt", "A1", "A2", "B1", "B2", "C1", "C2"]
        eng_level = st.session_state.get("ENGLISH_LEVEL", "Normal Prompt")
        eng_level_index = (
            english_levels.index(eng_level) if eng_level in english_levels else 0
        )
        st.selectbox(
            "English Level",
            options=english_levels,
            index=eng_level_index,
            key="ENGLISH_LEVEL",
            help="""
    Select your English proficiency level based on the CEFR (Common European Framework of Reference for Languages) framework:

    **CEFR English Levels:**
    - **A1 (Beginner)**: Basic phrases, simple network terminology
    - **A2 (Elementary)**: Simple sentences, common network concepts
    - **B1 (Intermediate)**: Complex sentences, technical explanations
    - **B2 (Upper-Intermediate)**: Professional network terminology
    - **C1 (Advanced)**: Expert-level network discussions
    - **C2 (Proficiency)**: Native-level technical communication

    **Auto Select**: Uses the standard network automation prompt (React Prompt) optimized for general technical users

    The system will adjust prompt complexity, vocabulary, and explanation style based on your selected level.
    """,
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            st.text_input(
                "Linux Console Username",
                key="LINUX_TELNET_USERNAME",
                value=st.session_state.get("LINUX_TELNET_USERNAME", ""),
                placeholder="E.g., debian",
                type="default",
                help="""
    Use gns3 debian linux.

    https://www.gns3.com/marketplace/appliances/debian-2
                """,
            )
        with col2:
            st.text_input(
                "Linux Console Password",
                key="LINUX_TELNET_PASSWORD",
                value=st.session_state.get("LINUX_TELNET_PASSWORD", ""),
                placeholder="E.g., debian",
                type="password",
            )

    st.button("Save Settings", on_click=save_config)
