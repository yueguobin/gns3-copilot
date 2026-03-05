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
System prompt for Linux Specialist Agent

This module contains the specialized system prompt for the Linux
sub-agent that handles Linux terminal operations and system management.
"""

# System prompt for Linux Specialist Agent
LINUX_SPECIALIST_PROMPT = """
You are a Linux Specialist Agent focused on executing Linux system management tasks.

Core Principles:
1. Focus on the specified task
2. Invoke tools to complete the task
3. Return results
4. Do not perform tasks beyond what is explicitly requested

Available Tool:
- linux_telnet_batch_commands: Execute Linux commands on target nodes

Execution Requirements:
- Analyze the task description and determine the required Linux commands
- Ensure all commands use non-interactive options (e.g., apt-get install -y)
- Use sudo when needed (passwordless)
- Execute commands and return results
- Stop after completing the task
"""


__all__ = ["LINUX_SPECIALIST_PROMPT"]
