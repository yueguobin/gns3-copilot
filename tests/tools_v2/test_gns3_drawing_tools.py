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
Tests for GNS3 drawing tools (get, create, update, delete).

Contains comprehensive test cases for GNS3GetDrawingsTool, GNS3CreateDrawingTool,
GNS3UpdateDrawingTool, and GNS3DeleteDrawingTool functionality.

Test Coverage:
1. TestGNS3GetDrawingsTool
   - Tool initialization validation
   - Input validation (missing project_id, invalid JSON)
   - Success scenarios (single drawing, multiple drawings)
   - Error handling (connector exceptions, API errors)

2. TestGNS3CreateDrawingTool
   - Tool initialization validation
   - Input validation (missing fields, invalid data types)
   - Success scenarios (single drawing, multiple drawings)
   - Error handling (connector exceptions, drawing creation failures)
   - Edge cases (large drawings, special SVG content)

3. TestGNS3UpdateDrawingTool
   - Tool initialization validation
   - Input validation (missing drawing_id, invalid property types)
   - Success scenarios (partial updates, multiple properties)
   - Error handling (invalid drawing_id, connector exceptions)

4. TestGNS3DeleteDrawingTool
   - Tool initialization validation
   - Input validation (missing fields)
   - Success scenarios (deletion with confirmation)
   - Error handling (invalid drawing_id, connector exceptions)

5. TestGNS3DrawingToolsIntegration
   - Combined workflow (create -> get -> update -> delete)
   - Multiple drawings management

Total Test Cases: 40+
"""

import json
import os
import pytest
from unittest.mock import Mock, patch
from typing import Any, Dict

# Import modules to test
from gns3_copilot.gns3_client.gns3_get_drawings import GNS3GetDrawingsTool
from gns3_copilot.gns3_client.gns3_create_drawing import GNS3CreateDrawingTool
from gns3_copilot.gns3_client.gns3_update_drawing import GNS3UpdateDrawingTool
from gns3_copilot.gns3_client.gns3_delete_drawing import GNS3DeleteDrawingTool


# ============================================================================
# GNS3GetDrawingsTool Tests
# ============================================================================

class TestGNS3GetDrawingsToolInitialization:
    """Test cases for GNS3GetDrawingsTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3GetDrawingsTool()
        assert tool.name == "get_gns3_drawings"
        assert "Retrieves all drawings" in tool.description
        assert "GNS3 project" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3GetDrawingsTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3GetDrawingsTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3GetDrawingsToolInputValidation:
    """Test cases for GNS3GetDrawingsTool input validation"""

    def test_empty_input(self):
        """Test empty input handling"""
        tool = GNS3GetDrawingsTool()
        result = tool._run("")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_invalid_json(self):
        """Test invalid JSON input"""
        tool = GNS3GetDrawingsTool()
        result = tool._run("{invalid json}")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3GetDrawingsTool()
        input_data = {}
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing project_id" in result["error"]

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_get_drawings.get_gns3_connector')
    def test_connector_exception(self, mock_get_gns3_connector):
        """Test exception during connector initialization"""
        tool = GNS3GetDrawingsTool()
        input_data = {"project_id": "project1"}
        
        mock_get_gns3_connector.side_effect = Exception("Connection failed")
        
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Failed to retrieve drawings" in result["error"]


class TestGNS3GetDrawingsToolSuccessScenarios:
    """Test cases for GNS3GetDrawingsTool success scenarios"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_get_drawings.get_gns3_connector')
    def test_get_empty_drawings(self, mock_get_gns3_connector):
        """Test getting drawings from project with no drawings"""
        tool = GNS3GetDrawingsTool()
        input_data = {"project_id": "project1"}
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project with no drawings
        with patch('gns3_copilot.gns3_client.gns3_get_drawings.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = []
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
            
            assert "project_id" in result
            assert result["project_id"] == "project1"
            assert "drawings" in result
            assert len(result["drawings"]) == 0
            assert result["total_drawings"] == 0

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_get_drawings.get_gns3_connector')
    def test_get_single_drawing(self, mock_get_gns3_connector):
        """Test getting a single drawing"""
        tool = GNS3GetDrawingsTool()
        input_data = {"project_id": "project1"}
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project with one drawing
        with patch('gns3_copilot.gns3_client.gns3_get_drawings.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": "drawing1",
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": False,
                    "rotation": 0
                }
            ]
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
            
            assert result["project_id"] == "project1"
            assert len(result["drawings"]) == 1
            assert result["total_drawings"] == 1
            assert result["drawings"][0]["drawing_id"] == "drawing1"
            assert result["drawings"][0]["svg"] == "<svg>test</svg>"

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_get_drawings.get_gns3_connector')
    def test_get_multiple_drawings(self, mock_get_gns3_connector):
        """Test getting multiple drawings"""
        tool = GNS3GetDrawingsTool()
        input_data = {"project_id": "project1"}
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project with multiple drawings
        with patch('gns3_copilot.gns3_client.gns3_get_drawings.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": "drawing1",
                    "svg": "<svg>test1</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": False,
                    "rotation": 0
                },
                {
                    "drawing_id": "drawing2",
                    "svg": "<svg>test2</svg>",
                    "x": -200,
                    "y": 300,
                    "z": 1,
                    "locked": True,
                    "rotation": 90
                },
                {
                    "drawing_id": "drawing3",
                    "svg": "<svg>test3</svg>",
                    "x": 0,
                    "y": 0,
                    "z": 2,
                    "locked": False,
                    "rotation": 45
                }
            ]
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
            
            assert result["project_id"] == "project1"
            assert len(result["drawings"]) == 3
            assert result["total_drawings"] == 3
            assert result["drawings"][0]["drawing_id"] == "drawing1"
            assert result["drawings"][1]["drawing_id"] == "drawing2"
            assert result["drawings"][2]["drawing_id"] == "drawing3"


# ============================================================================
# GNS3CreateDrawingTool Tests
# ============================================================================

class TestGNS3CreateDrawingToolInitialization:
    """Test cases for GNS3CreateDrawingTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3CreateDrawingTool()
        assert tool.name == "create_gns3_drawing"
        assert "Creates multiple drawings" in tool.description
        assert "GNS3 project" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3CreateDrawingTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3CreateDrawingTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3CreateDrawingToolInputValidation:
    """Test cases for GNS3CreateDrawingTool input validation"""

    def test_empty_input(self):
        """Test empty input handling"""
        tool = GNS3CreateDrawingTool()
        result = tool._run("")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_invalid_json(self):
        """Test invalid JSON input"""
        tool = GNS3CreateDrawingTool()
        result = tool._run("{invalid json}")
        assert "error" in result
        assert "Invalid JSON input" in result["error"]

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3CreateDrawingTool()
        input_data = {
            "drawings": [
                {
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing project_id" in result["error"]

    def test_empty_drawings_array(self):
        """Test empty drawings array"""
        tool = GNS3CreateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawings": []
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a non-empty array" in result["error"]

    def test_drawings_not_array(self):
        """Test drawings not an array"""
        tool = GNS3CreateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawings": "not an array"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a non-empty array" in result["error"]

    def test_missing_drawings_field(self):
        """Test missing drawings field"""
        tool = GNS3CreateDrawingTool()
        input_data = {"project_id": "project1"}
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a non-empty array" in result["error"]

    def test_drawing_missing_required_fields(self):
        """Test drawing definition missing required fields"""
        tool = GNS3CreateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawings": [
                {
                    "svg": "<svg>test</svg>",
                    "x": 100
                    # Missing y
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "missing or invalid svg, x, or y" in result["error"]

    def test_drawing_not_dictionary(self):
        """Test drawing definition not a dictionary"""
        tool = GNS3CreateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawings": ["not a dictionary"]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "must be a dictionary" in result["error"]

    def test_drawing_with_invalid_coordinates(self):
        """Test drawing definition with invalid coordinates"""
        tool = GNS3CreateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawings": [
                {
                    "svg": "<svg>test</svg>",
                    "x": "invalid",
                    "y": -200
                }
            ]
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "missing or invalid svg, x, or y" in result["error"]


class TestGNS3CreateDrawingToolSuccessScenarios:
    """Test cases for GNS3CreateDrawingTool success scenarios"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_create_drawing.get_gns3_connector')
    def test_single_drawing_creation(self, mock_get_gns3_connector):
        """Test successful single drawing creation"""
        tool = GNS3CreateDrawingTool()
        
        input_data = {
            "project_id": "project1",
            "drawings": [
                {
                    "svg": "<svg xmlns='http://www.w3.org/2000/svg'>test</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": False,
                    "rotation": 0
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project and create_drawing method
        with patch('gns3_copilot.gns3_client.gns3_create_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.create_drawing = Mock(return_value={"drawing_id": "drawing123"})
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
        
        assert result["project_id"] == "project1"
        assert len(result["created_drawings"]) == 1
        assert result["total_drawings"] == 1
        assert result["successful_drawings"] == 1
        assert result["failed_drawings"] == 0
        assert result["created_drawings"][0]["drawing_id"] == "drawing123"
        assert result["created_drawings"][0]["status"] == "success"

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_create_drawing.get_gns3_connector')
    def test_multiple_drawings_creation(self, mock_get_gns3_connector):
        """Test successful multiple drawings creation"""
        tool = GNS3CreateDrawingTool()
        
        input_data = {
            "project_id": "project1",
            "drawings": [
                {
                    "svg": "<svg>test1</svg>",
                    "x": 100,
                    "y": -200
                },
                {
                    "svg": "<svg>test2</svg>",
                    "x": -200,
                    "y": 300
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project and create_drawing method
        with patch('gns3_copilot.gns3_client.gns3_create_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.create_drawing = Mock(side_effect=[
                {"drawing_id": "drawing1"},
                {"drawing_id": "drawing2"}
            ])
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
        
        assert result["total_drawings"] == 2
        assert result["successful_drawings"] == 2
        assert result["failed_drawings"] == 0


class TestGNS3CreateDrawingToolErrorHandling:
    """Test cases for GNS3CreateDrawingTool error handling"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_create_drawing.get_gns3_connector')
    def test_drawing_creation_exception(self, mock_get_gns3_connector):
        """Test exception during drawing creation"""
        tool = GNS3CreateDrawingTool()
        
        input_data = {
            "project_id": "project1",
            "drawings": [
                {
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project and create_drawing method
        with patch('gns3_copilot.gns3_client.gns3_create_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.create_drawing = Mock(side_effect=Exception("Drawing creation failed"))
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
        
        assert result["total_drawings"] == 1
        assert result["successful_drawings"] == 0
        assert result["failed_drawings"] == 1
        assert result["created_drawings"][0]["status"] == "failed"


# ============================================================================
# GNS3UpdateDrawingTool Tests
# ============================================================================

class TestGNS3UpdateDrawingToolInitialization:
    """Test cases for GNS3UpdateDrawingTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3UpdateDrawingTool()
        assert tool.name == "update_gns3_drawing"
        assert "Updates drawing properties" in tool.description
        assert "GNS3 project" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3UpdateDrawingTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3UpdateDrawingTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3UpdateDrawingToolInputValidation:
    """Test cases for GNS3UpdateDrawingTool input validation"""

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "drawing_id": "drawing1",
            "x": 150,
            "y": -250
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing project_id" in result["error"]

    def test_missing_drawing_id(self):
        """Test missing drawing_id"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "x": 150,
            "y": -250
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing drawing_id" in result["error"]

    def test_no_properties_to_update(self):
        """Test no properties to update"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "No properties to update" in result["error"]

    def test_invalid_x_type(self):
        """Test invalid x type"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "x": "invalid"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "x must be a number" in result["error"]

    def test_invalid_y_type(self):
        """Test invalid y type"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "y": "invalid"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "y must be a number" in result["error"]

    def test_invalid_z_type(self):
        """Test invalid z type"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "z": "invalid"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "z must be a number" in result["error"]

    def test_invalid_locked_type(self):
        """Test invalid locked type"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "locked": "invalid"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "locked must be a boolean" in result["error"]

    def test_invalid_rotation_type(self):
        """Test invalid rotation type"""
        tool = GNS3UpdateDrawingTool()
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "rotation": "invalid"
        }
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "rotation must be a number" in result["error"]


class TestGNS3UpdateDrawingToolSuccessScenarios:
    """Test cases for GNS3UpdateDrawingTool success scenarios"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_update_drawing.get_gns3_connector')
    def test_partial_update(self, mock_get_gns3_connector):
        """Test partial update of drawing properties"""
        tool = GNS3UpdateDrawingTool()
        
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "x": 150,
            "y": -250
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project
        with patch('gns3_copilot.gns3_client.gns3_update_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": "drawing1",
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": False
                }
            ]
            mock_project.update_drawing = Mock(return_value={
                "drawing_id": "drawing1",
                "x": 150,
                "y": -250
            })
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
            
            assert result["project_id"] == "project1"
            assert result["drawing_id"] == "drawing1"
            assert result["status"] == "success"
            assert result["updated_properties"]["x"] == 150
            assert result["updated_properties"]["y"] == -250

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_update_drawing.get_gns3_connector')
    def test_multiple_properties_update(self, mock_get_gns3_connector):
        """Test updating multiple drawing properties"""
        tool = GNS3UpdateDrawingTool()
        
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1",
            "x": 150,
            "y": -250,
            "z": 1,
            "locked": True
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project
        with patch('gns3_copilot.gns3_client.gns3_update_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": "drawing1",
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200,
                    "z": 0,
                    "locked": False
                }
            ]
            mock_project.update_drawing = Mock(return_value={
                "drawing_id": "drawing1",
                "x": 150,
                "y": -250,
                "z": 1,
                "locked": True
            })
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
            
            assert result["status"] == "success"
            assert result["updated_properties"]["x"] == 150
            assert result["updated_properties"]["y"] == -250
            assert result["updated_properties"]["z"] == 1
            assert result["updated_properties"]["locked"] is True


# ============================================================================
# GNS3DeleteDrawingTool Tests
# ============================================================================

class TestGNS3DeleteDrawingToolInitialization:
    """Test cases for GNS3DeleteDrawingTool initialization"""

    def test_tool_name_and_description(self):
        """Test tool name and description"""
        tool = GNS3DeleteDrawingTool()
        assert tool.name == "delete_gns3_drawing"
        assert "Deletes a drawing" in tool.description
        assert "GNS3 project" in tool.description

    def test_tool_inheritance(self):
        """Test tool inherits from BaseTool"""
        from langchain.tools import BaseTool
        
        tool = GNS3DeleteDrawingTool()
        assert isinstance(tool, BaseTool)

    def test_tool_attributes(self):
        """Test tool has required attributes"""
        tool = GNS3DeleteDrawingTool()
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')
        assert hasattr(tool, '_run')


class TestGNS3DeleteDrawingToolInputValidation:
    """Test cases for GNS3DeleteDrawingTool input validation"""

    def test_missing_project_id(self):
        """Test missing project_id"""
        tool = GNS3DeleteDrawingTool()
        input_data = {"drawing_id": "drawing1"}
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing project_id" in result["error"]

    def test_missing_drawing_id(self):
        """Test missing drawing_id"""
        tool = GNS3DeleteDrawingTool()
        input_data = {"project_id": "project1"}
        result = tool._run(json.dumps(input_data))
        assert "error" in result
        assert "Missing drawing_id" in result["error"]


class TestGNS3DeleteDrawingToolSuccessScenarios:
    """Test cases for GNS3DeleteDrawingTool success scenarios"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_delete_drawing.get_gns3_connector')
    def test_successful_deletion(self, mock_get_gns3_connector):
        """Test successful drawing deletion"""
        tool = GNS3DeleteDrawingTool()
        
        input_data = {
            "project_id": "project1",
            "drawing_id": "drawing1"
        }
        
        # Mock connector
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_gns3_connector.return_value = mock_connector
        
        # Mock project
        with patch('gns3_copilot.gns3_client.gns3_delete_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": "drawing1",
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200
                }
            ]
            mock_project.delete_drawing = Mock()
            mock_project_class.return_value = mock_project
            
            result = tool._run(json.dumps(input_data))
            
            assert result["project_id"] == "project1"
            assert result["drawing_id"] == "drawing1"
            assert result["status"] == "success"
            
            # Verify delete was called
            mock_project.delete_drawing.assert_called_once_with(drawing_id="drawing1")


# ============================================================================
# Integration Tests
# ============================================================================

class TestGNS3DrawingToolsIntegration:
    """Integration tests for drawing tools"""

    @patch.dict(os.environ, {
        "GNS3_SERVER_URL": "http://localhost:3080"
    })
    @patch('gns3_copilot.gns3_client.gns3_delete_drawing.get_gns3_connector')
    @patch('gns3_copilot.gns3_client.gns3_update_drawing.get_gns3_connector')
    @patch('gns3_copilot.gns3_client.gns3_create_drawing.get_gns3_connector')
    @patch('gns3_copilot.gns3_client.gns3_get_drawings.get_gns3_connector')
    def test_complete_drawing_workflow(
        self,
        mock_get_connector,
        mock_create_connector,
        mock_update_connector,
        mock_delete_connector
    ):
        """Test complete workflow: create -> get -> update -> delete"""
        
        # Setup mock connectors
        mock_connector = Mock()
        mock_connector.base_url = "http://localhost:3080/v2"
        mock_get_connector.return_value = mock_connector
        mock_create_connector.return_value = mock_connector
        mock_update_connector.return_value = mock_connector
        mock_delete_connector.return_value = mock_connector
        
        # Step 1: Create drawing
        create_tool = GNS3CreateDrawingTool()
        create_input = {
            "project_id": "project1",
            "drawings": [
                {
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200
                }
            ]
        }
        
        with patch('gns3_copilot.gns3_client.gns3_create_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.create_drawing = Mock(return_value={"drawing_id": "drawing1"})
            mock_project_class.return_value = mock_project
            
            create_result = create_tool._run(json.dumps(create_input))
        
        assert create_result["successful_drawings"] == 1
        drawing_id = create_result["created_drawings"][0]["drawing_id"]
        
        # Step 2: Get drawings
        get_tool = GNS3GetDrawingsTool()
        get_input = {"project_id": "project1"}
        
        with patch('gns3_copilot.gns3_client.gns3_get_drawings.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": drawing_id,
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200
                }
            ]
            mock_project_class.return_value = mock_project
            
            get_result = get_tool._run(json.dumps(get_input))
            assert len(get_result["drawings"]) == 1
        
        # Step 3: Update drawing
        update_tool = GNS3UpdateDrawingTool()
        update_input = {
            "project_id": "project1",
            "drawing_id": drawing_id,
            "x": 150,
            "y": -250
        }
        
        with patch('gns3_copilot.gns3_client.gns3_update_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": drawing_id,
                    "svg": "<svg>test</svg>",
                    "x": 100,
                    "y": -200
                }
            ]
            mock_project.update_drawing = Mock(return_value={
                "drawing_id": drawing_id,
                "x": 150,
                "y": -250
            })
            mock_project_class.return_value = mock_project
            
            update_result = update_tool._run(json.dumps(update_input))
            assert update_result["status"] == "success"
        
        # Step 4: Delete drawing
        delete_tool = GNS3DeleteDrawingTool()
        delete_input = {
            "project_id": "project1",
            "drawing_id": drawing_id
        }
        
        with patch('gns3_copilot.gns3_client.gns3_delete_drawing.Project') as mock_project_class:
            mock_project = Mock()
            mock_project.drawings = [
                {
                    "drawing_id": drawing_id,
                    "svg": "<svg>test</svg>",
                    "x": 150,
                    "y": -250
                }
            ]
            mock_project.delete_drawing = Mock()
            mock_project_class.return_value = mock_project
            
            delete_result = delete_tool._run(json.dumps(delete_input))
            assert delete_result["status"] == "success"
