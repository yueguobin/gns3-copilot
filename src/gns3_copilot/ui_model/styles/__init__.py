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

"""CSS styles management module."""

from pathlib import Path


def get_styles() -> str:
    """Read and return all CSS styles wrapped in style tags.

    Returns:
        str: CSS content from main.css file wrapped in <style> tags,
             or empty string if file doesn't exist.
    """
    css_file = Path(__file__).parent / "main.css"
    if css_file.exists():
        css_content = css_file.read_text(encoding="utf-8")
        return f"<style>{css_content}</style>"
    return ""
