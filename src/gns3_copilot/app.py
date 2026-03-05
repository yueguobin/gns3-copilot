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
GNS3 Copilot Streamlit application entry point.

Main application module that initializes and runs the Streamlit-based web interface
with navigation between settings, chat, and help pages.
"""

import streamlit as st

from gns3_copilot.ui_model.sidebar import render_sidebar, render_sidebar_about
from gns3_copilot.ui_model.styles import get_styles
from gns3_copilot.ui_model.utils import (
    check_startup_updates,
    init_app_config,
    initialize_page_config,
    inject_chat_styles,
    load_config,
    render_startup_update_result,
)

NAV_PAGES = [
    "ui_model/reading.py",
    "ui_model/chat.py",
    "ui_model/settings.py",
    "ui_model/help.py",
]


def main() -> None:
    """Main application entry point."""
    # Initialize page configuration early to ensure consistent layout
    initialize_page_config()

    # Initialize configuration database with default values
    init_app_config()

    # Load configuration from database into session state
    # This ensures all pages have access to the configuration
    load_config()

    # Apply centralized CSS styles
    st.markdown(get_styles(), unsafe_allow_html=True)

    # Inject chat-specific styles
    inject_chat_styles()

    # Check for updates on startup (blocking, runs once)
    check_startup_updates()

    # Prevent the app from crashing if a page path is missing
    try:
        pg = st.navigation(NAV_PAGES, position="sidebar")

        # Render sidebar with current page information
        current_page = pg.script_path if hasattr(pg, "script_path") else ""
        selected_thread_id, title = render_sidebar(current_page=current_page)

        # Store selected thread ID and title in session state for chat page
        if selected_thread_id is not None:
            st.session_state["selected_thread_id"] = selected_thread_id
        if title is not None:
            st.session_state["session_title"] = title

        pg.run()
    except Exception as exc:
        st.error("Failed to initialize application navigation.")
        st.exception(exc)
        st.stop()

    # Display update result only on Settings page
    if hasattr(pg, "script_path") and pg.script_path == "ui_model/settings.py":
        render_startup_update_result()

    # Render sidebar about section
    render_sidebar_about()


if __name__ == "__main__":
    main()
