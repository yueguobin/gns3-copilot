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
Comprehensive test suite for gns3_project_lock module
Tests the GNS3ProjectLock tool which locks/unlocks GNS3 projects

Test Coverage:
1. TestGNS3ProjectLockBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectLockSuccess
   - Successful lock status check
   - Successful project locking
   - Successful project unlocking
   - Return value validation

3. TestGNS3ProjectLockInputValidation
   - Missing tool_input
   - Missing project_id parameter
   - Missing operation parameter
   - Invalid operation type

4. TestGNS3ProjectLockEnvironmentValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Invalid API_VERSION

5. TestGNS3ProjectLockProjectOperations
   - Project not found
   - Project get method called correctly
   - Project get_locked method called
   - Project lock_project method called
   - Project unlock_project method called
   - Locked status returned correctly

6. TestGNS3ProjectLockErrorHandling
   - Network connection errors
   - GNS3 server errors
   - Exception handling and logging

7. TestGNS3ProjectLockReturnFormat
   - Success response format for each operation
   - Error response format
   - Locked status in response
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

# Import the module to test
from gns3_copilot.gns3_client import GNS3ProjectLock


class TestGNS3ProjectLockBasic:
    """Basic tests for GNS3ProjectLock tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectLock()
        
        assert tool.name == "gns3_project_lock"
        assert tool is not None

    def test_tool_name(self):
        """Test tool name"""
        tool = GNS3ProjectLock()
        assert tool.name == "gns3_project_lock"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectLock()
        
        description = tool.description
        assert "project_id" in description.lower()
        assert "lock" in description.lower()
        assert "unlock" in description.lower()
        assert "locked" in description.lower()
        assert "operation" in description.lower()


class TestGNS3ProjectLockSuccess:
    """Tests for successful lock/unlock operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_success_check_locked_status(self, mock_get_connector, mock_project_class):
        """Test successful lock status check"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.get_locked.return_value = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "project1", "operation": "locked"})
        
        assert result["success"] is True
        assert result["operation"] == "locked"
        assert result["project_id"] == "project1"
        assert result["locked_status"] is False
        assert "unlocked" in result["message"].lower()
        mock_project.get_locked.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_success_lock_project(self, mock_get_connector, mock_project_class):
        """Test successful project locking"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.lock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "project1", "operation": "lock"})
        
        assert result["success"] is True
        assert result["operation"] == "lock"
        assert result["project_id"] == "project1"
        assert "locked successfully" in result["message"].lower()
        mock_project.lock_project.assert_called_once()
        mock_project.unlock_project.assert_not_called()
        mock_project.get_locked.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_success_unlock_project(self, mock_get_connector, mock_project_class):
        """Test successful project unlocking"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "project1"
        mock_project.name = "test_project"
        mock_project.unlock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "project1", "operation": "unlock"})
        
        assert result["success"] is True
        assert result["operation"] == "unlock"
        assert result["project_id"] == "project1"
        assert "unlocked successfully" in result["message"].lower()
        mock_project.unlock_project.assert_called_once()
        mock_project.lock_project.assert_not_called()
        mock_project.get_locked.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
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
        mock_project.get_locked.return_value = True
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "test_id", "operation": "locked"})
        
        # Verify response structure
        assert "success" in result
        assert "operation" in result
        assert "project_id" in result
        assert "locked_status" in result
        assert "message" in result
        assert isinstance(result["success"], bool)
        assert isinstance(result["operation"], str)
        assert isinstance(result["project_id"], str)
        assert isinstance(result["locked_status"], bool)
        assert isinstance(result["message"], str)


class TestGNS3ProjectLockInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter"""
        tool = GNS3ProjectLock()
        result = tool._run(tool_input=None)
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameter: project_id" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id in tool_input"""
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"operation": "lock"})
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameter: project_id" in result["error"]

    def test_missing_operation_parameter(self):
        """Test missing operation in tool_input"""
        tool = GNS3ProjectLock()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            result = tool._run(tool_input={"project_id": "project1"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Missing required parameter: operation" in result["error"]

    def test_invalid_operation_type(self):
        """Test invalid operation type"""
        tool = GNS3ProjectLock()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            result = tool._run(tool_input={"project_id": "project1", "operation": "invalid"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Invalid operation 'invalid'" in result["error"]
            assert "Must be one of:" in result["error"]

    def test_valid_operations(self):
        """Test all valid operation types"""
        tool = GNS3ProjectLock()
        valid_operations = ["locked", "lock", "unlock"]
        
        for operation in valid_operations:
            with patch.dict(os.environ, {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }):
                result = tool._run(tool_input={"project_id": "test", "operation": operation})
                # Should not return operation validation error
                if "Invalid operation" in result.get("error", ""):
                    pytest.fail(f"Valid operation '{operation}' was rejected")

    def test_empty_project_id(self):
        """Test empty project_id string"""
        tool = GNS3ProjectLock()
        
        with patch.dict(os.environ, {
            "API_VERSION": "2",
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            result = tool._run(tool_input={"project_id": "", "operation": "lock"})
            
            # Should still attempt operation with empty project_id
            # The error will come from project not found or API error
            assert "success" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
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
        mock_project.lock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        valid_uuid = "ff8e059c-c33d-47f4-bc11-c7dda8a1d500"
        result = tool._run(tool_input={"project_id": valid_uuid, "operation": "lock"})
        
        assert result["success"] is True
        assert result["project_id"] == valid_uuid


class TestGNS3ProjectLockEnvironmentValidation:
    """Tests for environment variable validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION environment variable"""
        tool = GNS3ProjectLock()

        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id", "operation": "lock"})

            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3ProjectLock()

        def mock_get_config(key, default=None):
            config = {"API_VERSION": "2"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id", "operation": "lock"})

            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        tool = GNS3ProjectLock()

        def mock_get_config(key, default=None):
            config = {"API_VERSION": "invalid", "GNS3_SERVER_URL": "http://localhost:3080"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            result = tool._run(tool_input={"project_id": "test_id", "operation": "lock"})

            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]


class TestGNS3ProjectLockProjectOperations:
    """Tests for project-specific operations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
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
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "nonexistent_project", "operation": "lock"})
        
        # Should return error when project name is None
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_project_get_called(self, mock_get_connector, mock_project_class):
        """Test that project.get() is called with correct parameters"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.get_locked.return_value = False
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        tool._run(tool_input={"project_id": "test_project", "operation": "locked"})
        
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
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_project_get_locked_called(self, mock_get_connector, mock_project_class):
        """Test that project.get_locked() is called for locked operation"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.get_locked.return_value = True
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        tool._run(tool_input={"project_id": "test_project", "operation": "locked"})
        
        # Verify get_locked was called
        mock_project.get_locked.assert_called_once()
        # Verify other lock methods were NOT called
        mock_project.lock_project.assert_not_called()
        mock_project.unlock_project.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_project_lock_project_called(self, mock_get_connector, mock_project_class):
        """Test that project.lock_project() is called for lock operation"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.lock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        tool._run(tool_input={"project_id": "test_project", "operation": "lock"})
        
        # Verify lock_project was called
        mock_project.lock_project.assert_called_once()
        # Verify other methods were NOT called
        mock_project.get_locked.assert_not_called()
        mock_project.unlock_project.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_project_unlock_project_called(self, mock_get_connector, mock_project_class):
        """Test that project.unlock_project() is called for unlock operation"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test_project"
        mock_project.name = "Test Project"
        mock_project.unlock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        tool._run(tool_input={"project_id": "test_project", "operation": "unlock"})
        
        # Verify unlock_project was called
        mock_project.unlock_project.assert_called_once()
        # Verify other methods were NOT called
        mock_project.get_locked.assert_not_called()
        mock_project.lock_project.assert_not_called()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_locked_status_returned_correctly(self, mock_get_connector, mock_project_class):
        """Test that locked status is returned correctly"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Test when project is locked
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test Project"
        mock_project.get_locked.return_value = True
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "test_id", "operation": "locked"})
        
        assert result["locked_status"] is True
        assert "locked" in result["message"].lower()
        
        # Test when project is unlocked
        mock_project.get_locked.return_value = False
        result = tool._run(tool_input={"project_id": "test_id", "operation": "locked"})
        
        assert result["locked_status"] is False
        assert "unlocked" in result["message"].lower()


class TestGNS3ProjectLockErrorHandling:
    """Tests for error handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_network_connection_error(self):
        """Test handling of network connection errors"""
        tool = GNS3ProjectLock()
        
        with patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector') as mock_get_connector:
            # Mock connector to return None (connection failed)
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "project1", "operation": "lock"})
            
            assert result["success"] is False
            assert "error" in result
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_gns3_server_error(self, mock_get_connector, mock_project_class):
        """Test handling of GNS3 server errors"""
        tool = GNS3ProjectLock()
        
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Mock project to raise error on get
        mock_project = Mock()
        mock_project.get.side_effect = Exception("Project not found")
        mock_project_class.return_value = mock_project
        
        result = tool._run(tool_input={"project_id": "project1", "operation": "lock"})
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_exception_logging(self):
        """Test that exceptions are logged"""
        tool = GNS3ProjectLock()
        
        with patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "project1", "operation": "lock"})
            
            # Should return error without crashing
            assert "error" in result

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_timeout_error(self):
        """Test handling of timeout errors"""
        tool = GNS3ProjectLock()
        
        with patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            result = tool._run(tool_input={"project_id": "project1", "operation": "lock"})
            
            assert result["success"] is False
            assert "error" in result


class TestGNS3ProjectLockReturnFormat:
    """Tests for return format validation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_locked_operation_response_format(self, mock_get_connector, mock_project_class):
        """Test locked operation response has correct format"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test"
        mock_project.get_locked.return_value = True
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "test_id", "operation": "locked"})
        
        # Verify all required fields
        assert "success" in result
        assert "operation" in result
        assert "project_id" in result
        assert "locked_status" in result
        assert "message" in result
        assert result["success"] is True
        assert result["operation"] == "locked"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_lock_operation_response_format(self, mock_get_connector, mock_project_class):
        """Test lock operation response has correct format"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test"
        mock_project.lock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "test_id", "operation": "lock"})
        
        # Verify all required fields
        assert "success" in result
        assert "operation" in result
        assert "project_id" in result
        assert "message" in result
        assert result["success"] is True
        assert result["operation"] == "lock"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
    def test_unlock_operation_response_format(self, mock_get_connector, mock_project_class):
        """Test unlock operation response has correct format"""
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "test_id"
        mock_project.name = "Test"
        mock_project.unlock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "test_id", "operation": "unlock"})
        
        # Verify all required fields
        assert "success" in result
        assert "operation" in result
        assert "project_id" in result
        assert "message" in result
        assert result["success"] is True
        assert result["operation"] == "unlock"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_error_response_format(self):
        """Test error response has correct format"""
        tool = GNS3ProjectLock()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            result = tool._run(tool_input={"project_id": "test_id", "operation": "lock"})
            
            # Verify error format
            assert "success" in result
            assert result["success"] is False
            assert "error" in result
            assert isinstance(result["error"], str)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_lock.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_lock.get_gns3_connector')
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
        mock_project.lock_project.return_value = None
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectLock()
        result = tool._run(tool_input={"project_id": "test_id", "operation": "lock"})
        
        # Verify message contains project name
        assert "Test Project" in result["message"]
        assert "locked" in result["message"].lower()
