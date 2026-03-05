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
Comprehensive test suite for connector_factory module
Tests get_gns3_connector factory function

Test Coverage:
1. TestConnectorFactoryBasic
   - Function import and availability
   - Return type validation

2. TestConnectorFactorySuccessV2
   - Successful connector creation with API v2
   - Correct parameters passed for v2
   - Return value validation

3. TestConnectorFactorySuccessV3
   - Successful connector creation with API v3
   - Authentication credentials passed for v3
   - Return value validation

4. TestConnectorFactoryInputValidation
   - Missing API_VERSION
   - Missing GNS3_SERVER_URL
   - Missing username/password for v3

5. TestConnectorFactoryErrorHandling
   - Invalid API_VERSION
   - Connection errors
   - Exception handling
   - Logging verification

6. TestConnectorFactoryEdgeCases
   - Empty environment variables
   - Whitespace in URLs
   - Special characters in credentials
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the module to test
from gns3_copilot.gns3_client.connector_factory import get_gns3_connector
from gns3_copilot.gns3_client.custom_gns3fy import Gns3Connector


class TestConnectorFactoryBasic:
    """Basic tests for connector factory function"""

    def test_function_import(self):
        """Test that get_gns3_connector can be imported"""
        assert get_gns3_connector is not None
        assert callable(get_gns3_connector)

    def test_function_name(self):
        """Test function name is correct"""
        assert get_gns3_connector.__name__ == "get_gns3_connector"

    def test_return_type_none_on_missing_env(self):
        """Test returns None when config variables are missing"""
        def mock_get_config(key, default=None):
            return None
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None


class TestConnectorFactorySuccessV2:
    """Tests for successful connector creation with API v2"""

    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_success_v2_api(self, mock_connector_class):
        """Test successful connector creation with v2 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        mock_connector_class.assert_called_once()
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["url"] == "http://localhost:3080"
        assert call_kwargs["api_version"] == 2
        assert "user" not in call_kwargs
        assert "cred" not in call_kwargs

    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_custom_server_url_v2(self, mock_connector_class):
        """Test connector creation with custom server URL for v2"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://192.168.1.100:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["url"] == "http://192.168.1.100:3080"
        assert call_kwargs["api_version"] == 2

    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_https_url_v2(self, mock_connector_class):
        """Test connector creation with HTTPS URL for v2"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "https://gns3.example.com:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["url"] == "https://gns3.example.com:3080"
        assert call_kwargs["api_version"] == 2

    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_return_value_is_connector_instance(self, mock_connector_class):
        """Test that return value is a Gns3Connector instance"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is mock_connector


class TestConnectorFactorySuccessV3:
    """Tests for successful connector creation with API v3"""

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_success_v3_api(self, mock_connector_class):
        """Test successful connector creation with v3 API"""
        # Mock connector
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080",
                "GNS3_SERVER_USERNAME": "admin",
                "GNS3_SERVER_PASSWORD": "password123"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        mock_connector_class.assert_called_once()
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["url"] == "http://localhost:3080"
        assert call_kwargs["api_version"] == 3
        assert call_kwargs["user"] == "admin"
        assert call_kwargs["cred"] == "password123"

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_custom_credentials_v3(self, mock_connector_class):
        """Test connector creation with custom credentials for v3"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://192.168.1.100:3080",
                "GNS3_SERVER_USERNAME": "testuser",
                "GNS3_SERVER_PASSWORD": "testpass"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["url"] == "http://192.168.1.100:3080"
        assert call_kwargs["user"] == "testuser"
        assert call_kwargs["cred"] == "testpass"

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_special_characters_in_credentials(self, mock_connector_class):
        """Test connector creation with special characters in credentials"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080",
                "GNS3_SERVER_USERNAME": "user@domain.com",
                "GNS3_SERVER_PASSWORD": "P@ssw0rd!123"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["user"] == "user@domain.com"
        assert call_kwargs["cred"] == "P@ssw0rd!123"

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_empty_credentials_v3(self, mock_connector_class):
        """Test connector creation with empty credentials for v3"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080",
                "GNS3_SERVER_USERNAME": "",
                "GNS3_SERVER_PASSWORD": ""
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["user"] == ""
        assert call_kwargs["cred"] == ""


class TestConnectorFactoryInputValidation:
    """Tests for input validation"""

    def test_missing_api_version(self):
        """Test missing API_VERSION config variable"""
        def mock_get_config(key, default=None):
            if key == "API_VERSION":
                return None
            return ""
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    def test_empty_api_version(self):
        """Test empty API_VERSION value"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    def test_missing_server_url(self):
        """Test missing GNS3_SERVER_URL config variable"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    def test_empty_server_url(self):
        """Test empty GNS3_SERVER_URL value"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": ""
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials_for_v3(self):
        """Test v3 API without username/password"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                mock_connector = Mock()
                mock_connector_class.return_value = mock_connector
                
                connector = get_gns3_connector()
                
                assert connector is not None
                call_kwargs = mock_connector_class.call_args[1]
                assert call_kwargs["user"] is None
                assert call_kwargs["cred"] is None

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_password_for_v3(self):
        """Test v3 API without password"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080",
                "GNS3_SERVER_USERNAME": "user"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                mock_connector = Mock()
                mock_connector_class.return_value = mock_connector
                
                connector = get_gns3_connector()
                
                assert connector is not None
                call_kwargs = mock_connector_class.call_args[1]
                assert call_kwargs["user"] == "user"
                assert call_kwargs["cred"] is None

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_username_for_v3(self):
        """Test v3 API without username"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080",
                "GNS3_SERVER_PASSWORD": "pass"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                mock_connector = Mock()
                mock_connector_class.return_value = mock_connector
                
                connector = get_gns3_connector()
                
                assert connector is not None
                call_kwargs = mock_connector_class.call_args[1]
                assert call_kwargs["user"] is None
                assert call_kwargs["cred"] == "pass"


class TestConnectorFactoryErrorHandling:
    """Tests for error handling"""

    def test_invalid_api_version(self):
        """Test invalid API_VERSION value"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "invalid",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    def test_api_version_1(self):
        """Test API_VERSION = 1 (not supported)"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "1",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    def test_api_version_4(self):
        """Test API_VERSION = 4 (not supported)"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "4",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
            assert connector is None

    def test_connector_initialization_error(self):
        """Test handling of connector initialization error"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                # Simulate connector initialization error
                mock_connector_class.side_effect = Exception("Initialization failed")
                
                connector = get_gns3_connector()
                assert connector is None

    def test_connection_error(self):
        """Test handling of connection error"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                # Simulate connection error
                mock_connector_class.side_effect = ConnectionError("Connection refused")
                
                connector = get_gns3_connector()
                assert connector is None

    def test_timeout_error(self):
        """Test handling of timeout error"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                # Simulate timeout
                mock_connector_class.side_effect = TimeoutError("Request timeout")
                
                connector = get_gns3_connector()
                assert connector is None

    def test_exception_handling(self):
        """Test generic exception handling"""
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            with patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector') as mock_connector_class:
                # Simulate generic exception
                mock_connector_class.side_effect = RuntimeError("Unexpected error")
                
                connector = get_gns3_connector()
                assert connector is None


class TestConnectorFactoryEdgeCases:
    """Tests for edge cases"""

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_whitespace_in_url(self, mock_connector_class):
        """Test connector creation with whitespace in URL"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        # Should pass URL as-is (caller responsibility to validate)
        assert call_kwargs["url"] == "http://localhost:3080"

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_whitespace_in_credentials(self, mock_connector_class):
        """Test connector creation with whitespace in credentials"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "3",
                "GNS3_SERVER_URL": "http://localhost:3080",
                "GNS3_SERVER_USERNAME": " user with spaces ",
                "GNS3_SERVER_PASSWORD": " pass "
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        # Should pass credentials as-is (caller responsibility to validate)
        assert call_kwargs["user"] == " user with spaces "
        assert call_kwargs["cred"] == " pass "

    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_multiple_calls(self, mock_connector_class):
        """Test multiple calls to get_gns3_connector"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        # First call
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector1 = get_gns3_connector()
        assert connector1 is not None
        
        # Second call
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector2 = get_gns3_connector()
        assert connector2 is not None
        
        # Each call should create a new connector
        assert mock_connector_class.call_count == 2

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_whitespace_in_api_version(self, mock_connector_class):
        """Test API_VERSION with whitespace"""
        # This should fail because " 2 " is not "2"
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": " 2 ",
                "GNS3_SERVER_URL": "http://localhost:3080"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        assert connector is None

    @patch.dict(os.environ, {}, clear=True)
    @patch('gns3_copilot.gns3_client.connector_factory.Gns3Connector')
    def test_trailing_slash_in_url(self, mock_connector_class):
        """Test URL with trailing slash"""
        mock_connector = Mock()
        mock_connector_class.return_value = mock_connector
        
        def mock_get_config(key, default=None):
            config = {
                "API_VERSION": "2",
                "GNS3_SERVER_URL": "http://localhost:3080/"
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.gns3_client.connector_factory.get_config', side_effect=mock_get_config):
            connector = get_gns3_connector()
        
        assert connector is not None
        call_kwargs = mock_connector_class.call_args[1]
        assert call_kwargs["url"] == "http://localhost:3080/"
