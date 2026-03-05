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
Comprehensive test suite for gns3_project_delete module
Tests GNS3ProjectDelete tool which deletes GNS3 projects

Test Coverage:
1. TestGNS3ProjectDeleteBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectDeleteSuccess
   - Successful project deletion with v2 API (by project_id)
   - Successful project deletion with v2 API (by name)
   - Successful project deletion with v3 API
   - Return value validation
   - Project details captured before deletion

3. TestGNS3ProjectDeleteInputValidation
   - Missing tool_input
   - Missing both project_id and name
   - Empty input validation

4. TestGNS3ProjectDeleteEnvironmentValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Invalid API_VERSION

5. TestGNS3ProjectDeleteOperations
   - Project deletion by project_id
   - Project deletion by name
   - Project get and delete methods called correctly
   - Project details retrieval before deletion

6. TestGNS3ProjectDeleteErrorHandling
   - Project not found (by name)
   - Project not found (by project_id)
   - Network connection errors
   - GNS3 server errors
   - Exception handling and logging

7. TestGNS3ProjectDeleteReturnFormat
   - Success response format
   - Error response format
   - Project details in response
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

# Import module to test
from gns3_copilot.gns3_client.gns3_project_delete import GNS3ProjectDelete


class TestGNS3ProjectDeleteBasic:
    """Basic tests for GNS3ProjectDelete tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectDelete()
        
        assert tool.name == "delete_gns3_project"
        assert tool is not None

    def test_tool_name(self):
        """Test tool name"""
        tool = GNS3ProjectDelete()
        assert tool.name == "delete_gns3_project"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectDelete()
        
        description = tool.description
        assert "delete" in description.lower()
        assert "project_id" in description.lower()
        assert "required" in description.lower()
        assert "name" in description.lower()


class TestGNS3ProjectDeleteSuccess:
    """Tests for successful project deletion operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_success_v2_api_by_project_id(self, mock_get_connector, mock_project_class):
        """Test successful project deletion with v2 API by project_id"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.status = "closed"
        mock_project.path = "/path/to/project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "project1"})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project1"
        assert result["project"]["name"] == "test_project"
        assert result["project"]["status"] == "closed"
        assert "deleted successfully" in result["message"]
        mock_project.get.assert_called_once()
        mock_project.delete.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_success_v2_api_by_name(self, mock_get_connector, mock_project_class):
        """Test successful project deletion with v2 API by name"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project2"
        mock_project.name = "my_project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/my_project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"name": "my_project"})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project2"
        assert result["project"]["name"] == "my_project"
        assert result["project"]["status"] == "opened"
        mock_project.get.assert_called_once()
        mock_project.delete.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "testuser",
        "GNS3_SERVER_PASSWORD": "testpass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_success_v3_api(self, mock_get_connector, mock_project_class):
        """Test successful project deletion with v3 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v3"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project3"
        mock_project.name = "v3_project"
        mock_project.status = "closed"
        mock_project.path = "/path/to/v3_project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "project3"})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project3"
        assert result["project"]["name"] == "v3_project"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
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
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
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
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_details_captured_before_deletion(self, mock_get_connector, mock_project_class):
        """Test that project details are captured before deletion"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project.path = "/path/to/Test Project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
        # Verify project details are in response
        assert result["project"]["project_id"] == "test_id"
        assert result["project"]["name"] == "Test Project"
        assert result["project"]["status"] == "opened"
        assert result["project"]["path"] == "/path/to/Test Project"


class TestGNS3ProjectDeleteInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter"""
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input=None)
        
        assert result["success"] is False
        assert "error" in result
        assert "No input provided" in result["error"]

    def test_missing_both_identifiers(self):
        """Test missing both project_id and name - returns same as empty input"""
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={})
        
        # Empty dict is treated as "No input provided"
        assert result["success"] is False
        assert "error" in result
        assert "No input provided" in result["error"]

    def test_empty_input_dict(self):
        """Test empty input dictionary"""
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={})
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_valid_project_id_input(self, mock_get_connector, mock_project_class):
        """Test valid project_id input"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
        assert result["success"] is True

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_valid_name_input(self, mock_get_connector, mock_project_class):
        """Test valid name input"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "test"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"name": "test"})
        
        assert result["success"] is True


class TestGNS3ProjectDeleteEnvironmentValidation:
    """Tests for environment variable validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION environment variable"""
        tool = GNS3ProjectDelete()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3ProjectDelete()
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        tool = GNS3ProjectDelete()
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "invalid",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]


class TestGNS3ProjectDeleteOperations:
    """Tests for project-specific operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_get_called(self, mock_get_connector, mock_project_class):
        """Test that project.get() is called before deletion"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        tool._run(tool_input={"project_id": "test_id"})
        
        # Verify get was called
        mock_project.get.assert_called_once_with(
            get_nodes=False, get_links=False, get_stats=False
        )

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_delete_called(self, mock_get_connector, mock_project_class):
        """Test that project.delete() is called"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        tool._run(tool_input={"project_id": "test_id"})
        
        # Verify delete was called
        mock_project.delete.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_initialized_with_id(self, mock_get_connector, mock_project_class):
        """Test that Project is initialized with project_id"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        tool._run(tool_input={"project_id": "test_id"})
        
        # Verify Project was initialized with project_id
        call_args = mock_project_class.call_args
        assert call_args[1]["project_id"] == "test_id"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_initialized_with_name(self, mock_get_connector, mock_project_class):
        """Test that Project is initialized with name"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        tool._run(tool_input={"name": "Test Project"})
        
        # Verify Project was initialized with name
        call_args = mock_project_class.call_args
        assert call_args[1]["name"] == "Test Project"


class TestGNS3ProjectDeleteErrorHandling:
    """Tests for error handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_not_found_by_name(self, mock_get_connector, mock_project_class):
        """Test project not found by name"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project with no project_id (not found)
        mock_project = Mock()
        mock_project.project_id = None
        mock_project.name = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"name": "nonexistent_project"})
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_not_found_by_id(self, mock_get_connector, mock_project_class):
        """Test project not found by project_id"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project with no project_id (not found)
        mock_project = Mock()
        mock_project.project_id = None
        mock_project.name = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "nonexistent_id"})
        
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_network_connection_error(self):
        """Test handling of network connection errors"""
        tool = GNS3ProjectDelete()
        
        with patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector') as mock_get_connector:
            # Mock connector to return None (connection failed)
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "test_id"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_project_delete_server_error(self, mock_get_connector, mock_project_class):
        """Test handling of project deletion server error"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise error on delete
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test"
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project.delete.side_effect = Exception("Server error")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
    def test_value_error_handling(self, mock_get_connector, mock_project_class):
        """Test handling of ValueError"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise ValueError
        mock_project = Mock()
        mock_project.get.side_effect = ValueError("Invalid parameter")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]


class TestGNS3ProjectDeleteReturnFormat:
    """Tests for return format validation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
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
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
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

    def test_error_response_format(self):
        """Test error response has correct format"""
        tool = GNS3ProjectDelete()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id"})
            
            # Verify error format
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert isinstance(result["error"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
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
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "project123"})
        
        # Verify project details
        assert result["project"]["project_id"] == "project123"
        assert result["project"]["name"] == "My Lab"
        assert result["project"]["status"] == "opened"
        assert result["project"]["path"] == "/home/gns3/gns3/projects/My Lab"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_delete.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_delete.get_gns3_connector')
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
        mock_project.status = "closed"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectDelete()
        result = tool._run(tool_input={"project_id": "test_id"})
        
        # Verify message contains project name
        assert "Test Project" in result["message"]
        assert "deleted successfully" in result["message"]
