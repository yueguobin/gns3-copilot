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
Sidebar component for GNS3 Copilot application.

This module provides reusable sidebar UI components for GNS3 Copilot
Streamlit application, including page configuration controls and session
management. The sidebar is rendered centrally in app.py and provides
consistent functionality across all pages.

Features:
    - Page height adjustment slider (global)
    - Zoom scale adjustment slider (global)
    - Session history management (global)
    - About section (global)

Usage:
    The sidebar is rendered in app.py before page navigation:

        from gns3_copilot.ui_model.sidebar import render_sidebar, render_sidebar_about

        # Render sidebar with current page information
        selected_thread_id, title = render_sidebar(current_page="ui_model/chat.py")

        # Store results in session_state for use by other pages
        st.session_state["selected_thread_id"] = selected_thread_id
        st.session_state["session_title"] = title

        # Render about section after navigation
        render_sidebar_about()

Notes:
    - Configuration changes (height, zoom) are persisted to SQLite database
    - Thread IDs are managed through LangGraph checkpointer

See Also:
    - src/gns3_copilot/app.py: Main application entry point
    - src/gns3_copilot/agent: LangGraph agent and checkpointer
    - src/gns3_copilot/ui_model/chat: Chat page that uses sidebar state
"""

import tempfile
from datetime import datetime
from typing import Any

import streamlit as st

from gns3_copilot import __version__
from gns3_copilot.agent import agent, langgraph_checkpointer, list_thread_ids
from gns3_copilot.agent.checkpoint_utils import (
    export_checkpoint_to_file,
    import_checkpoint_from_file,
)
from gns3_copilot.log_config import setup_logger
from gns3_copilot.ui_model.utils import new_session, save_config

logger = setup_logger("chat")


def render_sidebar(
    current_page: str,
) -> tuple[Any | None, str | None]:
    """
    Render() global sidebar for all pages.

    This function renders sidebar controls including:
    - Page height adjustment
    - Zoom scale adjustment
    - Session history management

    Args:
        current_page: The current active page path

    Returns:
        Tuple of (selected_thread_id, title) - can be None if no session is selected
    """
    with st.sidebar:
        # Initialize sidebar configuration values
        # Get current container height from session state or default to 900
        current_height = st.session_state.get("CONTAINER_HEIGHT")
        if current_height is None or not isinstance(current_height, int):
            current_height = 900

        # Get current zoom scale from session state
        current_zoom = st.session_state.get("zoom_scale_topology")
        if current_zoom is None:
            current_zoom = 0.8

        with st.expander(":material/settings: Display Settings", expanded=False):
            # Note: We don't use key parameter here to avoid automatic session_state management
            new_height = st.slider(
                ":material/height: Page Height (px)",
                min_value=300,
                max_value=1500,
                value=current_height,
                step=50,
                help="Adjust height for chat and GNS3 view",
            )

            # If height changed, update session state and save to database
            if new_height != current_height:
                st.session_state["CONTAINER_HEIGHT"] = new_height
                # Save to database using centralized save function
                try:
                    save_config()
                except Exception as e:
                    logger.error("Failed to update CONTAINER_HEIGHT: %s", e)

            new_zoom = st.slider(
                ":material/zoom_in: Zoom Scale",
                min_value=0.5,
                max_value=1.2,
                value=current_zoom,
                step=0.05,
                help="Adjust zoom scale for GNS3 topology view",
            )

            # If zoom changed, update session state and save to database
            if new_zoom != current_zoom:
                st.session_state["zoom_scale_topology"] = new_zoom
                try:
                    save_config()
                except Exception as e:
                    logger.error("Failed to update ZOOM_SCALE_TOPOLOGY: %s", e)

        # st.markdown("---")

        # Session management - render for all pages
        selected_thread_id = None
        title = None

        try:
            selected_thread_id, title = _render_session_management()
        except Exception as e:
            logger.error("Failed to render session management: %s", e)
            st.error("Failed to load session history. Please check the logs.")

        return selected_thread_id, title


def _render_session_management() -> tuple[Any | None, str | None]:
    """
    Render session history and management controls.

    Returns:
        Tuple of (selected_thread_id, title)
    """
    thread_ids = list_thread_ids(langgraph_checkpointer)

    # Display name/value are title and id
    # The first option is an empty/placeholder selection
    session_options: list[tuple[str, str | None]] = [("(Please select session)", None)]

    for tid in thread_ids:
        ckpt = langgraph_checkpointer.get({"configurable": {"thread_id": tid}})
        title_value = (
            ckpt.get("channel_values", {}).get("conversation_title") if ckpt else None
        ) or "New Session"
        # Same title name caused to issue where selecting conversations always selected to same thread id.
        # Use part of thread_id to avoid same title name
        unique_title = f"{title_value} ({tid[:6]})"
        session_options.append((unique_title, tid))

    logger.debug("session_options : %s", session_options)

    selected = st.selectbox(
        ":material/history: Session History",
        options=session_options,
        format_func=lambda x: x[0],  # view conversation_title
        key="session_select",  # new key for state management
    )

    title, selected_thread_id = selected

    logger.debug("selectbox selected : %s, %s", title, selected_thread_id)

    st.markdown(
        f"<span style='font-size: 13px;'>Current Session: `{title} thread_id: {selected_thread_id}`</span>",
        unsafe_allow_html=True,
    )

    # Display current project (saved to session_state by chat.py)
    current_project = st.session_state.get("current_project")
    if current_project:
        st.markdown(
            f"<span style='font-size: 13px;'>Current Project: `{current_project[0]}`</span>",
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button(
            ":material/add_circle:",
            on_click=lambda: new_session(session_options),
            help="Create a new session",
        )
    with col2:
        # Only allow deletion if the user has selected a valid thread_id
        if selected_thread_id is not None:
            if st.button(":material/delete:", help="Delete current selection session"):
                langgraph_checkpointer.delete_thread(thread_id=selected_thread_id)
                st.success(
                    f"_Delete Success_: {title} \n\n _Thread_id_: `{selected_thread_id}`"
                )
                st.rerun()
    with col3:
        # Export button - only show if a session is selected
        if selected_thread_id is not None:
            if st.button(":material/download:", help="Export current session"):
                with st.spinner("Exporting session..."):
                    try:
                        # Create a temporary file for export
                        with tempfile.NamedTemporaryFile(
                            mode="w", delete=False, suffix=".json", encoding="utf-8"
                        ) as tmp_file:
                            temp_path = tmp_file.name

                        # Export checkpoint to temporary file
                        success = export_checkpoint_to_file(
                            langgraph_checkpointer, selected_thread_id, temp_path
                        )

                        if success:
                            # Read exported data
                            with open(temp_path, encoding="utf-8") as f:
                                export_data = f.read()

                            # Generate safe filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            # Extract title without the thread_id suffix
                            display_title = (
                                title.split(" (")[0] if " (" in title else title
                            )
                            safe_title = (
                                display_title.replace(" ", "_")
                                .replace("/", "_")
                                .replace("\\", "_")
                                .replace(":", "_")
                                .replace("*", "_")
                                .replace("?", "_")
                                .replace('"', "_")
                                .replace("<", "_")
                                .replace(">", "_")
                                .replace("|", "_")[:50]
                            )
                            filename = f"{safe_title}_{timestamp}.json"

                            # Provide download button
                            st.download_button(
                                label=":material/download_file:",
                                data=export_data,
                                file_name=filename,
                                mime="application/json",
                                key=f"download_{selected_thread_id}",
                                help="Download exported file",
                            )
                            st.success("✅")
                            logger.info(
                                "Exported session %s to %s",
                                selected_thread_id,
                                filename,
                            )

                            # Clean up temporary file
                            import os

                            os.unlink(temp_path)
                        else:
                            st.error("❌ Failed to export session")
                            logger.error(
                                "Failed to export session %s", selected_thread_id
                            )
                    except Exception as e:
                        st.error(f"❌ Export error: {str(e)}")
                        logger.error("Export error: %s", e)

    # st.markdown("---")

    # Import session functionality in expander
    with st.expander(":material/upload: Import Session", expanded=False):
        # Initialize import success flag in session_state
        if "import_success" not in st.session_state:
            st.session_state["import_success"] = False

        uploaded_file = st.file_uploader(
            "Upload a previously exported session file",
            type=["json", "txt"],
            help="Select a .json or .txt file exported from GNS3 Copilot",
            key="file_uploader_import",
        )

        # Only import if a file is uploaded and we haven't marked it as successful yet
        if uploaded_file is not None and not st.session_state["import_success"]:
            with st.spinner("Importing session..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".json", encoding="utf-8", mode="w"
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue().decode("utf-8"))
                        temp_path = tmp_file.name

                    logger.info(
                        "Importing session from file: %s (size: %d bytes)",
                        uploaded_file.name,
                        uploaded_file.size,
                    )

                    # Import the checkpoint
                    success, result = import_checkpoint_from_file(
                        langgraph_checkpointer, temp_path
                    )

                    # Clean up temporary file
                    import os

                    os.unlink(temp_path)

                    if success:
                        new_thread_id = result
                        st.session_state["import_success"] = True
                        st.success(
                            f"✅ **Import successful!**\n\n"
                            f"New thread ID: `{new_thread_id[:8]}...`\n\n"
                            f"Select the new session from the dropdown above."
                        )
                        logger.info(
                            "Successfully imported session to new thread: %s",
                            new_thread_id,
                        )
                        # Refresh the session list after a short delay to show success message
                        import time

                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"❌ **Import failed:** {result}")
                        logger.error("Import failed: %s", result)
                        # Reset flag on failure so user can try again
                        st.session_state["import_success"] = False
                except Exception as e:
                    st.error(f"❌ **Import error:** {str(e)}")
                    logger.error("Import exception: %s", e)
                    # Reset flag on error so user can try again
                    st.session_state["import_success"] = False

        # Show "Import Another File" button if import was successful
        if st.session_state["import_success"] and uploaded_file is not None:
            if st.button(
                ":material/add:",
                key="import_another_button",
                help="Import another file",
            ):
                st.session_state["import_success"] = False
                st.rerun()

    # If a valid thread id is selected, load the historical messages
    if selected_thread_id is not None:
        # Store the selected ID for use in the main interface
        st.session_state["current_thread_id"] = selected_thread_id
        st.session_state["state_history"] = agent.get_state(
            {"configurable": {"thread_id": selected_thread_id}}
        )

    return selected_thread_id, title


def render_sidebar_about() -> None:
    """Render the about section in the sidebar."""
    with st.sidebar:
        # st.markdown("---")
        st.markdown("### :material/info: About")
        st.markdown(
            f"""
            **GNS3 Copilot** {__version__} is an AI-powered network engineering assistant
            designed to help you with GNS3 network simulation tasks.

            :material/book: [Documentation](https://github.com/yueguobin/gns3-copilot)
            """
        )
