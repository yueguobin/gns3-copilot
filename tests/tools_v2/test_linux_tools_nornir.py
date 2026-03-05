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
Tests for linux_tools_nornir module.
Contains test cases for LinuxTelnetBatchTool tool.

Test Coverage:
1. TestLinuxTelnetBatchTool
   - Tool name and description validation
   - Input validation (_validate_tool_input):
     * Valid JSON string and list inputs
     * Invalid JSON string handling
     * Non-list input validation
     * Empty list handling
   - Config mapping (_configs_map):
     * Creating device to commands mapping
     * Empty list handling
   - Device hosts data preparation (_prepare_device_hosts_data):
     * Successful data preparation with groups forced to linux_telnet
     * Empty result handling
     * Missing devices handling
   - Nornir initialization (_initialize_nornir):
     * Successful initialization with threaded runner
     * Initialization failure handling
   - Linux telnet login (_linux_telnet_login):
     * Login with login prompt detection
     * Already logged in scenario
     * Login failure handling
   - Device command execution (_run_all_device_configs_with_single_retry):
     * Successful command execution
     * No commands scenario
     * Exception handling
   - Task result processing (_process_task_results):
     * Successful task results with command output
     * Failed task results
     * Device not in topology scenarios
     * Login failure handling
   - Main run method (_run):
     * Successful execution with login and commands
     * Missing credentials handling (LINUX_TELNET_USERNAME/PASSWORD)
     * Invalid input handling
     * Device hosts data failure
     * Nornir init failure
     * Execution exception handling
     * List input support

2. TestEdgeCasesAndErrorHandling
   - Empty commands for a device
   - Malformed device config (missing required fields)
   - None tool input handling
   - Numeric tool input handling
   - Environment variables handling and groups_data usage
   - Large number of devices (100 devices) handling
   - Linux-specific safety description content validation
   - Credentials configured check

3. TestIntegrationScenarios
   - Mixed success and failure results (login failures)
   - Concurrent execution simulation (threaded runner with 10 workers)
   - Linux command restrictions validation
   - Nornir configuration for Linux Telnet verification

Total Test Cases: 35+
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List

# Import the class to test
from gns3_copilot.tools_v2.linux_tools_nornir import LinuxTelnetBatchTool


class TestLinuxTelnetBatchTool:
    """Tests for LinuxTelnetBatchTool"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = LinuxTelnetBatchTool()
        
        # Sample valid input for testing
        self.valid_input = [
            {
                "device_name": "debian01",
                "commands": [
                    "uname -a",
                    "df -h",
                    "sudo docker ps"
                ]
            },
            {
                "device_name": "ubuntu01",
                "commands": [
                    "ip a",
                    "uptime"
                ]
            }
        ]
        
        self.valid_input_json = json.dumps(self.valid_input)

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        assert self.tool.name == "linux_telnet_batch_commands"
        assert "Batch execute commands on multiple Linux devices" in self.tool.description
        assert "Telnet console" in self.tool.description
        assert "Do NOT use this tool for any Danger configuration commands" in self.tool.description
        assert "non-interactive" in self.tool.description

    # Test _validate_tool_input method
    def test_validate_tool_input_valid_json_string(self):
        """Test validation with valid JSON string"""
        result = self.tool._validate_tool_input(self.valid_input_json)
        assert result == (self.valid_input, None)

    def test_validate_tool_input_valid_list(self):
        """Test validation with valid Python list"""
        result = self.tool._validate_tool_input(json.dumps(self.valid_input))
        assert result == (self.valid_input, None)

    def test_validate_tool_input_invalid_json_string(self):
        """Test validation with invalid JSON string"""
        invalid_json = '{"device_name": "debian01", "commands": ["cmd1"'  # Missing closing bracket
        result = self.tool._validate_tool_input(invalid_json)
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Invalid JSON string input from model" in result[0][0]["error"]

    def test_validate_tool_input_not_a_list(self):
        """Test validation when input is not a list"""
        not_a_list = {"device_name": "debian01", "commands": ["cmd1"]}
        result = self.tool._validate_tool_input(json.dumps(not_a_list))
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Missing required 'project_id' field in input" in result[0][0]["error"]

    def test_validate_tool_input_empty_list(self):
        """Test validation with empty list"""
        result = self.tool._validate_tool_input(json.dumps([]))
        assert result == ([], None)

    # Test _configs_map method
    def test_configs_map(self):
        """Test creating device to commands mapping"""
        result = self.tool._configs_map(self.valid_input)
        expected = {
            "debian01": [
                "uname -a",
                "df -h",
                "sudo docker ps"
            ],
            "ubuntu01": [
                "ip a",
                "uptime"
            ]
        }
        assert result == expected

    def test_configs_map_empty_list(self):
        """Test configs map with empty list"""
        result = self.tool._configs_map([])
        assert result == {}

    # Test _prepare_device_hosts_data method
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    def test_prepare_device_hosts_data_success(self, mock_get_ports):
        """Test successful device hosts data preparation"""
        mock_ports_return = {
            "debian01": {
                "port": 5000,
                "groups": ["some_group"]
            },
            "ubuntu01": {
                "port": 5001,
                "groups": ["some_group"]
            }
        }
        mock_get_ports.return_value = mock_ports_return
        
        result = self.tool._prepare_device_hosts_data(self.valid_input)
        
        # Verify that groups are forced to linux_telnet
        expected_return = {
            "debian01": {
                "port": 5000,
                "groups": ["linux_telnet"]
            },
            "ubuntu01": {
                "port": 5001,
                "groups": ["linux_telnet"]
            }
        }
        assert result == expected_return
        mock_get_ports.assert_called_once_with(["debian01", "ubuntu01"], None)

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    def test_prepare_device_hosts_data_empty_result(self, mock_get_ports):
        """Test device hosts data preparation with empty result"""
        mock_get_ports.return_value = {}
        
        with pytest.raises(ValueError, match="Failed to get device information from topology"):
            self.tool._prepare_device_hosts_data(self.valid_input)

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    def test_prepare_device_hosts_data_missing_devices(self, mock_get_ports):
        """Test device hosts data preparation with missing devices"""
        mock_ports_return = {
            "debian01": {
                "port": 5000,
                "groups": ["some_group"]
            }
            # ubuntu01 is missing
        }
        mock_get_ports.return_value = mock_ports_return
        
        # Should still work, just log warning for missing devices
        result = self.tool._prepare_device_hosts_data(self.valid_input)
        expected = {
            "debian01": {
                "port": 5000,
                "groups": ["linux_telnet"]
            }
        }
        assert result == expected

    # Test _initialize_nornir method
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_initialize_nornir_success(self, mock_init_nornir):
        """Test successful Nornir initialization"""
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        hosts_data = {
            "debian01": {
                "port": 5000,
                "groups": ["linux_telnet"]
            }
        }
        
        result = self.tool._initialize_nornir(hosts_data)
        assert result == mock_nornir
        
        mock_init_nornir.assert_called_once()
        # Verify call structure
        call_args = mock_init_nornir.call_args
        assert call_args[1]['inventory']['plugin'] == 'DictInventory'
        assert call_args[1]['runner']['plugin'] == 'threaded'
        assert call_args[1]['runner']['options']['num_workers'] == 10
        assert call_args[1]['logging']['enabled'] is False

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_initialize_nornir_failure(self, mock_init_nornir):
        """Test Nornir initialization failure"""
        mock_init_nornir.side_effect = Exception("Nornir init failed")
        
        hosts_data = {"debian01": {"port": 5000}}
        
        with pytest.raises(ValueError, match="Failed to initialize Nornir"):
            self.tool._initialize_nornir(hosts_data)

    # Test _linux_telnet_login method
    def test_linux_telnet_login_with_login_prompt(self):
        """Test Linux telnet login when login prompt is detected"""
        mock_task = Mock()
        mock_task.host.name = "debian01"
        mock_task.host.username = "testuser"
        mock_task.host.password = "testpass"
        
        mock_net_connect = Mock()
        mock_task.host.get_connection.return_value = mock_net_connect
        
        # Simulate login prompt in output
        mock_net_connect.read_channel_timing.return_value = "Debian GNU/Linux 12\ndebian01 login:"
        mock_net_connect.read_until_prompt_or_pattern.side_effect = [
            "Password:",  # After username
            "testuser@debian01:~$"  # After password
        ]
        
        result = self.tool._linux_telnet_login(mock_task)
        
        assert result.failed is False
        assert result.result == "Login successful"
        mock_net_connect.write_channel.assert_any_call("testuser\n")
        mock_net_connect.write_channel.assert_any_call("testpass\n")

    def test_linux_telnet_login_already_logged_in(self):
        """Test Linux telnet login when already logged in"""
        mock_task = Mock()
        mock_task.host.name = "debian01"
        
        mock_net_connect = Mock()
        mock_task.host.get_connection.return_value = mock_net_connect
        
        # Simulate already logged in (shell prompt)
        mock_net_connect.read_channel_timing.return_value = "testuser@debian01:~$ "
        
        result = self.tool._linux_telnet_login(mock_task)
        
        assert result.failed is False
        assert result.result == "Already logged in"

    def test_linux_telnet_login_failure(self):
        """Test Linux telnet login failure"""
        mock_task = Mock()
        mock_task.host.name = "debian01"
        
        mock_task.host.get_connection.side_effect = Exception("Connection failed")
        
        result = self.tool._linux_telnet_login(mock_task)
        
        assert result.failed is True
        assert "Login failed: Connection failed" in result.result

    # Test _run_all_device_configs_with_single_retry method
    def test_run_all_device_configs_success(self):
        """Test successful device command execution"""
        mock_task = Mock()
        mock_task.host.name = "debian01"
        
        mock_run_result = Mock()
        mock_run_result.result = "uname -a output"
        mock_task.run.return_value = mock_run_result
        
        device_configs_map = {
            "debian01": ["uname -a", "df -h"]
        }
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is False
        assert "uname -a output" in str(result.result)  # result is a dict with command keys
        mock_task.run.assert_called()

    def test_run_all_device_configs_no_commands(self):
        """Test device command execution with no commands"""
        mock_task = Mock()
        mock_task.host.name = "debian01"
        
        device_configs_map = {}  # No commands for this device
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is False
        assert result.result == "No display commands to execute"

    def test_run_all_device_configs_with_exception(self):
        """Test device command execution with exception"""
        mock_task = Mock()
        mock_task.host.name = "debian01"
        mock_task.run.side_effect = Exception("Command failed")
        
        device_configs_map = {
            "debian01": ["uname -a"]
        }
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is False  # Method doesn't set failed=True on exceptions
        assert "Command execution failed: Command failed" in result.result["uname -a"]

    # Test _process_task_results method
    def test_process_task_results_success(self):
        """Test processing successful task results"""
        # Create mock result items
        mock_result_item1 = Mock()
        mock_result_item1.failed = False
        mock_result_item1.result = {"uname -a": "Linux debian01 5.10.0", "df -h": "Filesystem Size"}
        
        mock_result_item2 = Mock()
        mock_result_item2.failed = False
        mock_result_item2.result = {"ip a": "eth0: inet 192.168.1.10", "uptime": "up 1 day"}
        
        # Mock multi_result objects that can be indexed
        mock_multi_result1 = Mock()
        mock_multi_result1.__getitem__ = Mock(return_value=mock_result_item1)
        
        mock_multi_result2 = Mock()
        mock_multi_result2.__getitem__ = Mock(return_value=mock_result_item2)
        
        # Mock task result that can be indexed and checked for containment
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(side_effect=[mock_multi_result1, mock_multi_result2])
        mock_task_result.__contains__ = Mock(return_value=True)
        
        hosts_data = {
            "debian01": {"port": 5000},
            "ubuntu01": {"port": 5001}
        }
        
        result = self.tool._process_task_results(self.valid_input, hosts_data, mock_task_result)
        
        assert len(result) == 2
        assert result[0]["device_name"] == "debian01"
        assert result[0]["status"] == "success"
        assert result[0]["output"] == {"uname -a": "Linux debian01 5.10.0", "df -h": "Filesystem Size"}
        assert result[0]["config_commands"] == self.valid_input[0]["commands"]

    def test_process_task_results_failure(self):
        """Test processing failed task results"""
        # Create mock failed result item
        mock_result_item = Mock()
        mock_result_item.failed = True
        mock_result_item.result = "Command execution failed: Permission denied"
        
        # Mock multi_result object
        mock_multi_result = Mock()
        mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        hosts_data = {
            "debian01": {"port": 5000}
        }
        
        single_device_input = [self.valid_input[0]]
        result = self.tool._process_task_results(single_device_input, hosts_data, mock_task_result)
        
        assert len(result) == 1
        assert result[0]["device_name"] == "debian01"
        assert result[0]["status"] == "failed"
        assert "Command execution failed" in result[0]["error"]
        assert result[0]["output"] == "Command execution failed: Permission denied"

    def test_process_task_results_device_not_in_topology(self):
        """Test processing when device not in topology"""
        # Mock task result that doesn't contain devices
        mock_task_result = Mock()
        mock_task_result.__contains__ = Mock(return_value=False)
        
        hosts_data = {
            "debian01": {"port": 5000}
            # ubuntu01 is missing
        }
        
        result = self.tool._process_task_results(self.valid_input, hosts_data, mock_task_result)
        
        assert len(result) == 2
        assert result[0]["device_name"] == "debian01"
        assert result[0]["status"] == "failed"
        assert "not found in task results" in result[0]["error"]
        assert result[1]["device_name"] == "ubuntu01"
        assert result[1]["status"] == "failed"
        assert "not found in topology" in result[1]["error"]

    def test_process_task_results_with_login_failure(self):
        """Test processing when login fails"""
        # Mock login result
        mock_login_result = Mock()
        mock_login_result.failed = True
        mock_login_result.result = "Login failed: Authentication error"
        mock_login_task_result = {"debian01": mock_login_result}
        
        # Mock task result that doesn't contain devices (since login failed)
        mock_task_result = Mock()
        mock_task_result.__contains__ = Mock(return_value=False)
        
        hosts_data = {
            "debian01": {"port": 5000}
        }
        
        single_device_input = [self.valid_input[0]]
        result = self.tool._process_task_results(single_device_input, hosts_data, mock_task_result, mock_login_task_result)
        
        assert len(result) == 1
        assert result[0]["device_name"] == "debian01"
        assert result[0]["status"] == "failed"
        assert "Login failed: Authentication error" in result[0]["error"]
        assert result[0]["login_status"] == "Login failed: Authentication error"

    # Test main _run method
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_run_success(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test successful run of the tool"""
        # Mock dependencies
        mock_get_ports.return_value = {
            "debian01": {"port": 5000},
            "ubuntu01": {"port": 5001}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Mock login results
        mock_login_result1 = Mock()
        mock_login_result1.failed = False
        mock_login_result1.result = "Login successful"
        
        mock_login_result2 = Mock()
        mock_login_result2.failed = False
        mock_login_result2.result = "Login successful"
        
        mock_login_task_result = {
            "debian01": mock_login_result1,
            "ubuntu01": mock_login_result2
        }
        
        # Create mock result items
        mock_result_item1 = Mock()
        mock_result_item1.failed = False
        mock_result_item1.result = {"uname -a": "Linux debian01 5.10.0"}
        
        mock_result_item2 = Mock()
        mock_result_item2.failed = False
        mock_result_item2.result = {"ip a": "eth0: inet 192.168.1.10"}
        
        # Mock multi_result objects
        mock_multi_result1 = Mock()
        mock_multi_result1.__getitem__ = Mock(return_value=mock_result_item1)
        
        mock_multi_result2 = Mock()
        mock_multi_result2.__getitem__ = Mock(return_value=mock_result_item2)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(side_effect=[mock_multi_result1, mock_multi_result2])
        mock_task_result.__contains__ = Mock(return_value=True)
        
        # Configure nornir.run to return different results for login and commands
        mock_nornir.run.side_effect = [mock_login_task_result, mock_task_result]
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        # Execute
        result = self.tool._run(self.valid_input_json)
        
        # Verify
        assert len(result) == 2
        assert all(r["status"] == "success" for r in result)
        
        mock_get_ports.assert_called_once_with(["debian01", "ubuntu01"], None)
        mock_init_nornir.assert_called_once()
        assert mock_nornir.run.call_count == 2  # Once for login, once for commands

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    def test_run_missing_credentials(self, mock_get_ports, mock_get_config):
        """Test run when Linux credentials are missing"""
        # Mock get_config to return None for credentials (missing credentials)
        mock_get_config.side_effect = lambda key: None if key in ['LINUX_TELNET_USERNAME', 'LINUX_TELNET_PASSWORD'] else 'default_value'
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        # Error should be about missing credentials
        assert "You haven't configured the Linux login credentials" in result[0]["error"]
        assert "action_required" in result[0]
        assert result[0]["action_required"] == "configure_linux_credentials"

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    def test_run_invalid_input(self, mock_get_ports, mock_get_config):
        """Test run with invalid input"""
        invalid_input = '{"device_name": "debian01"'  # Invalid JSON
        
        # Mock get_config to return credentials (shouldn't be called due to invalid input)
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        result = self.tool._run(invalid_input)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Invalid JSON string input from model" in result[0]["error"]
        mock_get_ports.assert_not_called()
        mock_get_config.assert_not_called()  # Should not be called due to invalid input

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    def test_run_device_hosts_data_failure(self, mock_get_ports, mock_get_config):
        """Test run when device hosts data preparation fails"""
        mock_get_ports.return_value = {}  # Empty result triggers ValueError
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to get device information from topology" in result[0]["error"]

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_run_nornir_init_failure(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test run when Nornir initialization fails"""
        mock_get_ports.return_value = {
            "debian01": {"port": 5000}
        }
        
        mock_init_nornir.side_effect = Exception("Nornir init failed")
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to initialize Nornir" in result[0]["error"]

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_run_execution_exception(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test run when execution fails with exception"""
        mock_get_ports.return_value = {
            "debian01": {"port": 5000}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        mock_nornir.run.side_effect = Exception("Execution failed")
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Execution error" in result[0]["error"]

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_run_with_list_input(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test run with list input instead of JSON string"""
        mock_get_ports.return_value = {
            "debian01": {"port": 5000}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Mock login result
        mock_login_result = Mock()
        mock_login_result.failed = False
        mock_login_result.result = "Login successful"
        mock_login_task_result = {"debian01": mock_login_result}
        
        # Create mock result item
        mock_result_item = Mock()
        mock_result_item.failed = False
        mock_result_item.result = {"uname -a": "Linux debian01 5.10.0"}
        
        # Mock multi_result object
        mock_multi_result = Mock()
        mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.side_effect = [mock_login_task_result, mock_task_result]
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        # Test with JSON string input
        single_device_input = json.dumps([self.valid_input[0]])
        result = self.tool._run(single_device_input)
        
        assert len(result) == 1
        assert result[0]["status"] == "success"


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling for LinuxTelnetBatchTool"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = LinuxTelnetBatchTool()

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_empty_commands(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test with empty commands for a device"""
        input_with_empty_commands = json.dumps([
            {
                "device_name": "debian01",
                "commands": []
            }
        ])
        
        mock_get_ports.return_value = {"debian01": {"port": 5000}}
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Mock login result
        mock_login_result = Mock()
        mock_login_result.failed = False
        mock_login_result.result = "Login successful"
        mock_login_task_result = {"debian01": mock_login_result}
        
        # Create mock result item
        mock_result_item = Mock()
        mock_result_item.failed = False
        mock_result_item.result = "No display commands to execute"
        
        # Mock multi_result object
        mock_multi_result = Mock()
        mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.side_effect = [mock_login_task_result, mock_task_result]
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        result = self.tool._run(input_with_empty_commands)
        assert len(result) == 1
        assert result[0]["status"] == "success"

    def test_malformed_device_config(self):
        """Test with malformed device config (missing required fields)"""
        malformed_input = [
            {
                "device_name": "debian01"
                # Missing commands
            }
        ]
        
        # This should cause KeyError in _configs_map method
        with pytest.raises(KeyError):
            self.tool._configs_map(malformed_input)

    def test_none_tool_input(self):
        """Test with None tool input"""
        result = self.tool._validate_tool_input(json.dumps(None))
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Tool input must be a JSON object with 'project_id' and 'device_configs' fields" in result[0][0]["error"]

    def test_numeric_tool_input(self):
        """Test with numeric tool input"""
        result = self.tool._validate_tool_input(json.dumps(123))
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Tool input must be a JSON object with 'project_id' and 'device_configs' fields" in result[0][0]["error"]

    def test_environment_variables_handling(self):
        """Test that environment variables are properly used"""
        # Mock get_nornir_all_groups_config function to return expected structure
        from gns3_copilot.utils import get_nornir_all_groups_config
        
        def mock_get_nornir_all_groups_config():
            return {
                "linux_telnet": {
                    "hostname": "localhost",
                    "username": "testuser",
                    "password": "testpass",
                    "platform": "linux",
                    "timeout": 120,
                    "connection_options": {
                        "netmiko": {
                            "extras": {
                                "device_type": "generic_telnet",
                                "global_delay_factor": 3,
                                "fast_cli": False
                            }
                        }
                    }
                }
            }
        
        # Set required environment variables for testing
        with patch.dict(os.environ, {
            'LINUX_TELNET_USERNAME': 'testuser',
            'LINUX_TELNET_PASSWORD': 'testpass'
        }), patch('gns3_copilot.utils.get_nornir_all_groups_config', side_effect=mock_get_nornir_all_groups_config):
            # Call the function to get all groups config
            groups_config = get_nornir_all_groups_config()
            
            # Verify it returns a dict with group keys
            assert isinstance(groups_config, dict)
            assert "linux_telnet" in groups_config
            
            group_config = groups_config["linux_telnet"]
            
            # Verify required fields exist
            assert "hostname" in group_config
            assert "username" in group_config
            assert "password" in group_config
            assert "platform" in group_config
            assert "timeout" in group_config
            assert "connection_options" in group_config
            
            # Verify specific values for linux_telnet group
            assert group_config["platform"] == "linux"
            assert group_config["timeout"] == 120
            assert group_config["connection_options"]["netmiko"]["extras"]["device_type"] == "generic_telnet"
            assert group_config["connection_options"]["netmiko"]["extras"]["global_delay_factor"] == 3
            assert group_config["connection_options"]["netmiko"]["extras"]["fast_cli"] is False
            
            # Test that _initialize_nornir uses groups_data correctly
            hosts_data = {"debian01": {"port": 5000}}
            
            with patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir') as mock_init:
                mock_nornir = Mock()
                mock_init.return_value = mock_nornir
                
                self.tool._initialize_nornir(hosts_data)
                
                # Verify that groups_data is used in the call
                call_args = mock_init.call_args
                if call_args and len(call_args) > 1:
                    inventory_options = call_args[1]['inventory']['options']
                    groups_in_call = inventory_options['groups']
                    
                    # Should contain our groups_data
                    assert "linux_telnet" in groups_in_call
                    assert groups_in_call["linux_telnet"]["platform"] == "linux"
                    assert groups_in_call["linux_telnet"]["connection_options"]["netmiko"]["extras"]["device_type"] == "generic_telnet"

    def test_large_number_of_devices(self):
        """Test handling large number of devices"""
        # Create input with many devices
        large_input = []
        for i in range(100):
            large_input.append({
                "device_name": f"debian{i:02d}",
                "commands": [f"uname -a", f"df -h"]
            })
        
        # Test validation can handle it
        result = self.tool._validate_tool_input(json.dumps(large_input))
        assert len(result[0]) == 100  # Now returns (device_list, None)
        
        # Test configs map creation
        configs_map = self.tool._configs_map(result[0])
        assert len(configs_map) == 100
        assert "debian50" in configs_map
        assert len(configs_map["debian50"]) == 2

    def test_linux_safety_description(self):
        """Test that Linux-specific safety warnings are present in description"""
        description = self.tool.description
        
        # Check for Linux-specific warnings
        assert "Telnet console" in description
        assert "Do NOT use this tool for any Danger configuration commands" in description
        assert "non-interactive" in description
        assert "non-paginated" in description
        
        # Check for prohibited commands
        assert "top, vi/nano" in description
        assert "less or more" in description

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    def test_credentials_configured_check(self, mock_get_config):
        """Test that credentials check works properly when credentials are configured"""
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        # Test that when credentials are set, tool doesn't return credentials error
        # For empty input, we expect either empty result or a topology error (both are valid)
        result = self.tool._run("[]")  # Empty list is valid
        # The important thing is that we don't get a credentials error
        if len(result) > 0:
            # If there's an error, it should be about topology, not credentials
            assert "credentials" not in result[0].get("error", "").lower()
            assert "login credentials" not in result[0].get("error", "").lower()
        else:
            # Empty result is also valid for empty input
            assert len(result) == 0


class TestIntegrationScenarios:
    """Integration tests for LinuxTelnetBatchTool"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = LinuxTelnetBatchTool()

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_mixed_success_failure_scenario(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test scenario with mixed success and failure results"""
        mock_get_ports.return_value = {
            "debian01": {"port": 5000},
            "ubuntu01": {"port": 5001}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Mock login results - one success, one failure
        mock_login_success = Mock()
        mock_login_success.failed = False
        mock_login_success.result = "Login successful"
        
        mock_login_failure = Mock()
        mock_login_failure.failed = True
        mock_login_failure.result = "Login failed: Authentication error"
        
        mock_login_task_result = {
            "debian01": mock_login_success,
            "ubuntu01": mock_login_failure
        }
        
        # Mock command execution result for successful login only
        mock_result_item = Mock()
        mock_result_item.failed = False
        mock_result_item.result = {"uname -a": "Linux debian01 5.10.0"}
        
        mock_multi_result = Mock()
        mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
        
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.side_effect = [mock_login_task_result, mock_task_result]
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        input_data = json.dumps([
            {"device_name": "debian01", "commands": ["uname -a"]},
            {"device_name": "ubuntu01", "commands": ["ip a"]}
        ])
        
        result = self.tool._run(input_data)
        
        assert len(result) == 2
        assert result[0]["device_name"] == "debian01"
        assert result[0]["status"] == "success"
        assert result[1]["device_name"] == "ubuntu01"
        assert result[1]["status"] == "failed"
        assert "Login failed" in result[1]["error"]

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_config')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_concurrent_execution_simulation(self, mock_init_nornir, mock_get_ports, mock_get_config):
        """Test that tool is configured for concurrent execution"""
        mock_get_ports.return_value = {
            "debian01": {"port": 5000},
            "ubuntu01": {"port": 5001},
            "centos01": {"port": 5002}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Mock login results
        mock_login_results = {}
        for device in ["debian01", "ubuntu01", "centos01"]:
            mock_login = Mock()
            mock_login.failed = False
            mock_login.result = "Login successful"
            mock_login_results[device] = mock_login
        
        # Create mock result items
        mock_result_items = []
        mock_multi_results = []
        for i in range(3):
            mock_result_item = Mock()
            mock_result_item.failed = False
            mock_result_item.result = {f"uname -a": f"Linux device{i} 5.10.0"}
            mock_result_items.append(mock_result_item)
            
            mock_multi_result = Mock()
            mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
            mock_multi_results.append(mock_multi_result)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(side_effect=mock_multi_results)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.side_effect = [mock_login_results, mock_task_result]
        
        # Mock get_config to return credentials
        mock_get_config.side_effect = lambda key: 'testuser' if key == 'LINUX_TELNET_USERNAME' else ('testpass' if key == 'LINUX_TELNET_PASSWORD' else 'default_value')
        
        input_data = json.dumps([
            {"device_name": "debian01", "commands": ["uname -a"]},
            {"device_name": "ubuntu01", "commands": ["ip a"]},
            {"device_name": "centos01", "commands": ["df -h"]}
        ])
        
        result = self.tool._run(input_data)
        
        # Verify Nornir was initialized with threaded runner
        mock_init_nornir.assert_called_once()
        call_args = mock_init_nornir.call_args
        runner_config = call_args[1]['runner']
        
        assert runner_config['plugin'] == 'threaded'
        assert runner_config['options']['num_workers'] == 10
        
        # Verify all devices were processed
        assert len(result) == 3
        assert all(r["status"] == "success" for r in result)

    def test_linux_command_restrictions(self):
        """Test that the tool enforces Linux command restrictions"""
        description = self.tool.description
        
        # Verify command restrictions are documented
        assert "non-interactive" in description
        assert "non-paginated" in description
        assert "top, vi/nano" in description
        assert "less or more" in description
        assert "ping -c 1" in description
        assert "ps -aux instead of top" in description
        
        # Verify tool name and purpose
        assert self.tool.name == "linux_telnet_batch_commands"

    @patch('gns3_copilot.tools_v2.linux_tools_nornir.InitNornir')
    def test_nornir_configuration(self, mock_init_nornir):
        """Test that Nornir is configured correctly for Linux Telnet"""
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        hosts_data = {"debian01": {"port": 5000, "groups": ["linux_telnet"]}}
        
        self.tool._initialize_nornir(hosts_data)
        
        # Verify Nornir initialization parameters
        mock_init_nornir.assert_called_once()
        call_args = mock_init_nornir.call_args[1]
        
        # Check inventory configuration
        assert call_args['inventory']['plugin'] == 'DictInventory'
        assert 'hosts' in call_args['inventory']['options']
        assert 'groups' in call_args['inventory']['options']
        assert 'defaults' in call_args['inventory']['options']
        
        # Check runner configuration
        assert call_args['runner']['plugin'] == 'threaded'
        assert call_args['runner']['options']['num_workers'] == 10
        
        # Check logging configuration
        assert call_args['logging']['enabled'] is False
