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
Tests for config_tools_nornir module.
Contains test cases for ExecuteMultipleDeviceConfigCommands tool.

Test Coverage:
1. TestExecuteMultipleDeviceConfigCommands
   - Tool name and description validation
   - Input validation (_validate_tool_input):
     * Valid JSON string and list inputs
     * Invalid JSON string handling
     * Non-list input validation
     * Empty list handling
     * Bytes and bytearray input conversion
   - Config mapping (_configs_map):
     * Creating device to config commands mapping
     * Empty list handling
   - Device hosts data preparation (_prepare_device_hosts_data):
     * Successful data preparation
     * Empty result handling
     * Missing devices handling
   - Nornir initialization (_initialize_nornir):
     * Successful initialization
     * Initialization failure handling
   - Task result processing (_process_task_results):
     * Successful task results
     * Failed task results
     * Device not in topology scenarios
     * Device not in task results scenarios
   - Device config execution (_run_all_device_configs_with_single_retry):
     * Successful execution
     * No commands scenario
     * Retry success scenario
     * Retry failure scenario
   - Main run method (_run):
     * Successful execution
     * Invalid input handling
     * Device hosts data failure
     * Nornir init failure
     * Execution exception handling
     * List input support

2. TestEdgeCasesAndErrorHandling
   - Empty config commands for a device
   - Malformed device config (missing required fields)
   - None tool input handling
   - Numeric tool input handling
   - Environment variables handling and groups_data usage
   - Large number of devices (100 devices) handling

3. TestIntegrationScenarios
   - Mixed success and failure results scenario
   - Concurrent execution simulation (threaded runner with 10 workers)
   - Safety description content validation (forbidden operations warnings)

Total Test Cases: 30+
"""

import json
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Any, Dict, List

# Import the class to test
from gns3_copilot.tools_v2.config_tools_nornir import ExecuteMultipleDeviceConfigCommands


class TestExecuteMultipleDeviceConfigCommands:
    """Tests for ExecuteMultipleDeviceConfigCommands tool"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = ExecuteMultipleDeviceConfigCommands()
        
        # Sample valid input for testing
        self.valid_input = [
            {
                "device_name": "R-1",
                "config_commands": [
                    "interface Loopback0",
                    "ip address 1.1.1.1 255.255.255.255",
                    "description CONFIG_BY_TOOL"
                ]
            },
            {
                "device_name": "R-2",
                "config_commands": [
                    "interface Loopback0",
                    "ip address 2.2.2.2 255.255.255.255",
                    "description CONFIG_BY_TOOL"
                ]
            }
        ]
        
        self.valid_input_json = json.dumps(self.valid_input)

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        assert self.tool.name == "execute_multiple_device_config_commands"
        assert "CONFIGURATION" in self.tool.description
        assert "dangerous operations" in self.tool.description

    # Test _validate_tool_input method
    def test_validate_tool_input_valid_json_string(self):
        """Test validation with valid JSON string"""
        result = self.tool._validate_tool_input(self.valid_input_json)
        assert result == (self.valid_input, None)

    def test_validate_tool_input_valid_list(self):
        """Test validation with valid Python list"""
        result = self.tool._validate_tool_input(self.valid_input)
        assert result == (self.valid_input, None)

    def test_validate_tool_input_invalid_json_string(self):
        """Test validation with invalid JSON string"""
        invalid_json = '{"device_name": "R-1", "config_commands": ["cmd1"'  # Missing closing bracket
        result = self.tool._validate_tool_input(invalid_json)
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Invalid JSON string input from model" in result[0][0]["error"]

    def test_validate_tool_input_not_a_list(self):
        """Test validation when input is not a list"""
        not_a_list = {"device_name": "R-1", "config_commands": ["cmd1"]}
        result = self.tool._validate_tool_input(not_a_list)
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Missing required 'project_id' field in input" in result[0][0]["error"]

    def test_validate_tool_input_empty_list(self):
        """Test validation with empty list"""
        result = self.tool._validate_tool_input([])
        assert result == ([], None)

    def test_validate_tool_input_bytes(self):
        """Test validation with bytes input"""
        bytes_input = self.valid_input_json.encode('utf-8')
        result = self.tool._validate_tool_input(bytes_input)
        assert result == (self.valid_input, None)

    def test_validate_tool_input_bytearray(self):
        """Test validation with bytearray input"""
        bytearray_input = bytearray(self.valid_input_json.encode('utf-8'))
        result = self.tool._validate_tool_input(bytearray_input)
        assert result == (self.valid_input, None)

    # Test _configs_map method
    def test_configs_map(self):
        """Test creating device to config commands mapping"""
        result = self.tool._configs_map(self.valid_input)
        expected = {
            "R-1": [
                "interface Loopback0",
                "ip address 1.1.1.1 255.255.255.255",
                "description CONFIG_BY_TOOL"
            ],
            "R-2": [
                "interface Loopback0",
                "ip address 2.2.2.2 255.255.255.255",
                "description CONFIG_BY_TOOL"
            ]
        }
        assert result == expected

    def test_configs_map_empty_list(self):
        """Test configs map with empty list"""
        result = self.tool._configs_map([])
        assert result == {}

    # Test _prepare_device_hosts_data method
    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    def test_prepare_device_hosts_data_success(self, mock_get_ports):
        """Test successful device hosts data preparation"""
        mock_ports_return = {
            "R-1": {
                "port": 5000,
                "groups": ["cisco_IOSv_telnet"]
            },
            "R-2": {
                "port": 5001,
                "groups": ["cisco_IOSv_telnet"]
            }
        }
        mock_get_ports.return_value = mock_ports_return
        
        result = self.tool._prepare_device_hosts_data(self.valid_input)
        assert result == mock_ports_return
        mock_get_ports.assert_called_once_with(["R-1", "R-2"], None)

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    def test_prepare_device_hosts_data_empty_result(self, mock_get_ports):
        """Test device hosts data preparation with empty result"""
        mock_get_ports.return_value = {}
        
        with pytest.raises(ValueError, match="Failed to get device information from topology"):
            self.tool._prepare_device_hosts_data(self.valid_input)

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    def test_prepare_device_hosts_data_missing_devices(self, mock_get_ports):
        """Test device hosts data preparation with missing devices"""
        mock_ports_return = {
            "R-1": {
                "port": 5000,
                "groups": ["cisco_IOSv_telnet"]
            }
            # R-2 is missing
        }
        mock_get_ports.return_value = mock_ports_return
        
        # Should still work, just log warning for missing devices
        result = self.tool._prepare_device_hosts_data(self.valid_input)
        assert result == mock_ports_return

    # Test _initialize_nornir method
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_initialize_nornir_success(self, mock_init_nornir):
        """Test successful Nornir initialization"""
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        hosts_data = {
            "R-1": {
                "port": 5000,
                "groups": ["cisco_IOSv_telnet"]
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

    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_initialize_nornir_failure(self, mock_init_nornir):
        """Test Nornir initialization failure"""
        mock_init_nornir.side_effect = Exception("Nornir init failed")
        
        hosts_data = {"R-1": {"port": 5000}}
        
        with pytest.raises(ValueError, match="Failed to initialize Nornir"):
            self.tool._initialize_nornir(hosts_data)

    # Test _process_task_results method
    def test_process_task_results_success(self):
        """Test processing successful task results"""
        # Create mock result items
        mock_result_item1 = Mock()
        mock_result_item1.failed = False
        mock_result_item1.result = "Configuration applied successfully"
        
        mock_result_item2 = Mock()
        mock_result_item2.failed = False
        mock_result_item2.result = "Configuration applied successfully"
        
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
            "R-1": {"port": 5000},
            "R-2": {"port": 5001}
        }
        
        result = self.tool._process_task_results(self.valid_input, hosts_data, mock_task_result)
        
        assert len(result) == 2
        assert result[0]["device_name"] == "R-1"
        assert result[0]["status"] == "success"
        assert result[0]["output"] == "Configuration applied successfully"
        assert result[0]["config_commands"] == self.valid_input[0]["config_commands"]

    def test_process_task_results_failure(self):
        """Test processing failed task results"""
        # Create mock failed result item
        mock_result_item = Mock()
        mock_result_item.failed = True
        mock_result_item.result = "Configuration failed: Permission denied"
        
        # Mock multi_result object
        mock_multi_result = Mock()
        mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        hosts_data = {
            "R-1": {"port": 5000}
        }
        
        single_device_input = [self.valid_input[0]]
        result = self.tool._process_task_results(single_device_input, hosts_data, mock_task_result)
        
        assert len(result) == 1
        assert result[0]["device_name"] == "R-1"
        assert result[0]["status"] == "failed"
        assert "Configuration execution failed" in result[0]["error"]
        assert result[0]["output"] == "Configuration failed: Permission denied"

    def test_process_task_results_device_not_in_topology(self):
        """Test processing when device not in topology"""
        # Mock task result that doesn't contain devices
        mock_task_result = Mock()
        mock_task_result.__contains__ = Mock(return_value=False)
        
        hosts_data = {
            "R-1": {"port": 5000}
            # R-2 is missing
        }
        
        result = self.tool._process_task_results(self.valid_input, hosts_data, mock_task_result)
        
        assert len(result) == 2
        assert result[0]["device_name"] == "R-1"
        assert result[0]["status"] == "failed"
        assert "not found in task results" in result[0]["error"]
        assert result[1]["device_name"] == "R-2"
        assert result[1]["status"] == "failed"
        assert "not found in topology" in result[1]["error"]

    def test_process_task_results_device_not_in_task_results(self):
        """Test processing when device not in task results"""
        # Mock task result that doesn't contain devices
        mock_task_result = Mock()
        mock_task_result.__contains__ = Mock(return_value=False)
        
        hosts_data = {
            "R-1": {"port": 5000},
            "R-2": {"port": 5001}
        }
        
        result = self.tool._process_task_results(self.valid_input, hosts_data, mock_task_result)
        
        assert len(result) == 2
        assert result[0]["status"] == "failed"
        assert "not found in task results" in result[0]["error"]
        assert result[1]["status"] == "failed"
        assert "not found in task results" in result[1]["error"]

    # Test _run_all_device_configs_with_single_retry method
    def test_run_all_device_configs_success(self):
        """Test successful device config execution"""
        mock_task = Mock()
        mock_task.host.name = "R-1"
        
        mock_run_result = Mock()
        mock_run_result.result = "Config applied"
        mock_task.run.return_value = mock_run_result
        
        device_configs_map = {
            "R-1": ["interface Loopback0", "ip address 1.1.1.1 255.255.255.255"]
        }
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is False
        assert result.result == "Config applied"
        mock_task.run.assert_called_once()

    def test_run_all_device_configs_no_commands(self):
        """Test device config execution with no commands"""
        mock_task = Mock()
        mock_task.host.name = "R-1"
        
        device_configs_map = {}  # No commands for this device
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is False
        assert result.result == "No configuration commands to execute"

    def test_run_all_device_configs_with_retry_success(self):
        """Test device config execution with retry success"""
        mock_task = Mock()
        mock_task.host.name = "R-1"
        
        mock_run_result1 = Mock()
        mock_run_result2 = Mock()
        mock_run_result2.result = "Config applied after retry"
        
        # First call fails with netmiko error, second succeeds
        mock_task.run.side_effect = [
            Exception("netmiko_send_config (failed)"),
            mock_run_result2
        ]
        
        device_configs_map = {
            "R-1": ["interface Loopback0"]
        }
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is False
        assert result.result == "Config applied after retry"
        assert mock_task.run.call_count == 2

    def test_run_all_device_configs_with_retry_failure(self):
        """Test device config execution with retry failure"""
        mock_task = Mock()
        mock_task.host.name = "R-1"
        mock_task.run.side_effect = Exception("Some other error")
        
        device_configs_map = {
            "R-1": ["interface Loopback0"]
        }
        
        result = self.tool._run_all_device_configs_with_single_retry(mock_task, device_configs_map)
        
        assert result.failed is True
        assert "Configuration failed (Unhandled Exception)" in result.result

    # Test main _run method
    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_run_success(self, mock_init_nornir, mock_get_ports):
        """Test successful run of the tool"""
        # Mock dependencies
        mock_get_ports.return_value = {
            "R-1": {"port": 5000},
            "R-2": {"port": 5001}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Create mock result items
        mock_result_item1 = Mock()
        mock_result_item1.failed = False
        mock_result_item1.result = "Configuration applied successfully"
        
        mock_result_item2 = Mock()
        mock_result_item2.failed = False
        mock_result_item2.result = "Configuration applied successfully"
        
        # Mock multi_result objects
        mock_multi_result1 = Mock()
        mock_multi_result1.__getitem__ = Mock(return_value=mock_result_item1)
        
        mock_multi_result2 = Mock()
        mock_multi_result2.__getitem__ = Mock(return_value=mock_result_item2)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(side_effect=[mock_multi_result1, mock_multi_result2])
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.return_value = mock_task_result
        
        # Execute
        result = self.tool._run(self.valid_input_json)
        
        # Verify
        assert len(result) == 2
        assert all(r["status"] == "success" for r in result)
        
        mock_get_ports.assert_called_once_with(["R-1", "R-2"], None)
        mock_init_nornir.assert_called_once()
        mock_nornir.run.assert_called_once()

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    def test_run_invalid_input(self, mock_get_ports):
        """Test run with invalid input"""
        invalid_input = '{"device_name": "R-1"'  # Invalid JSON
        
        result = self.tool._run(invalid_input)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Invalid JSON string input from model" in result[0]["error"]
        mock_get_ports.assert_not_called()

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    def test_run_device_hosts_data_failure(self, mock_get_ports):
        """Test run when device hosts data preparation fails"""
        mock_get_ports.return_value = {}  # Empty result triggers ValueError
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to get device information from topology" in result[0]["error"]

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_run_nornir_init_failure(self, mock_init_nornir, mock_get_ports):
        """Test run when Nornir initialization fails"""
        mock_get_ports.return_value = {
            "R-1": {"port": 5000}
        }
        
        mock_init_nornir.side_effect = Exception("Nornir init failed")
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Failed to initialize Nornir" in result[0]["error"]

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_run_execution_exception(self, mock_init_nornir, mock_get_ports):
        """Test run when execution fails with exception"""
        mock_get_ports.return_value = {
            "R-1": {"port": 5000}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        mock_nornir.run.side_effect = Exception("Execution failed")
        
        result = self.tool._run(self.valid_input_json)
        
        assert len(result) == 1
        assert "error" in result[0]
        assert "Execution error" in result[0]["error"]

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_run_with_list_input(self, mock_init_nornir, mock_get_ports):
        """Test run with list input instead of JSON string"""
        mock_get_ports.return_value = {
            "R-1": {"port": 5000}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Create mock result item
        mock_result_item = Mock()
        mock_result_item.failed = False
        mock_result_item.result = "Configuration applied successfully"
        
        # Mock multi_result object
        mock_multi_result = Mock()
        mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.return_value = mock_task_result
        
        # Test with list input
        single_device_input = [self.valid_input[0]]
        result = self.tool._run(single_device_input)
        
        assert len(result) == 1
        assert result[0]["status"] == "success"


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling for ExecuteMultipleDeviceConfigCommands"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = ExecuteMultipleDeviceConfigCommands()

    def test_empty_config_commands(self):
        """Test with empty config commands for a device"""
        input_with_empty_commands = [
            {
                "device_name": "R-1",
                "config_commands": []
            }
        ]
        
        @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
        @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
        def test_execution(mock_init_nornir, mock_get_ports):
            mock_get_ports.return_value = {"R-1": {"port": 5000}}
            
            mock_nornir = Mock()
            mock_init_nornir.return_value = mock_nornir
            
            # Create mock result item
            mock_result_item = Mock()
            mock_result_item.failed = False
            mock_result_item.result = "No configuration commands to execute"
            
            # Mock multi_result object
            mock_multi_result = Mock()
            mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
            
            # Mock task result
            mock_task_result = Mock()
            mock_task_result.__getitem__ = Mock(return_value=mock_multi_result)
            mock_task_result.__contains__ = Mock(return_value=True)
            
            mock_nornir.run.return_value = mock_task_result
            
            result = self.tool._run(input_with_empty_commands)
            assert len(result) == 1
            assert result[0]["status"] == "success"
        
        test_execution()

    def test_malformed_device_config(self):
        """Test with malformed device config (missing required fields)"""
        malformed_input = [
            {
                "device_name": "R-1"
                # Missing config_commands
            }
        ]
        
        # This should cause KeyError in _configs_map method
        with pytest.raises(KeyError):
            self.tool._configs_map(malformed_input)

    def test_none_tool_input(self):
        """Test with None tool input"""
        result = self.tool._validate_tool_input(None)
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Tool input must be a JSON object with 'project_id' and 'device_configs' fields" in result[0][0]["error"]

    def test_numeric_tool_input(self):
        """Test with numeric tool input"""
        result = self.tool._validate_tool_input(123)
        assert len(result) == 2  # Now returns (error_list, None)
        assert "error" in result[0][0]
        assert "Tool input must be a JSON object with 'project_id' and 'device_configs' fields" in result[0][0]["error"]

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_nornir_groups_config')
    def test_environment_variables_handling(self, mock_get_nornir_groups_config):
        """Test that environment variables are properly used"""
        # Mock get_nornir_groups_config function to return expected structure
        mock_get_nornir_groups_config.return_value = {
            "platform": "cisco_ios",
            "hostname": "localhost",
            "username": "admin",
            "password": "password",
            "timeout": 120,
            "connection_options": {
                "netmiko": {
                    "extras": {
                        "device_type": "cisco_ios_telnet"
                    }
                }
            }
        }
        
        from gns3_copilot.utils import get_nornir_groups_config
        groups_data = get_nornir_groups_config()
        
        # Verify structure
        assert "platform" in groups_data
        assert "hostname" in groups_data
        assert "username" in groups_data
        assert "password" in groups_data
        assert "timeout" in groups_data
        assert "connection_options" in groups_data
        
        # Verify specific values
        assert groups_data["platform"] == "cisco_ios"
        assert groups_data["timeout"] == 120
        assert groups_data["connection_options"]["netmiko"]["extras"]["device_type"] == "cisco_ios_telnet"

    def test_large_number_of_devices(self):
        """Test handling large number of devices"""
        # Create input with many devices
        large_input = []
        for i in range(100):
            large_input.append({
                "device_name": f"R-{i}",
                "config_commands": [f"interface Loopback{i}", f"ip address {i}.{i}.{i}.{i} 255.255.255.255"]
            })
        
        # Test validation can handle it
        result = self.tool._validate_tool_input(large_input)
        assert len(result[0]) == 100  # Now returns (device_list, None)
        
        # Test configs map creation
        configs_map = self.tool._configs_map(large_input)
        assert len(configs_map) == 100
        assert f"R-50" in configs_map
        assert len(configs_map[f"R-50"]) == 2


class TestIntegrationScenarios:
    """Integration tests for ExecuteMultipleDeviceConfigCommands"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tool = ExecuteMultipleDeviceConfigCommands()

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_mixed_success_failure_scenario(self, mock_init_nornir, mock_get_ports):
        """Test scenario with mixed success and failure results"""
        mock_get_ports.return_value = {
            "R-1": {"port": 5000},
            "R-2": {"port": 5001}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Create mock result items
        mock_success_result_item = Mock()
        mock_success_result_item.failed = False
        mock_success_result_item.result = "Configuration applied successfully"
        
        mock_failure_result_item = Mock()
        mock_failure_result_item.failed = True
        mock_failure_result_item.result = "Permission denied"
        
        # Mock multi_result objects
        mock_success_multi_result = Mock()
        mock_success_multi_result.__getitem__ = Mock(return_value=mock_success_result_item)
        
        mock_failure_multi_result = Mock()
        mock_failure_multi_result.__getitem__ = Mock(return_value=mock_failure_result_item)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(side_effect=[mock_success_multi_result, mock_failure_multi_result])
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.return_value = mock_task_result
        
        input_data = [
            {"device_name": "R-1", "config_commands": ["interface Loopback0"]},
            {"device_name": "R-2", "config_commands": ["interface Loopback0"]}
        ]
        
        result = self.tool._run(input_data)
        
        assert len(result) == 2
        assert result[0]["device_name"] == "R-1"
        assert result[0]["status"] == "success"
        assert result[1]["device_name"] == "R-2"
        assert result[1]["status"] == "failed"
        assert "Permission denied" in result[1]["error"]

    @patch('gns3_copilot.tools_v2.config_tools_nornir.get_device_ports_from_topology')
    @patch('gns3_copilot.tools_v2.config_tools_nornir.InitNornir')
    def test_concurrent_execution_simulation(self, mock_init_nornir, mock_get_ports):
        """Test that tool is configured for concurrent execution"""
        mock_get_ports.return_value = {
            "R-1": {"port": 5000},
            "R-2": {"port": 5001},
            "R-3": {"port": 5002}
        }
        
        mock_nornir = Mock()
        mock_init_nornir.return_value = mock_nornir
        
        # Create mock result items
        mock_result_items = []
        mock_multi_results = []
        for i in range(3):
            mock_result_item = Mock()
            mock_result_item.failed = False
            mock_result_item.result = "Configuration applied successfully"
            mock_result_items.append(mock_result_item)
            
            mock_multi_result = Mock()
            mock_multi_result.__getitem__ = Mock(return_value=mock_result_item)
            mock_multi_results.append(mock_multi_result)
        
        # Mock task result
        mock_task_result = Mock()
        mock_task_result.__getitem__ = Mock(side_effect=mock_multi_results)
        mock_task_result.__contains__ = Mock(return_value=True)
        
        mock_nornir.run.return_value = mock_task_result
        
        input_data = [
            {"device_name": "R-1", "config_commands": ["interface Loopback0"]},
            {"device_name": "R-2", "config_commands": ["interface Loopback0"]},
            {"device_name": "R-3", "config_commands": ["interface Loopback0"]}
        ]
        
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

    def test_safety_description_content(self):
        """Test that safety warnings are present in description"""
        description = self.tool.description
        
        # Check for forbidden operations
        forbidden_operations = [
            "reload", "reboot", "write erase", "erase startup-config",
            "format", "erase nvram", "delete flash", "boot system",
            "factory-reset", "user confirmation"
        ]
        
        for operation in forbidden_operations:
            assert operation in description.lower(), f"Missing safety warning for {operation}"
        
        # Check for safety warning message
        assert "important safety warning" in description.lower() or "important safety note" in description.lower()
