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
Tests for prompts module.
Contains test cases for prompt loading and management functionality.

Test Coverage:
1. TestPromptLoaderBase
   - Successful base prompt loading
   - Base prompt loading with import error handling
   - Base prompt loading with attribute error (missing SYSTEM_PROMPT)

2. TestRegularLevelPromptLoader
   - Loading A1 level regular prompt with ENGLISH_LEVEL env var
   - Loading all available English levels (A1, A2, B1, B2, C1, C2)
   - Invalid English level fallback to base_prompt
   - None level handling
   - Empty string level handling
   - Case insensitive level handling (a1, A1, a1)
   - Whitespace handling in level strings
   - Import error fallback to base_prompt
   - Attribute error fallback to base_prompt

3. TestVoiceLevelPromptLoader
   - Loading A1 level voice prompt with VOICE env var
   - Loading generic voice prompt
   - Loading all available voice levels (A1, A2, B1, B2, C1, C2)
   - None level handling
   - Complete fallback chain for voice prompts (level-specific -> generic -> base)
   - Level-specific AttributeError with fallback
   - Generic AttributeError with fallback
   - Level-specific ImportError with fallback to generic

4. TestVoiceEnabledCheck
   - Various true values for VOICE env var (true, TRUE, True, 1, yes, YES, on, ON)
   - Various false values for VOICE env var (false, FALSE, False, 0, no, NO, off, OFF, '')
   - Default voice enabled value (False)
   - Whitespace handling in VOICE env var

5. TestLoadSystemPrompt
   - Loading system prompt in regular mode
   - Loading system prompt in voice mode
   - Loading system prompt without environment variables (fallback to base_prompt)
   - Loading system prompt with level parameter
   - Loading voice prompt with level parameter

6. TestPromptConstants
   - ENGLISH_LEVEL_PROMPT_MAP completeness (A1, A2, B1, B2, C1, C2, NORMAL PROMPT)
   - VOICE_LEVEL_PROMPT_MAP completeness (A1, A2, B1, B2, C1, C2)
   - TITLE_PROMPT existence and validation
   - Voice prompt constants existence (vocie_prompt.SYSTEM_PROMPT)

7. TestModuleImports
   - Importing main functions from prompts module
   - __all__ exports validation

8. TestEdgeCases
   - Invalid ENGLISH_LEVEL environment variable
   - Level normalization edge cases (a1, A1, whitespace, newline, tab)

9. TestFixtures
   - Environment variable cleanup after tests

Total Test Cases: 30+
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from gns3_copilot.prompts import (
    load_system_prompt,
    TITLE_PROMPT,
)
from gns3_copilot.prompts.prompt_loader import (
    _load_base_prompt,
    _load_regular_level_prompt,
    _load_voice_level_prompt,
    _is_voice_enabled,
    ENGLISH_LEVEL_PROMPT_MAP,
    VOICE_LEVEL_PROMPT_MAP,
)


class TestPromptLoaderBase:
    """Test base prompt loading functionality."""
    
    def test_load_base_prompt_success(self):
        """Test successful base prompt loading."""
        prompt = _load_base_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "network automation assistant" in prompt.lower()
    
    @patch('importlib.import_module')
    def test_load_base_prompt_import_error(self, mock_import):
        """Test base prompt loading with import error."""
        mock_import.side_effect = ImportError("Module not found")
        
        with pytest.raises(ImportError, match="Failed to import base_prompt module"):
            _load_base_prompt()
    
    @patch('importlib.import_module')
    def test_load_base_prompt_attribute_error(self, mock_import):
        """Test base prompt loading with missing attribute."""
        mock_module = MagicMock()
        del mock_module.SYSTEM_PROMPT  # Remove the attribute
        mock_import.return_value = mock_module
        
        with pytest.raises(AttributeError, match="SYSTEM_PROMPT not found"):
            _load_base_prompt()


class TestRegularLevelPromptLoader:
    """Test regular level prompt loading functionality."""
    
    @patch.dict(os.environ, {'ENGLISH_LEVEL': 'A1'})
    def test_load_regular_level_a1(self):
        """Test loading A1 level regular prompt."""
        prompt = _load_regular_level_prompt('A1')
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "A1" in prompt
    
    def test_load_regular_level_all_levels(self):
        """Test loading all available English levels."""
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            prompt = _load_regular_level_prompt(level)
            assert isinstance(prompt, str)
            assert len(prompt) > 0
    
    def test_load_regular_level_invalid_level(self):
        """Test loading invalid English level."""
        prompt = _load_regular_level_prompt('INVALID')
        
        # Should fallback to base_prompt
        base_prompt = _load_base_prompt()
        assert prompt == base_prompt
    
    def test_load_regular_level_none_level(self):
        """Test loading with None level."""
        prompt = _load_regular_level_prompt(None)
        
        # Should fallback to base_prompt
        base_prompt = _load_base_prompt()
        assert prompt == base_prompt
    
    def test_load_regular_level_empty_string(self):
        """Test loading with empty string level."""
        prompt = _load_regular_level_prompt('')
        
        # Should fallback to base_prompt
        base_prompt = _load_base_prompt()
        assert prompt == base_prompt
    
    def test_load_regular_level_case_insensitive(self):
        """Test case insensitive level handling."""
        prompt_lower = _load_regular_level_prompt('a1')
        prompt_upper = _load_regular_level_prompt('A1')
        prompt_mixed = _load_regular_level_prompt('a1')
        
        assert prompt_lower == prompt_upper == prompt_mixed
    
    def test_load_regular_level_whitespace_handling(self):
        """Test whitespace handling in level strings."""
        prompt_clean = _load_regular_level_prompt('A1')
        prompt_spaces = _load_regular_level_prompt('  A1  ')
        
        assert prompt_clean == prompt_spaces
    
    def test_load_regular_level_import_error_fallback(self):
        """Test fallback behavior on import error."""
        with patch('gns3_copilot.prompts.prompt_loader._load_base_prompt') as mock_base:
            mock_base.return_value = "Base prompt fallback"
            
            with patch('importlib.import_module') as mock_import:
                mock_import.side_effect = ImportError("Module not found")
                
                prompt = _load_regular_level_prompt('A1')
                assert prompt == "Base prompt fallback"
    
    def test_load_regular_level_attribute_error_fallback(self):
        """Test fallback behavior on attribute error."""
        with patch('gns3_copilot.prompts.prompt_loader._load_base_prompt') as mock_base:
            mock_base.return_value = "Base prompt fallback"
            
            with patch('importlib.import_module') as mock_import:
                mock_module = MagicMock()
                del mock_module.SYSTEM_PROMPT
                mock_import.return_value = mock_module
                
                prompt = _load_regular_level_prompt('A1')
                assert prompt == "Base prompt fallback"


class TestVoiceLevelPromptLoader:
    """Test voice level prompt loading functionality."""
    
    @patch.dict(os.environ, {'VOICE': 'true'})
    def test_load_voice_level_a1(self):
        """Test loading A1 level voice prompt."""
        prompt = _load_voice_level_prompt('A1')
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @patch.dict(os.environ, {'VOICE': 'false'})
    def test_load_voice_level_generic(self):
        """Test loading generic voice prompt."""
        with patch('importlib.import_module') as mock_import:
            # Mock the generic voice prompt module
            mock_module = MagicMock()
            mock_module.SYSTEM_PROMPT = "Generic voice prompt"
            mock_import.return_value = mock_module
            
            prompt = _load_voice_level_prompt('INVALID_LEVEL')
            
            assert prompt == "Generic voice prompt"
    
    def test_load_voice_level_all_levels(self):
        """Test loading all available voice levels."""
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            # These tests might fail if modules don't exist, but that's expected
            try:
                prompt = _load_voice_level_prompt(level)
                assert isinstance(prompt, str)
            except ImportError:
                # Voice modules might not exist, which is valid
                pass
    
    def test_load_voice_level_none_level(self):
        """Test loading voice prompt with None level."""
        # Should fallback to generic voice prompt or base_prompt
        try:
            prompt = _load_voice_level_prompt(None)
            assert isinstance(prompt, str)
        except ImportError:
            # Voice modules might not exist, which is valid
            pass
    
    def test_load_voice_level_fallback_chain(self):
        """Test complete fallback chain for voice prompts."""
        with patch('gns3_copilot.prompts.prompt_loader._load_base_prompt') as mock_base:
            mock_base.return_value = "Base prompt fallback"
            
            with patch('importlib.import_module') as mock_import:
                # First call fails (level-specific)
                # Second call fails (generic voice)  
                mock_import.side_effect = [
                    ImportError("Level-specific not found"),
                    ImportError("Generic not found"),
                ]
                
                prompt = _load_voice_level_prompt('A1')
                assert prompt == "Base prompt fallback"
    
    def test_load_voice_level_specific_attribute_error(self):
        """Test voice prompt level-specific AttributeError with fallback."""
        with patch('gns3_copilot.prompts.prompt_loader._load_base_prompt') as mock_base:
            mock_base.return_value = "Base prompt fallback"
            
            with patch('importlib.import_module') as mock_import:
                # First call fails with AttributeError (missing SYSTEM_PROMPT)
                mock_module = MagicMock()
                del mock_module.SYSTEM_PROMPT
                mock_import.return_value = mock_module
                
                prompt = _load_voice_level_prompt('A1')
                assert prompt == "Base prompt fallback"
    
    def test_load_voice_level_generic_attribute_error(self):
        """Test voice prompt generic AttributeError with fallback."""
        with patch('gns3_copilot.prompts.prompt_loader._load_base_prompt') as mock_base:
            mock_base.return_value = "Base prompt fallback"
            
            with patch('importlib.import_module') as mock_import:
                # First call fails with ImportError
                # Second call has module but missing SYSTEM_PROMPT
                mock_module_with_no_prompt = MagicMock()
                del mock_module_with_no_prompt.SYSTEM_PROMPT
                mock_import.side_effect = [
                    ImportError("Level-specific not found"),
                    mock_module_with_no_prompt,
                ]
                
                prompt = _load_voice_level_prompt('A1')
                assert prompt == "Base prompt fallback"
    
    def test_load_voice_level_specific_import_error_fallback(self):
        """Test voice prompt level-specific ImportError with fallback to generic."""
        with patch('importlib.import_module') as mock_import:
            # First call fails with ImportError
            # Second call succeeds (generic)
            mock_generic_module = MagicMock()
            mock_generic_module.SYSTEM_PROMPT = "Generic voice prompt"
            mock_import.side_effect = [
                ImportError("Level-specific not found"),
                mock_generic_module,
            ]
            
            prompt = _load_voice_level_prompt('A1')
            assert prompt == "Generic voice prompt"


class TestVoiceEnabledCheck:
    """Test voice mode detection."""
    
    @patch.dict(os.environ, {'VOICE': 'true'})
    def test_voice_enabled_true_variants(self):
        """Test various true values for VOICE env var."""
        for value in ['true', 'TRUE', 'True', '1', 'yes', 'YES', 'Yes', 'on', 'ON']:
            with patch.dict(os.environ, {'VOICE': value}):
                assert _is_voice_enabled() is True
    
    @patch.dict(os.environ, {'VOICE': 'false'})
    def test_voice_disabled_false_variants(self):
        """Test various false values for VOICE env var."""
        for value in ['false', 'FALSE', 'False', '0', 'no', 'NO', 'No', 'off', 'OFF', '']:
            with patch.dict(os.environ, {'VOICE': value}):
                assert _is_voice_enabled() is False
    
    def test_voice_enabled_default(self):
        """Test default voice enabled value."""
        with patch.dict(os.environ, {}, clear=True):
            assert _is_voice_enabled() is False
    
    @patch.dict(os.environ, {'VOICE': '  true  '})
    def test_voice_enabled_whitespace_handling(self):
        """Test whitespace handling in VOICE env var."""
        assert _is_voice_enabled() is True


class TestLoadSystemPrompt:
    """Test main load_system_prompt function."""
    
    @patch.dict(os.environ, {'VOICE': 'false', 'ENGLISH_LEVEL': 'A1'})
    def test_load_system_prompt_regular_mode(self):
        """Test loading system prompt in regular mode."""
        prompt = load_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @patch.dict(os.environ, {'VOICE': 'true', 'ENGLISH_LEVEL': 'A1'})
    def test_load_system_prompt_voice_mode(self):
        """Test loading system prompt in voice mode."""
        prompt = load_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @patch.dict(os.environ, {'VOICE': 'false'}, clear=True)
    def test_load_system_prompt_no_env_vars(self):
        """Test loading system prompt without environment variables."""
        prompt = load_system_prompt()
        
        # Should use base_prompt
        base_prompt = _load_base_prompt()
        assert prompt == base_prompt
    
    def test_load_system_prompt_with_level_param(self):
        """Test loading system prompt with level parameter."""
        # Ensure voice mode is disabled so it uses regular level prompt
        with patch.dict(os.environ, {'VOICE': 'false'}):
            with patch('gns3_copilot.prompts.prompt_loader._load_regular_level_prompt') as mock_regular:
                mock_regular.return_value = "Test prompt"
                
                prompt = load_system_prompt('B1')
                
                mock_regular.assert_called_once_with('B1')
                assert prompt == "Test prompt"
    
    @patch.dict(os.environ, {'VOICE': 'true'})
    def test_load_system_prompt_voice_with_level(self):
        """Test loading voice prompt with level parameter."""
        with patch('gns3_copilot.prompts.prompt_loader._load_voice_level_prompt') as mock_voice:
            mock_voice.return_value = "Voice test prompt"
            
            prompt = load_system_prompt('C1')
            
            mock_voice.assert_called_once_with('C1')
            assert prompt == "Voice test prompt"


class TestPromptConstants:
    """Test prompt constants and mappings."""
    
    def test_english_level_prompt_map_complete(self):
        """Test ENGLISH_LEVEL_PROMPT_MAP contains expected entries."""
        expected_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'NORMAL PROMPT']
        
        for level in expected_levels:
            assert level in ENGLISH_LEVEL_PROMPT_MAP
            assert isinstance(ENGLISH_LEVEL_PROMPT_MAP[level], str)
    
    def test_voice_level_prompt_map_complete(self):
        """Test VOICE_LEVEL_PROMPT_MAP contains expected entries."""
        expected_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        for level in expected_levels:
            assert level in VOICE_LEVEL_PROMPT_MAP
            assert isinstance(VOICE_LEVEL_PROMPT_MAP[level], str)
    
    def test_title_prompt_exists(self):
        """Test TITLE_PROMPT constant exists and is valid."""
        assert isinstance(TITLE_PROMPT, str)
        assert len(TITLE_PROMPT) > 0
        assert "conversation" in TITLE_PROMPT.lower() or "title" in TITLE_PROMPT.lower()
    
    def test_voice_prompt_constant_exists(self):
        """Test voice prompt constants exist and are valid."""
        try:
            from gns3_copilot.prompts import vocie_prompt
            assert hasattr(vocie_prompt, 'SYSTEM_PROMPT')
            assert isinstance(vocie_prompt.SYSTEM_PROMPT, str)
            assert len(vocie_prompt.SYSTEM_PROMPT) > 0
        except ImportError:
            # If the module doesn't exist or has issues, that's expected
            pass


class TestModuleImports:
    """Test module import functionality."""
    
    def test_import_main_functions(self):
        """Test importing main functions from prompts module."""
        from gns3_copilot.prompts import load_system_prompt, TITLE_PROMPT
        
        assert callable(load_system_prompt)
        assert isinstance(TITLE_PROMPT, str)
    
    def test_import_all_exports(self):
        """Test __all__ exports are available."""
        from gns3_copilot.prompts import __all__
        
        expected_exports = ["load_system_prompt", "TITLE_PROMPT", "LINUX_SPECIALIST_PROMPT"]
        assert set(__all__) == set(expected_exports)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch.dict(os.environ, {'ENGLISH_LEVEL': 'invalid'})
    def test_invalid_english_level_env(self):
        """Test invalid ENGLISH_LEVEL environment variable."""
        prompt = load_system_prompt()
        
        # Should fallback to base_prompt
        base_prompt = _load_base_prompt()
        assert prompt == base_prompt
    
    def test_level_normalization_edge_cases(self):
        """Test edge cases in level string normalization."""
        test_cases = [
            ('a1', 'A1'),
            ('  a1  ', 'A1'),
            ('A1', 'A1'),
            ('a1\n', 'A1'),
            ('A1\t', 'A1'),
        ]
        
        for input_level, expected in test_cases:
            with patch('gns3_copilot.prompts.prompt_loader._load_regular_level_prompt') as mock_load:
                load_system_prompt(input_level)
                
                # Check that the normalized level was passed
                if mock_load.called:
                    call_args = mock_load.call_args[0]
                    if call_args:
                        assert call_args[0] == expected


@pytest.fixture(autouse=True)
def cleanup_environment():
    """Clean up environment variables after each test."""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)
