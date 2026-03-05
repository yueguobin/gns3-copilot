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

def test_setup():
    # This is a temporary test to verify environment configuration is correct
    assert True


def test_package_import():
    """Test that main package can be imported normally"""
    import gns3_copilot

    assert gns3_copilot.__version__ is not None
    assert gns3_copilot.__author__ == "Guobin Yue"
    assert (
        gns3_copilot.__description__
        == "AI-powered network automation assistant for GNS3"
    )


def test_main_module_import():
    """Test that main module can be imported normally"""
    from gns3_copilot.main import main

    assert callable(main)


def test_app_module_import():
    """Test that app module can be imported normally"""
    from gns3_copilot.app import main as app_main

    assert callable(app_main)


def test_agent_module_import():
    """Test that agent module can be imported normally"""
    # Check if module can be imported, not specific classes
    import gns3_copilot.agent.gns3_copilot

    assert gns3_copilot.agent.gns3_copilot is not None


def test_gns3_client_module_import():
    """Test that GNS3 client module can be imported normally"""
    from gns3_copilot.gns3_client.custom_gns3fy import (
        Gns3Connector,
        Link,
        Node,
        Project,
    )
    from gns3_copilot.gns3_client.gns3_topology_reader import GNS3TopologyTool

    assert Gns3Connector is not None
    assert Node is not None
    assert Link is not None
    assert Project is not None
    assert GNS3TopologyTool is not None


def test_tools_module_import():
    """Test that tools module can be imported normally"""
    from gns3_copilot.tools_v2.gns3_create_link import GNS3LinkTool
    from gns3_copilot.tools_v2.gns3_create_node import GNS3CreateNodeTool
    from gns3_copilot.tools_v2.gns3_start_node import GNS3StartNodeTool

    assert GNS3CreateNodeTool is not None
    assert GNS3LinkTool is not None
    assert GNS3StartNodeTool is not None


def test_ui_modules_import():
    """Test that UI modules can be imported normally"""
    # Check if modules can be imported, not specific functions
    import gns3_copilot.ui_model.chat
    import gns3_copilot.ui_model.help
    import gns3_copilot.ui_model.settings

    assert gns3_copilot.ui_model.chat is not None
    assert gns3_copilot.ui_model.help is not None
    assert gns3_copilot.ui_model.settings is not None
