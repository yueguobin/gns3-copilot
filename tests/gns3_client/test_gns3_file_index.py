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
Comprehensive test suite for gns3_file_index module
Tests file index management functions for GNS3 projects

Test Coverage:
1. TestGetIndexPath
   - Index path generation
   - Index file name constant

2. TestLoadFileIndex
   - Loading existing index
   - Creating new index when not found
   - Index structure validation

3. TestSaveFileIndex
   - Saving index data
   - Index format validation
   - Error handling

4. TestCreateEmptyIndex
   - Empty index structure
   - Default values
   - Timestamp generation

5. TestAddFileToIndex
   - Adding new files
   - Updating existing files
   - Size parameter handling
   - Timestamp updates

6. TestGetFileList
   - Retrieving file list
   - Empty index handling
   - Invalid index handling

7. TestFileIndexEdgeCases
   - Multiple files
   - Duplicate files
   - Large file lists
   - Special characters in paths
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the module to test
from gns3_copilot.gns3_client.gns3_file_index import (
    _get_index_path,
    load_file_index,
    save_file_index,
    _create_empty_index,
    add_file_to_index,
    get_file_list,
    INDEX_FILE_NAME,
)


class TestGetIndexPath:
    """Tests for _get_index_path function"""

    def test_index_path_returns_constant(self):
        """Test that index path returns the constant file name"""
        project_id = "test-project-id"
        result = _get_index_path(project_id)
        
        assert result == INDEX_FILE_NAME

    def test_index_path_constant_value(self):
        """Test the constant index file name"""
        assert INDEX_FILE_NAME == ".gns3_copilot_file_index.json"


class TestCreateEmptyIndex:
    """Tests for _create_empty_index function"""

    def test_empty_index_structure(self):
        """Test that empty index has correct structure"""
        project_id = "test-project-id"
        index = _create_empty_index(project_id)
        
        assert isinstance(index, dict)
        assert "project_id" in index
        assert "files" in index
        assert "created_at" in index
        assert "updated_at" in index

    def test_empty_index_project_id(self):
        """Test that empty index contains project_id"""
        project_id = "1445a4ba-4635-430b-a332-bef438f65932"
        index = _create_empty_index(project_id)
        
        assert index["project_id"] == project_id

    def test_empty_index_files_list(self):
        """Test that empty index has empty files list"""
        project_id = "test-id"
        index = _create_empty_index(project_id)
        
        assert isinstance(index["files"], list)
        assert len(index["files"]) == 0

    def test_empty_index_timestamps(self):
        """Test that empty index has valid timestamps"""
        project_id = "test-id"
        index = _create_empty_index(project_id)
        
        assert isinstance(index["created_at"], str)
        assert isinstance(index["updated_at"], str)
        # Timestamps should be valid ISO format strings
        # They may have minor time differences due to two datetime.now() calls

    def test_empty_index_timestamp_format(self):
        """Test that timestamps are in ISO format"""
        project_id = "test-id"
        index = _create_empty_index(project_id)
        
        # Should be parseable as datetime
        datetime.fromisoformat(index["created_at"])
        datetime.fromisoformat(index["updated_at"])


class TestLoadFileIndex:
    """Tests for load_file_index function"""

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_load_existing_index(self, mock_get_index_path):
        """Test loading an existing index"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # Mock get_file to return valid JSON
        index_content = """
        {
            "project_id": "test-project-id",
            "files": [
                {
                    "path": "test.txt",
                    "created_at": "2026-01-01T10:00:00",
                    "updated_at": null,
                    "size": 100
                }
            ]
        }
        """
        mock_project.get_file.return_value = index_content
        
        index = load_file_index(mock_project)
        
        assert isinstance(index, dict)
        assert "files" in index
        assert len(index["files"]) == 1
        assert index["files"][0]["path"] == "test.txt"

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_load_index_creates_new_if_not_found(self, mock_get_index_path):
        """Test that new index is created when file not found"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # Mock get_file to raise FileNotFoundError
        mock_project.get_file.side_effect = FileNotFoundError("Not found")
        
        index = load_file_index(mock_project)
        
        assert isinstance(index, dict)
        assert "files" in index
        assert len(index["files"]) == 0
        assert index["project_id"] == "test-project-id"

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_load_index_invalid_structure(self, mock_get_index_path):
        """Test loading index with invalid structure creates new one"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # Mock get_file to return invalid structure (list instead of dict)
        mock_project.get_file.return_value = "[]"
        
        index = load_file_index(mock_project)
        
        assert isinstance(index, dict)
        assert "files" in index
        assert isinstance(index["files"], list)

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_load_index_missing_files_field(self, mock_get_index_path):
        """Test that missing files field is added"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # Mock get_file to return index without files field
        index_content = '{"project_id": "test"}'
        mock_project.get_file.return_value = index_content
        
        index = load_file_index(mock_project)
        
        assert "files" in index
        assert isinstance(index["files"], list)

    def test_load_index_no_project_id(self):
        """Test that ValueError is raised when project_id is None"""
        mock_project = Mock()
        mock_project.project_id = None
        
        with pytest.raises(ValueError, match="Project ID must be set"):
            load_file_index(mock_project)


class TestSaveFileIndex:
    """Tests for save_file_index function"""

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_save_index_success(self, mock_get_index_path):
        """Test successful index save"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        index_data = {
            "project_id": "test-project-id",
            "files": [],
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:00:00"
        }
        
        # Should not raise any exception
        save_file_index(mock_project, index_data)
        
        # Verify write_file was called
        mock_project.write_file.assert_called_once()

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_save_index_adds_project_id(self, mock_get_index_path):
        """Test that project_id is added to index"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        index_data = {
            "files": [],
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:00:00"
        }
        
        save_file_index(mock_project, index_data)
        
        # Verify project_id was added
        call_args = mock_project.write_file.call_args
        import json
        saved_data = json.loads(call_args[1]["data"])
        assert saved_data["project_id"] == "test-project-id"

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_save_index_json_format(self, mock_get_index_path):
        """Test that index is saved as JSON"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        index_data = {
            "project_id": "test-project-id",
            "files": [],
            "created_at": "2026-01-01T10:00:00",
            "updated_at": "2026-01-01T10:00:00"
        }
        
        save_file_index(mock_project, index_data)
        
        # Verify write_file was called with string data
        call_args = mock_project.write_file.call_args
        assert isinstance(call_args[1]["data"], str)

    def test_save_index_no_project_id(self):
        """Test that ValueError is raised when project_id is None"""
        mock_project = Mock()
        mock_project.project_id = None
        
        index_data = {"files": []}
        
        with pytest.raises(ValueError, match="Project ID must be set"):
            save_file_index(mock_project, index_data)

    @patch('gns3_copilot.gns3_client.gns3_file_index._get_index_path')
    def test_save_index_error_handling(self, mock_get_index_path):
        """Test error handling when save fails"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        index_data = {"files": []}
        
        mock_project.write_file.side_effect = Exception("Write failed")
        
        with pytest.raises(ValueError, match="Failed to save file index"):
            save_file_index(mock_project, index_data)


class TestAddFileToIndex:
    """Tests for add_file_to_index function"""

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_add_new_file(self, mock_load, mock_save):
        """Test adding a new file to index"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        
        result = add_file_to_index(mock_project, "test.txt", size=100)
        
        assert len(result["files"]) == 1
        assert result["files"][0]["path"] == "test.txt"
        assert result["files"][0]["size"] == 100
        mock_save.assert_called_once()

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_update_existing_file(self, mock_load, mock_save):
        """Test updating an existing file"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": [
                {
                    "path": "test.txt",
                    "created_at": "2026-01-01T10:00:00",
                    "updated_at": None,
                    "size": 100
                }
            ]
        }
        
        result = add_file_to_index(mock_project, "test.txt", size=200)
        
        assert len(result["files"]) == 1
        assert result["files"][0]["size"] == 200
        assert result["files"][0]["updated_at"] is not None

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_add_file_without_size(self, mock_load, mock_save):
        """Test adding file without specifying size"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        
        result = add_file_to_index(mock_project, "test.txt")
        
        assert len(result["files"]) == 1
        assert result["files"][0]["path"] == "test.txt"
        assert "size" not in result["files"][0]

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_add_multiple_files(self, mock_load, mock_save):
        """Test adding multiple files"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # First file
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        add_file_to_index(mock_project, "file1.txt", size=100)
        
        # Second file
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": [
                {
                    "path": "file1.txt",
                    "created_at": "2026-01-01T10:00:00",
                    "updated_at": None,
                    "size": 100
                }
            ]
        }
        result = add_file_to_index(mock_project, "file2.txt", size=200)
        
        assert len(result["files"]) == 2

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_updated_timestamp(self, mock_load, mock_save):
        """Test that updated_at timestamp is set"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        
        result = add_file_to_index(mock_project, "test.txt", size=100)
        
        assert result["updated_at"] is not None
        assert isinstance(result["updated_at"], str)


class TestGetFileList:
    """Tests for get_file_list function"""

    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_get_file_list(self, mock_load):
        """Test retrieving file list"""
        mock_project = Mock()
        
        mock_load.return_value = {
            "files": [
                {"path": "file1.txt", "size": 100},
                {"path": "file2.txt", "size": 200}
            ]
        }
        
        file_list = get_file_list(mock_project)
        
        assert len(file_list) == 2
        assert file_list[0]["path"] == "file1.txt"
        assert file_list[1]["path"] == "file2.txt"

    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_get_empty_file_list(self, mock_load):
        """Test retrieving empty file list"""
        mock_project = Mock()
        
        mock_load.return_value = {
            "files": []
        }
        
        file_list = get_file_list(mock_project)
        
        assert isinstance(file_list, list)
        assert len(file_list) == 0

    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_get_file_list_no_files_field(self, mock_load):
        """Test handling index without files field"""
        mock_project = Mock()
        
        mock_load.return_value = {}
        
        file_list = get_file_list(mock_project)
        
        assert isinstance(file_list, list)
        assert len(file_list) == 0

    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_get_file_list_invalid_files_type(self, mock_load):
        """Test handling invalid files type"""
        mock_project = Mock()
        
        mock_load.return_value = {
            "files": "not a list"
        }
        
        file_list = get_file_list(mock_project)
        
        assert isinstance(file_list, list)
        assert len(file_list) == 0

    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_get_file_list_error_handling(self, mock_load):
        """Test error handling when load fails"""
        mock_project = Mock()
        
        mock_load.side_effect = Exception("Load failed")
        
        file_list = get_file_list(mock_project)
        
        assert isinstance(file_list, list)
        assert len(file_list) == 0


class TestFileIndexEdgeCases:
    """Tests for edge cases"""

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_add_file_with_special_chars(self, mock_load, mock_save):
        """Test adding file with special characters in path"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        
        result = add_file_to_index(mock_project, "config_v2.0.txt", size=100)
        
        assert result["files"][0]["path"] == "config_v2.0.txt"

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_add_nested_path(self, mock_load, mock_save):
        """Test adding file with nested path"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        
        result = add_file_to_index(mock_project, "configs/router1.cfg", size=100)
        
        assert result["files"][0]["path"] == "configs/router1.cfg"

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_add_duplicate_path_updates(self, mock_load, mock_save):
        """Test that adding duplicate path updates existing entry"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # First addition
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": []
        }
        add_file_to_index(mock_project, "test.txt", size=100)
        
        # Second addition (same path)
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": [
                {
                    "path": "test.txt",
                    "created_at": "2026-01-01T10:00:00",
                    "updated_at": None,
                    "size": 100
                }
            ]
        }
        result = add_file_to_index(mock_project, "test.txt", size=200)
        
        # Should still have only one entry with updated size
        assert len(result["files"]) == 1
        assert result["files"][0]["size"] == 200

    @patch('gns3_copilot.gns3_client.gns3_file_index.save_file_index')
    @patch('gns3_copilot.gns3_client.gns3_file_index.load_file_index')
    def test_large_file_index(self, mock_load, mock_save):
        """Test handling large file index"""
        mock_project = Mock()
        mock_project.project_id = "test-project-id"
        
        # Create large index
        files = [
            {"path": f"file{i}.txt", "created_at": "2026-01-01T10:00:00", "updated_at": None, "size": 100}
            for i in range(1000)
        ]
        
        mock_load.return_value = {
            "project_id": "test-project-id",
            "files": files
        }
        
        file_list = get_file_list(mock_project)
        
        assert len(file_list) == 1000
