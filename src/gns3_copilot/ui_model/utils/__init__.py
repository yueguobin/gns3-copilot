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
Utility modules for Streamlit UI Model in GNS3 Copilot.

This package provides utility functions and helpers that support the Streamlit
user interface components. It includes modules for configuration management,
GNS3 server connectivity checking, update management, and general UI rendering.

Modules:
    app_ui: General UI rendering functions (sidebar, about page)
    chat_helpers: Chat session management helper functions
    config_manager: Configuration loading and persistence to .env files
    gns3_checker: GNS3 server API connectivity validation
    project_manager_ui: Project management UI components (create, select projects)
    update_ui: Application update checking and UI components
    updater: Core update logic (version checking, update execution)

Key Functions:
    - check_startup_updates(): Perform startup update checks
    - check_and_display_updates(): Check for updates and display results
    - render_startup_update_result(): Display update check results
    - render_update_settings(): Render update configuration UI
    - load_config_from_env(): Load configuration from .env file
    - save_config_to_env(): Save configuration to .env file
    - check_gns3_api(): Validate GNS3 server connectivity
    - new_session(): Create a new chat session with unique thread ID
    - render_sidebar_about(): Render sidebar about information

Example:
    Import utility functions in UI modules:
        from gns3_copilot.ui_model.utils import (
            check_gns3_api,
            load_config_from_env,
            render_update_settings,
        )
"""

from gns3_copilot.ui_model.utils.app_ui import (
    initialize_page_config,
    inject_chat_styles,
    render_sidebar_about,
)
from gns3_copilot.ui_model.utils.chat_helpers import (
    build_topology_iframe_url,
    generate_topology_iframe_html,
    new_session,
)
from gns3_copilot.ui_model.utils.config_manager import (
    init_app_config,
    load_config,
    save_config,
)
from gns3_copilot.ui_model.utils.gns3_checker import check_gns3_api
from gns3_copilot.ui_model.utils.iframe_viewer import (
    render_iframe_viewer,
)
from gns3_copilot.ui_model.utils.llm_providers import (
    get_all_providers,
    get_provider_config,
)
from gns3_copilot.ui_model.utils.notes_manager import (  # type: ignore[attr-defined]
    render_notes_editor,
)
from gns3_copilot.ui_model.utils.project_manager_ui import (
    render_create_project_form,
    render_project_cards,
)
from gns3_copilot.ui_model.utils.update_ui import (
    check_startup_updates,
    render_startup_update_result,
    render_update_settings,
)

__all__ = [
    # Iframe Viewer
    "render_iframe_viewer",
    # Notes Manager
    "render_notes_editor",
    # Update UI
    "check_startup_updates",
    "render_startup_update_result",
    "render_update_settings",
    # Config Manager
    "init_app_config",
    "load_config",
    "save_config",
    # GNS3 Checker
    "check_gns3_api",
    # LLM Providers
    "get_all_providers",
    "get_provider_config",
    # Chat Helpers
    "new_session",
    "build_topology_iframe_url",
    "generate_topology_iframe_html",
    # Project Manager UI
    "render_create_project_form",
    "render_project_cards",
    # App UI
    "render_sidebar_about",
    "initialize_page_config",
    "inject_chat_styles",
]

# Dynamic version management
try:
    from importlib.metadata import version

    __version__ = version("gns3-copilot")
except Exception:
    __version__ = "unknown"

__author__ = "Guobin Yue"
__description__ = "AI-powered network automation assistant for GNS3"
__url__ = "https://github.com/yueguobin/gns3-copilot"
