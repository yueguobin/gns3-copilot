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
import io
import os
from typing import IO, Any, BinaryIO, Literal, cast

from openai import OpenAI
from openai._types import NOT_GIVEN

from gns3_copilot.log_config import setup_logger
from gns3_copilot.utils import get_config

logger = setup_logger("openai_stt")

DEFAULT_GNS3_PROMPT = (
    "GNS3, Cisco, router, switch, OSPF, BGP, EIGRP, ISIS, VLAN, STP, "
    "interface, FastEthernet, GigabitEthernet, loopback, config terminal, "
    "no shutdown, show running-config, Wireshark, encapsulation."
)


def get_stt_config() -> dict[str, Any]:
    """
    Get STT configuration from SQLite database with sensible defaults.
    """
    return {
        "api_key": get_config("STT_API_KEY", ""),
        "base_url": get_config("STT_BASE_URL", "http://127.0.0.1:8001/v1"),
        "model": get_config("STT_MODEL", "whisper-1"),
        "language": get_config("STT_LANGUAGE", None),
        "temperature": float(get_config("STT_TEMPERATURE", "0.0")),
        "response_format": "json",  # Fixed to json format
    }


def speech_to_text(
    audio_data: bytes | BinaryIO,
    model: str | None = None,
    language: str | None = None,
    prompt: str | None = DEFAULT_GNS3_PROMPT,
    response_format: str | None = None,
    temperature: float | None = None,
    timestamp_granularities: list[Literal["word", "segment"]] | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    """
    Transcribe audio to text using OpenAI Whisper API.

    Returns:
        str: The transcribed text (always in JSON format)
    """
    # Log received input parameters (excluding sensitive data)
    logger.info(
        "Received parameters: model=%s, language=%s, response_format=%s, temperature=%s, base_url=%s",
        model or "default",
        language,
        response_format,
        temperature,
        base_url or "default",
    )
    config = get_stt_config()

    # Determine specific type to avoid Optional
    f_model: str = model if model is not None else str(config["model"])
    # Always use json format for response
    f_response_format: str = "json"
    f_temperature: float = (
        temperature if temperature is not None else float(config["temperature"])
    )
    f_api_key: str = api_key if api_key is not None else str(config["api_key"])
    f_base_url: str = base_url if base_url is not None else str(config["base_url"])
    f_language: str | None = (
        language if language is not None else config.get("language")
    )

    if not audio_data:
        raise ValueError("Audio data cannot be empty")

    # Use IO[bytes] to unify type declarations for BytesIO and BinaryIO
    audio_file: IO[bytes]
    file_name: str = "audio.wav"

    if isinstance(audio_data, bytes):
        size_mb = len(audio_data) / (1024 * 1024)
        audio_file = io.BytesIO(audio_data)

    else:
        audio_file = audio_data
        file_name = getattr(audio_file, "name", "audio.wav")

        audio_file.seek(0, os.SEEK_END)
        size_mb = audio_file.tell() / (1024 * 1024)
        audio_file.seek(0)

    if size_mb > 25:
        raise ValueError(f"Audio file size too large ({size_mb:.2f}MB).")

    try:
        client = OpenAI(
            api_key=f_api_key if f_api_key else "local-dummy",
            base_url=f_base_url,
            timeout=60.0,
        )

        response = client.audio.transcriptions.create(
            file=cast(tuple[str, IO[bytes]], (file_name, audio_file)),
            model=f_model,
            language=cast(Any, f_language or NOT_GIVEN),
            prompt=cast(Any, prompt or NOT_GIVEN),
            response_format=cast(Literal["json"], f_response_format),
            temperature=f_temperature,
            timestamp_granularities=cast(Any, timestamp_granularities or NOT_GIVEN),
        )

        # Always return text string from JSON response
        # With response_format="json", response is always a Transcription object
        if hasattr(response, "model_dump"):
            data = response.model_dump()
            result: str = str(data.get("text", ""))
        else:
            result = str(response)

        # Log result
        logger.info("STT result: %s", result[:500])

        return result

    except Exception as e:
        logger.error(f"STT API call failed: {type(e).__name__} - {str(e)}")
        raise Exception(f"Speech-to-text service error: {str(e)}") from e


def speech_to_text_simple(audio_data: bytes | BinaryIO, **kwargs: Any) -> str:
    """
    Simplified version that always returns a plain transcription string.
    """
    result = speech_to_text(audio_data=audio_data, **kwargs)
    return str(result)


# Module Test
if __name__ == "__main__":
    print("Whisper STT module initialized...")

    # Display current configuration
    print("\n=== Current STT Configuration ===")
    config = get_stt_config()
    for key, value in config.items():
        if "key" in key.lower() and value:
            print(f"{key}: ***")
        else:
            print(f"{key}: {value}")

    # Example usage
    print("\n=== Example Usage ===")
    print("Using SQLite configuration:")
    print("result = speech_to_text(audio_data)")
    print()
    print("Overriding specific parameters:")
    print(
        "result = speech_to_text(audio_data, model='gpt-4o-transcribe', language='en')"
    )
