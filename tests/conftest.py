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
Pytest configuration and fixtures for GNS3 Copilot test suite.
"""

import os
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_env():
    """
    Fixture that sets up mock environment variables for testing.
    
    This fixture is automatically applied to all tests via pytest.ini's usefixtures.
    It provides a consistent environment for tests that require environment variables.
    
    Environment variables set:
    - API_VERSION: GNS3 API version (defaults to "2")
    - GNS3_SERVER_URL: GNS3 server URL (defaults to "http://localhost:3080")
    """
    mock_env_vars = {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080",
    }
    
    with patch.dict(os.environ, mock_env_vars, clear=False):
        yield mock_env_vars


@pytest.fixture
def mock_gns3_v2_env():
    """
    Fixture that sets up mock GNS3 v2 environment variables.
    """
    mock_env_vars = {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080",
    }
    
    with patch.dict(os.environ, mock_env_vars, clear=False):
        yield mock_env_vars


@pytest.fixture
def mock_gns3_v3_env():
    """
    Fixture that sets up mock GNS3 v3 environment variables with authentication.
    """
    mock_env_vars = {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_USERNAME": "admin",
        "GNS3_PASSWORD": "password",
    }
    
    with patch.dict(os.environ, mock_env_vars, clear=False):
        yield mock_env_vars
