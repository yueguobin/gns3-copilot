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
Comprehensive test suite for gns3_project_read_file module
Tests GNS3ProjectReadFile tool which reads files from GNS3 projects

Test Coverage:
1. TestGNS3ProjectReadFileBasic
   - Tool initialization
   - Tool name and description validation

2. TestGNS3ProjectReadFileSuccess
   - Successful file read operation
   - Content retrieval verification
   - Return value validation

3. TestGNS3ProjectReadFileInputValidation
   - Missing tool_input
   - Invalid JSON format
   - Missing required fields (project_id, path)
   - Invalid project_id format

4. TestGNS3ProjectReadFileProjectIDValidation
   - Valid UUID format
   - Invalid UUID formats
   - UUID pattern validation

5. TestGNS3ProjectReadFileOperations
   - Read different file types
   - Read nested path files
   - Read empty files
   - Read files with special content

6. TestGNS3ProjectReadFileErrorHandling
   - Connection errors
   - File not found errors
   - JSON parsing errors
   - Exception handling

7. TestGNS3ProjectReadFileReturnFormat
   - Success response format
   - Error response format
   - Content field validation
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
from gns3_copilot.gns3_client.gns3_project_read_file import (
    GNS3ProjectReadFileTool,
)


class TestGNS3ProjectReadFileBasic:
    """Basic tests for GNS3ProjectReadFile tool initialization"""

    def test_tool_initialization(self):
        """Test tool initialization"""
        tool = GNS3ProjectReadFileTool()
        
        assert tool is not None
        assert tool.name == "gns3_project_read_file"

    def test_tool_name(self):
        """Test tool name is correct"""
        tool = GNS3ProjectReadFileTool()
        assert tool.name == "gns3_project_read_file"

    def test_tool_description(self):
        """Test tool description contains key information"""
        tool = GNS3ProjectReadFileTool()
        
        description = tool.description
        assert "project_id" in description
        assert "path" in description
        assert "reads" in description.lower()
        assert "file" in description.lower()

    def test_tool_is_langchain_tool(self):
        """Test that tool is a LangChain BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3ProjectReadFileTool()
        assert isinstance(tool, BaseTool)


class TestGNS3ProjectReadFileSuccess:
    """Tests for successful file read operations"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_success_read_file(self, mock_get_connector, mock_project_class):
        """Test successful file read operation"""
        # Mock connector
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        # Mock project
        mock_project = Mock()
        mock_project.get_file.return_value = "This is file content"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test_file.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        assert result["project_id"] == input_data["project_id"]
        assert result["path"] == input_data["path"]
        assert result["content"] == "This is file content"
        mock_project.get_file.assert_called_once_with(
            path=input_data["path"]
        )

    @patch.dict("os.environ", {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "user",
        "GNS3_SERVER_PASSWORD": "pass"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_success_read_file_v3(self, mock_get_connector, mock_project_class):
        """Test successful file read with API v3"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.return_value = "config content"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "config.cfg"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        assert result["content"] == "config content"
        mock_project.get_file.assert_called_once()

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_read_multiline_content(self, mock_get_connector, mock_project_class):
        """Test reading multiline content"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        multiline_content = """Line 1
Line 2
Line 3
"""
        mock_project.get_file.return_value = multiline_content
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "multiline.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        assert result["content"] == multiline_content


class TestGNS3ProjectReadFileInputValidation:
    """Tests for input validation"""

    def test_missing_tool_input(self):
        """Test missing tool_input parameter (None)"""
        tool = GNS3ProjectReadFileTool()
        result = tool._run(None)
        
        # When None is passed, json.loads() fails with TypeError
        assert "error" in result

    def test_invalid_json_format(self):
        """Test invalid JSON format"""
        tool = GNS3ProjectReadFileTool()
        result = tool._run("not valid json")
        
        assert "Invalid JSON input" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id field"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "path": "test.txt"
        }
        result = tool._run(json.dumps(input_data))
        
        assert result["error"] == "Missing project_id."

    def test_missing_path(self):
        """Test missing path field"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932"
        }
        result = tool._run(json.dumps(input_data))
        
        assert result["error"] == "Missing path."

    def test_empty_project_id(self):
        """Test empty project_id string"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "",
            "path": "test.txt"
        }
        result = tool._run(json.dumps(input_data))
        
        # Empty string is caught by "not project_id" check before UUID validation
        assert result["error"] == "Missing project_id."

    def test_empty_project_id_string(self):
        """Test empty project_id returns missing error"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "",
            "path": "test.txt"
        }
        result = tool._run(json.dumps(input_data))
        
        # Empty string fails the "not project_id" check
        assert result["error"] == "Missing project_id."

    def test_empty_path(self):
        """Test empty path string"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": ""
        }
        result = tool._run(json.dumps(input_data))
        
        assert result["error"] == "Missing path."


class TestGNS3ProjectReadFileProjectIDValidation:
    """Tests for project_id UUID validation"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_valid_uuid_format(self):
        """Test valid UUID format is accepted"""
        tool = GNS3ProjectReadFileTool()
        
        valid_uuid = "1445a4ba-4635-430b-a332-bef438f65932"
        
        with patch('gns3_copilot.gns3_client.gns3_project_read_file.Project') as mock_project_class:
            with patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector') as mock_get_connector:
                mock_connector = Mock()
                mock_get_connector.return_value = mock_connector
                
                mock_project = Mock()
                mock_project.get_file.return_value = "content"
                mock_project_class.return_value = mock_project
                
                input_data = {
                    "project_id": valid_uuid,
                    "path": "test.txt"
                }
                
                result = tool._run(json.dumps(input_data))
                
                assert "Invalid project_id format" not in result.get("error", "")

    def test_invalid_uuid_format_short(self):
        """Test invalid UUID format (too short)"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "12345678",
            "path": "test.txt"
        }
        result = tool._run(json.dumps(input_data))
        
        assert "Invalid project_id format" in result["error"]

    def test_invalid_uuid_format_no_dashes(self):
        """Test invalid UUID format (no dashes)"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "1445a4ba4635430ba332bef438f65932",
            "path": "test.txt"
        }
        result = tool._run(json.dumps(input_data))
        
        assert "Invalid project_id format" in result["error"]

    def test_invalid_uuid_format_random(self):
        """Test invalid UUID format (random string)"""
        tool = GNS3ProjectReadFileTool()
        input_data = {
            "project_id": "not-a-uuid",
            "path": "test.txt"
        }
        result = tool._run(json.dumps(input_data))
        
        assert "Invalid project_id format" in result["error"]

    def test_uuid_uppercase(self):
        """Test UUID with uppercase letters"""
        tool = GNS3ProjectReadFileTool()
        
        with patch('gns3_copilot.gns3_client.gns3_project_read_file.Project') as mock_project_class:
            with patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector') as mock_get_connector:
                mock_connector = Mock()
                mock_get_connector.return_value = mock_connector
                
                mock_project = Mock()
                mock_project.get_file.return_value = "content"
                mock_project_class.return_value = mock_project
                
                input_data = {
                    "project_id": "1445A4BA-4635-430B-A332-BEF438F65932",
                    "path": "test.txt"
                }
                
                result = tool._run(json.dumps(input_data))
                
                assert "Invalid project_id format" not in result.get("error", "")


class TestGNS3ProjectReadFileOperations:
    """Tests for file-specific operations"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_read_nested_path(self, mock_get_connector, mock_project_class):
        """Test reading file with nested path"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.return_value = "config content"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "configs/router1.cfg"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        mock_project.get_file.assert_called_once_with(
            path=input_data["path"]
        )

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_read_empty_file(self, mock_get_connector, mock_project_class):
        """Test reading empty file"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.return_value = ""
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "empty.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        assert result["content"] == ""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_read_large_file(self, mock_get_connector, mock_project_class):
        """Test reading large file"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        large_content = "x" * 10000
        mock_project.get_file.return_value = large_content
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "large.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        assert result["content"] == large_content

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_read_special_chars_content(self, mock_get_connector, mock_project_class):
        """Test reading file with special characters"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        special_content = "Special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/~`\nUnicode: 你好世界"
        mock_project.get_file.return_value = special_content
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "special.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "success"
        assert result["content"] == special_content


class TestGNS3ProjectReadFileErrorHandling:
    """Tests for error handling"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_connector_creation_failure(self):
        """Test handling of connector creation failure"""
        tool = GNS3ProjectReadFileTool()
        
        with patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector') as mock_get_connector:
            mock_get_connector.return_value = None
            
            input_data = {
                "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
                "path": "test.txt"
            }
            
            result = tool._run(json.dumps(input_data))
            
            assert "Failed to create GNS3 connector" in result["error"]

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_file_not_found(self, mock_get_connector, mock_project_class):
        """Test handling of file not found error"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.side_effect = FileNotFoundError("File not found")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "nonexistent.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert result["status"] == "failed"
        assert "Failed to read file" in result["error"]

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_value_error_handling(self, mock_get_connector, mock_project_class):
        """Test handling of ValueError"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.side_effect = ValueError("Invalid value")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert "error" in result


class TestGNS3ProjectReadFileReturnFormat:
    """Tests for return format validation"""

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_success_response_format(self, mock_get_connector, mock_project_class):
        """Test success response has correct format"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.return_value = "content"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        # Verify all required fields
        assert "project_id" in result
        assert "path" in result
        assert "content" in result
        assert "status" in result
        assert result["status"] == "success"

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_failure_response_format(self, mock_get_connector, mock_project_class):
        """Test failure response has correct format"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.side_effect = Exception("Read failed")
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error format
        assert "status" in result
        assert "error" in result
        assert result["status"] == "failed"
        assert isinstance(result["error"], str)

    @patch.dict("os.environ", {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.Project')
    @patch('gns3_copilot.gns3_client.gns3_project_read_file.get_gns3_connector')
    def test_content_type(self, mock_get_connector, mock_project_class):
        """Test that content field is a string"""
        mock_connector = Mock()
        mock_get_connector.return_value = mock_connector
        
        mock_project = Mock()
        mock_project.get_file.return_value = "test content"
        mock_project_class.return_value = mock_project
        
        tool = GNS3ProjectReadFileTool()
        
        input_data = {
            "project_id": "1445a4ba-4635-430b-a332-bef438f65932",
            "path": "test.txt"
        }
        
        result = tool._run(json.dumps(input_data))
        
        assert isinstance(result["content"], str)
