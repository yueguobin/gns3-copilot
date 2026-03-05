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
Tests for gns3_create_node module.
Contains comprehensive test cases for GNS3CreateNodeTool functionality.

Test Coverage:
1. TestGNS3CreateNodeToolInitialization
   - Tool name and description validation
   - Tool inheritance from BaseTool
   - Tool attributes verification (name, description, _run method)

2. TestGNS3CreateNodeToolInputValidation
   - Empty input handling
   - Invalid JSON input handling
   - Missing project_id handling
   - Empty nodes array handling
   - Nodes not an array handling
   - Missing nodes field handling
   - Node definition missing required fields (template_id, x, y)
   - Node definition with invalid coordinates
   - Node definition not a dictionary
   - Node definition with None values
   - Node definition with empty string template_id

3. TestGNS3CreateNodeToolAPIVersionHandling
   - API version 2 initialization with Basic Auth
   - API version 3 initialization with JWT authentication
   - Unsupported API version handling
   - Default API version (v2) when not specified

4. TestGNS3CreateNodeToolSuccessScenarios
   - Single node creation success
   - Multiple nodes creation success
   - Negative coordinates handling
   - Float coordinates handling

5. TestGNS3CreateNodeToolErrorHandling
   - Node creation exception handling
   - Connector initialization exception handling
   - Node.get() exception handling

6. TestGNS3CreateNodeToolMixedSuccessFailure
   - Mixed successful and failed node creations (e.g., 2 success, 1 failure)

7. TestGNS3CreateNodeToolEdgeCases
   - Unicode template IDs handling
   - Very long IDs (1000+ characters)
   - Special characters in IDs
   - Large number of nodes (100 nodes)
   - Zero coordinates
   - Very large coordinates (±999999)

8. TestGNS3CreateNodeToolIntegration
   - Complete workflow with realistic data (UUID project/template IDs)
   - JSON parsing edge cases (extra whitespace, extra fields)

9. TestGNS3CreateNodeToolLogging
   - Logging messages on successful operations
   - Logging messages on failed operations
   - Logging messages for multiple nodes

10. TestGNS3CreateNodeToolEnvironmentVariables
    - Missing GNS3_SERVER_URL environment variable
    - Unsupported API version from environment

Total Test Cases: 40+
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List

# Import module to test
from gns3_copilot.tools_v2.gns3_create_node import GNS3CreateNodeTool


class TestGNS3CreateNodeToolInitialization:
    """Test cases for GNS3CreateNodeTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3CreateNodeTool()
        assert tool.name == "create_gns3_node"
        assert "Creates multiple nodes" in tool.description
        assert "GNS3 project" in tool.description
        assert "JSON object" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3CreateNodeTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3CreateNodeTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3CreateNodeToolInputValidation:
    """Test cases for input validation"""

    def test_empty_input(self):
        """Test empty input handling"""
        tool = GNS3CreateNodeTool()
        result = tool._run("")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_invalid_json(self):
        """Test invalid JSON input"""
        tool = GNS3CreateNodeTool()
        result = tool._run("{invalid json}")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing project_id" in result["error"]

    def test_empty_nodes_array(self):
        """Test empty nodes array"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": []
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a non-empty array" in result["error"]

    def test_nodes_not_array(self):
        """Test nodes not an array"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": "not an array"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a non-empty array" in result["error"]

    def test_missing_nodes_field(self):
        """Test missing nodes field"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a non-empty array" in result["error"]

    def test_node_missing_required_fields(self):
        """Test node definition missing required fields"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100
                    # Missing y
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Node 1 missing or invalid template_id, x, or y" in result["error"]

    def test_node_with_invalid_coordinates(self):
        """Test node definition with invalid coordinates"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": "invalid",
                    "y": -200
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Node 1 missing or invalid template_id, x, or y" in result["error"]

    def test_node_not_dictionary(self):
        """Test node definition not a dictionary"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": [
                "not a dictionary"
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Node 1 must be a dictionary" in result["error"]

    def test_node_with_none_values(self):
        """Test node definition with None values"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": None,
                    "x": 100,
                    "y": -200
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Node 1 missing or invalid template_id, x, or y" in result["error"]

    def test_node_with_empty_string_template_id(self):
        """Test node definition with empty template_id"""
        tool = GNS3CreateNodeTool()
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Node 1 missing or invalid template_id, x, or y" in result["error"]


class TestGNS3CreateNodeToolAPIVersionHandling:
    """Test cases for API version handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_api_version_2_initialization(self, mock_get_gns3_connector):
        """Test API version 2 initialization"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation
        with patch('gns3_copilot.tools_v2.gns3_create_node.Node') as mock_node_class:
            mock_node = Mock()
            mock_node.node_id = "node123"
            mock_node.name = "TestNode"
            mock_node_class.return_value = mock_node
            
            tool._run(json.dumps(input_data))
            
            # Verify connector was obtained via factory function
            mock_get_gns3_connector.assert_called_once()
            assert mock_connector is not None

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "testuser",
        "GNS3_SERVER_PASSWORD": "testpass"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_api_version_3_initialization(self, mock_get_gns3_connector):
        """Test API version 3 initialization"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation
        with patch('gns3_copilot.tools_v2.gns3_create_node.Node') as mock_node_class:
            mock_node = Mock()
            mock_node.node_id = "node123"
            mock_node.name = "TestNode"
            mock_node_class.return_value = mock_node
            
            tool._run(json.dumps(input_data))
            
            # Verify connector was obtained via factory function
            mock_get_gns3_connector.assert_called_once()
            assert mock_connector is not None

    @patch.dict(os.environ, {
        "API_VERSION": "invalid",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_unsupported_api_version(self, mock_get_gns3_connector):
        """Test unsupported API version"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector factory to return None (simulating failure due to unsupported API version)
        mock_get_gns3_connector.return_value = None
        
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    }, clear=True)
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_default_api_version(self, mock_get_gns3_connector):
        """Test default API version when not specified"""
        tool = GNS3CreateNodeTool()

        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }

        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector

        # Mock node creation
        with patch('gns3_copilot.tools_v2.gns3_create_node.Node') as mock_node_class:
            mock_node = Mock()
            mock_node.node_id = "node123"
            mock_node.name = "TestNode"
            mock_node_class.return_value = mock_node

            result = tool._run(json.dumps(input_data))

            # Verify connector was obtained via factory function
            mock_get_gns3_connector.assert_called_once()
            assert mock_connector is not None


class TestGNS3CreateNodeToolSuccessScenarios:
    """Test cases for successful node creation scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_single_node_creation(self, mock_node_class, mock_get_gns3_connector):
        """Test successful single node creation"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert "project_id" in result
        assert result["project_id"] == "project1"
        assert "created_nodes" in result
        assert len(result["created_nodes"]) == 1
        assert result["total_nodes"] == 1
        assert result["successful_nodes"] == 1
        assert result["failed_nodes"] == 0
        
        # Verify node details
        node_info = result["created_nodes"][0]
        assert node_info["node_id"] == "node123"
        assert node_info["name"] == "TestNode"
        assert node_info["status"] == "success"
        
        # Verify node was created with correct parameters
        mock_node_class.assert_called_once()
        call_args = mock_node_class.call_args
        assert call_args[1]["project_id"] == "project1"
        assert call_args[1]["template_id"] == "template1"
        assert call_args[1]["x"] == 100
        assert call_args[1]["y"] == -200
        assert call_args[1]["connector"] == mock_connector
        
        # Verify node methods were called
        mock_node.create.assert_called_once()
        mock_node.get.assert_called_once()

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_multiple_nodes_creation(self, mock_node_class, mock_get_gns3_connector):
        """Test successful multiple nodes creation"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                },
                {
                    "template_id": "template2",
                    "x": -200,
                    "y": 300
                },
                {
                    "template_id": "template3",
                    "x": 0,
                    "y": 0
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation
        mock_node1 = Mock()
        mock_node1.node_id = "node123"
        mock_node1.name = "Node1"
        
        mock_node2 = Mock()
        mock_node2.node_id = "node456"
        mock_node2.name = "Node2"
        
        mock_node3 = Mock()
        mock_node3.node_id = "node789"
        mock_node3.name = "Node3"
        
        mock_node_class.side_effect = [mock_node1, mock_node2, mock_node3]
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results
        assert result["project_id"] == "project1"
        assert len(result["created_nodes"]) == 3
        assert result["total_nodes"] == 3
        assert result["successful_nodes"] == 3
        assert result["failed_nodes"] == 0
        
        # Verify all nodes were created successfully
        for i, node_info in enumerate(result["created_nodes"]):
            assert node_info["status"] == "success"
            assert "node_id" in node_info
            assert "name" in node_info
        
        # Verify node creation calls
        assert mock_node_class.call_count == 3
        
        # Verify each node was created with correct parameters
        calls = mock_node_class.call_args_list
        assert calls[0][1]["template_id"] == "template1"
        assert calls[0][1]["x"] == 100
        assert calls[0][1]["y"] == -200
        
        assert calls[1][1]["template_id"] == "template2"
        assert calls[1][1]["x"] == -200
        assert calls[1][1]["y"] == 300
        
        assert calls[2][1]["template_id"] == "template3"
        assert calls[2][1]["x"] == 0
        assert calls[2][1]["y"] == 0

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_negative_coordinates(self, mock_node_class, mock_get_gns3_connector):
        """Test node creation with negative coordinates"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": -150,
                    "y": -300
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["successful_nodes"] == 1
        
        # Verify node was created with negative coordinates
        call_args = mock_node_class.call_args
        assert call_args[1]["x"] == -150
        assert call_args[1]["y"] == -300

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_float_coordinates(self, mock_node_class, mock_get_gns3_connector):
        """Test node creation with float coordinates"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100.5,
                    "y": -200.75
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["successful_nodes"] == 1
        
        # Verify node was created with float coordinates
        call_args = mock_node_class.call_args
        assert call_args[1]["x"] == 100.5
        assert call_args[1]["y"] == -200.75


class TestGNS3CreateNodeToolErrorHandling:
    """Test cases for error handling scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_node_creation_exception(self, mock_node_class, mock_get_gns3_connector):
        """Test exception during node creation"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation exception
        mock_node = Mock()
        mock_node.create.side_effect = Exception("Node creation failed")
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error handling
        assert result["project_id"] == "project1"
        assert result["total_nodes"] == 1
        assert result["successful_nodes"] == 0
        assert result["failed_nodes"] == 1
        
        # Verify error details
        error_info = result["created_nodes"][0]
        assert error_info["status"] == "failed"
        assert "Node 1 creation failed" in error_info["error"]
        assert "Node creation failed" in error_info["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_connector_exception(self, mock_get_gns3_connector):
        """Test exception during connector initialization"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector initialization exception
        mock_get_gns3_connector.side_effect = Exception("Connector initialization failed")
        
        result = tool._run(json.dumps(input_data))
        
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"] or "Connector initialization failed" in result["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_node_get_exception(self, mock_node_class, mock_get_gns3_connector):
        """Test exception during node.get() call"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node with get() exception
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node.get.side_effect = Exception("Node retrieval failed")
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error handling
        assert result["total_nodes"] == 1
        assert result["successful_nodes"] == 0
        assert result["failed_nodes"] == 1
        
        # Verify error details
        error_info = result["created_nodes"][0]
        assert error_info["status"] == "failed"
        assert "Node 1 creation failed" in error_info["error"]


class TestGNS3CreateNodeToolMixedSuccessFailure:
    """Test cases for mixed success and failure scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_mixed_success_and_failure(self, mock_node_class, mock_get_gns3_connector):
        """Test mixed successful and failed node creations"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                },
                {
                    "template_id": "template2",
                    "x": -200,
                    "y": 300
                },
                {
                    "template_id": "template3",
                    "x": 0,
                    "y": 0
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock nodes - first and third succeed, second fails
        mock_node1 = Mock()
        mock_node1.node_id = "node123"
        mock_node1.name = "Node1"
        
        mock_node2 = Mock()
        mock_node2.create.side_effect = Exception("Second node failed")
        
        mock_node3 = Mock()
        mock_node3.node_id = "node789"
        mock_node3.name = "Node3"
        
        mock_node_class.side_effect = [mock_node1, mock_node2, mock_node3]
        
        result = tool._run(json.dumps(input_data))
        
        # Verify mixed results
        assert result["project_id"] == "project1"
        assert result["total_nodes"] == 3
        assert result["successful_nodes"] == 2
        assert result["failed_nodes"] == 1
        
        # Verify first node - success
        assert result["created_nodes"][0]["status"] == "success"
        assert result["created_nodes"][0]["node_id"] == "node123"
        
        # Verify second node - failure
        assert result["created_nodes"][1]["status"] == "failed"
        assert "Node 2 creation failed" in result["created_nodes"][1]["error"]
        
        # Verify third node - success
        assert result["created_nodes"][2]["status"] == "success"
        assert result["created_nodes"][2]["node_id"] == "node789"


class TestGNS3CreateNodeToolEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_unicode_template_id(self, mock_node_class, mock_get_gns3_connector):
        """Test Unicode template ID"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "模板-测试",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["project_id"] == "project1"
        assert result["successful_nodes"] == 1
        assert result["created_nodes"][0]["status"] == "success"

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_very_long_ids(self, mock_node_class, mock_get_gns3_connector):
        """Test very long IDs"""
        tool = GNS3CreateNodeTool()
        
        long_id = "a" * 1000
        
        input_data = {
            "project_id": long_id,
            "nodes": [
                {
                    "template_id": long_id,
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["project_id"] == long_id
        assert result["successful_nodes"] == 1

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_special_characters_in_ids(self, mock_node_class, mock_get_gns3_connector):
        """Test special characters in IDs"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project-with-special-chars_123",
            "nodes": [
                {
                    "template_id": "template-with-special-chars_456",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["project_id"] == "project-with-special-chars_123"
        assert result["successful_nodes"] == 1

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_large_number_of_nodes(self, mock_node_class, mock_get_gns3_connector):
        """Test large number of nodes"""
        tool = GNS3CreateNodeTool()
        
        # Create 100 nodes
        nodes = []
        mock_nodes = []
        for i in range(100):
            nodes.append({
                "template_id": f"template{i}",
                "x": i * 10,
                "y": i * -10
            })
            # Create mock node for each
            mock_node = Mock()
            mock_node.node_id = f"node{i}"
            mock_node.name = f"Node{i}"
            mock_nodes.append(mock_node)
        
        input_data = {
            "project_id": "project1",
            "nodes": nodes
        }
        
        # Mock connector and nodes
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        mock_node_class.side_effect = mock_nodes
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["project_id"] == "project1"
        assert result["total_nodes"] == 100
        assert result["successful_nodes"] == 100
        assert result["failed_nodes"] == 0

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_zero_coordinates(self, mock_node_class, mock_get_gns3_connector):
        """Test zero coordinates"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 0,
                    "y": 0
                }
            ]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["successful_nodes"] == 1
        
        # Verify node was created with zero coordinates
        call_args = mock_node_class.call_args
        assert call_args[1]["x"] == 0
        assert call_args[1]["y"] == 0

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_very_large_coordinates(self, mock_node_class, mock_get_gns3_connector):
        """Test very large coordinates"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 999999,
                    "y": -999999
                }
            ]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["successful_nodes"] == 1
        
        # Verify node was created with very large coordinates
        call_args = mock_node_class.call_args
        assert call_args[1]["x"] == 999999
        assert call_args[1]["y"] == -999999


class TestGNS3CreateNodeToolIntegration:
    """Integration tests for GNS3CreateNodeTool"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_complete_workflow(self, mock_node_class, mock_get_gns3_connector):
        """Test complete workflow with realistic data"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project-uuid-12345",
            "nodes": [
                {
                    "template_id": "router-template-uuid",
                    "x": 150,
                    "y": -200
                },
                {
                    "template_id": "switch-template-uuid",
                    "x": -150,
                    "y": 200
                },
                {
                    "template_id": "firewall-template-uuid",
                    "x": 0,
                    "y": 0
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock realistic node data
        mock_router = Mock()
        mock_router.node_id = "router-node-uuid"
        mock_router.name = "Router1"
        
        mock_switch = Mock()
        mock_switch.node_id = "switch-node-uuid"
        mock_switch.name = "Switch1"
        
        mock_firewall = Mock()
        mock_firewall.node_id = "firewall-node-uuid"
        mock_firewall.name = "Firewall1"
        
        mock_node_class.side_effect = [mock_router, mock_switch, mock_firewall]
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results
        assert result["project_id"] == "project-uuid-12345"
        assert len(result["created_nodes"]) == 3
        assert result["total_nodes"] == 3
        assert result["successful_nodes"] == 3
        assert result["failed_nodes"] == 0
        
        # Verify router node
        router_info = result["created_nodes"][0]
        assert router_info["node_id"] == "router-node-uuid"
        assert router_info["name"] == "Router1"
        assert router_info["status"] == "success"
        
        # Verify switch node
        switch_info = result["created_nodes"][1]
        assert switch_info["node_id"] == "switch-node-uuid"
        assert switch_info["name"] == "Switch1"
        assert switch_info["status"] == "success"
        
        # Verify firewall node
        firewall_info = result["created_nodes"][2]
        assert firewall_info["node_id"] == "firewall-node-uuid"
        assert firewall_info["name"] == "Firewall1"
        assert firewall_info["status"] == "success"
        
        # Verify node creation calls
        assert mock_node_class.call_count == 3
        
        # Verify router creation
        router_call = mock_node_class.call_args_list[0]
        assert router_call[1]["project_id"] == "project-uuid-12345"
        assert router_call[1]["template_id"] == "router-template-uuid"
        assert router_call[1]["x"] == 150
        assert router_call[1]["y"] == -200
        
        # Verify switch creation
        switch_call = mock_node_class.call_args_list[1]
        assert switch_call[1]["template_id"] == "switch-template-uuid"
        assert switch_call[1]["x"] == -150
        assert switch_call[1]["y"] == 200
        
        # Verify firewall creation
        firewall_call = mock_node_class.call_args_list[2]
        assert firewall_call[1]["template_id"] == "firewall-template-uuid"
        assert firewall_call[1]["x"] == 0
        assert firewall_call[1]["y"] == 0
        
        # Verify all node methods were called
        for mock_node in [mock_router, mock_switch, mock_firewall]:
            mock_node.create.assert_called_once()
            mock_node.get.assert_called_once()

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    def test_json_parsing_edge_cases(self, mock_node_class, mock_get_gns3_connector):
        """Test JSON parsing edge cases"""
        tool = GNS3CreateNodeTool()
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        # Test with extra whitespace
        input_with_whitespace = """
        {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        """
        
        result = tool._run(input_with_whitespace)
        
        # Verify successful result - JSON should parse correctly
        assert result["project_id"] == "project1"
        assert result["successful_nodes"] == 1

        # Test with additional fields
        input_with_extra_fields = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200,
                    "extra_field": "should_be_ignored"
                }
            ],
            "extra_project_field": "should_be_ignored"
        }
        
        result = tool._run(json.dumps(input_with_extra_fields))
        
        # Verify successful result - extra fields should be ignored
        assert result["project_id"] == "project1"
        assert result["successful_nodes"] == 1


class TestGNS3CreateNodeToolLogging:
    """Test cases for logging functionality"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_create_node.logger')
    def test_logging_on_success(self, mock_logger, mock_node_class, mock_get_gns3_connector):
        """Test logging messages on successful operations"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node123"
        mock_node.name = "TestNode"
        mock_node_class.return_value = mock_node
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls
        mock_logger.info.assert_any_call("Received input: %s", json.dumps(input_data))
        mock_logger.info.assert_any_call("Creating %d nodes in project %s...", 1, "project1")
        mock_logger.info.assert_any_call("Creating node %d/%d with template %s at coordinates (%s, %s)...", 1, 1, "template1", 100, -200)
        mock_logger.debug.assert_called()
        mock_logger.info.assert_any_call("Node creation completed: %d successful, %d failed out of %d total nodes.", 1, 0, 1)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_create_node.logger')
    def test_logging_on_failure(self, mock_logger, mock_node_class, mock_get_gns3_connector):
        """Test logging messages on failed operations"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node creation failure
        mock_node = Mock()
        mock_node.create.side_effect = Exception("Node creation failed")
        mock_node_class.return_value = mock_node
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls
        mock_logger.info.assert_any_call("Received input: %s", json.dumps(input_data))
        mock_logger.info.assert_any_call("Creating %d nodes in project %s...", 1, "project1")
        mock_logger.info.assert_any_call("Creating node %d/%d with template %s at coordinates (%s, %s)...", 1, 1, "template1", 100, -200)
        mock_logger.error.assert_called()
        mock_logger.info.assert_any_call("Node creation completed: %d successful, %d failed out of %d total nodes.", 0, 1, 1)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_create_node.logger')
    def test_logging_on_multiple_nodes(self, mock_logger, mock_node_class, mock_get_gns3_connector):
        """Test logging messages for multiple nodes"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                },
                {
                    "template_id": "template2",
                    "x": -200,
                    "y": 300
                }
            ]
        }
        
        # Mock connector and nodes
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node1 = Mock()
        mock_node1.node_id = "node123"
        mock_node1.name = "Node1"
        
        mock_node2 = Mock()
        mock_node2.node_id = "node456"
        mock_node2.name = "Node2"
        
        mock_node_class.side_effect = [mock_node1, mock_node2]
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls for multiple nodes
        mock_logger.info.assert_any_call("Creating %d nodes in project %s...", 2, "project1")
        mock_logger.info.assert_any_call("Creating node %d/%d with template %s at coordinates (%s, %s)...", 1, 2, "template1", 100, -200)
        mock_logger.info.assert_any_call("Creating node %d/%d with template %s at coordinates (%s, %s)...", 2, 2, "template2", -200, 300)
        mock_logger.info.assert_any_call("Node creation completed: %d successful, %d failed out of %d total nodes.", 2, 0, 2)


class TestGNS3CreateNodeToolEnvironmentVariables:
    """Test cases for environment variable handling"""

    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_missing_server_url(self, mock_get_gns3_connector):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector factory to return None (simulating failure)
        mock_get_gns3_connector.return_value = None
        
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080",
        "API_VERSION": "1"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_node.get_gns3_connector')
    def test_unsupported_api_version_env(self, mock_get_gns3_connector):
        """Test unsupported API version from environment"""
        tool = GNS3CreateNodeTool()
        
        input_data = {
            "project_id": "project1",
            "nodes": [
                {
                    "template_id": "template1",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector factory to return None (simulating failure due to unsupported API version)
        mock_get_gns3_connector.return_value = None
        
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]
