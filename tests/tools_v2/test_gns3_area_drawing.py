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
Unit tests for GNS3 area annotation drawing tools.

Tests drawing utility functions and area drawing tool
for calculating ellipse parameters and generating SVG content.
"""

import math

from gns3_copilot.utils.gns3_drawing_utils import (
    calculate_two_node_ellipse,
    generate_ellipse_svg,
    generate_text_svg,
    COLOR_SCHEMES,
)


class TestCalculateTwoNodeEllipse:
    """Test cases for calculate_two_node_ellipse function."""

    def test_horizontal_layout(self):
        """Test ellipse calculation for horizontal node layout."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "Area 0"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)

        # Assert
        # Check metadata - center calculated from node centers (top-left + width/2, height/2)
        # Default device width is 50, height is 50
        expected_center_x = (100 + 25 + 300 + 25) / 2.0
        expected_center_y = (200 + 25 + 200 + 25) / 2.0
        assert abs(result["metadata"]["center_x"] - expected_center_x) < 0.1
        assert abs(result["metadata"]["center_y"] - expected_center_y) < 0.1
        assert result["metadata"]["distance"] == 200.0
        assert abs(result["metadata"]["angle_deg"]) < 0.1  # Should be ~0 degrees

        # Check ellipse parameters
        expected_rx = 200.0 / 2
        expected_ry = math.sqrt(50.0 ** 2 + 50.0 ** 2) / 2.0
        assert result["metadata"]["rx"] == expected_rx
        assert result["metadata"]["ry"] == expected_ry

        # Check SVG content
        assert "<svg" in result["ellipse"]["svg"]
        assert "<ellipse" in result["ellipse"]["svg"]
        assert "Area 0" in result["text"]["svg"]
        assert "<text" in result["text"]["svg"]

        # Check rotation - ellipse rotates, text doesn't
        assert result["ellipse"]["rotation"] == 0
        assert result["text"]["rotation"] == 0  # Text is always horizontal

        print("✅ test_horizontal_layout passed")

    def test_vertical_layout(self):
        """Test ellipse calculation for vertical node layout."""
        # Arrange
        node1 = {"x": 200, "y": 100}
        node2 = {"x": 200, "y": 300}
        area_name = "Area 1"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)

        # Assert
        # Check metadata - center calculated from node centers (top-left + width/2, height/2)
        expected_center_x = (200 + 25 + 200 + 25) / 2.0
        expected_center_y = (100 + 25 + 300 + 25) / 2.0
        assert abs(result["metadata"]["center_x"] - expected_center_x) < 0.1
        assert abs(result["metadata"]["center_y"] - expected_center_y) < 0.1
        assert result["metadata"]["distance"] == 200.0
        assert abs(result["metadata"]["angle_deg"] - 90.0) < 0.1  # Should be ~90 degrees

        # Check ellipse parameters
        expected_rx = 200.0 / 2
        expected_ry = math.sqrt(50.0 ** 2 + 50.0 ** 2) / 2.0
        assert result["metadata"]["rx"] == expected_rx
        assert result["metadata"]["ry"] == expected_ry

        # Check SVG content
        assert "<svg" in result["ellipse"]["svg"]
        assert "<ellipse" in result["ellipse"]["svg"]
        assert "Area 1" in result["text"]["svg"]

        # Check rotation
        assert result["ellipse"]["rotation"] == 90
        assert result["text"]["rotation"] == 0  # Text is always horizontal

        print("✅ test_vertical_layout passed")

    def test_diagonal_layout(self):
        """Test ellipse calculation for diagonal node layout."""
        # Arrange
        node1 = {"x": 100, "y": 100}
        node2 = {"x": 300, "y": 300}
        area_name = "Area 0"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)

        # Assert
        # Check metadata
        expected_center_x = (100 + 25 + 300 + 25) / 2.0
        expected_center_y = (100 + 25 + 300 + 25) / 2.0
        assert abs(result["metadata"]["center_x"] - expected_center_x) < 0.1
        assert abs(result["metadata"]["center_y"] - expected_center_y) < 0.1
        expected_distance = math.sqrt(200**2 + 200**2)
        assert abs(result["metadata"]["distance"] - expected_distance) < 0.1
        assert abs(result["metadata"]["angle_deg"] - 45.0) < 0.1  # Should be ~45 degrees

        # Check ellipse parameters
        expected_rx = expected_distance / 2
        expected_ry = math.sqrt(50.0 ** 2 + 50.0 ** 2) / 2.0
        assert abs(result["metadata"]["rx"] - expected_rx) < 0.1
        assert result["metadata"]["ry"] == expected_ry

        # Check SVG content
        assert "<svg" in result["ellipse"]["svg"]
        assert "<ellipse" in result["ellipse"]["svg"]

        # Check rotation
        assert result["ellipse"]["rotation"] == 45
        assert result["text"]["rotation"] == 0  # Text is always horizontal

        print("✅ test_diagonal_layout passed")

    def test_custom_text_offset_ratio(self):
        """Test ellipse calculation with custom text offset ratio."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "Area 0"
        custom_ratio = 0.5

        # Act
        result = calculate_two_node_ellipse(
            node1, node2, area_name, text_offset_ratio=custom_ratio
        )

        # Assert - text position should be adjusted based on ratio
        assert result["text"]["rotation"] == 0  # Text is always horizontal
        assert "text" in result
        assert "svg" in result["text"]

        print("✅ test_custom_text_offset_ratio passed")

    def test_color_scheme_area0(self):
        """Test color scheme for Area 0 (CORE_BACKBONE)."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "Area 0"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)

        # Assert - Area 0 uses CORE_BACKBONE color scheme
        # Check that colors are present in SVG
        assert "fill=" in result["ellipse"]["svg"]
        assert "fill=" in result["text"]["svg"]

        # Check for expected fill color (hex format)
        expected_fill = "#2980B9"
        assert expected_fill in result["ellipse"]["svg"]

        # Check for fill-opacity attribute
        assert 'fill-opacity="0.8"' in result["ellipse"]["svg"]

        # Check for expected text color (white for dark background)
        expected_text_color = "#FFFFFF"
        assert expected_text_color in result["text"]["svg"]

        print("✅ test_color_scheme_area0 passed")

    def test_color_scheme_other_area(self):
        """Test color scheme for Area 1 (NORMAL_AREA)."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "Area 1"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)

        # Assert - Area 1 uses NORMAL_AREA color scheme
        assert "fill=" in result["ellipse"]["svg"]
        assert "fill=" in result["text"]["svg"]

        # Check for expected fill color (hex format)
        expected_fill = "#5AA9DD"
        assert expected_fill in result["ellipse"]["svg"]

        # Check for fill-opacity attribute
        assert 'fill-opacity="0.8"' in result["ellipse"]["svg"]

        # Check for expected text color (black for light background)
        expected_text_color = "#000000"
        assert expected_text_color in result["text"]["svg"]

        print("✅ test_color_scheme_other_area passed")

    def test_color_scheme_default(self):
        """Test color scheme for default/uncategorized labels."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "My Network Area"  # Doesn't match any pattern, uses DEFAULT

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)

        # Assert
        # Uses DEFAULT since no keywords match
        expected_text_color = COLOR_SCHEMES["DEFAULT"]["stroke"]
        assert expected_text_color in result["text"]["svg"]

        print("✅ test_color_scheme_default passed")

    def test_svg_structure_ellipse(self):
        """Test that generated ellipse SVG has correct structure."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "Area 0"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)
        svg = result["ellipse"]["svg"]

        # Assert
        # Check SVG structure - implementation doesn't include xmlns attribute
        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert '<ellipse' in svg
        # No border/stroke in new design
        assert 'stroke=' not in svg
        # Using fill-opacity attribute instead of rgba()
        assert 'fill-opacity=' in svg
        # Check for hex color format
        assert '#' in svg

        print("✅ test_svg_structure_ellipse passed")

    def test_svg_structure_text(self):
        """Test that generated text SVG has correct structure."""
        # Arrange
        node1 = {"x": 100, "y": 200}
        node2 = {"x": 300, "y": 200}
        area_name = "Area 0"

        # Act
        result = calculate_two_node_ellipse(node1, node2, area_name)
        svg = result["text"]["svg"]

        # Assert
        assert svg.startswith('<svg')
        assert svg.endswith('</svg>')
        assert '<text' in svg
        assert 'font-size=' in svg
        assert 'font-weight="bold"' in svg
        assert 'text-anchor="middle"' in svg

        print("✅ test_svg_structure_text passed")


def run_all_tests():
    """Run all unit tests."""
    print("=" * 80)
    print("Running GNS3 Area Drawing Unit Tests")
    print("=" * 80)

    test_class = TestCalculateTwoNodeEllipse()

    # Run two-node tests
    test_class.test_horizontal_layout()
    test_class.test_vertical_layout()
    test_class.test_diagonal_layout()
    test_class.test_custom_text_offset_ratio()
    test_class.test_color_scheme_area0()
    test_class.test_color_scheme_other_area()
    test_class.test_color_scheme_default()
    test_class.test_svg_structure_ellipse()
    test_class.test_svg_structure_text()

    print("=" * 80)
    print("✅ All unit tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
