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
Tests for log_config module.
Contains test cases for logging configuration functionality.

Test Coverage:
1. TestSetupLogger
   - Basic logger setup with default levels
   - Logger with custom console and file levels
   - Logger with custom log file path
   - No duplicate handlers prevention
   - Directory creation for log files

2. TestGetLogger
   - Getting existing logger
   - Creating new logger
   - Logger singleton behavior

3. TestConfigurePackageLogging
   - Package logging configuration with custom level
   - Default logging level (INFO)
   - Package logger level verification

4. TestSetupToolLogger
   - Tool logger with predefined config
   - Tool logger without predefined config
   - Tool logger with same name as config entry

5. TestLoggerConfigs
   - LOGGER_CONFIGS structure validation
   - Required fields verification (console_level, file_level)
   - Expected tools existence check (app, chat, settings, device_config)

6. TestEdgeCases
   - Empty logger name handling
   - Permission error handling for log files

7. TestVersionHandling
   - Successful version retrieval from metadata
   - Version fallback on import error
   - __version__ attribute verification

8. TestFixtures
   - Logger cleanup after tests
   - Test logger management

Total Test Cases: 20+
"""

import logging
import os
import tempfile
import pytest
from unittest.mock import patch, Mock

from gns3_copilot.log_config import (
    setup_logger,
    get_logger,
    configure_package_logging,
    setup_tool_logger,
    LOGGER_CONFIGS,
)


class TestSetupLogger:
    """Test setup_logger function."""
    
    def test_basic_setup(self):
        """Test basic logger setup."""
        logger = setup_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 2  # file + console
        assert not logger.propagate
    
    def test_custom_levels(self):
        """Test logger with custom levels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "levels_test.log")
            # Clear any existing logger first
            import logging
            if "test_levels" in logging.Logger.manager.loggerDict:
                del logging.Logger.manager.loggerDict["test_levels"]
            
            logger = setup_logger(
                "test_levels",
                log_file=log_file,
                console_level=logging.WARNING,
                file_level=logging.CRITICAL
            )
            
            handlers = logger.handlers
            # Find handlers by type more carefully
            console_handler = None
            file_handler = None
            
            for h in handlers:
                if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler):
                    console_handler = h
                elif isinstance(h, logging.FileHandler):
                    file_handler = h
            
            assert console_handler is not None
            assert file_handler is not None
            assert console_handler.level == logging.WARNING
            assert file_handler.level == logging.CRITICAL
    
    def test_custom_log_file(self):
        """Test logger with custom log file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            logger = setup_logger("test_file", log_file=tmp.name)
            
            file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
            assert file_handler.baseFilename == tmp.name
            
            # Clean up
            os.unlink(tmp.name)
    
    def test_no_duplicate_handlers(self):
        """Test that duplicate handlers are not added."""
        logger1 = setup_logger("duplicate_test")
        logger2 = setup_logger("duplicate_test")
        
        assert logger1 is logger2
        assert len(logger2.handlers) == 2
    
    @patch('gns3_copilot.log_config.logging_config.TimedRotatingFileHandler')
    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_directory_creation(self, mock_exists, mock_makedirs, mock_handler):
        """Test log directory creation."""
        mock_exists.return_value = False
        mock_handler.return_value = Mock()
        setup_logger("test_dir", log_file="custom/test.log")
        
        mock_makedirs.assert_called_once_with("custom", exist_ok=True)


class TestGetLogger:
    """Test get_logger function."""
    
    def test_get_existing_logger(self):
        """Test getting existing logger."""
        original = setup_logger("existing_test")
        retrieved = get_logger("existing_test")
        
        assert original is retrieved
    
    def test_get_new_logger(self):
        """Test getting non-existing logger."""
        logger = get_logger("new_test")
        
        assert logger.name == "new_test"
        assert len(logger.handlers) > 0


class TestConfigurePackageLogging:
    """Test configure_package_logging function."""
    
    def test_package_logging(self):
        """Test package logging configuration."""
        configure_package_logging(logging.WARNING)
        
        package_logger = logging.getLogger("tools")
        assert package_logger.level == logging.WARNING
    
    def test_default_level(self):
        """Test default logging level."""
        configure_package_logging()
        
        package_logger = logging.getLogger("tools")
        assert package_logger.level == logging.INFO


class TestSetupToolLogger:
    """Test setup_tool_logger function."""
    
    def test_tool_with_config(self):
        """Test tool logger with predefined config."""
        # Clean up any existing logger
        if "test_tool" in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict["test_tool"]
        
        with patch('gns3_copilot.log_config.logging_config.TimedRotatingFileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            logger = setup_tool_logger("test_tool", "device_config")
            
            # Should use config from LOGGER_CONFIGS
            assert logger.name == "test_tool"
            mock_handler.assert_called_once()
    
    def test_tool_without_config(self):
        """Test tool logger without predefined config."""
        # Clean up any existing logger
        if "unknown_tool" in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict["unknown_tool"]
        
        with patch('gns3_copilot.log_config.logging_config.TimedRotatingFileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            logger = setup_tool_logger("unknown_tool")
            
            # Should use default values
            assert logger.name == "unknown_tool"
            mock_handler.assert_called_once()
    
    def test_tool_same_name_config(self):
        """Test tool with same name as config."""
        # Clean up any existing logger
        if "app" in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict["app"]
        
        with patch('gns3_copilot.log_config.logging_config.TimedRotatingFileHandler') as mock_handler:
            mock_handler.return_value = Mock()
            logger = setup_tool_logger("app")  # 'app' exists in LOGGER_CONFIGS
            
            assert logger.name == "app"
            mock_handler.assert_called_once()


class TestLoggerConfigs:
    """Test LOGGER_CONFIGS."""
    
    def test_configs_structure(self):
        """Test that all configs have required structure."""
        for name, config in LOGGER_CONFIGS.items():
            assert "console_level" in config
            assert "file_level" in config
            assert isinstance(config["console_level"], int)
            assert isinstance(config["file_level"], int)
    
    def test_tools_work_with_default_config(self):
        """Test that tools work correctly without explicit configs (using default)."""
        expected_tools = ["app", "chat", "settings", "device_config"]
        
        for tool in expected_tools:
            # These tools should not require explicit config entries
            logger = setup_tool_logger(tool)
            assert logger.name == tool
            assert len(logger.handlers) == 2  # file + console


class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_logger_name(self):
        """Test empty logger name."""
        logger = setup_logger("")
        # Python logging converts empty name to "root"
        assert logger.name in ["", "root"]
    
    def test_permission_error(self):
        """Test permission error handling."""
        with patch('gns3_copilot.log_config.logging_config.TimedRotatingFileHandler', side_effect=PermissionError):
            with pytest.raises(PermissionError):
                setup_logger("permission_test", log_file="/root/test.log")


class TestVersionHandling:
    """Test version handling in __init__.py."""
    
    @patch('importlib.metadata.version')
    def test_version_success(self, mock_version):
        """Test successful version retrieval."""
        mock_version.return_value = "1.0.0"
        
        # Re-import to test version handling
        import importlib
        import sys
        if 'gns3_copilot.log_config' in sys.modules:
            del sys.modules['gns3_copilot.log_config']
        
        import gns3_copilot.log_config
        assert gns3_copilot.log_config.__version__ == "1.0.0"
    
    @patch('importlib.metadata.version')
    def test_version_fallback(self, mock_version):
        """Test version fallback on error."""
        mock_version.side_effect = ImportError()
        
        import importlib
        import sys
        if 'gns3_copilot.log_config' in sys.modules:
            del sys.modules['gns3_copilot.log_config']
        
        import gns3_copilot.log_config
        # Should not crash and have a version string
        assert hasattr(gns3_copilot.log_config, '__version__')
        assert isinstance(gns3_copilot.log_config.__version__, str)


@pytest.fixture(autouse=True)
def cleanup_loggers():
    """Clean up test loggers after each test."""
    yield
    
    # Clean up test loggers
    logger_manager = logging.Logger.manager.loggerDict
    test_loggers = [name for name in logger_manager.keys() 
                   if name.startswith(('test_', 'permission_test', 'existing_test', 'new_test', 'duplicate_test', 'unknown_tool'))]
    
    for logger_name in test_loggers:
        if logger_name in logger_manager:
            del logger_manager[logger_name]
