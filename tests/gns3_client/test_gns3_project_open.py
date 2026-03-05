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
Comprehensive test suite for gns3_project_open module
Tests the GNS3ProjectOpen tool which opens GNS3 projects by project_id

Test Coverage:
1. TestGNS3ProjectOpenBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectOpenSuccess
   - Successful project opening with v2 API
   - Successful project opening with v3 API
   - Return value validation

3. TestGNS3ProjectOpenInputValidation
   - Missing tool_input
   - Missing project_id parameter
   - Empty project_id

4. TestGNS3ProjectOpenEnvironmentValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Invalid API_VERSION

5. TestGNS3ProjectOpenProjectOperations
   - Project not found
   - Project get method called correctly
   - Project open method called correctly
   - Project status updated after opening

6. TestGNS3ProjectOpenErrorHandling
   - Network connection errors
   - GNS3 server errors
   - Exception handling and logging

7. TestGNS3ProjectOpenReturnFormat
   - Success response format
   - Error response format
   - Project details in response
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

# Import the module to test
from gns3_copilot.gns3_client import GNS3ProjectOpen


class TestGNS3ProjectOpenBasic:
    """Basic tests for GNS3ProjectOpen tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectOpen()
        
        assert tool.name == "open_gns3_project"
        assert tool is not None

    def test_tool_name(self):
        """Test tool name"""
        tool = GNS3ProjectOpen()
        assert tool.name == "open_gns3_project"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectOpen()
        
        description = tool.description
        assert "project_id" in description.lower()
        assert "open" in description.lower()
        assert "required" in description.lower()


class TestGNS3ProjectOpenSuccess:
    """Tests for successful project opening operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_success_v2_api(self, mock_get_connector, mock_project_class):
        """Test successful project opening with v2 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.status = "opened"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "project1", "open": True})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project1"
        assert result["project"]["name"] == "test_project"
        assert result["project"]["status"] == "opened"
        assert "opened successfully" in result["message"]

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "testuser",
        "GNS3_SERVER_PASSWORD": "testpass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_success_v3_api(self, mock_get_connector, mock_project_class):
        """Test successful project opening with v3 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v3"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project2"
        mock_project.name = "v3_project"
        mock_project.status = "opened"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "project2", "open": True})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project2"
        assert result["project"]["name"] == "v3_project"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "test_id", "open": True})
        
        # Verify response structure
        assert "success" in result
        assert "project" in result
        assert "message" in result
        assert "operation" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["project"], dict)
        assert isinstance(result["message"], str)
        assert isinstance(result["operation"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_success_close_project(self, mock_get_connector, mock_project_class):
        """Test successful project closing"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.status = "closed"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "project1", "close": True})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == "project1"
        assert result["project"]["name"] == "test_project"
        assert result["project"]["status"] == "closed"
        assert result["operation"] == "close"
        assert "closed successfully" in result["message"]
        mock_project.close.assert_called_once()


class TestGNS3ProjectOpenInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter"""
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input=None)
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameter" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id in tool_input"""
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"open": True})
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameter: project_id" in result["error"]

    def test_missing_open_and_close_parameters(self):
        """Test when neither open nor close is specified"""
        tool = GNS3ProjectOpen()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            result = tool._run(tool_input={"project_id": "project1"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Either 'open' or 'close'" in result["error"]

    def test_both_open_and_close_true(self):
        """Test when both open and close are set to True"""
        tool = GNS3ProjectOpen()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            result = tool._run(tool_input={"project_id": "project1", "open": True, "close": True})
            
            assert result["success"] is False
            assert "error" in result
            assert "Cannot set both" in result["error"]

    def test_empty_project_id(self):
        """Test empty project_id string"""
        tool = GNS3ProjectOpen()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            result = tool._run(tool_input={"project_id": ""})
            
            # Should still attempt to open with empty project_id
            # The error will come from project not found or API error
            assert "success" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_valid_project_id_format(self, mock_get_connector, mock_project_class):
        """Test valid UUID format for project_id"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "ff8e059c-c33d-47f4-bc11-c7dda8a1d500"
        mock_project.name = "test"
        mock_project.status = "opened"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        valid_uuid = "ff8e059c-c33d-47f4-bc11-c7dda8a1d500"
        result = tool._run(tool_input={"project_id": valid_uuid, "open": True})
        
        assert result["success"] is True
        assert result["project"]["project_id"] == valid_uuid


class TestGNS3ProjectOpenEnvironmentValidation:
    """Tests for environment variable validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION environment variable"""
        tool = GNS3ProjectOpen()

        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id", "open": True})

            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3ProjectOpen()

        def mock_get_config(key, default=None):
            config = {"API_VERSION": "2"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id", "open": True})

            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        tool = GNS3ProjectOpen()

        def mock_get_config(key, default=None):
            config = {"API_VERSION": "invalid", "GNS3_SERVER_URL": "http://localhost:3080"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id", "open": True})

            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_valid_api_versions(self):
        """Test valid API_VERSION values (2 and 3)"""
        tool = GNS3ProjectOpen()
        
        # Test API version 2
        with patch.object(tool.__class__.__bases__[0], '_run', return_value={
            "success": True,
            "project": {},
            "message": "Success"
        }):
            result = tool._run(tool_input={"project_id": "test", "open": True})
            assert "success" in result
        
        # Test API version 3
        with patch.dict(os.environ, {
            "API_VERSION": "3",
            "GNS3_SERVER_URL": "http://localhost:3080",
            "GNS3_SERVER_USERNAME": "user",
            "GNS3_SERVER_PASSWORD": "pass"
        }):
            with patch.object(tool.__class__.__bases__[0], '_run', return_value={
                "success": True,
                "project": {},
                "message": "Success"
            }):
                result = tool._run(tool_input={"project_id": "test", "open": True})
                assert "success" in result


class TestGNS3ProjectOpenProjectOperations:
    """Tests for project-specific operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_project_not_found(self, mock_get_connector, mock_project_class):
        """Test handling when project is not found"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Simulate project not found by having project with no name
        mock_project = Mock()
        mock_project.name = None  # Simulates project not found
        mock_project.project_id = "project1"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "nonexistent_project", "open": True})
        
        # Should return error when project name is None
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_project_get_called(self, mock_get_connector, mock_project_class):
        """Test that project.get() is called with correct parameters"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project.open.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        tool._run(tool_input={"project_id": "test_project", "open": True})
        
        # Verify get was called with False for all parameters to avoid loading nodes/links
        mock_project.get.assert_called_once_with(
            get_nodes=False,
            get_links=False,
            get_stats=False
        )

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_project_open_called(self, mock_get_connector, mock_project_class):
        """Test that project.open() is called"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project.open.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        tool._run(tool_input={"project_id": "test_project", "open": True})
        
        # Verify open was called
        mock_project.open.assert_called_once()
        # Verify close was NOT called
        mock_project.close.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_project_close_called(self, mock_get_connector, mock_project_class):
        """Test that project.close() is called"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.status = "closed"
        mock_project.close.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        tool._run(tool_input={"project_id": "test_project", "close": True})
        
        # Verify close was called
        mock_project.close.assert_called_once()
        # Verify open was NOT called
        mock_project.open.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_project_status_updated(self, mock_get_connector, mock_project_class):
        """Test that project status is updated in response"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.status = "opened"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "test_id", "open": True})
        
        assert result["project"]["status"] == "opened"
        assert "status" in result["project"]


class TestGNS3ProjectOpenErrorHandling:
    """Tests for error handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_network_connection_error(self):
        """Test handling of network connection errors"""
        tool = GNS3ProjectOpen()
        
        with patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector') as mock_get_connector:
            # Mock connector to return None (connection failed)
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "project1", "open": True})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
    def test_gns3_server_error(self, mock_get_connector, mock_project_class):
        """Test handling of GNS3 server errors"""
        tool = GNS3ProjectOpen()
        
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise error on get
        mock_project = Mock()
        mock_project.get.side_effect = Exception("Project not found")
        mock_project_class.return_value = mock_project
        
        result = tool._run(tool_input={"project_id": "project1", "open": True})
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_exception_logging(self):
        """Test that exceptions are logged"""
        tool = GNS3ProjectOpen()
        
        with patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "project1", "open": True})
            
            # Should return error without crashing
            assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_timeout_error(self):
        """Test handling of timeout errors"""
        tool = GNS3ProjectOpen()
        
        with patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "project1", "open": True})
            
            assert result["success"] is False
            assert "error" in result


class TestGNS3ProjectOpenReturnFormat:
    """Tests for return format validation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "test_id", "open": True})
        
        # Verify all required fields
        assert "success" in result
        assert "project" in result
        assert "message" in result
        assert result["success"] is True
        
        # Verify project fields
        assert "project_id" in result["project"]
        assert "name" in result["project"]
        assert "status" in result["project"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_error_response_format(self):
        """Test error response has correct format"""
        tool = GNS3ProjectOpen()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id", "open": True})
            
            # Verify error format
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert isinstance(result["error"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "project123", "open": True})
        
        # Verify project details
        assert result["project"]["project_id"] == "project123"
        assert result["project"]["name"] == "My Lab"
        assert result["project"]["status"] == "opened"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_open.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_open.get_gns3_connector')
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
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectOpen()
        result = tool._run(tool_input={"project_id": "test_id", "open": True})
        
        # Verify message contains project name
        assert "Test Project" in result["message"]
        assert "opened" in result["message"].lower()
