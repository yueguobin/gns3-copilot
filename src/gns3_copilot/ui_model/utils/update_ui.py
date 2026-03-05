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
Update Management UI Module for GNS3 Copilot.

This module provides Streamlit UI functions for checking, displaying, and
managing application updates. It handles both startup update checks and
manual update requests from the Settings page.

Key Functions:
    check_startup_updates(): Check for updates when application starts
    check_and_display_updates(): Perform update check and store result in session state
    render_startup_update_result(): Display update check result in sidebar/main area
    render_update_settings(): Render update configuration UI in Settings page
    check_and_prompt_update(): Check for updates and prompt user to update
    perform_update(): Execute the update process with progress feedback

Internal Functions:
    _load_startup_setting(): Load the check_updates_on_startup setting from config file
    perform_update_check(): Perform the actual update check synchronously
    load_settings(): Load settings from the settings file
    save_settings(): Save settings to the settings file

Configuration:
    SETTINGS_FILE: Path to settings.json file (~/.config/gns3-copilot/settings.json)

Session State Keys:
    - startup_update_checked: Flag to prevent duplicate checks in same session
    - startup_update_result: Dict containing update check result
    - check_updates: Flag to trigger manual update check
    - updating: Flag indicating update is in progress
    - dismiss_update: Flag to suppress update prompts until next session

Example:
    Check for updates on startup (in app.py):
        from gns3_copilot.ui_model.utils import (
            check_startup_updates,
            render_startup_update_result,
        )

        # At the beginning of app.py
        check_startup_updates()
        render_startup_update_result()

    Render update settings (in settings.py):
        from gns3_copilot.ui_model.utils import render_update_settings

        render_update_settings()
"""

import json
from pathlib import Path
from typing import Any

import streamlit as st

from gns3_copilot.ui_model.utils.updater import (
    is_update_available,
    load_skipped_version,
    run_update,
    save_skipped_version,
)

SETTINGS_FILE = Path.home() / ".config" / "gns3-copilot" / "settings.json"


def _load_startup_setting() -> bool:
    """Load the check_updates_on_startup setting from config file."""
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text())
            return bool(data.get("check_updates_on_startup"))
        except Exception:
            return False
    return False


def perform_update_check() -> dict[str, str]:
    """Perform the actual update check synchronously."""
    try:
        available, current, latest = is_update_available()
        if available:
            return {"status": "available", "current": current, "latest": latest}
        else:
            return {"status": "up_to_date", "current": current, "latest": latest}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_and_display_updates() -> None:
    """Check for updates and display results - runs once on startup."""
    if not _load_startup_setting():
        return

    # Skip if already checked in this session
    if "startup_update_checked" in st.session_state:
        return

    # Initialize skipped_update_version in session state
    if "skipped_update_version" not in st.session_state:
        st.session_state["skipped_update_version"] = load_skipped_version()

    # Mark as checked immediately to prevent re-running
    st.session_state["startup_update_checked"] = True

    # Perform the check with a spinner
    with st.spinner("Checking for updates..."):
        result = perform_update_check()
        st.session_state["startup_update_result"] = result

    # Force a rerun to display the result
    st.rerun()


def render_startup_update_result() -> None:
    """Display the startup update check result if available."""
    result = st.session_state.get("startup_update_result")

    if not result:
        return

    status = result.get("status")

    # Update available
    if status == "available":
        latest = result["latest"]

        # Session dismiss
        if st.session_state.get("_update_dismissed"):
            return

        # Persistent skip
        skipped_version = st.session_state.get("skipped_update_version")
        if skipped_version == latest:
            return

        # Render warning FIRST
        st.warning(
            f"⚠️ **Update available:** {result['current']} → {latest}\n\n"
            "Go to **Settings → GNS3 Copilot Updates** to update."
        )

        # Render actions BELOW the warning
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Dismiss", key="dismiss_update"):
                st.session_state["_update_dismissed"] = True
                st.rerun()

        with col2:
            if st.button("Skip this version", key="skip_update"):
                st.session_state["skipped_update_version"] = latest
                save_skipped_version(latest)
                st.rerun()

    # Up to date
    elif status == "up_to_date":
        if st.session_state.get("_up_to_date_dismissed"):
            return

        st.success(f"✅ You're using the latest version ({result['current']})")

        if st.button("Dismiss", key="dismiss_uptodate"):
            st.session_state["_up_to_date_dismissed"] = True
            st.rerun()

    # Error encountered
    elif status == "error":
        if st.session_state.get("_error_dismissed"):
            return

        st.error(f"❌ Update check failed: {result.get('error', 'Unknown error')}")

        if st.button("Dismiss", key="dismiss_error"):
            st.session_state["_error_dismissed"] = True
            st.rerun()


def check_startup_updates() -> None:
    """Check for updates on startup and display results."""
    check_and_display_updates()


def render_update_settings() -> None:
    """Render the update settings section in Settings page."""
    settings = load_settings()
    current_value = settings.get("check_updates_on_startup", False)
    check_on_startup = st.checkbox(
        "Check for updates on startup",
        value=current_value,
    )
    if check_on_startup != current_value:
        settings["check_updates_on_startup"] = check_on_startup
        save_settings(settings)

    if st.button("Check now for updates"):
        st.session_state.pop("dismiss_update", None)
        st.session_state["check_updates"] = True

    # Always check if we should run the update check/prompt
    if st.session_state.get("check_updates") or st.session_state.get("updating"):
        check_and_prompt_update()


def check_and_prompt_update() -> None:
    """Check for updates and prompt the user to update."""
    if st.session_state.get("dismiss_update"):
        st.session_state.pop("check_updates", None)
        return

    # Check if update is in progress
    if st.session_state.get("updating"):
        perform_update()
        st.session_state["updating"] = False
        st.session_state["dismiss_update"] = True
        st.session_state.pop("check_updates", None)
        return

    with st.spinner("Checking for updates..."):
        try:
            available, current, latest = is_update_available()
        except Exception:
            st.error(
                "Unable to check for updates. Please check your internet connection."
            )
            st.session_state.pop("check_updates", None)
            return

    if not available:
        st.info(f"You are running the latest version ({current}).")
        st.session_state.pop("check_updates", None)
        return

    st.warning("Update available")
    st.markdown(
        f"""
        **Current version:** {current}
        **Latest version:** {latest}
        Do you want to update to version **{latest}**?
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update", type="primary", key="update_btn"):
            st.session_state["updating"] = True
            st.rerun()
    with col2:
        if st.button("Cancel", key="cancel_btn"):
            st.session_state["dismiss_update"] = True
            st.session_state.pop("check_updates", None)
            st.rerun()


def perform_update() -> None:
    """Perform the actual update."""
    with st.spinner("Updating GNS3 Copilot..."):
        success, message = run_update()

    if success:
        st.success(message)
        st.warning("⚠️ **Please restart the application to use the new version.**")
        st.markdown("""
        **To restart:**
        1. Close this browser tab
        2. Stop the Streamlit process (Ctrl+C in terminal)
        3. Run `gns3-copilot` again
        """)
    else:
        st.error(message)


def load_settings() -> dict[Any, Any]:
    """Load settings from the settings file."""
    if SETTINGS_FILE.exists():
        try:
            result = json.loads(SETTINGS_FILE.read_text())
            return result if isinstance(result, dict) else {}
        except Exception:
            return {}
    return {}


def save_settings(settings: dict[Any, Any]) -> None:
    """Save settings to the settings file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))
