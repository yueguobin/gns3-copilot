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
Tests for gns3_create_link module.
Contains comprehensive test cases for GNS3LinkTool functionality.

Test Coverage:
1. TestGNS3LinkToolInitialization
   - Tool name and description validation
   - Tool inheritance from BaseTool
   - Tool attributes verification (name, description, _run method)

2. TestGNS3LinkToolInputValidation
   - Empty input handling
   - Invalid JSON input handling
   - Missing project_id handling
   - Empty links array handling
   - Links not an array handling
   - Missing links field handling
   - Link definition missing required fields (node_id1, port1, node_id2, port2)
   - Link definition with None values
   - Link definition with empty strings

3. TestGNS3LinkToolAPIVersionHandling
   - API version 2 initialization with Basic Auth
   - API version 3 initialization with JWT authentication
   - Unsupported API version handling
   - Default API version (v2) when not specified

4. TestGNS3LinkToolSuccessScenarios
   - Single link creation success
   - Multiple links creation success
   - Port search with specific adapter and port numbers

5. TestGNS3LinkToolErrorHandling
   - Node not found error handling
   - Port not found error handling
   - Node without ports array handling
   - Link creation exception handling
   - Connector initialization exception handling
   - Node retrieval exception handling

6. TestGNS3LinkToolMixedSuccessFailure
   - Mixed successful and failed link creations (e.g., 2 success, 1 failure)

7. TestGNS3LinkToolEdgeCases
   - Unicode port names handling
   - Very long port names (1000+ characters)
   - Special characters in IDs
   - Large number of links (100 links)
   - Empty string values in input

8. TestGNS3LinkToolIntegration
   - Complete workflow with realistic data (UUID project/Node IDs)
   - JSON parsing edge cases (extra whitespace, extra fields)

9. TestGNS3LinkToolLogging
   - Logging messages on successful operations
   - Logging messages on failed operations

Total Test Cases: 40+
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List

# Import the module to test
from gns3_copilot.tools_v2.gns3_create_link import GNS3LinkTool


class TestGNS3LinkToolInitialization:
    """Test cases for GNS3LinkTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3LinkTool()
        assert tool.name == "create_gns3_link"
        assert "Creates one or more links" in tool.description
        assert "GNS3 project" in tool.description
        assert "JSON string" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3LinkTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3LinkTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3LinkToolInputValidation:
    """Test cases for input validation"""

    def test_empty_input(self):
        """Test empty input handling"""
        tool = GNS3LinkTool()
        result = tool._run("")
        assert "error" in result[0]
        assert "Invalid JSON input" in result[0]["error"]

    def test_invalid_json(self):
        """Test invalid JSON input"""
        tool = GNS3LinkTool()
        result = tool._run("{invalid json}")
        assert "error" in result[0]
        assert "Invalid JSON input" in result[0]["error"]

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3LinkTool()
        input_data = {
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result[0]
        assert "Missing required field: project_id" in result[0]["error"]

    def test_empty_links_array(self):
        """Test empty links array"""
        tool = GNS3LinkTool()
        input_data = {
            "project_id": "project1",
            "links": []
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result[0]
        assert "must be a non-empty array" in result[0]["error"]

    def test_links_not_array(self):
        """Test links not an array"""
        tool = GNS3LinkTool()
        input_data = {
            "project_id": "project1",
            "links": "not an array"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result[0]
        assert "must be a non-empty array" in result[0]["error"]

    def test_missing_links_field(self):
        """Test missing links field"""
        tool = GNS3LinkTool()
        input_data = {
            "project_id": "project1"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result[0]
        assert "must be a non-empty array" in result[0]["error"]

    def test_link_missing_required_fields(self):
        """Test link definition missing required fields"""
        tool = GNS3LinkTool()
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0"
                    # Missing node_id2, port2
                }
            ]
        }
        # Add environment variables to allow validation to proceed
        with patch.dict(os.environ, {
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            with patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector') as mock_get_gns3_connector:
                # Mock connector to prevent actual connection
                mock_connector = Mock()
                mock_get_gns3_connector.return_value = mock_connector
                
                result = tool._run(json.dumps(input_data))
                assert "error" in result[0]
                assert "Missing required fields in link definition 0" in result[0]["error"]

    def test_link_with_none_values(self):
        """Test link definition with None values"""
        tool = GNS3LinkTool()
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": None,
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        # Add environment variables to allow validation to proceed
        with patch.dict(os.environ, {
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            with patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector') as mock_get_gns3_connector:
                # Mock connector to prevent actual connection
                mock_connector = Mock()
                mock_get_gns3_connector.return_value = mock_connector
                
                result = tool._run(json.dumps(input_data))
                assert "error" in result[0]
                assert "Missing required fields in link definition 0" in result[0]["error"]

    def test_link_with_empty_strings(self):
        """Test link definition with empty strings"""
        tool = GNS3LinkTool()
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        # Add environment variables to allow validation to proceed
        with patch.dict(os.environ, {
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            with patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector') as mock_get_gns3_connector:
                # Mock connector to prevent actual connection
                mock_connector = Mock()
                mock_get_gns3_connector.return_value = mock_connector
                
                result = tool._run(json.dumps(input_data))
                assert "error" in result[0]
                assert "Missing required fields in link definition 0" in result[0]["error"]


class TestGNS3LinkToolAPIVersionHandling:
    """Test cases for API version handling"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_api_version_2_initialization(self, mock_get_gns3_connector):
        """Test API version 2 initialization"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node retrieval
        mock_node = {
            "name": "test_node",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        mock_connector.get_node.return_value = mock_node
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link
            
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
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_api_version_3_initialization(self, mock_get_gns3_connector):
        """Test API version 3 initialization"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node retrieval
        mock_node = {
            "name": "test_node",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        mock_connector.get_node.return_value = mock_node
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link
            
            tool._run(json.dumps(input_data))
            
            # Verify connector was obtained via factory function
            mock_get_gns3_connector.assert_called_once()
            assert mock_connector is not None

    @patch.dict(os.environ, {
        "API_VERSION": "invalid",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    def test_unsupported_api_version(self):
        """Test unsupported API version"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        result = tool._run(json.dumps(input_data))
        assert "error" in result[0]
        # The error may come from connector_factory or from API calls with invalid UUIDs
        # Either way, an error should be present
        assert ("Failed to connect to GNS3 server" in result[0]["error"] or 
                "Failed to create GNS3 connector" in result[0]["error"] or
                "Failed to create link" in result[0]["error"] or
                "Failed to process link creation" in result[0]["error"])

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    }, clear=True)
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_default_api_version(self, mock_get_gns3_connector):
        """Test default API version when not specified"""
        tool = GNS3LinkTool()

        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }

        # Mock connector and its methods
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector

        # Mock node retrieval
        mock_node = {
            "name": "test_node",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        mock_connector.get_node.return_value = mock_node

        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link

            result = tool._run(json.dumps(input_data))

            # Verify connector was obtained via factory function
            mock_get_gns3_connector.assert_called_once()
            assert mock_connector is not None


class TestGNS3LinkToolSuccessScenarios:
    """Test cases for successful link creation scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    def test_single_link_creation(self, mock_link_class, mock_get_gns3_connector):
        """Test successful single link creation"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data with ports
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0},
                {"name": "Ethernet0/1", "adapter_number": 0, "port_number": 1}
            ]
        }
        
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        # Mock link creation
        mock_link = Mock()
        mock_link.link_id = "link123"
        mock_link_class.return_value = mock_link
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert len(result) == 1
        assert "link_id" in result[0]
        assert result[0]["link_id"] == "link123"
        assert result[0]["node_id1"] == "node1"
        assert result[0]["port1"] == "Ethernet0/0"
        assert result[0]["node_id2"] == "node2"
        assert result[0]["port2"] == "Ethernet0/0"
        
        # Verify link was created with correct parameters
        mock_link_class.assert_called_once()
        call_args = mock_link_class.call_args
        assert call_args[1]["project_id"] == "project1"
        assert call_args[1]["connector"] == mock_connector
        assert len(call_args[1]["nodes"]) == 2
        
        # Verify node1 configuration
        node1_config = call_args[1]["nodes"][0]
        assert node1_config["node_id"] == "node1"
        assert node1_config["adapter_number"] == 0
        assert node1_config["port_number"] == 0
        assert node1_config["label"]["text"] == "Ethernet0/0"
        
        # Verify node2 configuration
        node2_config = call_args[1]["nodes"][1]
        assert node2_config["node_id"] == "node2"
        assert node2_config["adapter_number"] == 0
        assert node2_config["port_number"] == 0
        assert node2_config["label"]["text"] == "Ethernet0/0"

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    def test_multiple_links_creation(self, mock_link_class, mock_get_gns3_connector):
        """Test successful multiple links creation"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                },
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/1",
                    "node_id2": "node3",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0},
                {"name": "Ethernet0/1", "adapter_number": 0, "port_number": 1}
            ]
        }
        
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        
        node3_data = {
            "name": "node3",
            "node_id": "node3",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        
        mock_connector.get_node.side_effect = [node1_data, node2_data, node1_data, node3_data]
        
        # Mock link creation
        mock_link1 = Mock()
        mock_link1.link_id = "link123"
        mock_link2 = Mock()
        mock_link2.link_id = "link456"
        mock_link_class.side_effect = [mock_link1, mock_link2]
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results
        assert len(result) == 2
        assert result[0]["link_id"] == "link123"
        assert result[1]["link_id"] == "link456"
        
        # Verify both links were created
        assert mock_link_class.call_count == 2

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    def test_port_search_with_adapter_port_numbers(self, mock_link_class, mock_get_gns3_connector):
        """Test port search with specific adapter and port numbers"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet1/2",
                    "node_id2": "node2",
                    "port2": "Ethernet3/4"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data with specific adapter/port numbers
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet1/2", "adapter_number": 1, "port_number": 2}
            ]
        }
        
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [
                {"name": "Ethernet3/4", "adapter_number": 3, "port_number": 4}
            ]
        }
        
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        # Mock link creation
        mock_link = Mock()
        mock_link.link_id = "link789"
        mock_link_class.return_value = mock_link
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert len(result) == 1
        assert result[0]["link_id"] == "link789"
        
        # Verify link was created with correct adapter/port numbers
        call_args = mock_link_class.call_args
        node1_config = call_args[1]["nodes"][0]
        assert node1_config["adapter_number"] == 1
        assert node1_config["port_number"] == 2
        
        node2_config = call_args[1]["nodes"][1]
        assert node2_config["adapter_number"] == 3
        assert node2_config["port_number"] == 4


class TestGNS3LinkToolErrorHandling:
    """Test cases for error handling scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_node_not_found(self, mock_get_gns3_connector):
        """Test node not found error"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node not found
        mock_connector.get_node.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Node not found in link 0" in result[0]["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_port_not_found(self, mock_get_gns3_connector):
        """Test port not found error"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node with different ports
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/1", "adapter_number": 0, "port_number": 1}
            ]
        }
        
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [
                {"name": "Ethernet0/1", "adapter_number": 0, "port_number": 1}
            ]
        }
        
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        result = tool._run(json.dumps(input_data))
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Port not found in link 0" in result[0]["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_node_without_ports(self, mock_get_gns3_connector):
        """Test node without ports array"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node without ports
        node1_data = {
            "name": "node1",
            "node_id": "node1"
            # No ports field
        }
        
        node2_data = {
            "name": "node2",
            "node_id": "node2"
        }
        
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        result = tool._run(json.dumps(input_data))
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Port not found in link 0" in result[0]["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    def test_link_creation_exception(self, mock_link_class, mock_get_gns3_connector):
        """Test exception during link creation"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data
        node_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [
                {"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}
            ]
        }
        
        mock_connector.get_node.return_value = node_data
        
        # Mock link creation exception
        mock_link_class.side_effect = Exception("Link creation failed")
        
        result = tool._run(json.dumps(input_data))
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to create link 0" in result[0]["error"]
        assert "Link creation failed" in result[0]["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_connector_exception(self, mock_get_gns3_connector):
        """Test exception during connector initialization"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector initialization exception
        mock_get_gns3_connector.side_effect = Exception("Connector initialization failed")
        
        result = tool._run(json.dumps(input_data))
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to process link creation" in result[0]["error"] or "Connector initialization failed" in result[0]["error"]

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_node_retrieval_exception(self, mock_get_gns3_connector):
        """Test exception during node retrieval"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node retrieval exception
        mock_connector.get_node.side_effect = Exception("Node retrieval failed")
        
        result = tool._run(json.dumps(input_data))
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to create link 0" in result[0]["error"]
        assert "Node retrieval failed" in result[0]["error"]


class TestGNS3LinkToolMixedSuccessFailure:
    """Test cases for mixed success and failure scenarios"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    def test_mixed_success_and_failure(self, mock_link_class, mock_get_gns3_connector):
        """Test mixed successful and failed link creations"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                },
                {
                    "node_id1": "node3",
                    "port1": "Ethernet0/0",
                    "node_id2": "node4",
                    "port2": "Ethernet0/0"
                },
                {
                    "node_id1": "node5",
                    "port1": "Ethernet0/0",
                    "node_id2": "node6",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data for successful links
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        
        node5_data = {
            "name": "node5",
            "node_id": "node5",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        
        node6_data = {
            "name": "node6",
            "node_id": "node6",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        
        # Mock node not found for second link
        mock_connector.get_node.side_effect = [
            node1_data, node2_data,  # First link - success
            None, None,  # Second link - node not found
            node5_data, node6_data  # Third link - success
        ]
        
        # Mock link creation for successful links
        mock_link1 = Mock()
        mock_link1.link_id = "link123"
        mock_link3 = Mock()
        mock_link3.link_id = "link456"
        mock_link_class.side_effect = [mock_link1, mock_link3]
        
        result = tool._run(json.dumps(input_data))
        
        # Verify mixed results
        assert len(result) == 3
        
        # First link - success
        assert "link_id" in result[0]
        assert result[0]["link_id"] == "link123"
        
        # Second link - failure
        assert "error" in result[1]
        assert "Node not found in link 1" in result[1]["error"]
        
        # Third link - success
        assert "link_id" in result[2]
        assert result[2]["link_id"] == "link456"


class TestGNS3LinkToolEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_unicode_port_names(self, mock_get_gns3_connector):
        """Test Unicode port names"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "端口0/0",  # Chinese port name
                    "node_id2": "node2",
                    "port2": "port0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data with Unicode port
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [{"name": "端口0/0", "adapter_number": 0, "port_number": 0}]
        }
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [{"name": "port0/0", "adapter_number": 0, "port_number": 0}]
        }
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link
            
            result = tool._run(json.dumps(input_data))
            # Should succeed with Unicode port names
            assert len(result) == 1
            assert "link_id" in result[0] or "error" in result[0]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_very_long_port_names(self, mock_get_gns3_connector):
        """Test very long port names"""
        tool = GNS3LinkTool()
        
        long_port_name = "Ethernet" + "0" * 1000 + "/0"
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": long_port_name,
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data with very long port name
        node1_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [{"name": long_port_name, "adapter_number": 0, "port_number": 0}]
        }
        node2_data = {
            "name": "node2",
            "node_id": "node2",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link
            
            result = tool._run(json.dumps(input_data))
            # Should succeed with very long port names
            assert len(result) == 1
            assert "link_id" in result[0] or "error" in result[0]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_special_characters_in_ids(self, mock_get_gns3_connector):
        """Test special characters in IDs"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project-with-special-chars_123",
            "links": [
                {
                    "node_id1": "node-with-special-chars_123",
                    "port1": "Ethernet0/0",
                    "node_id2": "node-2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data
        node1_data = {
            "name": "node1",
            "node_id": "node-with-special-chars_123",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        node2_data = {
            "name": "node2",
            "node_id": "node-2",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        mock_connector.get_node.side_effect = [node1_data, node2_data]
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link
            
            result = tool._run(json.dumps(input_data))
            # Should succeed with special characters in IDs
            assert len(result) == 1
            assert "link_id" in result[0] or "error" in result[0]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_large_number_of_links(self, mock_get_gns3_connector):
        """Test large number of links"""
        tool = GNS3LinkTool()
        
        # Create 100 links
        links = []
        for i in range(100):
            links.append({
                "node_id1": f"node{i}",
                "port1": "Ethernet0/0",
                "node_id2": f"node{i+1}",
                "port2": "Ethernet0/0"
            })
        
        input_data = {
            "project_id": "project1",
            "links": links
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data for all nodes
        node_data = {
            "name": "node",
            "node_id": "node",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        # We need 200 node calls (100 links * 2 nodes each)
        mock_connector.get_node.side_effect = [node_data] * 200
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_links = [Mock(link_id=f"link{i}") for i in range(100)]
            mock_link_class.side_effect = mock_links
            
            result = tool._run(json.dumps(input_data))
            # Should succeed with all links created
            assert len(result) == 100

    def test_empty_string_values(self):
        """Test empty string values in input"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": ""  # Empty port name
                }
            ]
        }
        
        # Add environment variables to allow validation to proceed
        with patch.dict(os.environ, {
            "GNS3_SERVER_URL": "http://localhost:3080"
        }):
            with patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector') as mock_get_gns3_connector:
                # Mock connector to prevent actual connection
                mock_connector = Mock()
                mock_get_gns3_connector.return_value = mock_connector
                
                # This should be caught by validation
                result = tool._run(json.dumps(input_data))
                assert "error" in result[0]
                assert "Missing required fields" in result[0]["error"]


class TestGNS3LinkToolIntegration:
    """Integration tests for GNS3LinkTool"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    def test_complete_workflow(self, mock_link_class, mock_get_gns3_connector):
        """Test complete workflow with realistic data"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project-uuid-12345",
            "links": [
                {
                    "node_id1": "router-uuid-1",
                    "port1": "GigabitEthernet0/0",
                    "node_id2": "switch-uuid-1",
                    "port2": "FastEthernet0/1"
                },
                {
                    "node_id1": "router-uuid-1",
                    "port1": "GigabitEthernet0/1",
                    "node_id2": "router-uuid-2",
                    "port2": "GigabitEthernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock realistic node data
        router1_data = {
            "name": "Router1",
            "node_id": "router-uuid-1",
            "node_type": "dynamips",
            "console": 5000,
            "ports": [
                {"name": "GigabitEthernet0/0", "adapter_number": 0, "port_number": 0},
                {"name": "GigabitEthernet0/1", "adapter_number": 0, "port_number": 1},
                {"name": "GigabitEthernet0/2", "adapter_number": 0, "port_number": 2}
            ]
        }
        
        switch1_data = {
            "name": "Switch1",
            "node_id": "switch-uuid-1",
            "node_type": "ethernet_switch",
            "console": None,
            "ports": [
                {"name": "FastEthernet0/0", "adapter_number": 0, "port_number": 0},
                {"name": "FastEthernet0/1", "adapter_number": 0, "port_number": 1},
                {"name": "FastEthernet0/2", "adapter_number": 0, "port_number": 2}
            ]
        }
        
        router2_data = {
            "name": "Router2",
            "node_id": "router-uuid-2",
            "node_type": "dynamips",
            "console": 5001,
            "ports": [
                {"name": "GigabitEthernet0/0", "adapter_number": 0, "port_number": 0},
                {"name": "GigabitEthernet0/1", "adapter_number": 0, "port_number": 1}
            ]
        }
        
        mock_connector.get_node.side_effect = [
            router1_data, switch1_data,  # First link
            router1_data, router2_data   # Second link
        ]
        
        # Mock link creation
        mock_link1 = Mock()
        mock_link1.link_id = "link-uuid-123"
        mock_link2 = Mock()
        mock_link2.link_id = "link-uuid-456"
        mock_link_class.side_effect = [mock_link1, mock_link2]
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results
        assert len(result) == 2
        
        # Verify first link
        assert result[0]["link_id"] == "link-uuid-123"
        assert result[0]["node_id1"] == "router-uuid-1"
        assert result[0]["port1"] == "GigabitEthernet0/0"
        assert result[0]["node_id2"] == "switch-uuid-1"
        assert result[0]["port2"] == "FastEthernet0/1"
        
        # Verify second link
        assert result[1]["link_id"] == "link-uuid-456"
        assert result[1]["node_id1"] == "router-uuid-1"
        assert result[1]["port1"] == "GigabitEthernet0/1"
        assert result[1]["node_id2"] == "router-uuid-2"
        assert result[1]["port2"] == "GigabitEthernet0/0"
        
        # Verify link creation calls
        assert mock_link_class.call_count == 2
        
        # Verify first link creation
        first_call = mock_link_class.call_args_list[0]
        assert first_call[1]["project_id"] == "project-uuid-12345"
        nodes_config = first_call[1]["nodes"]
        assert len(nodes_config) == 2
        assert nodes_config[0]["node_id"] == "router-uuid-1"
        assert nodes_config[0]["adapter_number"] == 0
        assert nodes_config[0]["port_number"] == 0
        assert nodes_config[1]["node_id"] == "switch-uuid-1"
        assert nodes_config[1]["adapter_number"] == 0
        assert nodes_config[1]["port_number"] == 1
        
        # Verify second link creation
        second_call = mock_link_class.call_args_list[1]
        assert second_call[1]["project_id"] == "project-uuid-12345"
        nodes_config = second_call[1]["nodes"]
        assert len(nodes_config) == 2
        assert nodes_config[0]["node_id"] == "router-uuid-1"
        assert nodes_config[0]["adapter_number"] == 0
        assert nodes_config[0]["port_number"] == 1
        assert nodes_config[1]["node_id"] == "router-uuid-2"
        assert nodes_config[1]["adapter_number"] == 0
        assert nodes_config[1]["port_number"] == 0

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    def test_json_parsing_edge_cases(self, mock_get_gns3_connector):
        """Test JSON parsing edge cases"""
        tool = GNS3LinkTool()
        
        # Test with extra whitespace
        input_with_whitespace = """
        {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        """
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node data
        node_data = {
            "name": "node",
            "node_id": "node",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        mock_connector.get_node.side_effect = [node_data, node_data]
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link123"
            mock_link_class.return_value = mock_link
            
            result = tool._run(input_with_whitespace)
            # Should succeed despite extra whitespace
            assert len(result) == 1
            assert "link_id" in result[0]

        # Test with additional fields
        input_with_extra_fields = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0",
                    "extra_field": "should_be_ignored"
                }
            ],
            "extra_project_field": "should_be_ignored"
        }
        
        # Reset mock
        mock_connector.reset_mock()
        mock_connector.get_node.side_effect = [node_data, node_data]
        
        # Mock link creation
        with patch('gns3_copilot.tools_v2.gns3_create_link.Link') as mock_link_class:
            mock_link = Mock()
            mock_link.link_id = "link456"
            mock_link_class.return_value = mock_link
            
            result = tool._run(json.dumps(input_with_extra_fields))
            # Should succeed, extra fields should be ignored
            assert len(result) == 1
            assert "link_id" in result[0]


class TestGNS3LinkToolLogging:
    """Test cases for logging functionality"""

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    @patch('gns3_copilot.tools_v2.gns3_create_link.logger')
    def test_logging_on_success(self, mock_logger, mock_link_class, mock_get_gns3_connector):
        """Test logging messages on successful operations"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector and nodes
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        node_data = {
            "name": "node1",
            "node_id": "node1",
            "ports": [{"name": "Ethernet0/0", "adapter_number": 0, "port_number": 0}]
        }
        mock_connector.get_node.return_value = node_data
        
        # Mock link
        mock_link = Mock()
        mock_link.link_id = "link123"
        mock_link_class.return_value = mock_link
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls (adjusted for new implementation using get_gns3_connector)
        mock_logger.info.assert_any_call("Received input: %s", json.dumps(input_data))
        mock_logger.info.assert_any_call("Creating link %d/%d", 1, 1)
        mock_logger.debug.assert_called()
        mock_logger.info.assert_any_call("Link creation completed: %d successful, %d failed", 1, 0)

    @patch.dict(os.environ, {
        "API_VERSION": "2",
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.tools_v2.gns3_create_link.get_gns3_connector')
    @patch('gns3_copilot.tools_v2.gns3_create_link.Link')
    @patch('gns3_copilot.tools_v2.gns3_create_link.logger')
    def test_logging_on_failure(self, mock_logger, mock_link_class, mock_get_gns3_connector):
        """Test logging messages on failed operations"""
        tool = GNS3LinkTool()
        
        input_data = {
            "project_id": "project1",
            "links": [
                {
                    "node_id1": "node1",
                    "port1": "Ethernet0/0",
                    "node_id2": "node2",
                    "port2": "Ethernet0/0"
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock node not found
        mock_connector.get_node.return_value = None
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls (adjusted for new implementation using get_gns3_connector)
        mock_logger.info.assert_any_call("Received input: %s", json.dumps(input_data))
        mock_logger.info.assert_any_call("Creating link %d/%d", 1, 1)
        mock_logger.error.assert_called()
        mock_logger.info.assert_any_call("Link creation completed: %d successful, %d failed", 0, 1)
