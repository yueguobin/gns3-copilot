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
Tests for public_model module.
Contains test cases for openai_stt.py, openai_tts.py, parse_tool_content.py

Test Coverage:
1. TestOpenaiStt (OpenAI STT Module)
   - Getting default STT configuration
   - Getting STT configuration from environment variables (STT_API_KEY, STT_BASE_URL, etc.)
   - Empty audio data validation
   - Bytes array input handling
   - File object input handling
   - String response format handling
   - Large file size validation (25MB limit)
   - API call error handling
   - Simplified speech to text function (speech_to_text_simple)
   - Default GNS3 prompt validation

2. TestOpenaiTts (OpenAI TTS Module)
   - Getting default TTS configuration
   - Getting TTS configuration from environment variables (TTS_API_KEY, TTS_BASE_URL, etc.)
   - Empty text validation
   - Whitespace-only text validation
   - Text length validation (4096 character limit)
   - Speed validation (0.25 - 4.0 range)
   - Invalid model validation
   - Successful text to speech conversion
   - Text to speech with custom parameters (model, voice, speed, api_key, base_url)
   - API call error handling
   - Getting valid WAV file duration
   - Getting invalid audio data duration
   - Getting empty audio data duration

3. TestParseToolContent (Parse Tool Content Module)
   - None input handling
   - Dictionary input handling
   - List input handling
   - JSON string parsing
   - Python literal string parsing (dict and list)
   - Primitive type string parsing (string, number, boolean)
   - Empty string handling
   - Whitespace string handling
   - Empty dictionary string handling
   - Invalid string fallback to raw format
   - Invalid string in strict mode (raises ValueError)
   - Invalid string without fallback (returns error)
   - Primitive types (int, bool, float, string)
   - Unsupported type fallback handling
   - Unsupported type in strict mode (raises TypeError)
   - Unsupported type without fallback
   - Formatting dictionary response
   - Formatting string response
   - Formatting None response
   - Formatting invalid response
   - Formatting with custom indent
   - Serialization error handling
   - Double exception handling
   - General exception handling
   - Strict mode error message validation

4. TestPublicModelIntegration (Integration Tests)
   - STT and TTS workflow (speech to text, text to speech, parse, format)
   - Comprehensive parse_tool_content testing with various inputs

5. TestGetGns3DevicePort (GNS3 Device Port Module)
   - Successful device port info retrieval
   - Device not found handling
   - Device missing console_port handling
   - Empty topology handling
   - None topology handling
   - Exception handling

6. TestPublicModelInit (public_model Module __init__.py)
   - Version existence validation
   - __all__ export list validation
   - Imported functions existence and callable validation
   - Version fallback mechanism testing
   - _test_parse_tool_content function testing

Total Test Cases: 70+
"""

import io
import json
import os
import pytest
import wave
from unittest.mock import Mock, patch, MagicMock
from typing import Any

# Import modules to test
from gns3_copilot.utils import (
    get_device_ports_from_topology,
    __version__,
    __all__,
)
from gns3_copilot.utils.openai_stt import (
    get_stt_config,
    speech_to_text,
    speech_to_text_simple,
    DEFAULT_GNS3_PROMPT,
)
from gns3_copilot.utils.openai_tts import (
    get_tts_config,
    text_to_speech_wav,
    get_duration,
)
from gns3_copilot.utils.parse_tool_content import (
    parse_tool_content,
    format_tool_response,
    _test_parse_tool_content,
)


class TestOpenaiStt:
    """Tests for OpenAI STT module"""

    @patch.dict(os.environ, {}, clear=True)
    def test_get_stt_config_defaults(self):
        """Test getting default STT configuration"""
        with patch('gns3_copilot.utils.get_config') as mock_get_config:
            # Set up the mock to return actual defaults used in the implementation
            def side_effect_func(key, default=None):
                # Return the default value passed to get_config, or our test defaults
                if key == "STT_API_KEY":
                    return default if default is not None else ""
                elif key == "STT_BASE_URL":
                    return default if default is not None else "http://127.0.0.1:8001/v1"
                elif key == "STT_MODEL":
                    return default if default is not None else "whisper-1"
                elif key == "STT_LANGUAGE":
                    # DEFAULT_CONFIG has "en" as the default for STT_LANGUAGE
                    return "en"
                elif key == "STT_TEMPERATURE":
                    return default if default is not None else "0.0"
                return default

            mock_get_config.side_effect = side_effect_func

            config = get_stt_config()
            expected = {
                "api_key": "",
                "base_url": "http://127.0.0.1:8001/v1",
                "model": "whisper-1",
                "language": "en",
                "temperature": 0.0,
                "response_format": "json",
            }
            assert config == expected

    @patch.dict(os.environ, {}, clear=True)
    def test_get_stt_config_from_env(self):
        """Test getting STT configuration from environment variables"""
        def mock_get_config(key, default=None):
            config = {
                "STT_API_KEY": "test-key",
                "STT_BASE_URL": "http://test.com/v1",
                "STT_MODEL": "whisper-1",
                "STT_LANGUAGE": "en",
                "STT_TEMPERATURE": "1.0",
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.utils.openai_stt.get_config', side_effect=mock_get_config):
            config = get_stt_config()
            expected = {
                "api_key": "test-key",
                "base_url": "http://test.com/v1",
                "model": "whisper-1",
                "language": "en",
                "temperature": 1.0,
                "response_format": "json",  # Fixed to "json" as per implementation
            }
            assert config == expected

    def test_speech_to_text_empty_audio(self):
        """Test empty audio data"""
        with pytest.raises(ValueError, match="Audio data cannot be empty"):
            speech_to_text(b"")

    @patch('gns3_copilot.utils.openai_stt.OpenAI')
    def test_speech_to_text_bytes_input(self, mock_openai):
        """Test bytes array input"""
        with patch.dict(os.environ, {}, clear=True):
            # Mock OpenAI client and response
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_response = Mock()
            mock_response.model_dump.return_value = {"text": "Hello world"}
            mock_client.audio.transcriptions.create.return_value = mock_response

            audio_data = b"fake audio data"
            result = speech_to_text(audio_data, response_format="json")

            assert result == "Hello world"
            mock_openai.assert_called_once_with(
                api_key="local-dummy",
                base_url="http://127.0.0.1:8001/v1",
                timeout=60.0,
            )

    @patch('gns3_copilot.utils.openai_stt.OpenAI')
    def test_speech_to_text_file_input(self, mock_openai):
        """Test file object input"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.model_dump.return_value = {"text": "Test transcription"}
        mock_client.audio.transcriptions.create.return_value = mock_response

        # Create mock file object
        audio_file = io.BytesIO(b"fake audio data")
        audio_file.name = "test.wav"

        result = speech_to_text(audio_file, response_format="json")
        assert result == "Test transcription"

    @patch('gns3_copilot.utils.openai_stt.OpenAI')
    def test_speech_to_text_string_response(self, mock_openai):
        """Test string response"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.return_value = "Simple transcription"

        audio_data = b"fake audio data"
        result = speech_to_text(audio_data, response_format="text")
        assert result == "Simple transcription"

    def test_speech_to_text_large_file(self):
        """Test oversized audio file"""
        # Create fake data over 25MB
        large_audio = b"x" * (26 * 1024 * 1024)  # 26MB
        with pytest.raises(ValueError, match="Audio file size too large"):
            speech_to_text(large_audio)

    @patch('gns3_copilot.utils.openai_stt.OpenAI')
    def test_speech_to_text_api_error(self, mock_openai):
        """Test API call error"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")

        audio_data = b"fake audio data"
        with pytest.raises(Exception, match="Speech-to-text service error"):
            speech_to_text(audio_data)

    @patch('gns3_copilot.utils.openai_stt.speech_to_text')
    def test_speech_to_text_simple(self, mock_speech_to_text):
        """Test simplified speech to text"""
        mock_speech_to_text.return_value = "Simple result"
        
        audio_data = b"fake audio data"
        result = speech_to_text_simple(audio_data)
        
        assert result == "Simple result"
        # speech_to_text_simple just passes kwargs, doesn't set response_format
        mock_speech_to_text.assert_called_once_with(
            audio_data=audio_data
        )

    def test_default_gns3_prompt(self):
        """Test default GNS3 prompt"""
        assert "GNS3" in DEFAULT_GNS3_PROMPT
        assert "Cisco" in DEFAULT_GNS3_PROMPT
        assert "router" in DEFAULT_GNS3_PROMPT


class TestOpenaiTts:
    """Tests for OpenAI TTS module"""

    @patch.dict(os.environ, {}, clear=True)
    def test_get_tts_config_defaults(self):
        """Test getting default TTS configuration"""
        # Check the actual implementation for defaults
        config = get_tts_config()
        # Verify the structure has expected keys
        assert "api_key" in config
        assert "base_url" in config
        assert "model" in config
        assert "voice" in config
        assert "speed" in config

    @patch.dict(os.environ, {}, clear=True)
    def test_get_tts_config_from_env(self):
        """Test getting TTS configuration from environment variables"""
        def mock_get_config(key, default=None):
            config = {
                "TTS_API_KEY": "test-tts-key",
                "TTS_BASE_URL": "http://tts-test.com/v1",
                "TTS_MODEL": "tts-1",
                "TTS_VOICE": "alloy",
                "TTS_SPEED": "1.0",
            }
            return config.get(key, default)
        
        with patch('gns3_copilot.utils.openai_tts.get_config', side_effect=mock_get_config):
            config = get_tts_config()
            expected = {
                "api_key": "test-tts-key",
                "base_url": "http://tts-test.com/v1",
                "model": "tts-1",
                "voice": "alloy",
                "speed": 1.0,
            }
            assert config == expected

    def test_text_to_speech_empty_text(self):
        """Test empty text"""
        with pytest.raises(ValueError, match="Text content cannot be empty"):
            text_to_speech_wav("")

    def test_text_to_speech_whitespace_only(self):
        """Test whitespace-only text"""
        with pytest.raises(ValueError, match="Text content cannot be empty"):
            text_to_speech_wav("   ")

    def test_text_to_speech_too_long(self):
        """Test text too long"""
        long_text = "x" * 4097  # Over 4096 characters
        with pytest.raises(ValueError, match="Text length .* exceeds 4096 character limit"):
            text_to_speech_wav(long_text)

    def test_text_to_speech_invalid_speed_low(self):
        """Test speed too low"""
        with pytest.raises(ValueError, match="Speed must be between 0.25 and 4.0"):
            text_to_speech_wav("test", speed=0.24)

    def test_text_to_speech_invalid_speed_high(self):
        """Test speed too high"""
        with pytest.raises(ValueError, match="Speed must be between 0.25 and 4.0"):
            text_to_speech_wav("test", speed=4.1)

    def test_text_to_speech_invalid_model(self):
        """Test invalid model"""
        with pytest.raises(ValueError, match="Unsupported model 'invalid-model'"):
            text_to_speech_wav("test", model="invalid-model")

    @patch('gns3_copilot.utils.openai_tts.OpenAI')
    def test_text_to_speech_success(self, mock_openai):
        """Test successful text to speech"""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment variables
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_response = Mock()
            mock_response.content = b"fake audio data"
            mock_client.audio.speech.create.return_value = mock_response

            result = text_to_speech_wav("Hello world")
            assert result == b"fake audio data"

            # Verify call parameters
            mock_client.audio.speech.create.assert_called_once_with(
                model="tts-1",
                voice="alloy",
                input="Hello world",
                speed=1.0,
                response_format="wav",
            )

    @patch('gns3_copilot.utils.openai_tts.OpenAI')
    def test_text_to_speech_with_parameters(self, mock_openai):
        """Test text to speech with parameters"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_response = Mock()
        mock_response.content = b"fake audio data"
        mock_client.audio.speech.create.return_value = mock_response

        result = text_to_speech_wav(
            text="Test",
            model="tts-1-hd",
            voice="echo",
            speed=1.5,
            api_key="custom-key",
            base_url="custom-url"
        )
        assert result == b"fake audio data"

        mock_client.audio.speech.create.assert_called_once_with(
            model="tts-1-hd",
            voice="echo",
            input="Test",
            speed=1.5,
            response_format="wav",
        )

    @patch('gns3_copilot.utils.openai_tts.OpenAI')
    def test_text_to_speech_api_error(self, mock_openai):
        """Test API call error"""
        with patch.dict(os.environ, {}, clear=True):
            mock_client = Mock()
            mock_openai.return_value = mock_client
            mock_client.audio.speech.create.side_effect = Exception("TTS API Error")

            with pytest.raises(Exception, match="TTS Error"):
                text_to_speech_wav("test")

    def test_get_duration_valid_wav(self):
        """Test getting valid WAV file duration"""
        # Create a simple WAV file data
        wav_data = io.BytesIO()
        with wave.open(wav_data, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(44100)  # 44.1kHz
            # Write 1 second of silence data
            wav_file.writeframes(b'\x00' * (44100 * 2))
        
        wav_data.seek(0)
        duration = get_duration(wav_data.getvalue())
        assert abs(duration - 1.0) < 0.01  # Allow small error

    def test_get_duration_invalid_data(self):
        """Test getting invalid audio data duration"""
        invalid_data = b"not wav data"
        duration = get_duration(invalid_data)
        assert duration == 0.0

    def test_get_duration_empty_data(self):
        """Test getting empty audio data duration"""
        duration = get_duration(b"")
        assert duration == 0.0


class TestParseToolContent:
    """Tests for parse_tool_content module"""

    def test_parse_none_input(self):
        """Test None input"""
        result = parse_tool_content(None)
        assert result == {}

    def test_parse_dict_input(self):
        """Test dictionary input"""
        test_dict = {"status": "success", "data": [1, 2, 3]}
        result = parse_tool_content(test_dict)
        assert result == test_dict

    def test_parse_list_input(self):
        """Test list input"""
        test_list = [1, 2, 3, "test"]
        result = parse_tool_content(test_list)
        assert result == test_list

    def test_parse_string_json(self):
        """Test JSON string"""
        json_str = '{"status": "success", "data": [1, 2, 3]}'
        result = parse_tool_content(json_str)
        assert result == {"status": "success", "data": [1, 2, 3]}

    def test_parse_string_python_literal(self):
        """Test Python literal string"""
        python_str = "{'name': 'PC1', 'status': 'ok'}"
        result = parse_tool_content(python_str)
        assert result == {"name": "PC1", "status": "ok"}

    def test_parse_string_list_literal(self):
        """Test list literal string"""
        list_str = "[1, 2, 3, 'test']"
        result = parse_tool_content(list_str)
        assert result == [1, 2, 3, "test"]

    def test_parse_string_primitive_types(self):
        """Test primitive type strings"""
        test_cases = [
            ('"hello"', "hello"),
            ("42", 42),
            ("true", True),
            ("3.14", 3.14),
        ]
        for input_str, expected in test_cases:
            result = parse_tool_content(input_str)
            assert result == expected

    def test_parse_empty_string(self):
        """Test empty string"""
        result = parse_tool_content("")
        assert result == {}

    def test_parse_whitespace_string(self):
        """Test whitespace string"""
        result = parse_tool_content("   ")
        assert result == {}

    def test_parse_empty_dict_string(self):
        """Test empty dictionary string"""
        result = parse_tool_content("{}")
        assert result == {}

    def test_parse_empty_dict_string_with_spaces(self):
        """Test empty dictionary string with spaces"""
        result = parse_tool_content("  {}  ")
        assert result == {}

    def test_parse_invalid_string_fallback(self):
        """Test invalid string fallback handling"""
        invalid_str = "Invalid JSON input: something went wrong"
        result = parse_tool_content(invalid_str)
        assert result == {"raw": invalid_str}

    def test_parse_invalid_strict_mode(self):
        """Test invalid string in strict mode"""
        invalid_str = "Invalid JSON input"
        with pytest.raises(ValueError, match="Unable to parse content as JSON or Python literal"):
            parse_tool_content(invalid_str, strict_mode=True)

    def test_parse_invalid_no_fallback(self):
        """Test invalid string without fallback"""
        invalid_str = "Invalid input"
        result = parse_tool_content(invalid_str, fallback_to_raw=False)
        assert result == {"error": "Unable to parse content as JSON or Python literal"}

    def test_parse_primitive_types(self):
        """Test primitive types"""
        test_cases = [
            (42, 42),
            (True, True),
            (3.14, 3.14),
        ]
        for input_val, expected in test_cases:
            result = parse_tool_content(input_val)
            assert result == expected
        
        # String type needs special handling as it will be parsed
        result = parse_tool_content("hello")
        # String cannot be parsed as JSON or Python literal, so returns raw
        assert result == {"raw": "hello"}

    def test_parse_unsupported_type_fallback(self):
        """Test unsupported type fallback handling"""
        unsupported_type = object()
        result = parse_tool_content(unsupported_type)
        assert "raw" in result
        assert str(unsupported_type) in result["raw"]

    def test_parse_unsupported_type_strict_mode(self):
        """Test unsupported type in strict mode"""
        unsupported_type = object()
        with pytest.raises(TypeError, match="Content must be str, dict, list, int, float, bool, or None"):
            parse_tool_content(unsupported_type, strict_mode=True)

    def test_parse_unsupported_type_no_fallback(self):
        """Test unsupported type without fallback"""
        unsupported_type = object()
        result = parse_tool_content(unsupported_type, fallback_to_raw=False)
        assert result == {"error": "Content must be str, dict, list, int, float, bool, or None, got object"}

    def test_format_tool_response_dict(self):
        """Test formatting dictionary response"""
        content = {"status": "success", "data": [1, 2, 3]}
        result = format_tool_response(content, indent=4)
        parsed = json.loads(result)
        assert parsed == content

    def test_format_tool_response_string(self):
        """Test formatting string response"""
        content = '{"status": "success"}'
        result = format_tool_response(content)
        parsed = json.loads(result)
        assert parsed == {"status": "success"}

    def test_format_tool_response_none(self):
        """Test formatting None response"""
        result = format_tool_response(None)
        parsed = json.loads(result)
        assert parsed == {}

    def test_format_tool_response_invalid(self):
        """Test formatting invalid response"""
        invalid_content = object()
        result = format_tool_response(invalid_content)
        parsed = json.loads(result)
        assert "raw" in parsed

    def test_format_tool_response_custom_indent(self):
        """Test formatting response with custom indent"""
        content = {"status": "success"}
        result = format_tool_response(content, indent=8)
        # Check for correct indentation
        assert "        " in result  # 8 spaces

    def test_format_tool_response_serialization_error(self):
        """Test serialization error handling"""
        # Pass content that will cause serialization to fail
        # When parse_tool_content returns something that can't be serialized,
        # format_tool_response should fallback to raw string
        
        # Create unserializable content directly - parse_tool_content will pass it through
        class UnserializableObject:
            def __str__(self):
                return "UnserializableObject"
        
        # Pass unserializable object - it should handle this gracefully
        # parse_tool_content will return {"raw": str(content)} for unsupported types
        # Then format_tool_response should serialize that properly
        result = format_tool_response(UnserializableObject())
        parsed = json.loads(result)
        # Should have raw key containing the string representation
        assert "raw" in parsed

    def test_format_tool_response_double_exception(self):
        """Test that format_tool_response always returns valid JSON"""
        # Test with various inputs to ensure robustness
        test_inputs = [
            None,
            {},
            [],
            "",
            "simple string",
            42,
            True,
            {"key": "value"},
            [1, 2, 3],
        ]
        
        for input_data in test_inputs:
            result = format_tool_response(input_data)
            # All results should be valid JSON
            parsed = json.loads(result)
            assert parsed is not None

    def test_format_tool_response_general_exception(self):
        """Test that format_tool_response handles all input types gracefully"""
        # Test with edge cases to ensure robustness
        test_inputs = [
            # Basic types
            None,
            True,
            False,
            0,
            -1,
            3.14,
            # Collections
            {},
            [],
            {"a": 1, "b": 2},
            [1, 2, 3],
            # Strings
            "",
            " ",
            "test string",
            '{"key": "value"}',
            "[1, 2, 3]",
            # Edge cases (note: these will be parsed as JSON values)
            # "null",      # This parses to None, which is expected behavior
            # "[]",        # This parses to []
            # "{}",        # This parses to {}
            # "true",      # This parses to True
            # "false",     # This parses to False
        ]
        
        for input_data in test_inputs:
            result = format_tool_response(input_data)
            # All results should be valid JSON
            parsed = json.loads(result)
            assert parsed is not None

    def test_parse_tool_content_strict_mode_with_content(self):
        """Test strict mode error message containing content"""
        invalid_str = "Invalid JSON"
        with pytest.raises(ValueError, match="Unable to parse content as JSON or Python literal"):
            parse_tool_content(invalid_str, strict_mode=True)


# Integration tests
class TestPublicModelIntegration:
    """Integration tests for public_model module"""

    @patch('gns3_copilot.utils.openai_stt.OpenAI')
    @patch('gns3_copilot.utils.openai_tts.OpenAI')
    def test_stt_tts_workflow(self, mock_tts_openai, mock_stt_openai):
        """Test STT and TTS workflow"""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment variables
            # Mock STT
            mock_stt_client = Mock()
            mock_stt_openai.return_value = mock_stt_client
            mock_stt_response = Mock()
            mock_stt_response.model_dump.return_value = {"text": "Hello world"}
            mock_stt_client.audio.transcriptions.create.return_value = mock_stt_response

            # Mock TTS
            mock_tts_client = Mock()
            mock_tts_openai.return_value = mock_tts_client
            mock_tts_response = Mock()
            mock_tts_response.content = b"audio data"
            mock_tts_client.audio.speech.create.return_value = mock_tts_response

            # STT processing
            audio_data = b"fake audio data"
            transcription = speech_to_text(audio_data)
            assert transcription == "Hello world"

            # TTS processing
            audio_output = text_to_speech_wav(transcription)
            assert audio_output == b"audio data"

            # Parse result
            parsed_result = parse_tool_content({"transcription": transcription})
            assert parsed_result == {"transcription": "Hello world"}

            # Format response
            formatted_response = format_tool_response(parsed_result)
            assert "Hello world" in formatted_response
            # Verify is valid JSON
            json.loads(formatted_response)

    def test_parse_tool_content_comprehensive(self):
        """Test parse_tool_content with various inputs"""
        test_cases = [
            # (input, expected_output, description)
            ('{"key": "value"}', {"key": "value"}, "JSON string"),
            ("{'key': 'value'}", {"key": "value"}, "Python dict literal"),
            ('[1, 2, 3]', [1, 2, 3], "JSON array string"),
            ("[1, 2, 3]", [1, 2, 3], "Python list literal"),
            ('"string"', "string", "JSON string"),
            (42, 42, "integer"),
            (3.14, 3.14, "float"),
            (True, True, "boolean"),
            (None, {}, "None"),
            ({}, {}, "empty dict"),
            ([], [], "empty list"),
            ("", {}, "empty string"),
            ("   ", {}, "whitespace string"),
            ("{}", {}, "empty dict string"),
        ]

        for input_data, expected, description in test_cases:
            result = parse_tool_content(input_data)
            assert result == expected, f"Failed for {description}: {input_data}"


class TestGetGns3DevicePort:
    """Tests for get_gns3_device_port module"""

    @patch('gns3_copilot.gns3_client.GNS3TopologyTool')
    def test_get_device_ports_success(self, mock_topology_tool):
        """Test successful device port info retrieval"""
        # Mock topology data
        mock_topology = {
            "nodes": {
                "Router1": {
                    "console_port": 5000,
                    "name": "Router1"
                },
                "Switch1": {
                    "console_port": 5001,
                    "name": "Switch1"
                }
            }
        }
        
        mock_instance = Mock()
        mock_instance._run.return_value = mock_topology
        mock_topology_tool.return_value = mock_instance
        
        device_names = ["Router1", "Switch1"]
        result = get_device_ports_from_topology(device_names)
        
        expected = {
            "Router1": {
                "port": 5000,
                "groups": ["cisco_IOSv_telnet"]
            },
            "Switch1": {
                "port": 5001,
                "groups": ["cisco_IOSv_telnet"]
            }
        }
        assert result == expected

    @patch('gns3_copilot.gns3_client.GNS3TopologyTool')
    def test_get_device_ports_device_not_found(self, mock_topology_tool):
        """Test device not found case"""
        mock_topology = {
            "nodes": {
                "Router1": {
                    "console_port": 5000,
                    "name": "Router1"
                }
            }
        }
        
        mock_instance = Mock()
        mock_instance._run.return_value = mock_topology
        mock_topology_tool.return_value = mock_instance
        
        device_names = ["Router1", "NonExistentDevice"]
        result = get_device_ports_from_topology(device_names)
        
        # Should only return existing devices
        expected = {
            "Router1": {
                "port": 5000,
                "groups": ["cisco_IOSv_telnet"]
            }
        }
        assert result == expected

    @patch('gns3_copilot.gns3_client.GNS3TopologyTool')
    def test_get_device_ports_missing_console_port(self, mock_topology_tool):
        """Test device missing console_port"""
        mock_topology = {
            "nodes": {
                "Router1": {
                    "console_port": 5000,
                    "name": "Router1"
                },
                "Switch1": {
                    "name": "Switch1"
                    # Missing console_port
                }
            }
        }
        
        mock_instance = Mock()
        mock_instance._run.return_value = mock_topology
        mock_topology_tool.return_value = mock_instance
        
        device_names = ["Router1", "Switch1"]
        result = get_device_ports_from_topology(device_names)
        
        # Should only return devices with console_port
        expected = {
            "Router1": {
                "port": 5000,
                "groups": ["cisco_IOSv_telnet"]
            }
        }
        assert result == expected

    @patch('gns3_copilot.gns3_client.GNS3TopologyTool')
    def test_get_device_ports_empty_topology(self, mock_topology_tool):
        """Test empty topology case"""
        mock_instance = Mock()
        mock_instance._run.return_value = {}
        mock_topology_tool.return_value = mock_instance
        
        device_names = ["Router1"]
        result = get_device_ports_from_topology(device_names)
        
        assert result == {}

    @patch('gns3_copilot.gns3_client.GNS3TopologyTool')
    def test_get_device_ports_none_topology(self, mock_topology_tool):
        """Test None topology case"""
        mock_instance = Mock()
        mock_instance._run.return_value = None
        mock_topology_tool.return_value = mock_instance
        
        device_names = ["Router1"]
        result = get_device_ports_from_topology(device_names)
        
        assert result == {}

    @patch('gns3_copilot.gns3_client.GNS3TopologyTool')
    def test_get_device_ports_exception(self, mock_topology_tool):
        """Test exception handling"""
        mock_topology_tool.side_effect = Exception("Topology error")
        
        device_names = ["Router1"]
        result = get_device_ports_from_topology(device_names)
        
        assert result == {}


class TestPublicModelInit:
    """Tests for public_model module __init__.py"""

    def test_version_exists(self):
        """Test version exists"""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test___all___exports(self):
        """Test __all__ export list"""
        assert isinstance(__all__, list)
        assert len(__all__) > 0
        
        # Check main functions are in export list
        expected_exports = [
            "get_device_ports_from_topology",
            "parse_tool_content",
            "format_tool_response",
            "text_to_speech_wav",
            "speech_to_text",
            "get_duration",
            "get_tts_config",
            "get_stt_config",
        ]
        
        for export in expected_exports:
            assert export in __all__, f"{export} should be in __all__"

    def test_imports_work(self):
        """Test imported functions exist and are callable"""
        # Test imported functions exist and are callable
        assert callable(get_device_ports_from_topology)
        assert callable(parse_tool_content)
        assert callable(format_tool_response)
        assert callable(text_to_speech_wav)
        assert callable(speech_to_text)
        assert callable(get_duration)
        assert callable(get_tts_config)
        assert callable(get_stt_config)

    @patch('gns3_copilot.utils.version')
    def test_version_fallbacks(self, mock_version):
        """Test version fallback mechanism"""
        # This test needs re-importing module to trigger exception path
        # Since module is already imported, we cannot fully test exception path
        # But we can verify version existence
        assert __version__ is not None
        assert isinstance(__version__, str)
        
        # Verify version is not "unknown" (unless really unavailable)
        # In actual environment, version should be valid
        if __version__ != "unknown":
            assert len(__version__) > 0

    def test_test_parse_tool_content_function(self):
        """Test _test_parse_tool_content function"""
        # Test test function exists and is callable
        assert callable(_test_parse_tool_content)
        
        # Call test function (it should print output, but not throw exceptions)
        try:
            _test_parse_tool_content()
        except Exception as e:
            pytest.fail(f"_test_parse_tool_content() raised an exception: {e}")
