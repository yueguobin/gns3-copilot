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
OpenAI TTS Interface Module
---------------------------
This module provides a robust interface for converting text to speech using
OpenAI-compatible APIs, specifically optimized for WAV output and automated
duration calculation.
"""

import io
from typing import Any

import soundfile as sf
from openai import (
    OpenAI,
)

from gns3_copilot.log_config import setup_logger
from gns3_copilot.utils import get_config

# Setup logger
logger = setup_logger("openai_tts")


def get_tts_config() -> dict[str, Any]:
    """
    Get TTS configuration from SQLite database with sensible defaults.
    """
    return {
        "api_key": get_config("TTS_API_KEY", "dummy-key"),
        "base_url": get_config("TTS_BASE_URL", "http://localhost:4123/v1"),
        "model": get_config("TTS_MODEL", "tts-1"),
        "voice": get_config("TTS_VOICE", "alloy"),
        "speed": float(get_config("TTS_SPEED", "1.0")),
    }


def text_to_speech_wav(
    text: str,
    model: str | None = None,
    voice: str | None = None,
    speed: float | None = None,
    instructions: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> bytes:
    """
    Convert text to speech audio in WAV format using OpenAI TTS API.
    """
    # Log received input parameters (excluding sensitive data)
    logger.info(
        "Received parameters: model=%s, voice=%s, speed=%s, base_url=%s, text_length=%d",
        model or "default",
        voice or "default",
        speed,
        base_url or "default",
        len(text),
    )
    config = get_tts_config()

    # Ensure variable types are determined to avoid issues with Optional
    final_model: str = model if model is not None else str(config["model"])
    final_voice: Any = (
        voice if voice is not None else config["voice"]
    )  # voice SDK type is complex, temporarily using Any or str
    final_speed: float = speed if speed is not None else float(config["speed"])
    final_api_key: str = api_key if api_key is not None else str(config["api_key"])
    final_base_url: str = base_url if base_url is not None else str(config["base_url"])

    if not text or not text.strip():
        raise ValueError("Error: Text content cannot be empty.")

    if len(text) > 4096:
        raise ValueError(
            f"Error: Text length ({len(text)}) exceeds 4096 character limit."
        )

    if not (0.25 <= final_speed <= 4.0):
        raise ValueError("Error: Speed must be between 0.25 and 4.0.")

    # Validate model
    valid_models = ["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
    if final_model not in valid_models:
        raise ValueError(f"Error: Unsupported model '{final_model}'.")

    try:
        client = OpenAI(api_key=final_api_key, base_url=final_base_url)
        logger.info(f"Generating TTS: model={final_model}, voice={final_voice}")

        # Explicit parameter passing, not using dictionary unpacking (**api_params)
        # This allows Mypy to directly check types, resolving many [arg-type] errors

        # Note: response_format must be a literal supported by the SDK
        response = client.audio.speech.create(
            model=final_model,
            voice=final_voice,
            input=text,
            speed=final_speed,
            response_format="wav",  # Explicit string
        )

        audio_bytes = response.content

        # Log result
        logger.info(
            "TTS result generated successfully, audio_size=%d bytes (%.2f MB)",
            len(audio_bytes),
            len(audio_bytes) / (1024 * 1024),
        )

        return audio_bytes

    except Exception as e:
        logger.error(f"TTS processing failed: {e}")
        raise Exception(f"TTS Error: {str(e)}") from e


def get_duration(audio_bytes: bytes) -> float:
    """
    Calculate the duration of WAV audio data in seconds using soundfile library.

    This function supports multiple WAV formats including PCM and IEEE Float
    (format code 3), which is not supported by Python's standard wave module.

    Args:
        audio_bytes: Raw WAV audio data as bytes

    Returns:
        Duration in seconds as float, returns 0.0 if calculation fails
    """
    # Validation 1: Check if audio_bytes is valid
    if not audio_bytes:
        logger.error("Audio bytes is empty or None")
        return 0.0

    # Validation 2: Check minimum audio data size
    if len(audio_bytes) < 100:
        logger.error(
            f"Audio data too small to be valid: {len(audio_bytes)} bytes "
            f"(minimum 100 bytes required)"
        )
        return 0.0

    try:
        # Log audio data size for debugging
        logger.info(
            f"Parsing audio, size: {len(audio_bytes)} bytes ({len(audio_bytes) / 1024:.2f} KB)"
        )

        # Wrap the byte stream in a BytesIO object
        with io.BytesIO(audio_bytes) as bio:
            # Reset buffer position to the beginning before reading
            bio.seek(0)

            # Use soundfile to read audio info
            # soundfile supports multiple formats including IEEE Float (format code 3)
            info = sf.info(bio)

            # Log audio parameters for debugging
            logger.debug(
                f"Audio parameters - duration: {info.duration:.2f}s, "
                f"samplerate: {info.samplerate}, channels: {info.channels}, "
                f"format: {info.format}, subtype: {info.subtype}"
            )

            # Validate samplerate
            if info.samplerate <= 0:
                logger.error(f"Invalid samplerate: {info.samplerate}")
                return 0.0

            # Validate duration
            if info.duration <= 0:
                logger.error(f"Invalid duration: {info.duration}")
                return 0.0

            # Log successful calculation
            logger.info(
                f"Successfully calculated audio duration: {info.duration:.2f} seconds"
            )

            return float(info.duration)

    except sf.LibsndfileError as e:
        logger.error(f"Soundfile parsing error: {e}")
        return 0.0
    except Exception as e:
        logger.error(f"Unexpected error calculating duration: {e}", exc_info=True)
        return 0.0


# --- Usage Example ---
if __name__ == "__main__":
    test_topology = (
        "Network Setup: Router 1 connects to Router 2 via Gigabit interface. "
        "The topology is now ready for OSPF configuration."
    )

    try:
        logger.info("Starting TTS test with default configuration")
        print("Generating audio...")
        print("Using environment variables for TTS configuration...")

        # Display current configuration
        config = get_tts_config()
        logger.info(
            f"TTS Configuration - Model: {config['model']}, Voice: {config['voice']}, Speed: {config['speed']}"
        )
        print(f"TTS Model: {config['model']}")
        print(f"TTS Voice: {config['voice']}")
        print(f"TTS Speed: {config['speed']}")
        print(f"TTS Base URL: {config['base_url']}")
        print(
            f"TTS API Key: {'***' if config['api_key'] != 'dummy-key' else 'dummy-key'}"
        )

        # Generate audio using environment variables (no explicit parameters needed)
        audio_data = text_to_speech_wav(
            text=test_topology
            # All other parameters will be loaded from SQLite config
        )

        duration = get_duration(audio_data)
        logger.info(
            f"TTS audio generated successfully, duration: {duration:.2f} seconds"
        )
        print(f"Success! Audio Duration: {duration:.2f} seconds")

        with open("network_info.wav", "wb") as f:
            f.write(audio_data)
        logger.info("Audio file saved as network_info.wav")
        print("File saved as network_info.wav")

        # Example with explicit parameter override
        print("\n--- Example with parameter override ---")
        logger.info("Testing TTS with parameter override")
        audio_data_override = text_to_speech_wav(
            text=test_topology,
            voice="onyx",  # Override voice from environment
            api_key="your-api-key",  # Override API key
            base_url="http://localhost:4123/v1",  # Override base URL
        )
        logger.info("Parameter override test completed successfully")
        print("Override example completed successfully!")

    except Exception as err:
        logger.error(f"TTS test process failed: {err}")
        print(f"Process failed: {err}")
