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
# mypy: ignore-errors
"""
GNS3 Copilot - AI-Powered Network Engineering Assistant

This module implements the main Streamlit web application for GNS3 Copilot,
an AI-powered assistant designed to help network engineers with GNS3-related
tasks through a conversational chat interface.

Features:
- Real-time chat interface with streaming responses
- Integration with LangChain agents for intelligent conversation
- Tool calling support for GNS3 network operations
- Message history and session state management
- Support for multiple message types (Human, AI, Tool messages)
- Interactive tool call and response visualization

The application leverages:
- Streamlit for the web UI
- LangGraph for AI agent functionality
- Custom GNS3 integration tools
- Session-based conversation tracking with unique thread IDs

Usage:
Run this module directly to start the GNS3 Copilot web interface:
    streamlit run app.py

Note: Requires proper configuration of GNS3 server and API credentials.
"""

import json
import uuid
from time import sleep
from typing import Any

import streamlit as st
from langchain.messages import AIMessage, HumanMessage, ToolMessage

from gns3_copilot.agent import agent
from gns3_copilot.gns3_client import GNS3ProjectList
from gns3_copilot.log_config import setup_logger
from gns3_copilot.ui_model.utils import (
    build_topology_iframe_url,
    generate_topology_iframe_html,
    render_create_project_form,
    render_project_cards,
)
from gns3_copilot.utils import (
    format_tool_response,
    get_duration,
    speech_to_text,
    text_to_speech_wav,
)

logger = setup_logger("chat")

# Initialize session state for thread ID
if "thread_id" not in st.session_state:
    # If thread_id is not in session_state, create and save a new one
    st.session_state["thread_id"] = str(uuid.uuid4())

# Initialize iframe URL mode (project page vs login page)
if "gns3_url_mode" not in st.session_state:
    st.session_state.gns3_url_mode = "project"

# Initialize iframe visibility state
# Used to show/hide GNS3 topology interface
if "show_iframe" not in st.session_state:
    st.session_state.show_iframe = False

# Initialize temp_selected_project for new sessions
if "temp_selected_project" not in st.session_state:
    st.session_state["temp_selected_project"] = None

current_thread_id = st.session_state["thread_id"]

# Get selected thread ID and title from session state (set by sidebar)
selected_thread_id = st.session_state.get("selected_thread_id")
title = st.session_state.get("session_title")


# Unique thread ID for each session
# If a session is selected, continue the conversation using its thread ID;
# otherwise, initialize a new thread ID.
if selected_thread_id:
    config = {
        "configurable": {
            "thread_id": st.session_state["current_thread_id"],
            "max_iterations": 50,
        },
        "recursion_limit": 28,
    }
else:
    config = {
        "configurable": {"thread_id": current_thread_id, "max_iterations": 50},
        "recursion_limit": 28,
    }

# --- Get current state ---
if selected_thread_id:
    # Historical session: get from agent state
    snapshot = agent.get_state(config)
    selected_p = snapshot.values.get("selected_project")
else:
    # New session: get from temp storage
    selected_p = st.session_state.get("temp_selected_project")

# --- Logic branch: If no project is selected, display project cards ---
if not selected_p:
    st.markdown(
        """
        <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>GNS3 Copilot - Workspace Selection</h3>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Please select a project to enter the conversation context. Closed projects can be opened directly.",
        width=800,
    )

    # Render create project form
    render_create_project_form()

    # Get project list and render project cards
    projects = GNS3ProjectList()._run().get("projects", [])
    if projects:
        render_project_cards(projects, selected_thread_id, config)
    else:
        st.error("No projects found in GNS3.")
        if st.button("Refresh List"):
            st.rerun()
else:
    # Save current project to session_state for sidebar display
    st.session_state["current_project"] = selected_p

# --- Main workspace (only visible when a project is selected) ---
if selected_p:
    # Dynamic column layout based on iframe visibility
    if st.session_state.show_iframe:
        layout_col1, layout_col2 = st.columns([3, 7], gap="medium")
    else:
        layout_col1 = st.container()

    with layout_col1:
        history_container = st.container(
            height=st.session_state.CONTAINER_HEIGHT,
            border=False,
        )
        with history_container:
            st.markdown(
                """
                <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>Workspace</h3>
                """,
                unsafe_allow_html=True,
            )
            # StateSnapshot state example test/langgraph_checkpoint.json file
            # Display previous messages from state history
            if st.session_state.get("state_history") is not None:
                # StateSnapshot values dictionary
                values_dict = st.session_state["state_history"].values
                message_to_render = values_dict.get("messages", [])

                # Track current open assistant message block
                current_assistant_block = None

                # StateSnapshot values messages list
                for message_object in message_to_render:
                    # Handle different message types
                    if isinstance(message_object, HumanMessage):
                        # Close any open assistant chat message block before starting a new user message
                        if current_assistant_block is not None:
                            current_assistant_block.__exit__(None, None, None)
                            current_assistant_block = None
                        # UserMessage
                        with st.chat_message("user"):
                            st.markdown(message_object.content)

                    elif isinstance(message_object, (AIMessage, ToolMessage)):
                        # Open a new assistant chat message block if none is open
                        if current_assistant_block is None:
                            current_assistant_block = st.chat_message("assistant")
                            current_assistant_block.__enter__()

                        # Handle AIMessage with tool_calls
                        if isinstance(message_object, AIMessage):
                            # AIMessage content
                            # adapted for gemini
                            # Check if content is a list and safely extract the first text element
                            if (
                                isinstance(message_object.content, list)
                                and message_object.content
                                and "text" in message_object.content[0]
                            ):
                                st.markdown(message_object.content[0]["text"])
                            # Plain string content
                            elif isinstance(message_object.content, str):
                                st.markdown(message_object.content)
                            # AIMessage tool_calls
                            if (
                                isinstance(message_object.tool_calls, list)
                                and message_object.tool_calls
                            ):
                                for tool in message_object.tool_calls:
                                    tool_id = tool.get("id", "UNKNOWN_ID")
                                    tool_name = tool.get("name", "UNKNOWN_TOOL")
                                    tool_args = tool.get("args", {})
                                    # Display tool call details
                                    with st.expander(
                                        f"**Tool Call:** `{tool_name}`",
                                        expanded=False,
                                    ):
                                        st.json(
                                            {
                                                # "name": tool_name,
                                                # "id": tool_id,
                                                "tool_input": tool_args.get(
                                                    "tool_input"
                                                ),
                                                # "type": "tool_call",
                                            },
                                            expanded=True,
                                        )
                        # Handle ToolMessage
                        if isinstance(message_object, ToolMessage):
                            content_pretty = format_tool_response(
                                message_object.content
                            )
                            with st.expander(
                                "**Tool Response**",
                                expanded=False,
                            ):
                                st.json(json.loads(content_pretty), expanded=2)

                # Close any remaining open assistant chat message block
                if current_assistant_block is not None:
                    current_assistant_block.__exit__(None, None, None)

    # Only render layout_col2 content when show_iframe is True
    if st.session_state.show_iframe:
        with layout_col2:
            # Extract project_id from the selected project
            project_id = selected_p[
                1
            ]  # selected_p is a tuple: (name, p_id, dev_count, link_count, status)
            # Build the topology iframe URL based on API version and URL mode
            iframe_url = build_topology_iframe_url(project_id)

            iframe_container = st.container(
                height=st.session_state.CONTAINER_HEIGHT,
                # horizontal_alignment="center",
                vertical_alignment="center",
                border=False,
            )
            with iframe_container:
                # Set zoom scale (0.7 = 70%, 0.8 = 80%, 0.9 = 90%)
                zoom_scale = (
                    st.session_state.zoom_scale_topology
                )  # Scale to 80%, you can adjust between 0.7-0.9

                iframe_html = generate_topology_iframe_html(
                    iframe_url=iframe_url,
                    zoom_scale=zoom_scale,
                    container_height=st.session_state.CONTAINER_HEIGHT,
                )

                st.markdown(iframe_html, unsafe_allow_html=True)

    # st.divider()
    # --- Chat Input Area ---
    if st.session_state.show_iframe:
        # When Show Topology: there are two buttons on the right, needs to be wider
        # Left column is narrow, middle column is moderate, right column is wider
        col_ratio = [0.2, 0.6, 0.4]
    else:
        # When Hide Topology: there is only one button on the right
        # Left column is narrow, middle column is wide, right column is moderate
        col_ratio = [0.2, 0.7, 0.3]

    chat_input_left, chat_input_center, chat_input_right = st.columns(col_ratio)

    with chat_input_center:
        # Configure chat_input based on switch
        # Get voice enabled setting from session_state (loaded from .env file)
        voice_enabled = st.session_state.get("VOICE", False)
        if voice_enabled:
            prompt = st.chat_input(
                "Say or record something...",
                accept_audio=True,
                audio_sample_rate=24000,
                # width=600,
            )
        else:
            # When voice is disabled, do not enable accept_audio attribute
            prompt = st.chat_input(
                "Type your message here...",
                # width=600
            )
        # Handle input
        if prompt:
            user_text = ""
            if voice_enabled:
                # Mode A: prompt is an object (containing .text and .audio)
                if prompt.audio:
                    user_text = speech_to_text(prompt.audio)
                # If voice is not converted to text, or user directly types
                if not user_text:
                    user_text = prompt.text
            else:
                # Mode B: prompt is directly a string
                user_text = prompt
            # 3. Final check and run
            if not user_text or user_text.strip() == "":
                st.stop()

            with history_container:
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(user_text)

            # Migrate temp selected project to agent state for new sessions
            if not selected_thread_id and st.session_state.get("temp_selected_project"):
                temp_project = st.session_state["temp_selected_project"]
                agent.update_state(config, {"selected_project": temp_project})
                # Don't clear temp_selected_project immediately
                # It will be cleared after rerun when selected_p is retrieved from agent state

            with history_container:
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    active_text_placeholder = st.empty()
                    current_text_chunk = ""
                    # Core aggregation state: only stores currently streaming tool information
                    # Structure: {'id': str, 'name': str, 'args_string': str} or None
                    current_tool_state = None
                    # TTS local switch for message control
                    tts_played = False
                    # Initialize audio_bytes variable
                    audio_bytes = None
                    # Stream the agent response
                    for chunk in agent.stream(
                        {
                            "messages": [HumanMessage(content=user_text)],
                        },
                        config=config,
                        stream_mode="messages",
                    ):
                        for msg in chunk:
                            # with open('log.txt', "a", encoding='utf-8') as f:
                            #    f.write(f"{msg}\n\n")
                            if isinstance(msg, AIMessage):
                                # adapted for gemini
                                # Check if content is a list and safely extract the first text element
                                if (
                                    isinstance(msg.content, list)
                                    and msg.content
                                    and "text" in msg.content[0]
                                ):
                                    actual_text = msg.content[0]["text"]
                                    # Now actual_text is the clean text you need
                                    current_text_chunk += actual_text
                                    # Only display text in non-voice mode
                                    if not voice_enabled:
                                        active_text_placeholder.markdown(
                                            current_text_chunk, unsafe_allow_html=True
                                        )
                                elif isinstance(msg.content, str):
                                    current_text_chunk += str(msg.content)
                                    # Only display text in non-voice mode
                                    if not voice_enabled:
                                        active_text_placeholder.markdown(
                                            current_text_chunk, unsafe_allow_html=True
                                        )
                                # Determine if text message (i.e., msg.content) reception is complete
                                is_text_ending = (
                                    # Case 1: Tool call starts
                                    msg.tool_calls
                                    or
                                    # Case 2: End metadata received
                                    msg.response_metadata.get("finish_reason")
                                    in ["tool_calls", "stop"]
                                )
                                if (
                                    is_text_ending
                                    and not tts_played
                                    and current_text_chunk.strip()
                                    and voice_enabled
                                ):
                                    # Play once in a round of AIMessage/ToolMessage
                                    tts_played = True
                                    # Text_to_speech
                                    try:
                                        with st.spinner(
                                            "Generating voice...", width=200
                                        ):
                                            audio_bytes = text_to_speech_wav(
                                                current_text_chunk
                                            )
                                            st.audio(
                                                audio_bytes,
                                                format="audio/mp3",
                                                autoplay=True,
                                                width=200,
                                            )
                                            # Wait for audio playback to complete
                                            duration = get_duration(audio_bytes)
                                            logger.info(
                                                "TTS audio duration: %.2f seconds",
                                                duration,
                                            )
                                            sleep(duration)  # Extra buffer time
                                    except Exception as e:
                                        logger.error("TTS Error: %s", e)
                                        st.error(f"TTS Error: {e}")
                                # Get metadata (ID and name) from tool_calls
                                if msg.tool_calls:
                                    for tool in msg.tool_calls:
                                        tool_id = tool.get("id")
                                        # Only when ID is not empty, consider it as the start of a new tool call
                                        if tool_id:
                                            # Initialize current tool state (this is the only time to get ID)
                                            # Note: only one tool can be called at a time
                                            current_tool_state = {
                                                "id": tool_id,
                                                "name": tool.get(
                                                    "name", "UNKNOWN_TOOL"
                                                ),
                                                "args_string": "",
                                            }
                                # Concatenate parameter strings from tool_call_chunk
                                if (
                                    hasattr(msg, "tool_call_chunks")
                                    and msg.tool_call_chunks
                                ):
                                    if current_tool_state:
                                        tool_data = current_tool_state
                                        for chunk_update in msg.tool_call_chunks:
                                            args_chunk = chunk_update.get("args", "")
                                            # Core: string concatenation
                                            if isinstance(args_chunk, str):
                                                tool_data["args_string"] += args_chunk
                                # Determine if the tool_calls_chunks output is complete and
                                # display the st.expander() for tool_calls
                                if msg.response_metadata.get(
                                    "finish_reason"
                                ) == "tool_calls" or (
                                    msg.response_metadata.get("finish_reason") == "STOP"
                                    and current_tool_state is not None
                                ):
                                    tool_data = current_tool_state
                                    # Parse complete parameter string
                                    parsed_args: dict[str, Any] = {}
                                    try:
                                        parsed_args = json.loads(
                                            tool_data["args_string"]
                                        )
                                    except json.JSONDecodeError:
                                        parsed_args = {
                                            "error": "JSON parse failed after stream complete."
                                        }
                                    # Serialize the tool_input value in parsed_args to a JSON array
                                    # for expansion when using st.json
                                    try:
                                        command_list = json.loads(
                                            parsed_args["tool_input"]
                                        )
                                        parsed_args["tool_input"] = command_list
                                    except (json.JSONDecodeError, KeyError, TypeError):
                                        pass
                                    # Build the final display structure that meets your requirements
                                    display_tool_call = {
                                        "name": tool_data["name"],
                                        "id": tool_data["id"],
                                        # Inject tool_input structure
                                        "tool_input": parsed_args.get("tool_input"),
                                        "type": tool_data.get(
                                            "type", "tool_call"
                                        ),  # Maintain completeness
                                    }
                                    # Update Call Expander, display final parameters (collapsed)
                                    with st.expander(
                                        f"**Tool Call:** `{tool_data['name']}`",
                                        expanded=False,
                                    ):
                                        # Use the final complete structure
                                        st.json(display_tool_call, expanded=False)
                            if isinstance(msg, ToolMessage):
                                # Clear state after completion, ready to receive next tool call
                                current_tool_state = None
                                content_pretty = format_tool_response(msg.content)
                                with st.expander(
                                    "**Tool Response**",
                                    expanded=False,
                                ):
                                    st.json(json.loads(content_pretty), expanded=False)
                                active_text_placeholder = st.empty()
                                current_text_chunk = ""
                                tts_played = False
                # After the interaction, update the session state with the latest StateSnapshot
                state_history = agent.get_state(config)
                # Avoid updating if state_history is empty
                if not state_history[0]:
                    pass
                else:
                    # Update session state
                    st.session_state["state_history"] = state_history
                    # print(state_history)
                # with open('state_history.txt', "a", encoding='utf-8') as f:
                #    f.write(f"{state_history}\n\n")

    with chat_input_right:
        # Create two sub-columns in the right column, arrange buttons left and right
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(
                "Hide" if st.session_state.show_iframe else "Show",
                icon=":material/visibility:"
                if not st.session_state.show_iframe
                else ":material/visibility_off:",
                help="Show or hide the GNS3 project topology iframe",
            ):
                st.session_state.show_iframe = not st.session_state.show_iframe
                st.rerun()

        with btn_col2:
            if st.session_state.show_iframe:
                if st.button(
                    "Login"
                    if st.session_state.gns3_url_mode == "project"
                    else "Topology",
                    icon=":material/login:"
                    if st.session_state.gns3_url_mode == "project"
                    else ":material/device_hub:",
                    help="If the page is not displayed, please click me. Need to perform GNS3 web login once.",
                ):
                    st.session_state.gns3_url_mode = (
                        "login"
                        if st.session_state.gns3_url_mode == "project"
                        else "project"
                    )
                    st.rerun()

    with chat_input_left:
        st.empty()
