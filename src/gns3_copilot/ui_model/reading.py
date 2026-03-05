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
Reading page for GNS3 Copilot application.

This module provides a reading interface with Calibre ebook viewer and
a multi-note management system for taking and organizing reading notes.

Features:
- Calibre ebook viewer embedded in iframe
- Multi-note management system (create, select, delete notes)
- Notes saved as Markdown files
- Download notes functionality
- Automatic notes directory creation
"""

import streamlit as st

from gns3_copilot.ui_model.utils.iframe_viewer import render_iframe_viewer
from gns3_copilot.ui_model.utils.notes_manager import (  # type: ignore[attr-defined]
    render_notes_editor,
)

# Page title
st.markdown(
    """
    <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>Reading and Think</h3>
    """,
    unsafe_allow_html=True,
)

# Create two columns: Calibre viewer (left) and Note manager (right)
calibre_col, notes_col = st.columns([1, 1])

# ===== Left Column: Calibre Viewer =====
with calibre_col:
    render_iframe_viewer()

# ===== Right Column: Note Manager =====
with notes_col:
    render_notes_editor()
