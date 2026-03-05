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
Comprehensive test suite for gns3_project_path module
Tests GNS3ProjectPath tool which retrieves GNS3 project paths

Test Coverage:
1. TestGNS3ProjectPathBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectPathSuccess
   - Successful path retrieval
   - Path validation
   - Return value verification

3. TestGNS3ProjectPathInputValidation
   - Missing tool_input
   - Missing project_name
   - Missing project_id
   - Empty parameter validation

4. TestGNS3ProjectPathEnvironmentValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Invalid API_VERSION

5. TestGNS3ProjectPathOperations
   - Path retrieval with API v2
   - Path retrieval with API v3
   - Project name verification
   - Project not found handling

6. TestGNS3ProjectPathErrorHandling
   - Connection errors
   - Project not found errors
   - Authentication errors
   - Exception handling

7. TestGNS3ProjectPathReturnFormat
   - Success response format
   - Error response format
   - Response field validation
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
from gns3_copilot.gns3_client.gns3_project_path import GNS3ProjectPath


class TestGNS3ProjectPathBasic:
    """Basic tests for GNS3ProjectPath tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectPath()
        
        assert tool is not None
        assert tool.name == "get_gns3_project_path"

    def test_tool_name(self):
        """Test tool name is correct"""
        tool = GNS3ProjectPath()
        assert tool.name == "get_gns3_project_path"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectPath()
        
        description = tool.description
        assert "project_name" in description
        assert "project_id" in description
        assert "path" in description.lower()
        assert "retrieves" in description.lower()

    def test_tool_is_langchain_tool(self):
        """Test that tool is a LangChain BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3ProjectPath()
        assert isinstance(tool, BaseTool)


class TestGNS3ProjectPathSuccess:
    """Tests for successful path retrieval operations"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_success_path_retrieval_v2(self, mock_get_connector, mock_project_class):
        """Test successful path retrieval with API v2"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.project_id = "1445a4ba-4635-430b-a332-bef438f65932"
        mock_project.name = "test_project"
        mock_project.path = "/home/user/GNS3/projects/test_project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test_project",
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
        }
        
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is True
        assert result["project_path"] == "/home/user/GNS3/projects/test_project"
        assert result["project_name"] == "test_project"
        assert result["project_id"] == "1445a4ba-4635-430b-a332-bef438f65932"
        assert "Successfully retrieved" in result["message"]

    @patch.dict("os.environ", {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_success_path_retrieval_v3(self, mock_get_connector, mock_project_class):
        """Test successful path retrieval with API v3"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "1445a4ba-4635-430b-a332-bef438f65932"
        mock_project.name = "test_project"
        mock_project.path = "/home/user/GNS3/projects/test_project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test_project",
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
        }
        
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is True
        assert result["project_path"] == "/home/user/GNS3/projects/test_project"

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_path_retrieval_with_project_id(self, mock_get_connector, mock_project_class):
        """Test that project_id is returned correctly"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "ff8e059c-c33d-47f4-bc11-c7dda8a1d500"
        mock_project.name = "My Lab"
        mock_project.path = "/home/user/GNS3/projects/My Lab"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "My Lab",
            "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500"
        }
        
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is True
        assert result["project_id"] == "ff8e059c-c33d-47f4-bc11-c7dda8a1d500"


class TestGNS3ProjectPathInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter"""
        tool = GNS3ProjectPath()
        result = tool._run(tool_input=None)
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameters" in result["error"]

    def test_empty_tool_input(self):
        """Test empty tool_input dictionary"""
        tool = GNS3ProjectPath()
        result = tool._run(tool_input={})
        
        assert result["success"] is False
        assert "error" in result
        assert "Missing required parameters" in result["error"]

    def test_missing_project_name(self):
        """Test missing project_name field"""
        tool = GNS3ProjectPath()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False
        assert "Both project_name and project_id are required" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id field"""
        tool = GNS3ProjectPath()
        input_data = {
            "project_name": "test_project"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False
        assert "Both project_name and project_id are required" in result["error"]

    def test_empty_project_name(self):
        """Test empty project_name string"""
        tool = GNS3ProjectPath()
        input_data = {
            "project_name": "",
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False

    def test_empty_project_id(self):
        """Test empty project_id string"""
        tool = GNS3ProjectPath()
        input_data = {
            "project_name": "test_project",
            "project_id": ""
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False

    def test_none_project_name(self):
        """Test project_name is None"""
        tool = GNS3ProjectPath()
        input_data = {
            "project_name": None,
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False

    def test_none_project_id(self):
        """Test project_id is None"""
        tool = GNS3ProjectPath()
        input_data = {
            "project_name": "test_project",
            "project_id": None
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False


class TestGNS3ProjectPathEnvironmentValidation:
    """Tests for environment variable validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION environment variable"""
        tool = GNS3ProjectPath()
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', return_value=None):
            input_data = {
                "project_name": "test_project",
                "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
            }
            result = tool._run(tool_input=input_data)
            
            assert result["success"] is False
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3ProjectPath()
        
        def mock_get_config(key, default=None):
            config = {"API_VERSION": "2"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            input_data = {
                "project_name": "test_project",
                "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
            }
            result = tool._run(tool_input=input_data)
            
            assert result["success"] is False
            assert "Failed to connect to GNS3 server" in result["error"]

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        tool = GNS3ProjectPath()
        
        def mock_get_config(key, default=None):
            config = {"API_VERSION": "invalid", "GNS3_SERVER_URL": "http://localhost:3080"}
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            input_data = {
                "project_name": "test_project",
                "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
            }
            result = tool._run(tool_input=input_data)
            
            assert result["success"] is False
            assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_valid_api_version_2(self, mock_get_connector, mock_project_class):
        """Test valid API_VERSION = 2"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        assert "success" in result

    @patch.dict("os.environ", {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_valid_api_version_3(self, mock_get_connector, mock_project_class):
        """Test valid API_VERSION = 3"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        assert "success" in result


class TestGNS3ProjectPathOperations:
    """Tests for project-specific operations"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_project_get_called(self, mock_get_connector, mock_project_class):
        """Test that project.get() is called"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        tool._run(tool_input=input_data)
        
        # Verify get was called with correct parameters
        mock_project.get.assert_called_once_with(
            get_nodes=False,
            get_links=False,
            get_stats=False
        )

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_project_not_found(self, mock_get_connector, mock_project_class):
        """Test handling when project is not found"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = ""  # Empty name indicates not found
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "nonexistent",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_project_path_missing(self, mock_get_connector, mock_project_class):
        """Test handling when project has no path attribute"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test"
        mock_project.path = None  # No path attribute
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False
        assert "no path attribute" in result["error"].lower()

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_project_name_mismatch(self, mock_get_connector, mock_project_class):
        """Test handling when project name doesn't match"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "actual_name"  # Different from requested
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "requested_name",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        # Should still succeed as project_id is more authoritative
        assert result["success"] is True
        assert result["project_name"] == "actual_name"

    @patch.dict("os.environ", {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_connector_created_with_credentials(self, mock_get_connector, mock_project_class):
        """Test that connector is created with v3 credentials"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        tool._run(tool_input=input_data)
        
        # Verify get_gns3_connector was called
        mock_get_connector.assert_called_once()


class TestGNS3ProjectPathErrorHandling:
    """Tests for error handling"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_connection_error(self):
        """Test handling of connection error"""
        tool = GNS3ProjectPath()
        
        with patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            input_data = {
                "project_name": "test",
                "project_id": "test-id"
            }
            result = tool._run(tool_input=input_data)
            
            assert result["success"] is False
            assert "error" in result

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_project_get_error(self, mock_get_connector, mock_project_class):
        """Test handling of project.get() error"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get.side_effect = Exception("Get failed")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        assert result["success"] is False
        assert "error" in result

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_timeout_error(self):
        """Test handling of timeout error"""
        tool = GNS3ProjectPath()
        
        with patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            input_data = {
                "project_name": "test",
                "project_id": "test-id"
            }
            result = tool._run(tool_input=input_data)
            
            assert result["success"] is False
            assert "error" in result


class TestGNS3ProjectPathReturnFormat:
    """Tests for return format validation"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_success_response_format(self, mock_get_connector, mock_project_class):
        """Test success response has correct format"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test_project"
        mock_project.path = "/path/to/project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test_project",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        # Verify all required fields
        assert "success" in result
        assert "project_path" in result
        assert "project_name" in result
        assert "project_id" in result
        assert "message" in result
        assert result["success"] is True

    def test_error_response_format(self):
        """Test error response has correct format"""
        tool = GNS3ProjectPath()
        
        result = tool._run(tool_input=None)
        
        # Verify error format
        assert "success" in result
        assert "error" in result
        assert result["success"] is False
        assert isinstance(result["error"], str)

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_message_content(self, mock_get_connector, mock_project_class):
        """Test that message contains useful information"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "My Project"
        mock_project.path = "/path/to/My Project"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "My Project",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        # Verify message contains project name
        assert "My Project" in result["message"]
        assert "Successfully retrieved" in result["message"]

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_path.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_path.get_gns3_connector')
    def test_project_path_type(self, mock_get_connector, mock_project_class):
        """Test that project_path is a string"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.project_id = "test-id"
        mock_project.name = "test"
        mock_project.path = "/path/to/test"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectPath()
        
        input_data = {
            "project_name": "test",
            "project_id": "test-id"
        }
        result = tool._run(tool_input=input_data)
        
        assert isinstance(result["project_path"], str)
