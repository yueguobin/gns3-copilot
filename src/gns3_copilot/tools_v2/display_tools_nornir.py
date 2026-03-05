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
This module provides a tool to execute display commands on multiple devices
 in a GNS3 topology using Nornir.
"""

import json
import re
from typing import Any

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from netmiko.exceptions import ReadTimeout
from nornir import InitNornir
from nornir.core import Nornir
from nornir.core.task import AggregatedResult, Result, Task
from nornir_netmiko.tasks import netmiko_multiline

from gns3_copilot.log_config import setup_tool_logger
from gns3_copilot.utils import (
    get_config,
    get_device_ports_from_topology,
    get_nornir_defaults,
    get_nornir_groups_config,
)

# config log
logger = setup_tool_logger("display_tools_nornir")


class ExecuteMultipleDeviceCommands(BaseTool):
    """
    A tool to execute display (show) commands on multiple devices in a GNS3 topology using Nornir.
    This class uses Nornir to manage connections and execute commands on multiple devices
     concurrently.

    **Important:**
    This tool is strictly for read-only operations.
    It is forbidden to execute any configuration commands, including 'configure terminal' or
     any command that changes device state.
    Only use this tool for safe, non-intrusive 'show' or display commands.
    """

    name: str = "execute_multiple_device_commands"
    description: str = """
    Executes display (show) commands on multiple devices in the current GNS3 topology.
    Input should be a JSON object containing project_id and device configurations.
    Example input:
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "R-1",
                    "commands": ["show version", "show ip interface brief"]
                },
                {
                    "device_name": "R-2",
                    "commands": ["show version", "show ip ospf neighbor"]
                }
            ]
        }
    Returns a list of dictionaries, each containing the device name and command outputs.

    **Do NOT use this tool for any configuration commands (such as 'configure terminal').**
    """

    def _run(
        self,
        tool_input: str | bytes | list[Any] | dict[str, Any],
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Executes display commands on multiple devices in current GNS3 topology.

        Args:
            tool_input (str): A JSON string containing project_id and device commands to
            execute.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing device names and
            command outputs.
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        # Validate input
        device_configs_list, project_id = self._validate_tool_input(tool_input)
        if (
            isinstance(device_configs_list, list)
            and len(device_configs_list) > 0
            and "error" in device_configs_list[0]
        ):
            return device_configs_list

        # Create a mapping of device names to their display commands
        device_configs_map = self._configs_map(device_configs_list)

        # Prepare device hosts data
        try:
            hosts_data = self._prepare_device_hosts_data(
                device_configs_list, project_id
            )
        except ValueError as e:
            logger.error("Failed to prepare device hosts data: %s", e)
            return [{"error": str(e)}]

        # Initialize Nornir
        try:
            dynamic_nr = self._initialize_nornir(hosts_data)
        except ValueError as e:
            logger.error("Failed to initialize Nornir: %s", e)
            return [{"error": str(e)}]

        results = []

        # Execute all devices concurrently in a single run
        try:
            task_result = dynamic_nr.run(
                task=self._run_all_device_configs_with_single_retry,
                device_configs_map=device_configs_map,
            )

            # Process results for all devices
            results = self._process_task_results(
                device_configs_list, hosts_data, task_result
            )

        except Exception as e:
            # Overall execution failed
            logger.error("Error executing display on all devices: %s", e)
            return [{"error": f"Execution error: {str(e)}"}]

        logger.info(
            "Multiple device display execution completed. Results: %s",
            json.dumps(results, indent=2, ensure_ascii=False),
        )

        return results

    def _run_all_device_configs_with_single_retry(
        self, task: Task, device_configs_map: dict[str, list[str]]
    ) -> Result:
        """Execute display commands with single retry mechanism."""
        device_name = task.host.name
        config_commands = device_configs_map.get(device_name, [])

        if not config_commands:
            return Result(host=task.host, result="No display commands to execute")

        try:
            _result = task.run(
                task=netmiko_multiline,
                commands=config_commands,
                enable=True,
                read_timeout=60,
            )
            return Result(host=task.host, result=_result.result)

        except ReadTimeout as e:
            # Log ReadTimeout exception with full details
            logger.error(
                "ReadTimeout occurred for device %s: %s",
                device_name,
                str(e),
            )
            logger.debug(
                "ReadTimeout details for device %s - Exception type: %s, Message: %s",
                device_name,
                type(e).__name__,
                str(e),
            )
            return Result(
                host=task.host,
                result=f"display failed (ReadTimeout): {str(e)}",
                failed=True,
            )

        except Exception as e:
            # Handle prompt detection issues with Cisco IOSv L2 images where the '#' prompt character
            # may be delayed, causing Netmiko prompt detection failures. Implements retry logic.
            if "netmiko_multiline (failed)" in str(e):
                _result = task.run(
                    task=netmiko_multiline,
                    commands=config_commands,
                    enable=True,
                    read_timeout=60,
                )
                return Result(host=task.host, result=_result.result)

            # Log any other exceptions with full details
            logger.error(
                "display failed for device %s: %s (Exception type: %s)",
                device_name,
                str(e),
                type(e).__name__,
            )
            logger.debug(
                "Full exception details for device %s: %s",
                device_name,
                str(e),
            )
            return Result(
                host=task.host,
                result=f"display failed (Unhandled Exception): {str(e)}",
                failed=True,
            )

    def _validate_tool_input(
        self, tool_input: str | bytes | list[Any] | dict[str, Any]
    ) -> tuple[list[dict[str, Any]], str | None]:
        """
        Validate device display command input, handling both new and legacy input formats.
        Supports new format with project_id and device_configs, as well as legacy array format.

        Args:
            tool_input: The input received from the LangChain/LangGraph tool call.

        Returns:
            Tuple containing (device_configs_list, project_id) or (error_list, None)
        """

        parsed_input = None

        # Compatibility Check and Parsing ---
        # Check if the input is a string (or bytes) which needs to be parsed.
        if isinstance(tool_input, (str, bytes, bytearray)):
            # Handle models (like potentially DeepSeek) that return a raw JSON string.
            try:
                parsed_input = json.loads(tool_input)
                logger.info("Successfully parsed tool input from JSON string.")
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON string received as tool input: %s", e)
                return ([{"error": f"Invalid JSON string input from model: {e}"}], None)
        else:
            # Handle standard models (like GPT/OpenAI) where the framework
            # has already parsed the JSON into a Python object (dict or list).
            parsed_input = tool_input
            logger.info(
                "Using tool input directly as type: %s", type(parsed_input).__name__
            )

        # Handle new format: {"project_id": "...", "device_configs": [...]}
        if isinstance(parsed_input, dict):
            project_id = parsed_input.get("project_id")
            device_configs = parsed_input.get("device_configs")

            # Validate project_id
            if not project_id:
                error_msg = "Missing required 'project_id' field in input"
                logger.error(error_msg)
                return ([{"error": error_msg}], None)

            if not self._validate_project_id(project_id):
                error_msg = (
                    f"Invalid project_id format: {project_id}. Expected UUID format."
                )
                logger.error(error_msg)
                return ([{"error": error_msg}], None)

            # Validate device_configs
            if not isinstance(device_configs, list):
                error_msg = "'device_configs' must be an array"
                logger.error(error_msg)
                return ([{"error": error_msg}], None)

            if not device_configs:
                logger.warning("Device configs list is empty.")
                return [], project_id

            return device_configs, project_id

        # Handle legacy format: [...]
        elif isinstance(parsed_input, list):
            logger.warning(
                "Using legacy input format without project_id. Please use new format with project_id."
            )
            return parsed_input, None

        else:
            error_msg = (
                "Tool input must be a JSON object with 'project_id' and 'device_configs' fields, "
                f"or a legacy JSON array, but got {type(parsed_input).__name__}"
            )
            logger.error(error_msg)
            return ([{"error": error_msg}], None)

    def _validate_project_id(self, project_id: str) -> bool:
        """
        Validate project_id format (UUID).

        Args:
            project_id: The project ID to validate

        Returns:
            True if valid UUID format, False otherwise
        """
        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        return bool(re.match(uuid_pattern, project_id, re.IGNORECASE))

    def _configs_map(
        self, device_config_list: list[dict[str, Any]]
    ) -> dict[str, list[str]]:
        """Create a mapping of device names to their display commands."""
        device_configs_map = {}
        for device_config in device_config_list:
            device_name = device_config["device_name"]
            config_commands = device_config["commands"]
            device_configs_map[device_name] = config_commands

        return device_configs_map

    def _prepare_device_hosts_data(
        self, device_config_list: list[dict[str, Any]], project_id: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """Prepare device hosts data from topology information."""
        # Extract device names list
        device_names = [
            device_config["device_name"] for device_config in device_config_list
        ]

        # Get device port information with project_id
        hosts_data = get_device_ports_from_topology(device_names, project_id)

        if not hosts_data:
            error_msg = (
                f"Failed to get device information from topology or no valid devices found. "
                f"Project ID: {project_id}, Devices: {device_names}"
            )
            raise ValueError(error_msg)

        # Check for missing devices
        missing_devices = set(device_names) - set(hosts_data.keys())
        if missing_devices:
            logger.warning(
                "Some devices not found in topology (Project ID: %s): %s",
                project_id or "default",
                missing_devices,
            )

        return hosts_data

    def _initialize_nornir(self, hosts_data: dict[str, dict[str, Any]]) -> Nornir:
        """Initialize Nornir with the provided hosts data."""
        try:
            # Get latest environment configuration
            groups_data = get_nornir_groups_config("cisco_IOSv_telnet")
            defaults = get_nornir_defaults()

            # Log nornir account information
            gns3_host = get_config("GNS3_SERVER_HOST")

            logger.info(
                "Initializing Nornir with account: host=%s, platform=%s, timeout=%d",
                gns3_host,
                groups_data.get("platform"),
                groups_data.get("timeout"),
            )

            return InitNornir(
                inventory={
                    "plugin": "DictInventory",
                    "options": {
                        "hosts": hosts_data,
                        "groups": {"cisco_IOSv_telnet": groups_data},
                        "defaults": defaults,
                    },
                },
                runner={
                    "plugin": "threaded",
                    "options": {"num_workers": 10},
                },
                logging={"enabled": False},
            )
        except Exception as e:
            logger.error("Failed to initialize Nornir: %s", e)
            raise ValueError(f"Failed to initialize Nornir: {e}") from e

    def _process_task_results(
        self,
        device_configs_list: list[dict[str, Any]],
        hosts_data: dict[str, dict[str, Any]],
        task_result: AggregatedResult,
    ) -> list[dict[str, Any]]:
        """Process the task results and format them for return."""
        results = []

        for device_config in device_configs_list:
            device_name = device_config["device_name"]
            config_commands = device_config["commands"]

            # Check if device is in topology
            if device_name not in hosts_data:
                device_result = {
                    "device_name": device_name,
                    "status": "failed",
                    "error": (
                        f"Device '{device_name}' not found in topology or missing console_port"
                    ),
                }
                results.append(device_result)
                continue

            # Check if device has execution results
            if device_name not in task_result:
                device_result = {
                    "device_name": device_name,
                    "status": "failed",
                    "error": (f"Device '{device_name}' not found in task results"),
                }
                results.append(device_result)
                continue

            # Process execution results
            multi_result = task_result[device_name]
            device_result = {"device_name": device_name}

            if multi_result[0].failed:
                # Execution failed
                device_result["status"] = "failed"
                device_result["error"] = (
                    f"Configuration execution failed: {multi_result[0].result}"
                )
                device_result["output"] = multi_result[0].result
            else:
                # Execution successful
                device_result["status"] = "success"
                device_result["output"] = multi_result[0].result
                device_result["config_commands"] = config_commands

            results.append(device_result)

        return results


if __name__ == "__main__":
    # Example usage with new format
    device_commands = json.dumps(
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "R-2",
                    "commands": ["show version", "show ip interface brief"],
                },
                {
                    "device_name": "R-1",
                    "commands": ["show version", "show ip interface brief"],
                },
                {
                    "device_name": "SW-1",
                    "commands": ["show version", "show ip interface brief"],
                },
                {
                    "device_name": "SW-2",
                    "commands": ["show version", "show ip interface brief"],
                },
            ],
        }
    )

    exe_cmd = ExecuteMultipleDeviceCommands()

    failed_count = 0

    for _i in range(0, 1):
        exe_results = exe_cmd._run(tool_input=device_commands)
        for result in exe_results:
            for result in exe_results:
                if result.get("status") == "failed":
                    failed_count += 1

    print(f"Failed Count: {failed_count}")

    # print("Execution results:")
    # print(json.dumps(result, indent=2, ensure_ascii=False))
