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
Comprehensive test suite for gns3_project_write_file module
Tests GNS3ProjectWriteFile tool which writes files to GNS3 projects

Test Coverage:
1. TestGNS3ProjectWriteFileBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectWriteFileSuccess
   - Successful file write operation
   - File index update verification
   - Return value validation

3. TestGNS3ProjectWriteFileInputValidation
   - Missing tool_input
   - Invalid JSON format
   - Missing required fields (project_id, path, data)
   - Invalid project_id format

4. TestGNS3ProjectWriteFileProjectIDValidation
   - Valid UUID format
   - Invalid UUID formats
   - UUID pattern validation

5. TestGNS3ProjectWriteFileOperations
   - File write with different content types
   - File index update functionality
   - Multiple writes to same file
   - Large file handling

6. TestGNS3ProjectWriteFileErrorHandling
   - Connection errors
   - File write failures
   - JSON parsing errors
   - Exception handling

7. TestGNS3ProjectWriteFileReturnFormat
   - Success response format
   - Error response format
   - Response field validation
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
from gns3_copilot.gns3_client.gns3_project_write_file import (
    GNS3ProjectWriteFileTool,
)


class TestGNS3ProjectWriteFileBasic:
    """Basic tests for GNS3ProjectWriteFile tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectWriteFileTool()
        
        assert tool is not None
        assert tool.name == "gns3_project_write_file"

    def test_tool_name(self):
        """Test tool name is correct"""
        tool = GNS3ProjectWriteFileTool()
        assert tool.name == "gns3_project_write_file"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectWriteFileTool()
        
        description = tool.description
        assert "project_id" in description
        assert "path" in description
        assert "data" in description
        assert "writes" in description.lower()
        assert "file" in description.lower()

    def test_tool_is_langchain_tool(self):
        """Test that tool is a LangChain BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3ProjectWriteFileTool()
        assert isinstance(tool, BaseTool)


class TestGNS3ProjectWriteFileSuccess:
    """Tests for successful file write operations"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_success_write_file(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test successful file write operation"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test_file.txt",
            "data": "This is test content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "success"
        assert result["project_id"] == input_data["project_id"]
        assert result["path"] == input_data["path"]
        mock_project.write_file.assert_called_once_with(
            path=input_data["path"],
            data=input_data["data"]
        )
        mock_add_to_index.assert_called_once()

    @patch.dict("os.environ", {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_success_write_file_v3(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test successful file write with API v3"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "config.cfg",
            "data": "router config"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "success"
        mock_project.write_file.assert_called_once()

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_file_index_update(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test that file index is updated after write"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt",
            "data": "test content with 20 chars"
        }
        
        tool._run(json.dumps(input_data))
        
        # Verify file index was updated with correct size
        mock_add_to_index.assert_called_once()
        call_args = mock_add_to_index.call_args
        assert call_args[0][0] == mock_project
        assert call_args[0][1] == input_data["path"]
        # Size is passed as keyword argument
        assert call_args.kwargs["size"] == len(input_data["data"])

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_write_multiline_content(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test writing multiline content"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        multiline_data = """Line 1
Line 2
Line 3
"""
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "multiline.txt",
            "data": multiline_data
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "success"
        mock_project.write_file.assert_called_once_with(
            path=input_data["path"],
            data=multiline_data
        )


class TestGNS3ProjectWriteFileInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter (None)"""
        tool = GNS3ProjectWriteFileTool()
        result_str = tool._run(None)
        result = json.loads(result_str)
        
        # When None is passed, json.loads() fails with TypeError
        # This is caught by the general Exception handler
        assert "error" in result

    def test_invalid_json_format(self):
        """Test invalid JSON format"""
        tool = GNS3ProjectWriteFileTool()
        result_str = tool._run("not valid json")
        result = json.loads(result_str)
        
        assert "Invalid JSON input" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id field"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "path": "test.txt",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["error"] == "Missing project_id."

    def test_missing_path(self):
        """Test missing path field"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["error"] == "Missing path."

    def test_missing_data(self):
        """Test missing data field"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["error"] == "Missing data."

    def test_empty_project_id(self):
        """Test empty project_id string"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "",
            "path": "test.txt",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        # Empty string is caught by "not project_id" check before UUID validation
        assert result["error"] == "Missing project_id."

    def test_empty_path(self):
        """Test empty path string"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["error"] == "Missing path."

    def test_none_data(self):
        """Test data field is None"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt",
            "data": None
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["error"] == "Missing data."


class TestGNS3ProjectWriteFileProjectIDValidation:
    """Tests for project_id UUID validation"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_valid_uuid_format(self):
        """Test valid UUID format is accepted"""
        tool = GNS3ProjectWriteFileTool()
        
        valid_uuid = "1445a4ba-4635-430b-a332-bef438f65932"
        
        with patch('gns3_copilot.gns3_client.gns3_project_write_file.Project') as mock_project_class:
            with patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector') as mock_get_connector:
                with patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index'):
                    mock_connector = Mock()
                    mock_get_connector.return_value = mock_connector
                    
                    mock_project = Mock()
                    mock_project_class.return_value = mock_project
                    
                    input_data = {
                        "project_id": valid_uuid,
                        "path": "test.txt",
                        "data": "content"
                    }
                    
                    result_str = tool._run(json.dumps(input_data))
                    result = json.loads(result_str)
                    
                    assert "Invalid project_id format" not in result.get("error", "")

    def test_invalid_uuid_format_short(self):
        """Test invalid UUID format (too short)"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "12345678",
            "path": "test.txt",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert "Invalid project_id format" in result["error"]

    def test_invalid_uuid_format_no_dashes(self):
        """Test invalid UUID format (no dashes)"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "1445a4ba4635430ba332bef438f65932",
            "path": "test.txt",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert "Invalid project_id format" in result["error"]

    def test_invalid_uuid_format_random(self):
        """Test invalid UUID format (random string)"""
        tool = GNS3ProjectWriteFileTool()
        input_data = {
            "project_id": "not-a-uuid",
            "path": "test.txt",
            "data": "content"
        }
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert "Invalid project_id format" in result["error"]

    def test_uuid_uppercase(self):
        """Test UUID with uppercase letters"""
        tool = GNS3ProjectWriteFileTool()
        
        with patch('gns3_copilot.gns3_client.gns3_project_write_file.Project') as mock_project_class:
            with patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector') as mock_get_connector:
                with patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index'):
                    mock_connector = Mock()
                    mock_get_connector.return_value = mock_connector
                    
                    mock_project = Mock()
                    mock_project_class.return_value = mock_project
                    
                    input_data = {
                        "project_id": "1445A4BA-4635-430B-A332-BEF438F65932",
                        "path": "test.txt",
                        "data": "content"
                    }
                    
                    result_str = tool._run(json.dumps(input_data))
                    result = json.loads(result_str)
                    
                    assert "Invalid project_id format" not in result.get("error", "")


class TestGNS3ProjectWriteFileOperations:
    """Tests for file-specific operations"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_write_with_nested_path(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test writing file with nested path"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "configs/router1.cfg",
            "data": "config content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "success"
        mock_project.write_file.assert_called_once_with(
            path=input_data["path"],
            data=input_data["data"]
        )

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_write_with_special_chars_in_path(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test writing file with special characters in path"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "config_v2.0.txt",
            "data": "content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "success"

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_write_empty_string_data(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test writing empty string as data"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "empty.txt",
            "data": ""
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "success"
        mock_project.write_file.assert_called_once_with(
            path=input_data["path"],
            data=""
        )


class TestGNS3ProjectWriteFileErrorHandling:
    """Tests for error handling"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_connector_creation_failure(self):
        """Test handling of connector creation failure"""
        tool = GNS3ProjectWriteFileTool()
        
        with patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            input_data = {
                "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
                "path": "test.txt",
                "data": "content"
            }
            
            result_str = tool._run(json.dumps(input_data))
            result = json.loads(result_str)
            
            assert "Failed to create GNS3 connector" in result["error"]

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_file_write_failure(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test handling of file write failure"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.write_file.side_effect = Exception("Write failed")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt",
            "data": "content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert result["status"] == "failed"
        assert "Failed to write file" in result["error"]

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_value_error_handling(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test handling of ValueError"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.write_file.side_effect = ValueError("Invalid value")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt",
            "data": "content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        assert "error" in result


class TestGNS3ProjectWriteFileReturnFormat:
    """Tests for return format validation"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_success_response_format(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test success response has correct format"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt",
            "data": "content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        # Verify all required fields
        assert "project_id" in result
        assert "path" in result
        assert "status" in result
        assert result["status"] == "success"

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.add_file_to_index')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_write_file.get_gns3_connector')
    def test_failure_response_format(self, mock_get_connector, mock_project_class, mock_add_to_index):
        """Test failure response has correct format"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.write_file.side_effect = Exception("Write failed")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectWriteFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt",
            "data": "content"
        }
        
        result_str = tool._run(json.dumps(input_data))
        result = json.loads(result_str)
        
        # Verify error format
        assert "status" in result
        assert "error" in result
        assert result["status"] == "failed"
        assert isinstance(result["error"], str)
