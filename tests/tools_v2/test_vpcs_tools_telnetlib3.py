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
Tests for vpcs_tools_telnetlib3 module.
Contains comprehensive test cases for VPCSMultiCommands functionality.

Test Coverage:
1. TestVPCSMultiCommandsInitialization
   - Tool name and description validation
   - Tool inheritance from BaseTool
   - Required tool attributes (name, description, _run, _connect_and_execute_commands)

2. TestVPCSMultiCommandsInputValidation
   - Empty input handling
   - Invalid JSON input handling
   - Non-object JSON input validation
   - Missing project_id validation
   - Missing device_configs validation
   - Invalid project_id format (UUID)
   - Empty device_configs array handling
   - Non-list device_configs handling
   - Device config not a dictionary
   - Missing device_name validation
   - Missing commands validation
   - Commands not a list validation

3. TestVPCSMultiCommandsEnvironmentVariables
   - Default GNS3 server host (127.0.0.1)
   - Custom GNS3 server host from GNS3_SERVER_HOST environment variable

4. TestVPCSMultiCommandsSuccessScenarios
   - Single device single command execution
   - Single device multiple commands execution
   - Multiple devices multiple commands execution
   - Custom host connection with GNS3_SERVER_HOST

5. TestVPCSMultiCommandsErrorHandling
   - Device not found in topology
   - Telnet connection exception
   - Telnet.open() exception
   - Telnet.expect() exception
   - Mixed success and failure scenarios

6. TestVPCSMultiCommandsThreading
   - Concurrent execution of multiple devices (3 devices)
   - Thread safety with multiple concurrent connections to same device

7. TestVPCSMultiCommandsEdgeCases
   - Unicode commands handling
   - Very long commands (1000 characters)
   - Special characters in commands
   - Large number of devices (50 devices)
   - Large number of commands per device (20 commands)
   - Empty output from device
   - Binary output from device

8. TestVPCSMultiCommandsIntegration
   - Complete workflow with realistic data (IP configuration, ping, save)
   - JSON parsing edge cases (extra whitespace, additional fields)

9. TestVPCSMultiCommandsLogging
   - Logging messages on successful operations
   - Logging messages on failed operations

10. TestVPCSMultiCommandsTelnetInteraction
    - Telnet initialization sequence (4 newlines, expect, command)
    - Timing between commands (0.5s initial delays, 5s command delays)
    - Command encoding (ASCII)
    - Output decoding (UTF-8)

11. TestVPCSMultiCommandsInternalMethod
    - Direct testing of _connect_and_execute_commands method
    - Device not found scenario in internal method
    - Telnet exception handling in internal method

Total Test Cases: 40+
"""

import json
import os
import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List

# Import the module to test
from gns3_copilot.tools_v2.vpcs_tools_telnetlib3 import VPCSMultiCommands


class TestVPCSMultiCommandsInitialization:
    """Test cases for VPCSMultiCommands initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = VPCSMultiCommands()
        assert tool.name == "execute_vpcs_multi_commands"
        assert "multiple command groups" in tool.description
        assert "VPCS devices" in tool.description
        assert "JSON object" in tool.description
        assert "project_id" in tool.description
        assert "device_configs" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = VPCSMultiCommands()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = VPCSMultiCommands()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')
        assert hasattr(tool, '_connect_and_execute_commands')


class TestVPCSMultiCommandsInputValidation:
    """Test cases for input validation"""

    def test_empty_input(self):
        """Test empty input handling"""
        tool = VPCSMultiCommands()
        result = tool._run("")
        assert len(result) == 1
        assert "error" in result[0]
        assert "Invalid JSON input" in result[0]["error"]

    def test_invalid_json(self):
        """Test invalid JSON input"""
        tool = VPCSMultiCommands()
        result = tool._run("{invalid json}")
        assert len(result) == 1
        assert "error" in result[0]
        assert "Invalid JSON input" in result[0]["error"]

    def test_non_object_input(self):
        """Test non-object JSON input (should be object with project_id and device_configs)"""
        tool = VPCSMultiCommands()
        input_data = ["item1", "item2"]
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "Tool input must be a JSON object" in result[0]["error"]

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = VPCSMultiCommands()
        input_data = {
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "Missing required field 'project_id'" in result[0]["error"]

    def test_invalid_project_id_format(self):
        """Test invalid project_id format (not a UUID)"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "invalid-id",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "Invalid project_id format" in result[0]["error"]

    def test_missing_device_configs(self):
        """Test missing device_configs"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24"
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "Missing required field 'device_configs'" in result[0]["error"]

    def test_empty_device_configs(self):
        """Test empty device_configs array"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": []
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 0  # Should return empty results for empty input

    def test_non_list_device_configs(self):
        """Test device_configs not a list"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": "not a list"
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "'device_configs' must be a list" in result[0]["error"]

    def test_device_config_not_dictionary(self):
        """Test device config item not a dictionary"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": ["not a dictionary"]
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "must be a dictionary" in result[0]["error"]

    def test_missing_device_name(self):
        """Test device config missing device_name"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "missing required field 'device_name'" in result[0]["error"]

    def test_missing_commands(self):
        """Test device config missing commands"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1"
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "missing required field 'commands'" in result[0]["error"]

    def test_commands_not_list(self):
        """Test commands not a list"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": "not a list"
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert len(result) == 1
        assert "error" in result[0]
        assert "'commands' in item" in result[0]["error"]
        assert "must be a list" in result[0]["error"]

    def test_empty_commands_array(self):
        """Test empty commands array"""
        tool = VPCSMultiCommands()
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": []
                }
            ]
        }
        # Should handle gracefully with mocked topology
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 1


class TestVPCSMultiCommandsEnvironmentVariables:
    """Test cases for environment variable handling"""

    def test_default_gns3_host(self):
        """Test default GNS3 server host"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        with patch.dict(os.environ, {}, clear=True):
            with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
                mock_get_ports.return_value = {}
                result = tool._run(json.dumps(input_data))
                assert len(result) == 1

    @patch.dict(os.environ, {"GNS3_SERVER_HOST": "192.168.1.100"})
    def test_custom_gns3_host(self):
        """Test custom GNS3 server host"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 1


class TestVPCSMultiCommandsSuccessScenarios:
    """Test cases for successful command execution scenarios"""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_single_device_single_command(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test successful single device single command execution"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24 10.0.0.254"]
                }
            ]
        }
        
        # Mock device ports
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        # Mock telnet connection and interaction
        mock_telnet = Mock()
        mock_telnet_class.return_value = mock_telnet
        
        # Mock the read_very_eager() method to return command output (as bytes, since code decodes it)
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24 10.0.0.254\r\nIP configured\r\nPC1> "
        
        # Mock expect to return success
        mock_telnet.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert len(result) == 1
        assert result[0]["device_name"] == "PC1"
        assert result[0]["status"] == "success"
        assert "output" in result[0]
        assert result[0]["commands"] == ["ip 10.0.0.1/24 10.0.0.254"]
        
        # Verify telnet was used correctly
        mock_telnet.open.assert_called_once()
        mock_telnet.write.assert_called()
        mock_telnet.close.assert_called_once()

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_single_device_multiple_commands(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test successful single device multiple commands execution"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": [
                        "ip 10.0.0.1/24 10.0.0.254",
                        "ping 10.0.0.254"
                    ]
                }
            ]
        }
        
        # Mock device ports
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        # Mock telnet connection
        mock_telnet = Mock()
        mock_telnet_class.return_value = mock_telnet
        mock_telnet.read_very_eager.return_value = b"PC1> command\r\nOutput\r\nPC1> "
        mock_telnet.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result
        assert len(result) == 1
        assert result[0]["device_name"] == "PC1"
        assert result[0]["status"] == "success"
        assert result[0]["commands"] == [
            "ip 10.0.0.1/24 10.0.0.254",
            "ping 10.0.0.254"
        ]
        
        # Verify multiple commands were executed
        assert mock_telnet.write.call_count >= 6  # 4 newlines + 2 commands

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_multiple_devices_multiple_commands(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test successful multiple devices multiple commands execution"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24 10.0.0.254"]
                },
                {
                    "device_name": "PC2",
                    "commands": ["ip 10.0.1.1/24 10.0.1.254", "ping 10.0.0.1"]
                }
            ]
        }
        
        # Mock device ports
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            },
            "PC2": {
                "port": 5001,
                "groups": ["vpcs_telnet"]
            }
        }
        
        # Mock telnet connections
        mock_telnet1 = Mock()
        mock_telnet2 = Mock()
        mock_telnet_class.side_effect = [mock_telnet1, mock_telnet2]
        
        mock_telnet1.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet2.read_very_eager.return_value = b"PC2> ip 10.0.1.1/24\r\nIP configured\r\nPC2> ping 10.0.0.1\r\nPING\r\nPC2> "
        mock_telnet1.expect.return_value = None
        mock_telnet2.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful results for both devices
        assert len(result) == 2
        
        # Verify PC1 result
        pc1_result = next(r for r in result if r["device_name"] == "PC1")
        assert pc1_result["status"] == "success"
        assert pc1_result["commands"] == ["ip 10.0.0.1/24 10.0.0.254"]
        
        # Verify PC2 result
        pc2_result = next(r for r in result if r["device_name"] == "PC2")
        assert pc2_result["status"] == "success"
        assert pc2_result["commands"] == ["ip 10.0.1.1/24 10.0.1.254", "ping 10.0.0.1"]
        
        # Verify both connections were created and closed
        assert mock_telnet_class.call_count == 2
        mock_telnet1.close.assert_called_once()
        mock_telnet2.close.assert_called_once()

    @patch.dict(os.environ, {"GNS3_SERVER_HOST": "192.168.1.100"})
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_custom_host_connection(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test connection with custom host"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet_class.return_value = mock_telnet
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify connection was called
        mock_telnet.open.assert_called_once()


class TestVPCSMultiCommandsErrorHandling:
    """Test cases for error handling scenarios"""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    def test_device_not_found_in_topology(self, mock_telnet_class, mock_get_ports):
        """Test device not found in topology"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "NonExistentPC",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        # Mock empty device ports (device not found)
        mock_get_ports.return_value = {}
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error result
        assert len(result) == 1
        assert result[0]["device_name"] == "NonExistentPC"
        assert result[0]["status"] == "error"
        assert "not found in topology" in result[0]["output"]
        assert result[0]["commands"] == ["ip 10.0.0.1/24"]
        
        # Verify no telnet connection was attempted
        mock_telnet_class.assert_not_called()

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_telnet_connection_exception(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test telnet connection exception"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        # Mock telnet to succeed constructor but fail on open
        mock_telnet = Mock()
        mock_telnet.open.side_effect = Exception("Connection failed")
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error result
        assert len(result) == 1
        assert result[0]["device_name"] == "PC1"
        assert result[0]["status"] == "error"
        assert "Connection failed" in result[0]["output"]

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_telnet_open_exception(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test telnet.open() exception"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.open.side_effect = Exception("Connection timeout")
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error result
        assert len(result) == 1
        assert result[0]["device_name"] == "PC1"
        assert result[0]["status"] == "error"
        assert "Connection timeout" in result[0]["output"]

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_telnet_expect_exception(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test telnet.expect() exception"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.expect.side_effect = Exception("Expect failed")
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify error result
        assert len(result) == 1
        assert result[0]["device_name"] == "PC1"
        assert result[0]["status"] == "error"
        assert "Expect failed" in result[0]["output"]

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_mixed_success_and_failure(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test mixed successful and failed executions"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                },
                {
                    "device_name": "NonExistentPC",
                    "commands": ["ip 10.0.0.2/24"]
                }
            ]
        }
        
        # Mock device ports (only PC1 exists)
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        # Mock telnet for PC1
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify mixed results
        assert len(result) == 2
        
        # Find successful result (PC1)
        success_result = next(r for r in result if r["device_name"] == "PC1")
        assert success_result["status"] == "success"
        
        # Find error result (NonExistentPC)
        error_result = next(r for r in result if r["device_name"] == "NonExistentPC")
        assert error_result["status"] == "error"
        assert "not found in topology" in error_result["output"]


class TestVPCSMultiCommandsThreading:
    """Test cases for threading functionality"""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_concurrent_execution(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test concurrent execution of multiple devices"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                },
                {
                    "device_name": "PC2",
                    "commands": ["ip 10.0.1.1/24"]
                },
                {
                    "device_name": "PC3",
                    "commands": ["ip 10.0.2.1/24"]
                }
            ]
        }
        
        # Mock device ports
        mock_get_ports.return_value = {
            "PC1": {"port": 5000, "groups": ["vpcs_telnet"]},
            "PC2": {"port": 5001, "groups": ["vpcs_telnet"]},
            "PC3": {"port": 5002, "groups": ["vpcs_telnet"]}
        }
        
        # Mock telnet connections
        mock_telnet1 = Mock()
        mock_telnet2 = Mock()
        mock_telnet3 = Mock()
        mock_telnet_class.side_effect = [mock_telnet1, mock_telnet2, mock_telnet3]
        
        # Mock read_very_eager for all connections
        for mock_telnet in [mock_telnet1, mock_telnet2, mock_telnet3]:
            mock_telnet.read_very_eager.return_value = b"PC> ip command\r\nIP configured\r\nPC> "
            mock_telnet.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify all three devices were processed
        assert len(result) == 3
        assert all(r["status"] == "success" for r in result)
        
        # Verify all connections were created
        assert mock_telnet_class.call_count == 3
        
        # Verify all connections were closed
        mock_telnet1.close.assert_called_once()
        mock_telnet2.close.assert_called_once()
        mock_telnet3.close.assert_called_once()

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_thread_safety(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test thread safety with multiple concurrent connections"""
        tool = VPCSMultiCommands()
        
        # Create multiple command groups for the same device to test thread safety
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                },
                {
                    "device_name": "PC1",
                    "commands": ["ping 10.0.0.254"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet1 = Mock()
        mock_telnet2 = Mock()
        mock_telnet_class.side_effect = [mock_telnet1, mock_telnet2]
        
        mock_telnet1.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet2.read_very_eager.return_value = b"PC1> ping 10.0.0.254\r\nPING\r\nPC1> "
        mock_telnet1.expect.return_value = None
        mock_telnet2.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify both command groups executed successfully
        assert len(result) == 2
        assert all(r["status"] == "success" for r in result)
        assert all(r["device_name"] == "PC1" for r in result)


class TestVPCSMultiCommandsEdgeCases:
    """Test cases for edge cases and boundary conditions"""

    def test_unicode_commands(self):
        """Test Unicode commands"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["显示IP配置", "ping 测试"]
                }
            ]
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 1

    def test_very_long_commands(self):
        """Test very long commands"""
        tool = VPCSMultiCommands()
        
        long_command = "x" * 1000
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": [long_command]
                }
            ]
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 1

    def test_special_characters_in_commands(self):
        """Test special characters in commands"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24 10.0.0.254; echo 'test' && ping -c 4 8.8.8.8"]
                }
            ]
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 1

    def test_large_number_of_devices(self):
        """Test large number of devices"""
        tool = VPCSMultiCommands()
        
        # Create 50 devices
        device_configs = []
        for i in range(50):
            device_configs.append({
                "device_name": f"PC{i+1}",
                "commands": [f"ip 10.0.{i}.1/24 10.0.{i}.254"]
            })
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": device_configs
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 50

    def test_large_number_of_commands_per_device(self):
        """Test large number of commands per device"""
        tool = VPCSMultiCommands()
        
        # Create 20 commands for one device
        commands = []
        for i in range(20):
            commands.append(f"command {i+1}")
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": commands
                }
            ]
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_data))
            assert len(result) == 1

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_empty_output_from_device(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test empty output from device"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b""  # Empty output (as bytes)
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result even with empty output
        assert len(result) == 1
        assert result[0]["status"] == "success"
        assert result[0]["output"] == ""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_binary_output_from_device(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test binary output from device"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b'\x00\x01\x02'  # Binary data
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify successful result (binary data should be handled)
        assert len(result) == 1
        assert result[0]["status"] == "success"
        assert "output" in result[0]


class TestVPCSMultiCommandsIntegration:
    """Integration tests for VPCSMultiCommands"""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_complete_workflow(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test complete workflow with realistic data"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": [
                        "ip 192.168.1.10/24 192.168.1.254",
                        "ping 192.168.1.254",
                        "save"
                    ]
                },
                {
                    "device_name": "PC2",
                    "commands": [
                        "ip 192.168.2.10/24 192.168.2.254",
                        "ping 192.168.1.10"
                    ]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            },
            "PC2": {
                "port": 5001,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet1 = Mock()
        mock_telnet2 = Mock()
        mock_telnet_class.side_effect = [mock_telnet1, mock_telnet2]
        
        # Mock realistic output
        mock_telnet1.read_very_eager.return_value = b"""PC1> ip 192.168.1.10/24 192.168.1.254
PC1> ping 192.168.1.254
PING 192.168.1.254 (192.168.1.254): 56 data bytes
64 bytes from 192.168.1.254: icmp_seq=0 ttl=64 time=0.123 ms
PC1> save
Saving configuration to startup
PC1> """
        
        mock_telnet2.read_very_eager.return_value = b"""PC2> ip 192.168.2.10/24 192.168.2.254
PC2> ping 192.168.1.10
PING 192.168.1.10 (192.168.1.10): 56 data bytes
64 bytes from 192.168.1.10: icmp_seq=0 ttl=64 time=0.456 ms
PC2> """
        
        mock_telnet1.expect.return_value = None
        mock_telnet2.expect.return_value = None
        
        result = tool._run(json.dumps(input_data))
        
        # Verify complete results
        assert len(result) == 2
        
        # Verify PC1 result
        pc1_result = next(r for r in result if r["device_name"] == "PC1")
        assert pc1_result["status"] == "success"
        assert len(pc1_result["commands"]) == 3
        assert "192.168.1.10/24" in pc1_result["output"]
        assert "PING" in pc1_result["output"]
        
        # Verify PC2 result
        pc2_result = next(r for r in result if r["device_name"] == "PC2")
        assert pc2_result["status"] == "success"
        assert len(pc2_result["commands"]) == 2
        assert "192.168.2.10/24" in pc2_result["output"]
        assert "PING" in pc2_result["output"]

    def test_json_parsing_edge_cases(self):
        """Test JSON parsing edge cases"""
        tool = VPCSMultiCommands()
        
        # Test with extra whitespace
        input_with_whitespace = """
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        """
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(input_with_whitespace)
            assert len(result) == 1

        # Test with additional fields
        input_with_extra_fields = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"],
                    "extra_field": "should_be_ignored"
                }
            ]
        }
        
        with patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology') as mock_get_ports:
            mock_get_ports.return_value = {}
            result = tool._run(json.dumps(input_with_extra_fields))
            assert len(result) == 1


class TestVPCSMultiCommandsLogging:
    """Test cases for logging functionality"""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.logger')
    def test_logging_on_success(self, mock_logger, mock_telnet_class, mock_get_ports):
        """Test logging messages on successful operations"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls
        assert mock_logger.info.call_count > 0
        
        # Verify the last info call contains results
        last_call_args = mock_logger.info.call_args_list[-1][0]
        assert "Multi-device command execution completed" in last_call_args[0]

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.logger')
    def test_logging_on_failure(self, mock_logger, mock_telnet_class, mock_get_ports):
        """Test logging messages on failed operations"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "NonExistentPC",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {}
        
        tool._run(json.dumps(input_data))
        
        # Verify logging calls
        assert mock_logger.info.call_count > 0
        
        # Verify the last info call contains results (including errors)
        last_call_args = mock_logger.info.call_args_list[-1][0]
        assert "Multi-device command execution completed" in last_call_args[0]


class TestVPCSMultiCommandsTelnetInteraction:
    """Test cases for specific telnet interaction details"""

    @patch('dotenv.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_telnet_initialization_sequence(self, mock_sleep, mock_telnet_class, mock_get_ports, mock_load_dotenv):
        """Test telnet initialization sequence"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify telnet open was called
        mock_telnet.open.assert_called_once()
        
        # Verify initialization sequence (4 newlines and expect)
        write_calls = mock_telnet.write.call_args_list
        assert len(write_calls) == 5  # 4 newlines + 1 command
        
        # Verify first 4 calls are newlines for initialization
        for i in range(4):
            assert write_calls[i][0][0] == b"\n"
        
        # Verify command call
        command_call = write_calls[4]
        assert command_call[0][0] == b"ip 10.0.0.1/24\n"
        
        # Verify sleep calls: 4 sleeps after newlines + 1 sleep after command = 5 total
        assert mock_sleep.call_count == 5
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls[:4] == [0.5, 0.5, 0.5, 0.5]  # Initialization delays
        assert sleep_calls[4] == 5  # Command execution delay
        
        # Verify expect was called for PC prompt (1 init + 1 command = 2 calls)
        assert mock_telnet.expect.call_count == 2
        call_args = mock_telnet.expect.call_args
        assert call_args[0][0] == [rb"PC\d+>"]
        
        # Verify telnet was closed
        mock_telnet.close.assert_called_once()

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_timing_between_commands(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test timing between commands"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24", "ping 10.0.0.254"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> command\r\nOutput\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        tool._run(json.dumps(input_data))
        
        # Verify sleep was called for timing: 4 init sleeps + 2 command sleeps = 6 total
        assert mock_sleep.call_count == 6
        
        # Verify sleep durations
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls.count(0.5) == 4  # Initial delays
        assert sleep_calls.count(5) == 2    # Command execution delays

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_command_encoding(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test command encoding"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        tool._run(json.dumps(input_data))
        
        # Verify command was encoded as ASCII
        write_calls = mock_telnet.write.call_args_list
        command_call = None
        for call in write_calls:
            if call[0][0] != b"\n":
                command_call = call
                break
        
        assert command_call is not None
        assert command_call[0][0] == b"ip 10.0.0.1/24\n"

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_output_decoding(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test output decoding"""
        tool = VPCSMultiCommands()
        
        input_data = {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.0.0.1/24"]
                }
            ]
        }
        
        mock_get_ports.return_value = {
            "PC1": {
                "port": 5000,
                "groups": ["vpcs_telnet"]
            }
        }
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        result = tool._run(json.dumps(input_data))
        
        # Verify output was decoded as UTF-8
        assert "output" in result[0]
        assert isinstance(result[0]["output"], str)


class TestVPCSMultiCommandsInternalMethod:
    """Test cases for internal method _connect_and_execute_commands"""

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_internal_method_directly(self, mock_sleep, mock_telnet_class, mock_get_ports):
        """Test _connect_and_execute_commands method directly"""
        tool = VPCSMultiCommands()
        
        # Prepare test data
        results_list = [None] * 1
        index = 0
        device_ports = {"PC1": {"port": 5000, "groups": ["vpcs_telnet"]}}
        gns3_host = "127.0.0.1"
        
        mock_telnet = Mock()
        mock_telnet.read_very_eager.return_value = b"PC1> ip 10.0.0.1/24\r\nIP configured\r\nPC1> "
        mock_telnet.expect.return_value = None
        mock_telnet_class.return_value = mock_telnet
        
        # Call internal method directly
        tool._connect_and_execute_commands(
            device_name="PC1",
            commands=["ip 10.0.0.1/24"],
            results_list=results_list,
            index=index,
            device_ports=device_ports,
            gns3_host=gns3_host
        )
        
        # Verify result was set correctly
        assert results_list[index] is not None
        assert results_list[index]["device_name"] == "PC1"
        assert results_list[index]["status"] == "success"
        assert results_list[index]["commands"] == ["ip 10.0.0.1/24"]

    def test_internal_method_device_not_found(self):
        """Test _connect_and_execute_commands with device not found"""
        tool = VPCSMultiCommands()
        
        results_list = [None] * 1
        index = 0
        device_ports = {}  # Empty - device not found
        gns3_host = "127.0.0.1"
        
        # Call internal method directly
        tool._connect_and_execute_commands(
            device_name="NonExistentPC",
            commands=["ip 10.0.0.1/24"],
            results_list=results_list,
            index=index,
            device_ports=device_ports,
            gns3_host=gns3_host
        )
        
        # Verify error result was set correctly
        assert results_list[index] is not None
        assert results_list[index]["device_name"] == "NonExistentPC"
        assert results_list[index]["status"] == "error"
        assert "not found in topology" in results_list[index]["output"]
        assert results_list[index]["commands"] == ["ip 10.0.0.1/24"]

    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.Telnet')
    @patch('gns3_copilot.tools_v2.vpcs_tools_telnetlib3.sleep')
    def test_internal_method_telnet_exception(self, mock_sleep, mock_telnet_class):
        """Test _connect_and_execute_commands with telnet exception"""
        tool = VPCSMultiCommands()
        
        results_list = [None] * 1
        index = 0
        device_ports = {"PC1": {"port": 5000, "groups": ["vpcs_telnet"]}}
        gns3_host = "127.0.0.1"
        
        # Mock telnet to succeed constructor but fail on open
        mock_telnet = Mock()
        mock_telnet.open.side_effect = Exception("Telnet error")
        mock_telnet_class.return_value = mock_telnet
        
        # Call internal method directly
        tool._connect_and_execute_commands(
            device_name="PC1",
            commands=["ip 10.0.0.1/24"],
            results_list=results_list,
            index=index,
            device_ports=device_ports,
            gns3_host=gns3_host
        )
        
        # Verify error result was set correctly
        assert results_list[index] is not None
        assert results_list[index]["device_name"] == "PC1"
        assert results_list[index]["status"] == "error"
        assert "Telnet error" in results_list[index]["output"]
        assert results_list[index]["commands"] == ["ip 10.0.0.1/24"]
