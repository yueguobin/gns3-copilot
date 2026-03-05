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
Comprehensive test suite for gns3_project_update module
Tests GNS3ProjectUpdate tool which updates existing GNS3 projects

Test Coverage:
1. TestGNS3ProjectUpdateBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectUpdateSuccess
   - Successful project update with v2 API
   - Successful project update with v3 API
   - Return value validation
   - Optional parameters handling
   - Updated fields tracking

3. TestGNS3ProjectUpdateInputValidation
   - Missing tool_input
   - Missing both project_id and name
   - No update parameters provided
   - Valid project_id and name combinations

4. TestGNS3ProjectUpdateEnvironmentValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Invalid API_VERSION

5. TestGNS3ProjectUpdateOperations
   - Project update with auto control options
   - Project update with scene settings
   - Project update with display options
   - Project get method called correctly
   - Project ID and name lookup

6. TestGNS3ProjectUpdateErrorHandling
   - Network connection errors
   - GNS3 server errors
   - Project not found errors
   - Exception handling and logging

7. TestGNS3ProjectUpdateReturnFormat
   - Success response format
   - Error response format
   - Project details in response
   - Updated fields in response
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

# Import module to test
from gns3_copilot.gns3_client import GNS3ProjectUpdate


class TestGNS3ProjectUpdateBasic:
    """Basic tests for GNS3ProjectUpdate tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectUpdate()
        
        assert tool.name == "update_gns3_project"
        assert tool is not None

    def test_tool_name(self):
        """Test tool name"""
        tool = GNS3ProjectUpdate()
        assert tool.name == "update_gns3_project"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectUpdate()
        
        description = tool.description
        assert "update" in description.lower()
        assert "project" in description.lower()
        assert "required" in description.lower()
        assert "auto_start" in description.lower()
        assert "auto_close" in description.lower()
        assert "auto_open" in description.lower()
        assert "project_id" in description.lower()
        assert "name" in description.lower()


class TestGNS3ProjectUpdateSuccess:
    """Tests for successful project update operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_success_v2_api(self, mock_get_connector, mock_project_class):
        """Test successful project update with v2 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/project"
        mock_project.auto_start = False
        mock_project.auto_close = False
        mock_project.auto_open = False
        mock_project.scene_width = 2000
        mock_project.scene_height = 1000
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "project1",
            "auto_start": True
        })
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project1"
        assert result["project"]["name"] == "test_project"
        assert result["project"]["status"] == "opened"
        assert result["project"]["auto_start"] is True
        assert "auto_start" in result["updated_fields"]
        assert "updated successfully" in result["message"]
        mock_project.get.assert_called_once()
        mock_project.update.assert_called_once_with(auto_start=True)

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "testuser",
        "GNS3_SERVER_PASSWORD": "testpass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_success_v3_api(self, mock_get_connector, mock_project_class):
        """Test successful project update with v3 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v3"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project2"
        mock_project.name = "v3_project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/v3_project"
        mock_project.auto_start = False
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "project2",
            "auto_start": True
        })
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project2"
        assert result["project"]["name"] == "v3_project"
        assert result["project"]["auto_start"] is True

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_return_value_validation(self, mock_get_connector, mock_project_class):
        """Test return value structure is correct"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        # Verify response structure
        assert "success" in result
        assert "project" in result
        assert "updated_fields" in result
        assert "message" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["project"], dict)
        assert isinstance(result["updated_fields"], list)
        assert isinstance(result["message"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_with_multiple_parameters(self, mock_get_connector, mock_project_class):
        """Test project update with multiple parameters"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test_project"
        mock_project.auto_start = False
        mock_project.auto_close = False
        mock_project.auto_open = False
        mock_project.scene_width = 2000
        mock_project.scene_height = 1000
        mock_project.show_grid = False
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "project1",
            "auto_start": True,
            "auto_close": True,
            "auto_open": False,
            "scene_width": 3000,
            "show_grid": True
        })
        
        assert result["success"] is True
        mock_project.update.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_updated_fields_tracking(self, mock_get_connector, mock_project_class):
        """Test that updated fields are tracked correctly"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.auto_close = False
        mock_project.scene_width = 2000
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "test_id",
            "auto_start": True,
            "auto_close": True
        })
        
        assert result["success"] is True
        assert "auto_start" in result["updated_fields"]
        assert "auto_close" in result["updated_fields"]
        assert len(result["updated_fields"]) == 2

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_update_by_name(self, mock_get_connector, mock_project_class):
        """Test project update by name instead of project_id"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test_project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test_project"
        mock_project.auto_start = False
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "name": "test_project",
            "auto_start": True
        })
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "test_id"
        assert result["project"]["name"] == "test_project"


class TestGNS3ProjectUpdateInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter"""
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input=None)
        
        assert result["success"] is False
        assert "error" in result
        assert "No input provided" in result["error"]

    def test_missing_project_identifier(self):
        """Test missing both project_id and name"""
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"auto_start": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "project_id" in result["error"] or "name" in result["error"]

    def test_no_update_parameters(self):
        """Test no update parameters provided"""
        @patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        })
        def _test():
            tool = GNS3ProjectUpdate()
            result = tool._run(tool_input={"project_id": "test_id"})
            
            assert result["success"] is False
            assert "error" in result
            assert "No update parameters provided" in result["error"]
        
        _test()

    def test_valid_project_id_only(self):
        """Test valid project_id without name"""
        @patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        })
        @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
        @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
        def _test(mock_get_connector, mock_project_class):
            # Mock connector
            mock_connector = Mock()
            mock_connector.base_url = "http://localhost:3080/v2"
            mock_get_connector.return_value = mock_connector
            
            # Mock project
            mock_project = Mock()
            mock_project.project_id = "test_id"
            mock_project.name = "test"
            mock_project.status = "opened"
            mock_project.path = "/path/to/test"
            mock_project.auto_start = False
            
            # Make update() actually modify the mock's attributes
            def update_side_effect(**kwargs):
                for key, value in kwargs.items():
                    setattr(mock_project, key, value)
            
            mock_project.update.side_effect = update_side_effect
            mock_project_class.return_value = mock_project
            
            tool = GNS3ProjectUpdate()
            result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
            
            assert result["success"] is True
        
        _test()

    def test_valid_name_only(self):
        """Test valid name without project_id"""
        @patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        })
        @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
        @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
        def _test(mock_get_connector, mock_project_class):
            # Mock connector
            mock_connector = Mock()
            mock_connector.base_url = "http://localhost:3080/v2"
            mock_get_connector.return_value = mock_connector
            
            # Mock project
            mock_project = Mock()
            mock_project.project_id = "test_id"
            mock_project.name = "test_project"
            mock_project.status = "opened"
            mock_project.path = "/path/to/test"
            mock_project.auto_start = False
            
            # Make update() actually modify the mock's attributes
            def update_side_effect(**kwargs):
                for key, value in kwargs.items():
                    setattr(mock_project, key, value)
            
            mock_project.update.side_effect = update_side_effect
            mock_project_class.return_value = mock_project
            
            tool = GNS3ProjectUpdate()
            result = tool._run(tool_input={"name": "test_project", "auto_start": True})
            
            assert result["success"] is True
        
        _test()

    def test_none_values_filtered_out(self):
        """Test that None values are filtered from update parameters"""
        @patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        })
        @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
        @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
        def _test(mock_get_connector, mock_project_class):
            # Mock connector
            mock_connector = Mock()
            mock_connector.base_url = "http://localhost:3080/v2"
            mock_get_connector.return_value = mock_connector
            
            # Mock project
            mock_project = Mock()
            mock_project.project_id = "test_id"
            mock_project.name = "test"
            mock_project.status = "opened"
            mock_project.path = "/path/to/test"
            mock_project.auto_start = False
            
            # Make update() actually modify the mock's attributes
            def update_side_effect(**kwargs):
                for key, value in kwargs.items():
                    setattr(mock_project, key, value)
            
            mock_project.update.side_effect = update_side_effect
            mock_project_class.return_value = mock_project
            
            tool = GNS3ProjectUpdate()
            result = tool._run(tool_input={
                "project_id": "test_id",
                "auto_start": True,
                "auto_close": None,
                "auto_open": None
            })
            
            assert result["success"] is True
            # Verify update was called with only non-None parameters
            mock_project.update.assert_called_once_with(auto_start=True)
        
        _test()


class TestGNS3ProjectUpdateEnvironmentValidation:
    """Tests for environment variable validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION environment variable"""
        tool = GNS3ProjectUpdate()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3ProjectUpdate()
        
        def mock_get_config(key, default=None):
            config = {"API_VERSION": "2"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        tool = GNS3ProjectUpdate()
        
        def mock_get_config(key, default=None):
            config = {"API_VERSION": "invalid", "GNS3_SERVER_URL": "http://localhost:3080"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_valid_api_version_2(self, mock_get_connector, mock_project_class):
        """Test valid API_VERSION value (2)"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        assert "success" in result

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_valid_api_version_3(self, mock_get_connector, mock_project_class):
        """Test valid API_VERSION value (3)"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v3"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        assert "success" in result


class TestGNS3ProjectUpdateOperations:
    """Tests for project-specific operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_project_get_called(self, mock_get_connector, mock_project_class):
        """Test that project.get() is called to retrieve current state"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        tool._run(tool_input={"project_id": "test_project", "auto_start": True})
        
        # Verify get was called
        mock_project.get.assert_called_once_with(
            get_nodes=False,
            get_links=False,
            get_stats=False
        )

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_project_update_called(self, mock_get_connector, mock_project_class):
        """Test that project.update() is called with correct parameters"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.auto_close = False
        mock_project.auto_open = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        tool._run(tool_input={
            "project_id": "test_project",
            "auto_start": True,
            "auto_close": True
        })
        
        # Verify update was called with correct parameters
        mock_project.update.assert_called_once_with(auto_start=True, auto_close=True)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_auto_control_options_update(self, mock_get_connector, mock_project_class):
        """Test updating auto control options"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.auto_close = False
        mock_project.auto_open = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "test_id",
            "auto_start": True,
            "auto_close": False,
            "auto_open": True
        })
        
        assert result["success"] is True
        mock_project.update.assert_called_once_with(
            auto_start=True,
            auto_close=False,
            auto_open=True
        )

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_scene_settings_update(self, mock_get_connector, mock_project_class):
        """Test updating scene settings"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.scene_width = 2000
        mock_project.scene_height = 1000
        mock_project.grid_size = 75
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "test_id",
            "scene_width": 3000,
            "scene_height": 2000,
            "grid_size": 100
        })
        
        assert result["success"] is True
        mock_project.update.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_display_options_update(self, mock_get_connector, mock_project_class):
        """Test updating display options"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.show_grid = False
        mock_project.show_interface_labels = False
        mock_project.show_layers = False
        mock_project.snap_to_grid = False
        mock_project.zoom = 0
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "test_id",
            "show_grid": True,
            "show_interface_labels": True,
            "show_layers": True,
            "snap_to_grid": True,
            "zoom": 1
        })
        
        assert result["success"] is True
        mock_project.update.assert_called_once()


class TestGNS3ProjectUpdateErrorHandling:
    """Tests for error handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_network_connection_error(self, mock_get_connector, mock_project_class):
        """Test handling of network connection errors"""
        # Mock connector to return None
        mock_get_connector.return_value = None
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_project_not_found_by_id(self, mock_get_connector, mock_project_class):
        """Test handling when project not found by project_id"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project with no project_id (not found)
        mock_project = Mock()
        mock_project.project_id = None
        mock_project.name = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "nonexistent_id", "auto_start": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_project_not_found_by_name(self, mock_get_connector, mock_project_class):
        """Test handling when project not found by name"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project with no project_id (not found)
        mock_project = Mock()
        mock_project.project_id = None
        mock_project.name = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"name": "nonexistent_name", "auto_start": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_project_update_server_error(self, mock_get_connector, mock_project_class):
        """Test handling of project update server error"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise error on update
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.update.side_effect = Exception("Server error")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_value_error_handling(self, mock_get_connector, mock_project_class):
        """Test handling of ValueError"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise ValueError
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.update.side_effect = ValueError("Invalid parameter")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_timeout_error(self, mock_get_connector, mock_project_class):
        """Test handling of timeout errors"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise TimeoutError
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.update.side_effect = TimeoutError("Request timeout")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        assert result["success"] is False
        assert "error" in result


class TestGNS3ProjectUpdateReturnFormat:
    """Tests for return format validation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_success_response_format(self, mock_get_connector, mock_project_class):
        """Test success response has correct format"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
        
        # Verify all required fields
        assert "success" in result
        assert "project" in result
        assert "updated_fields" in result
        assert "message" in result
        assert result["success"] is True
        
        # Verify project fields
        assert "project_id" in result["project"]
        assert "name" in result["project"]
        assert "status" in result["project"]
        assert "path" in result["project"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_error_response_format(self):
        """Test error response has correct format"""
        tool = GNS3ProjectUpdate()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id", "auto_start": True})
            
            # Verify error format
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert isinstance(result["error"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_project_details_in_response(self, mock_get_connector, mock_project_class):
        """Test that project details are included in response"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project123"
        mock_project.name = "My Lab"
        mock_project.status = "opened"
        mock_project.path = "/home/gns3/gns3/projects/My Lab"
        mock_project.auto_start = True
        mock_project.auto_close = False
        mock_project.auto_open = False
        mock_project.scene_width = 2000
        mock_project.show_grid = True
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "project123",
            "auto_start": True,
            "scene_width": 2000,
            "show_grid": True
        })
        
        # Verify project details
        assert result["project"]["project_id"] == "project123"
        assert result["project"]["name"] == "My Lab"
        assert result["project"]["status"] == "opened"
        assert result["project"]["path"] == "/home/gns3/gns3/projects/My Lab"
        assert result["project"]["auto_start"] is True
        assert result["project"]["scene_width"] == 2000
        assert result["project"]["show_grid"] is True

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_updated_fields_in_response(self, mock_get_connector, mock_project_class):
        """Test that updated fields are correctly reported"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        mock_project.auto_close = False
        mock_project.auto_open = False
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "test_id",
            "auto_start": True,
            "auto_close": True,
            "auto_open": False
        })
        
        # Verify updated fields
        assert isinstance(result["updated_fields"], list)
        assert "auto_start" in result["updated_fields"]
        assert "auto_close" in result["updated_fields"]
        # auto_open should not be in updated_fields since it was False before and False after
        assert "auto_open" not in result["updated_fields"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_update.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_update.get_gns3_connector')
    def test_message_content(self, mock_get_connector, mock_project_class):
        """Test that message contains useful information"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project.auto_start = False
        
        # Make update() actually modify the mock's attributes
        def update_side_effect(**kwargs):
            for key, value in kwargs.items():
                setattr(mock_project, key, value)
        
        mock_project.update.side_effect = update_side_effect
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectUpdate()
        result = tool._run(tool_input={
            "project_id": "test_id",
            "auto_start": True
        })
        
        # Verify message contains project name
        assert "Test Project" in result["message"]
        assert "updated successfully" in result["message"]
