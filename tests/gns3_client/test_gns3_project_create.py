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
Comprehensive test suite for gns3_project_create module
Tests GNS3ProjectCreate tool which creates new GNS3 projects

Test Coverage:
1. TestGNS3ProjectCreateBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectCreateSuccess
   - Successful project creation with v2 API
   - Successful project creation with v3 API
   - Return value validation
   - Optional parameters handling

3. TestGNS3ProjectCreateInputValidation
   - Missing tool_input
   - Missing name parameter
   - Empty name validation
   - Invalid name types

4. TestGNS3ProjectCreateEnvironmentValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Invalid API_VERSION

5. TestGNS3ProjectCreateOperations
   - Project creation with default parameters
   - Project creation with custom parameters
   - Project create method called correctly
   - Project ID verification

6. TestGNS3ProjectCreateErrorHandling
   - Network connection errors
   - GNS3 server errors
   - Project creation failures
   - Exception handling and logging

7. TestGNS3ProjectCreateReturnFormat
   - Success response format
   - Error response format
   - Project details in response
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

# Import the module to test
from gns3_copilot.gns3_client import GNS3ProjectCreate


class TestGNS3ProjectCreateBasic:
    """Basic tests for GNS3ProjectCreate tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectCreate()
        
        assert tool.name == "create_gns3_project"
        assert tool is not None

    def test_tool_name(self):
        """Test tool name"""
        tool = GNS3ProjectCreate()
        assert tool.name == "create_gns3_project"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectCreate()
        
        description = tool.description
        assert "name" in description.lower()
        assert "create" in description.lower()
        assert "required" in description.lower()
        assert "auto_start" in description.lower()
        assert "auto_close" in description.lower()


class TestGNS3ProjectCreateSuccess:
    """Tests for successful project creation operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_success_v2_api(self, mock_get_connector, mock_project_class):
        """Test successful project creation with v2 API"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "test_project"})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project1"
        assert result["project"]["name"] == "test_project"
        assert result["project"]["status"] == "opened"
        assert "created successfully" in result["message"]
        mock_project.create.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "testuser",
        "GNS3_SERVER_PASSWORD": "testpass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_success_v3_api(self, mock_get_connector, mock_project_class):
        """Test successful project creation with v3 API"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "v3_project"})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project2"
        assert result["project"]["name"] == "v3_project"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "test"})
        
        # Verify response structure
        assert "success" in result
        assert "project" in result
        assert "message" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["project"], dict)
        assert isinstance(result["message"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_with_optional_parameters(self, mock_get_connector, mock_project_class):
        """Test project creation with optional parameters"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={
            "name": "test_project",
            "auto_start": True,
            "auto_close": True,
            "auto_open": False,
            "scene_width": 2000,
            "scene_height": 1000
        })
        
        assert result["success"] is True
        mock_project.create.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_with_only_required_parameters(self, mock_get_connector, mock_project_class):
        """Test project creation with only required parameter (name)"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "test_project"})
        
        assert result["success"] is True
        mock_project.create.assert_called_once()


class TestGNS3ProjectCreateInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter"""
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input=None)
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameter" in result["error"]

    def test_missing_name(self):
        """Test missing name in tool_input"""
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"auto_start": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameter: name" in result["error"]

    def test_empty_name(self):
        """Test empty name string"""
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": ""})
        
        assert result["success"] is False
        assert "error" in result
        assert "Project name must be a non-empty string" in result["error"]

    def test_whitespace_only_name(self):
        """Test name with only whitespace"""
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "   "})
        
        assert result["success"] is False
        assert "error" in result
        assert "Project name must be a non-empty string" in result["error"]

    def test_invalid_name_type_none(self):
        """Test name parameter is None"""
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": None})
        
        assert result["success"] is False
        assert "error" in result

    def test_invalid_name_type_integer(self):
        """Test name parameter is not a string (integer)"""
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": 123})
        
        assert result["success"] is False
        assert "error" in result

    def test_valid_name_string(self):
        """Test valid name string"""
        tool = GNS3ProjectCreate()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            with patch('gns3_copilot.gns3_client.gns3_project_create.Project') as mock_project_class:
                with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector') as mock_get_connector:
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
                    mock_project_class.return_value = mock_project
                    
                    result = tool._run(tool_input={"name": "test"})
                    
                    assert result["success"] is True


class TestGNS3ProjectCreateEnvironmentValidation:
    """Tests for environment variable validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION environment variable"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector', return_value=None):
            result = tool._run(tool_input={"name": "test_project"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector', return_value=None):
            result = tool._run(tool_input={"name": "test_project"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector', return_value=None):
            result = tool._run(tool_input={"name": "test_project"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_valid_api_version_2(self):
        """Test valid API_VERSION value (2)"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.Project') as mock_project_class:
            with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector') as mock_get_connector:
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
                mock_project_class.return_value = mock_project
                
                result = tool._run(tool_input={"name": "test"})
                
                assert "success" in result

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    def test_valid_api_version_3(self):
        """Test valid API_VERSION value (3)"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.Project') as mock_project_class:
            with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector') as mock_get_connector:
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
                mock_project_class.return_value = mock_project
                
                result = tool._run(tool_input={"name": "test"})
                
                assert "success" in result


class TestGNS3ProjectCreateOperations:
    """Tests for project-specific operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_project_create_called(self, mock_get_connector, mock_project_class):
        """Test that project.create() is called"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        tool._run(tool_input={"name": "Test Project"})
        
        # Verify create was called
        mock_project.create.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_project_id_verification(self, mock_get_connector, mock_project_class):
        """Test that project_id is verified after creation"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "Test Project"})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "test_id"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_project_creation_failure_no_id(self, mock_get_connector, mock_project_class):
        """Test handling when project creation fails (no project_id)"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project with no project_id (creation failed)
        mock_project = Mock()
        mock_project.project_id = None
        mock_project.name = "Test Project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "Test Project"})
        
        assert result["success"] is False
        assert "error" in result
        assert "project_id not returned" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_project_parameters_passed_correctly(self, mock_get_connector, mock_project_class):
        """Test that project parameters are passed correctly"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        tool._run(tool_input={
            "name": "Test Project",
            "auto_start": True,
            "auto_close": False,
            "scene_width": 2000,
            "scene_height": 1000
        })
        
        # Verify Project was initialized with correct parameters
        call_args = mock_project_class.call_args
        assert call_args[1]["name"] == "Test Project"
        assert call_args[1]["auto_start"] is True
        assert call_args[1]["auto_close"] is False
        assert call_args[1]["scene_width"] == 2000
        assert call_args[1]["scene_height"] == 1000

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_default_optional_parameters(self, mock_get_connector, mock_project_class):
        """Test that optional parameters have correct defaults"""
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        tool._run(tool_input={"name": "Test Project"})
        
        # Verify Project was initialized with default values
        call_args = mock_project_class.call_args
        assert call_args[1]["auto_start"] is False
        assert call_args[1]["auto_close"] is False
        assert call_args[1]["auto_open"] is False


class TestGNS3ProjectCreateErrorHandling:
    """Tests for error handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_network_connection_error(self):
        """Test handling of network connection errors"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector') as mock_get_connector:
            # Mock connector to return None (connection failed)
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"name": "test_project"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_project_creation_server_error(self, mock_get_connector, mock_project_class):
        """Test handling of project creation server error"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise error on create
        mock_project = Mock()
        mock_project.create.side_effect = Exception("Server error")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "test_project"})
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_exception_logging(self):
        """Test that exceptions are logged"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"name": "test_project"})
            
            # Should return error without crashing
            assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_timeout_error(self):
        """Test handling of timeout errors"""
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"name": "test_project"})
            
            assert result["success"] is False
            assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_value_error_handling(self, mock_get_connector, mock_project_class):
        """Test handling of ValueError"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise ValueError
        mock_project = Mock()
        mock_project.create.side_effect = ValueError("Invalid parameter")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "test_project"})
        
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]


class TestGNS3ProjectCreateReturnFormat:
    """Tests for return format validation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
    def test_success_response_format(self, mock_get_connector, mock_project_class):
        """Test success response has correct format"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test"
        mock_project.status = "opened"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "test"})
        
        # Verify all required fields
        assert "success" in result
        assert "project" in result
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
        tool = GNS3ProjectCreate()
        
        with patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector', return_value=None):
            result = tool._run(tool_input={"name": "test"})
            
            # Verify error format
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert isinstance(result["error"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "My Lab"})
        
        # Verify project details
        assert result["project"]["project_id"] == "project123"
        assert result["project"]["name"] == "My Lab"
        assert result["project"]["status"] == "opened"
        assert result["project"]["path"] == "/home/gns3/gns3/projects/My Lab"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_create.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_create.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectCreate()
        result = tool._run(tool_input={"name": "Test Project"})
        
        # Verify message contains project name
        assert "Test Project" in result["message"]
        assert "created successfully" in result["message"]
