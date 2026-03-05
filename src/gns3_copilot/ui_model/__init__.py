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
Streamlit UI Model Package for GNS3 Copilot.

This package contains all Streamlit-based user interface modules for the GNS3 Copilot
application. It provides a comprehensive set of pages and utilities for managing the
entire user experience including chat interactions, settings management, and help
documentation.

Modules:
    chat: Main chat interface with AI-powered network engineering assistant
    settings: Configuration management page for GNS3, LLM, and voice settings
    help: Bilingual help documentation and configuration guide
    utils: Utility modules supporting UI functionality

The ui_model package is responsible for:
- User interface presentation and interaction
- Session state management across pages
- Settings configuration and persistence
- Help and documentation display

Example:
    The main application entry point (app.py) uses Streamlit navigation to load
    these pages dynamically:
        st.navigation([
            "ui_model/settings.py",
            "ui_model/chat.py",
            "ui_model/help.py",
        ])
"""

# Dynamic version management
try:
    from importlib.metadata import version

    __version__ = version("gns3-copilot")
except Exception:
    __version__ = "unknown"

__author__ = "Guobin Yue"
__description__ = "AI-powered network automation assistant for GNS3"
__url__ = "https://github.com/yueguobin/gns3-copilot"
