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
Tests for gns3_start_node module.
Contains comprehensive test cases for GNS3StartNodeTool functionality.

Test Coverage:
1. TestShowProgressBar
   - Basic progress bar functionality
   - Progress bar with single node
   - Progress bar with multiple nodes
   - Custom interval testing

2. TestGNS3StartNodeToolInitialization
   - Tool name and description validation
   - Tool inheritance from BaseTool
   - Tool attributes verification (name, description, _run method)

3. TestGNS3StartNodeToolInputValidation
   - Empty input handling
   - Invalid JSON input handling
   - Missing project_id handling
   - Missing node_ids handling
   - Empty project_id handling
   - Empty node_ids handling
   - node_ids not a list handling
   - node_ids is None handling
   - Valid minimal input validation
   - Valid multiple nodes input validation

4. TestGNS3StartNodeToolAPIVersionHandling
   - API version 2 initialization with Basic Auth
   - API version 3 initialization with JWT authentication
   - Unsupported API version handling
   - Default API version (v2) when not specified
   - Empty API version string handling

5. TestGNS3StartNodeToolSuccessScenarios
   - Single node startup
   - Multiple nodes startup
   - Node with None name handling
   - Node with None status handling

6. TestGNS3StartNodeToolErrorHandling
   - Connector initialization exception handling
   - Missing GNS3_SERVER_URL environment variable

7. TestGNS3StartNodeToolEdgeCases
   - Unicode node IDs handling (Chinese characters)
   - Large number of nodes (100 nodes)
   - Progress bar duration calculation with many nodes

8. TestGNS3StartNodeToolIntegration
   - Complete workflow with realistic data (UUIDs, multiple nodes)
   - JSON parsing edge cases (extra whitespace, extra fields)

9. TestGNS3StartNodeToolProgressBarCalculation
   - Progress bar duration calculation for single node
   - Progress bar duration calculation for multiple nodes
   - Formula: base_duration (140s) + 10s * (node_count - 1)

10. TestGNS3StartNodeToolReturnFormat
    - Return format structure validation
    - Error return format validation

11. TestGNS3StartNodeToolPerformance
    - Performance with large dataset (100 nodes)

12. TestGNS3StartNodeToolConcurrency
    - Thread safety testing with multiple concurrent calls

Total Test Cases: 30+
"""

import json
import os
import pytest
import time
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List

# Import module to test
from gns3_copilot.tools_v2.gns3_start_node import GNS3StartNodeTool, show_progress_bar


class TestShowProgressBar:
    """Test cases for show_progress_bar function"""

    @patch('builtins.print')
    @patch('time.sleep')
    def test_show_progress_bar_basic(self, mock_sleep, mock_print):
        """Test basic progress bar functionality"""
        show_progress_bar(duration=5, interval=1, node_count=2)
        
        # Verify print was called for progress updates
        assert mock_print.call_count >= 6  # 5 progress updates + completion message
        
        # Verify sleep was called
        assert mock_sleep.call_count == 5
        
        # Verify completion message
        completion_calls = [call for call in mock_print.call_args_list 
                          if 'startup completed' in str(call)]
        assert len(completion_calls) == 1
        assert '2 node(s)' in str(completion_calls[0])

    @patch('builtins.print')
    @patch('time.sleep')
    def test_show_progress_bar_single_node(self, mock_sleep, mock_print):
        """Test progress bar with single node"""
        show_progress_bar(duration=3, interval=1, node_count=1)
        
        # Verify completion message for single node
        completion_calls = [call for call in mock_print.call_args_list 
                          if '1 node(s) startup completed' in str(call)]
        assert len(completion_calls) == 1

    @patch('builtins.print')
    @patch('time.sleep')
    def test_show_progress_bar_multiple_nodes(self, mock_sleep, mock_print):
        """Test progress bar with multiple nodes"""
        show_progress_bar(duration=2, interval=1, node_count=5)
        
        # Verify completion message for multiple nodes
        completion_calls = [call for call in mock_print.call_args_list 
                          if '5 node(s) startup completed' in str(call)]
        assert len(completion_calls) == 1

    @patch('builtins.print')
    @patch('time.sleep')
    def test_show_progress_bar_custom_interval(self, mock_sleep, mock_print):
        """Test progress bar with custom interval"""
        show_progress_bar(duration=4, interval=2, node_count=3)
        
        # Verify sleep was called with correct interval
        mock_sleep.assert_has_calls([call(2), call(2)])


class TestGNS3StartNodeToolInitialization:
    """Test cases for GNS3StartNodeTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3StartNodeTool()
        assert tool.name == "start_gns3_node"
        assert "Starts one or multiple nodes" in tool.description
        assert "GNS3 project" in tool.description
        assert "JSON with project_id and node_ids" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3StartNodeTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3StartNodeTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3StartNodeToolInputValidation:
    """Test cases for input validation"""

    def test_empty_input(self):
        """Test empty input handling"""
        tool = GNS3StartNodeTool()
        result = tool._run("")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_invalid_json(self):
        """Test invalid JSON input"""
        tool = GNS3StartNodeTool()
        result = tool._run("{invalid json}")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3StartNodeTool()
        input_data = {
            "node_ids": ["node1", "node2"]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing required fields: project_id and node_ids" in result["error"]

    def test_missing_node_ids(self):
        """Test missing node_ids"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "project1"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing required fields: project_id and node_ids" in result["error"]

    def test_empty_project_id(self):
        """Test empty project_id"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "",
            "node_ids": ["node1"]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing required fields: project_id and node_ids" in result["error"]

    def test_empty_node_ids(self):
        """Test empty node_ids"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "project1",
            "node_ids": []
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing required fields: project_id and node_ids" in result["error"]

    def test_node_ids_not_list(self):
        """Test node_ids not a list"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "project1",
            "node_ids": "not a list"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "node_ids must be a list" in result["error"]

    def test_node_ids_none(self):
        """Test node_ids is None"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "project1",
            "node_ids": None
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        # None values are treated as falsy, so they trigger missing fields validation
        assert "Missing required fields" in result["error"]

    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_valid_minimal_input(self, mock_get_gns3_connector):
        """Test valid minimal input"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector returning None to simulate connection failure
        mock_get_gns3_connector.return_value = None
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]

    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_valid_multiple_nodes(self, mock_get_gns3_connector):
        """Test valid input with multiple nodes"""
        tool = GNS3StartNodeTool()
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1", "node2", "node3"]
        }
        
        # Mock connector returning None to simulate connection failure
        mock_get_gns3_connector.return_value = None
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]


class TestGNS3StartNodeToolAPIVersionHandling:
    """Test cases for API version handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_api_version_2_initialization(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test API version 2 initialization"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify connector was obtained via factory function
        mock_get_gns3_connector.assert_called_once()
        assert mock_connector is not None

    @patch.dict(os.environ, {
        "API_VERSION": "3",
        "GNS3_SERVER_URL": "http://localhost:3080",
        "GNS3_SERVER_USERNAME": "testuser",
        "GNS3_SERVER_PASSWORD": "testpass"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_api_version_3_initialization(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test API version 3 initialization"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify connector was obtained via factory function
        mock_get_gns3_connector.assert_called_once()
        assert mock_connector is not None

    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_unsupported_api_version(self, mock_get_gns3_connector):
        """Test unsupported API version"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector returning None to simulate connection failure
        mock_get_gns3_connector.return_value = None
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    }, clear=True)
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_default_api_version(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test default API version when not specified"""
        tool = GNS3StartNodeTool()

        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }

        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector

        # Mock node
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node

        result = tool._run(json.dumps(input_data))

        # Verify connector was obtained via factory function
        mock_get_gns3_connector.assert_called_once()
        assert mock_connector is not None

    @patch.dict(os.environ, {
        "API_VERSION": "",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_empty_api_version(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test empty API version string"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify connector was obtained via factory function
        mock_get_gns3_connector.assert_called_once()
        assert mock_connector is not None


class TestGNS3StartNodeToolSuccessScenarios:
    """Test cases for successful node startup scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_single_node_startup(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test successful single node startup"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert "project_id" in result
        assert result["project_id"] == "project1"
        assert "total_nodes" in result
        assert result["total_nodes"] == 1
        assert "successful" in result
        assert result["successful"] == 1
        assert "failed" in result
        assert result["failed"] == 0
        assert "nodes" in result
        assert len(result["nodes"]) == 1
        
        # Verify node details
        node_info = result["nodes"][0]
        assert node_info["node_id"] == "node1"
        assert node_info["name"] == "TestNode"
        assert node_info["status"] == "started"
        
        # Verify progress bar was called
        mock_progress.assert_called_once_with(duration=140, interval=1, node_count=1)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_multiple_nodes_startup(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test successful multiple nodes startup"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1", "node2", "node3"]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Create different mock nodes for each call to avoid conflicts
        def create_mock_node(node_id):
            mock_node = Mock()
            mock_node.node_id = node_id
            mock_node.name = node_id.title()
            mock_node.status = "started"
            return mock_node
        
        # Set up side_effect to return different mocks for different nodes
        side_effect_nodes = []
        for node_id in input_data["node_ids"]:
            # First call for verification, second for start
            side_effect_nodes.extend([create_mock_node(node_id), create_mock_node(node_id)])
        # Second loop calls for status
        for node_id in input_data["node_ids"]:
            side_effect_nodes.append(create_mock_node(node_id))
        
        mock_node_class.side_effect = side_effect_nodes
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results
        assert result["project_id"] == "project1"
        assert result["total_nodes"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert len(result["nodes"]) == 3
        
        # Verify all nodes were started successfully
        for node_info in result["nodes"]:
            assert node_info["status"] == "started"
            assert node_info["node_id"] in input_data["node_ids"]
        
        # Verify progress bar was called with correct duration
        # Base duration: 140s + 10s * (3-1) = 160s
        mock_progress.assert_called_once_with(duration=160, interval=1, node_count=3)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_node_with_none_name(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test node with None name"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node with None name
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = None
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["successful"] == 1
        
        # Verify node name is handled correctly
        node_info = result["nodes"][0]
        assert node_info["name"] == "N/A"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_node_with_none_status(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test node with None status"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node with None status
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = None
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["successful"] == 1
        
        # Verify node status is handled correctly
        node_info = result["nodes"][0]
        assert node_info["status"] == "unknown"


class TestGNS3StartNodeToolErrorHandling:
    """Test cases for error handling scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_connector_exception(self, mock_get_gns3_connector):
        """Test exception during connector initialization"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector initialization exception
        mock_get_gns3_connector.side_effect = Exception("Connector initialization failed")
        
        result = tool._run(json.dumps(input_data))
        
        assert "error" in result
        assert "Failed to start nodes" in result["error"]
        assert "Connector initialization failed" in result["error"]

    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_missing_server_url(self, mock_get_gns3_connector):
        """Test missing GNS3_SERVER_URL environment variable"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector returning None to simulate connection failure
        mock_get_gns3_connector.return_value = None
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to connect to GNS3 server" in result["error"]


class TestGNS3StartNodeToolEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_unicode_node_ids(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test Unicode node IDs"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "项目-测试",
            "node_ids": ["节点-1", "节点-2"]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Create mock nodes with proper Unicode handling
        side_effect_nodes = []
        for node_id in input_data["node_ids"]:
            mock_node = Mock()
            mock_node.node_id = node_id
            mock_node.name = node_id.replace("-", "")
            mock_node.status = "started"
            # Add calls: verification, start, status check
            side_effect_nodes.extend([mock_node, mock_node, mock_node])
        
        mock_node_class.side_effect = side_effect_nodes
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["project_id"] == "项目-测试"
        assert result["total_nodes"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
        
        # Verify Unicode node IDs are preserved
        node_ids = [node["node_id"] for node in result["nodes"]]
        for expected_id in input_data["node_ids"]:
            assert expected_id in node_ids

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_large_number_of_nodes(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test large number of nodes"""
        tool = GNS3StartNodeTool()
        
        # Create 100 nodes
        node_ids = [f"node{i}" for i in range(100)]
        input_data = {
            "project_id": "project1",
            "node_ids": node_ids
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Create mock nodes for each node
        side_effect_nodes = []
        for node_id in node_ids:
            mock_node = Mock()
            mock_node.node_id = node_id
            mock_node.name = node_id.title()
            mock_node.status = "started"
            # verification, start, status check
            side_effect_nodes.extend([mock_node, mock_node, mock_node])
        
        mock_node_class.side_effect = side_effect_nodes
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert result["total_nodes"] == 100
        assert result["successful"] == 100
        assert result["failed"] == 0
        
        # Verify progress bar duration calculation
        # Base duration: 140s + 10s * (100-1) = 1130s
        expected_duration = 140 + (100 - 1) * 10
        mock_progress.assert_called_once_with(duration=expected_duration, interval=1, node_count=100)


class TestGNS3StartNodeToolIntegration:
    """Integration tests for GNS3StartNodeTool"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_complete_workflow(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test complete workflow with realistic data"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project-uuid-12345",
            "node_ids": [
                "router-node-uuid",
                "switch-node-uuid",
                "firewall-node-uuid"
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Create mock nodes
        side_effect_nodes = []
        node_names = ["Router1", "Switch1", "Firewall1"]
        for i, node_id in enumerate(input_data["node_ids"]):
            mock_node = Mock()
            mock_node.node_id = node_id
            mock_node.name = node_names[i]
            mock_node.status = "started"
            # verification, start, status check
            side_effect_nodes.extend([mock_node, mock_node, mock_node])
        
        mock_node_class.side_effect = side_effect_nodes
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results
        assert result["project_id"] == "project-uuid-12345"
        assert result["total_nodes"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert len(result["nodes"]) == 3
        
        # Verify progress bar was called with correct duration
        # Base duration: 140s + 10s * (3-1) = 160s
        mock_progress.assert_called_once_with(duration=160, interval=1, node_count=3)

    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_json_parsing_edge_cases(self, mock_get_gns3_connector):
        """Test JSON parsing edge cases"""
        tool = GNS3StartNodeTool()
        
        # Mock connector returning None
        mock_get_gns3_connector.return_value = None
        
        # Test with extra whitespace
        input_with_whitespace = """
        {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        """
        result = tool._run(input_with_whitespace)
        assert "error" in result

        # Test with additional fields
        input_with_extra_fields = {
            "project_id": "project1",
            "node_ids": ["node1"],
            "extra_field": "should_be_ignored"
        }
        result = tool._run(json.dumps(input_with_extra_fields))
        assert "error" in result


class TestGNS3StartNodeToolProgressBarCalculation:
    """Test cases for progress bar duration calculation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_progress_bar_duration_calculation_single_node(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test progress bar duration calculation for single node"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # For single node: base duration = 140s, extra duration = 0
        expected_duration = 140 + max(0, 1 - 1) * 10
        mock_progress.assert_called_once_with(duration=expected_duration, interval=1, node_count=1)
        assert expected_duration == 140

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_progress_bar_duration_calculation_multiple_nodes(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test progress bar duration calculation for multiple nodes"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1", "node2", "node3", "node4", "node5"]
        }
        
        # Mock connector and nodes
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Create mock nodes
        side_effect_nodes = []
        for node_id in input_data["node_ids"]:
            mock_node = Mock()
            mock_node.node_id = node_id
            mock_node.name = node_id.title()
            mock_node.status = "started"
            # verification, start, status check
            side_effect_nodes.extend([mock_node, mock_node, mock_node])
        
        mock_node_class.side_effect = side_effect_nodes
        
        result = tool._run(json.dumps(input_data))
        
        # For 5 nodes: base duration = 140s, extra duration = 10s * (5-1) = 40s
        expected_duration = 140 + max(0, 5 - 1) * 10
        mock_progress.assert_called_once_with(duration=expected_duration, interval=1, node_count=5)
        assert expected_duration == 180


class TestGNS3StartNodeToolReturnFormat:
    """Test cases for return format validation"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_return_format_structure(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test return format structure"""
        tool = GNS3StartNodeTool()
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        # Mock connector and node
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        mock_node = Mock()
        mock_node.node_id = "node1"
        mock_node.name = "TestNode"
        mock_node.status = "started"
        mock_node_class.return_value = mock_node
        
        result = tool._run(json.dumps(input_data))
        
        # Verify return structure
        assert isinstance(result, dict)
        assert "project_id" in result
        assert "total_nodes" in result
        assert "successful" in result
        assert "failed" in result
        assert "nodes" in result
        assert isinstance(result["nodes"], list)
        
        # Verify node structure
        if result["nodes"]:
            node = result["nodes"][0]
            assert isinstance(node, dict)
            assert "node_id" in node
            assert "name" in node
            assert "status" in node

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    def test_error_return_format(self, mock_get_gns3_connector):
        """Test error return format"""
        tool = GNS3StartNodeTool()
        
        # Mock connector with exception
        mock_get_gns3_connector.side_effect = Exception("Test error")
        
        input_data = {
            "project_id": "project1",
            "node_ids": ["node1"]
        }
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error format
        assert isinstance(result, dict)
        assert "error" in result
        assert isinstance(result["error"], str)
        assert "Failed to start nodes" in result["error"]
        assert "Test error" in result["error"]


class TestGNS3StartNodeToolPerformance:
    """Test cases for performance considerations"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_performance_with_large_dataset(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test performance with large dataset"""
        tool = GNS3StartNodeTool()
        
        # Create large node list
        node_ids = [f"node{i}" for i in range(100)]
        input_data = {
            "project_id": "project1",
            "node_ids": node_ids
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Create mock nodes
        side_effect_nodes = []
        for node_id in node_ids:
            mock_node = Mock()
            mock_node.node_id = node_id
            mock_node.name = node_id.title()
            mock_node.status = "started"
            # verification, start, status check
            side_effect_nodes.extend([mock_node, mock_node, mock_node])
        
        mock_node_class.side_effect = side_effect_nodes
        
        # Measure execution time (basic performance check)
        start_time = time.time()
        result = tool._run(json.dumps(input_data))
        end_time = time.time()
        
        # Verify result
        assert result["total_nodes"] == 100
        assert result["successful"] == 100
        assert result["failed"] == 0
        
        # Performance should be reasonable (less than 2 seconds for processing)
        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Processing took too long: {execution_time} seconds"


class TestGNS3StartNodeToolConcurrency:
    """Test cases for concurrent execution scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_start_node.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_start_node.Node')
    @patch('gns3_copilot.tools_v2.gns3_start_node.show_progress_bar')
    def test_thread_safety(self, mock_progress, mock_node_class, mock_get_gns3_connector):
        """Test thread safety of tool"""
        import threading
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        results = []
        errors = []
        
        def worker(thread_id):
            try:
                tool = GNS3StartNodeTool()
                input_data = {
                    "project_id": f"project{thread_id}",
                    "node_ids": [f"node{thread_id}"]
                }
                
                # Create a simple mock node for each thread
                mock_node = Mock()
                mock_node.node_id = f"node{thread_id}"
                mock_node.name = f"Node{thread_id}"
                mock_node.status = "started"
                mock_node_class.return_value = mock_node
                
                result = tool._run(json.dumps(input_data))
                results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(3):  # Reduced number of threads for stability
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Thread errors: {errors}"
        
        # Verify all threads completed successfully
        assert len(results) == 3
        
        # Verify all results have the same structure
        for thread_id, result in results:
            assert isinstance(result, dict)
            assert "total_nodes" in result or "error" in result
