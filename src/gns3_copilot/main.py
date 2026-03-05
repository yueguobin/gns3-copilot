#!/usr/bin/env python3
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
GNS3 Copilot main entry point.

This module provides a command-line interface for launching the GNS3 Copilot
Streamlit application with support for Streamlit parameter passthrough.
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import types

# Conditional imports at top level
# Check if streamlit exists without actually importing it
STREAMLIT_AVAILABLE = importlib.util.find_spec("streamlit") is not None

if STREAMLIT_AVAILABLE:
    # If streamlit is needed later, it can be imported inside functions or keep current logic
    pass

# Global variables with proper typing
gns3_copilot: Optional["types.ModuleType"] = None
__version__: str = "unknown"
GNS3_COPILOT_AVAILABLE: bool = False

try:
    import gns3_copilot as gns3_copilot_import
    from gns3_copilot import __version__ as version_import

    gns3_copilot = gns3_copilot_import
    __version__ = version_import
    GNS3_COPILOT_AVAILABLE = True
except ImportError:
    pass


def get_app_path() -> str | None:
    """Get the path to the app.py file."""
    # Try to find app.py in the current directory first
    current_dir = Path.cwd()
    app_path = current_dir / "app.py"

    if app_path.exists():
        return str(app_path)

    # If not found, try to find it relative to this script
    script_dir = Path(__file__).parent.parent
    app_path = script_dir / "app.py"

    if app_path.exists():
        return str(app_path)

    # As a last resort, try to find it in the package installation
    if gns3_copilot is not None:
        try:
            module_file = gns3_copilot.__file__
            if module_file is not None:
                package_dir = Path(module_file).parent
                app_path = package_dir / "app.py"
                if app_path.exists():
                    return str(app_path)
        except (AttributeError, ImportError):
            pass

    return None


def check_streamlit() -> bool:
    """Check if streamlit is available."""
    return STREAMLIT_AVAILABLE


def print_help() -> None:
    """Print help information."""
    help_text = """
GNS3 Copilot - AI-powered network automation assistant for GNS3

USAGE:
    gns3-copilot [STREAMLIT_OPTIONS]

EXAMPLES:
    # Basic startup
    gns3-copilot

    # Specify custom port
    gns3-copilot --server.port 8080

    # Specify address and port
    gns3-copilot --server.address 0.0.0.0 --server.port 8080

    # Run in headless mode
    gns3-copilot --server.headless true

    # Set log level
    gns3-copilot --logger.level debug

    # Disable usage statistics
    gns3-copilot --browser.gatherUsageStats false

COMMON STREAMLIT OPTIONS:
    --server.port PORT           Port to run on (default: 8501)
    --server.address ADDRESS     Address to bind to (default: localhost)
    --server.headless true/false Run in headless mode
    --logger.level LEVEL         Log level (error, warning, info, debug)
    --browser.gatherUsageStats true/false
                                Gather usage statistics
    --theme.base light/dark      Set base theme

For a complete list of Streamlit options, run:
    streamlit run --help

ALTERNATIVE USAGE:
    You can also run the app directly with streamlit:
    streamlit run app.py [STREAMLIT_OPTIONS]
"""
    print(help_text)


def print_version() -> None:
    """Print version information."""
    if GNS3_COPILOT_AVAILABLE:
        print(f"GNS3 Copilot version {__version__}")
    else:
        print("GNS3 Copilot version unknown")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="gns3-copilot",
        description="GNS3 Copilot - AI-powered network automation assistant for GNS3",
        add_help=False,  # We'll handle help ourselves to allow unknown args
    )

    # Add our custom arguments
    parser.add_argument(
        "--help", "-h", action="store_true", help="Show this help message and exit"
    )
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show version information and exit"
    )

    # Parse known args, leaving unknown args for streamlit
    args, unknown_args = parser.parse_known_args()

    # Handle our custom arguments
    if args.help:
        print_help()
        return 0

    if args.version:
        print_version()
        return 0

    # Check if streamlit is available
    if not check_streamlit():
        print("Error: Streamlit is not installed. Please install it with:")
        print("  pip install streamlit")
        return 1

    # Find the app.py file
    app_path = get_app_path()
    if not app_path:
        print("Error: Could not find app.py file.")
        print(
            "Please ensure you're running this from the project directory "
            "or that the package is properly installed."
        )
        return 1

    # Build the streamlit command
    cmd = ["streamlit", "run", app_path] + unknown_args

    # Print startup information
    print("Starting GNS3 Copilot...")
    print(f"App file: {app_path}")
    if unknown_args:
        print(f"Additional arguments: {' '.join(unknown_args)}")
    print()

    exit_code = 0
    try:
        # Run streamlit
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        exit_code = 1
    except KeyboardInterrupt:
        print("\nGNS3 Copilot stopped by user.")
        exit_code = 0
    except FileNotFoundError:
        print(
            "Error: 'streamlit' command not found. "
            "Please ensure Streamlit is installed and in your PATH."
        )
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
