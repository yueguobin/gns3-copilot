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
Project Management UI Components for GNS3 Copilot.

This module provides reusable UI components for GNS3 project management,
including project creation, selection, and status display operations.

Functions:
    render_create_project_form(): Render the "Create New Project" expander form
    render_project_cards(projects, selected_thread_id, config): Render project selection cards
"""

from time import sleep
from typing import Any

import streamlit as st

from gns3_copilot.agent import agent
from gns3_copilot.gns3_client import (
    GNS3ProjectCreate,
    GNS3ProjectDelete,
    GNS3ProjectOpen,
)
from gns3_copilot.log_config import setup_logger

logger = setup_logger("project_manager_ui")


def render_create_project_form() -> None:
    """
    Render the "Create New Project" expander form.

    Displays a collapsible form with project name input and advanced options
    for creating a new GNS3 project. Handles form validation, project creation,
    and user feedback.

    Side Effects:
        - Creates a new GNS3 project when form is submitted
        - Displays success/error messages
        - Triggers st.rerun() on successful creation
    """
    with st.expander("Create New Project", expanded=False, width=800):
        new_name = st.text_input("Project Name", placeholder="Enter project name...")

        # Advanced options
        with st.expander("Advanced Options", expanded=False):
            auto_start = st.checkbox("Auto start project", value=False)
            auto_close = st.checkbox("Auto close on disconnect", value=False)
            auto_open = st.checkbox("Auto open on GNS3 start", value=False)
            col_width, col_height = st.columns(2)
            with col_width:
                scene_width = st.number_input(
                    "Scene Width", value=2000, min_value=500, max_value=5000
                )
            with col_height:
                scene_height = st.number_input(
                    "Scene Height", value=1000, min_value=500, max_value=5000
                )

        if st.button(
            ":material/add_circle:",
            key="btn_create_project",
            type="primary",
            help="Create Project",
        ):
            if new_name and new_name.strip():
                # Build project parameters
                params: dict[str, Any] = {"name": new_name.strip()}
                if auto_start:
                    params["auto_start"] = True
                if auto_close:
                    params["auto_close"] = True
                if auto_open:
                    params["auto_open"] = True
                params["scene_width"] = scene_width
                params["scene_height"] = scene_height

                # Call GNS3ProjectCreate tool
                create_tool = GNS3ProjectCreate()
                result = create_tool._run(params)

                if result.get("success"):
                    st.success(f"Project '{new_name}' created successfully!")
                    sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed to create project: {result.get('error')}")
            else:
                st.warning("Please enter a project name.")


def render_project_cards(
    projects: list[tuple[str, str, int, int, str]],
    selected_thread_id: str | None,
    config: dict[str, Any],
) -> None:
    """
    Render project selection cards with status information.

    Displays a grid of project cards showing project details, status,
    and appropriate action buttons based on project state (opened/closed).

    Args:
        projects: List of project tuples (name, project_id, device_count,
                  link_count, status)
        selected_thread_id: Currently selected thread ID from session
        config: Agent configuration dictionary

    Side Effects:
        - Updates session state when project is selected
        - Opens/closes projects via GNS3ProjectOpen tool
        - Triggers st.rerun() on state changes
    """
    if projects:
        cols = st.columns([1, 1], width=800)
        for i, p in enumerate(projects):
            # Destructure project tuple for clarity: name, ID, device count, link count, status
            name, p_id, dev_count, link_count, status = p
            # Check status
            is_opened = status.lower() == "opened"
            with cols[i % 2]:
                # If closed status, use container with background color or different title format
                with st.container(border=True, width=400):
                    # Add status icon to title
                    status_icon = "🟢" if is_opened else "⚪"
                    st.markdown(f"###### {status_icon} {name}")
                    st.caption(f"ID: {p_id[:8]}")
                    # Display device and link information
                    st.write(f"{dev_count} Devices | {link_count} Links")
                    # --- Button logic ---
                    # Show different buttons based on project status
                    if is_opened:
                        # Opened project: show Select Project, Close Project, and Delete Project buttons
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            if st.button(
                                ":material/select_all:",
                                key=f"btn_select_{p_id}",
                                use_container_width=True,
                                type="primary",
                                help="Select Project",
                            ):
                                if selected_thread_id:
                                    # Historical session: update agent state
                                    agent.update_state(config, {"selected_project": p})
                                else:
                                    # New session: store in temp storage
                                    st.session_state["temp_selected_project"] = p
                                st.toast(f"Project {name} selected!")
                                st.rerun()
                        with col_btn2:
                            if st.button(
                                ":material/close:",
                                key=f"btn_close_{p_id}",
                                use_container_width=True,
                                type="secondary",
                                help="Close Project",
                            ):
                                close_tool = GNS3ProjectOpen()
                                result = close_tool._run(
                                    {"project_id": p_id, "close": True}
                                )

                                if result.get("success"):
                                    st.toast(f"Project {name} closed!")
                                    # Wait a moment and refresh to update project status
                                    sleep(1)
                                    st.rerun()
                                else:
                                    st.error(
                                        f"Failed to close project {name}: {result.get('error', 'Unknown error')}"
                                    )
                        with col_btn3:
                            if st.button(
                                ":material/delete:",
                                key=f"btn_delete_{p_id}",
                                use_container_width=True,
                                help="Delete Project",
                            ):
                                # Store project info for confirmation
                                st.session_state["delete_confirmation_project"] = p
                                st.rerun()
                        # Show confirmation dialog if needed
                        if st.session_state.get("delete_confirmation_project") == p:
                            st.warning(
                                f"Are you sure you want to delete project '{name}'? This action cannot be undone!"
                            )
                            col_confirm, col_cancel = st.columns(2)
                            with col_confirm:
                                if st.button(
                                    ":material/check_circle:",
                                    key=f"btn_confirm_delete_{p_id}",
                                    type="primary",
                                    use_container_width=True,
                                    help="Confirm",
                                ):
                                    delete_tool = GNS3ProjectDelete()
                                    result = delete_tool._run({"project_id": p_id})
                                    if result.get("success"):
                                        st.session_state.pop(
                                            "delete_confirmation_project", None
                                        )
                                        sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"Failed to delete project '{name}': {result.get('error', 'Unknown error')}"
                                        )
                            with col_cancel:
                                if st.button(
                                    ":material/cancel:",
                                    key=f"btn_cancel_delete_{p_id}",
                                    use_container_width=True,
                                    help="Cancel",
                                ):
                                    st.session_state.pop(
                                        "delete_confirmation_project", None
                                    )
                                    st.rerun()
                    else:
                        # Closed project: show Open Project and Delete Project buttons
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button(
                                ":material/open_in_new:",
                                key=f"btn_open_{p_id}",
                                use_container_width=True,
                                type="secondary",
                                help="Open Project",
                            ):
                                open_tool = GNS3ProjectOpen()
                                result = open_tool._run(
                                    {"project_id": p_id, "open": True}
                                )
                                if result.get("success"):
                                    st.toast(f"Project {name} opened!")
                                    # Wait a moment and refresh to update project status
                                    sleep(1)
                                    st.rerun()
                                else:
                                    st.error(
                                        f"Failed to open project {name}: {result.get('error', 'Unknown error')}"
                                    )
                        with col_btn2:
                            if st.button(
                                ":material/delete:",
                                key=f"btn_delete_{p_id}",
                                use_container_width=True,
                                help="Delete Project",
                            ):
                                # Store project info for confirmation
                                st.session_state["delete_confirmation_project"] = p
                                st.rerun()
                        # Show confirmation dialog if needed
                        if st.session_state.get("delete_confirmation_project") == p:
                            st.warning(
                                f"Are you sure you want to delete project '{name}'? This action cannot be undone!"
                            )
                            col_confirm, col_cancel = st.columns(2)
                            with col_confirm:
                                if st.button(
                                    ":material/check_circle:",
                                    key=f"btn_confirm_delete_{p_id}",
                                    type="primary",
                                    use_container_width=True,
                                    help="Confirm",
                                ):
                                    delete_tool = GNS3ProjectDelete()
                                    result = delete_tool._run({"project_id": p_id})
                                    if result.get("success"):
                                        st.session_state.pop(
                                            "delete_confirmation_project", None
                                        )
                                        sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(
                                            f"Failed to delete project '{name}': {result.get('error', 'Unknown error')}"
                                        )
                            with col_cancel:
                                if st.button(
                                    ":material/cancel:",
                                    key=f"btn_cancel_delete_{p_id}",
                                    use_container_width=True,
                                    help="Cancel",
                                ):
                                    st.session_state.pop(
                                        "delete_confirmation_project", None
                                    )
                                    st.rerun()
