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
# type: ignore
"""
Notes management component for creating and managing markdown notes.

This module provides a comprehensive notes management system with:
- Note editor with auto-save functionality
- Notes list with selection
- Download and delete operations
- Create new notes
- AI-powered note organization
- Notes stored as Markdown files
"""

import os
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

from gns3_copilot.agent.model_factory import create_note_organizer_model
from gns3_copilot.log_config import setup_logger
from gns3_copilot.prompts.notes_prompt import SYSTEM_PROMPT

logger = setup_logger("notes_manager")

# Initialize session state for note management
if "current_note_filename" not in st.session_state:
    st.session_state.current_note_filename = None

if "current_note_content" not in st.session_state:
    st.session_state.current_note_content = ""

if "new_note_name" not in st.session_state:
    st.session_state.new_note_name = ""


def get_notes_directory() -> str:
    """
    Get the notes directory path from session state or default.

    Returns:
        The absolute path to the notes directory.
    """
    notes_dir = st.session_state.get("READING_NOTES_DIR", "notes")
    # Type assertion to ensure notes_dir is a string
    if not isinstance(notes_dir, str):
        notes_dir = "notes"
    # Use default value "notes" if the configured value is empty
    if not notes_dir or not notes_dir.strip():
        notes_dir = "notes"
    # Make it absolute path relative to current working directory
    if not os.path.isabs(notes_dir):
        notes_dir = os.path.join(os.getcwd(), notes_dir)
    return notes_dir


def ensure_notes_directory() -> str:
    """
    Ensure the notes directory exists, create if not.

    Returns:
        The absolute path to the notes directory.
    """
    notes_dir = get_notes_directory()
    if not os.path.exists(notes_dir):
        try:
            os.makedirs(notes_dir)
            logger.info("Created notes directory: %s", notes_dir)
        except Exception as e:
            logger.error("Failed to create notes directory: %s", e)
            st.error(f"Failed to create notes directory: {e}")
    return notes_dir


def list_note_files() -> list[str]:
    """
    List all markdown note files in the notes directory.

    Returns:
        A sorted list of markdown filenames.
    """
    notes_dir = ensure_notes_directory()
    note_files = []
    try:
        for filename in os.listdir(notes_dir):
            if filename.endswith(".md"):
                note_files.append(filename)
        note_files.sort()  # Sort alphabetically
    except Exception as e:
        logger.error("Failed to list note files: %s", e)
    return note_files


def load_note_content(filename: str) -> str:
    """
    Load note content from file.

    Args:
        filename: The name of the note file to load.

    Returns:
        The content of the note file, or empty string on error.
    """
    notes_dir = ensure_notes_directory()
    filepath = os.path.join(notes_dir, filename)
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        logger.debug("Loaded note: %s", filename)
        return content
    except Exception as e:
        logger.error("Failed to load note %s: %s", filename, e)
        return ""


def save_note_content(filename: str, content: str) -> bool:
    """
    Save note content to file.

    Args:
        filename: The name of the note file to save.
        content: The content to write to the file.

    Returns:
        True if successful, False otherwise.
    """
    notes_dir = ensure_notes_directory()
    filepath = os.path.join(notes_dir, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Saved note: %s", filename)
        return True
    except Exception as e:
        logger.error("Failed to save note %s: %s", filename, e)
        return False


def delete_note_file(filename: str) -> bool:
    """
    Delete a note file.

    Args:
        filename: The name of the note file to delete.

    Returns:
        True if successful, False otherwise.
    """
    notes_dir = ensure_notes_directory()
    filepath = os.path.join(notes_dir, filename)
    try:
        os.remove(filepath)
        logger.info("Deleted note: %s", filename)
        return True
    except Exception as e:
        logger.error("Failed to delete note %s: %s", filename, e)
        return False


def create_new_note_callback() -> None:
    """Callback wrapper for create_new_note to satisfy Streamlit button on_click type."""
    create_new_note()


def _save_and_rerun_note(note_name: str, filepath: str, initial_content: str) -> None:
    """
    Save new note content and trigger UI refresh.

    Args:
        note_name: Name of the note file.
        filepath: Full path to the note file.
        initial_content: Initial content to write to the file.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(initial_content)
    logger.info("Created new note: %s", note_name)
    # Clear the input field after successful creation and rerun to update UI
    st.session_state.new_note_name = ""
    st.rerun()


def create_new_note() -> None:
    """
    Create a new note file.
    """
    note_name = st.session_state.get("new_note_name", "").strip()
    if not note_name:
        st.error("Please enter a note name.")
        return

    # Ensure filename ends with .md
    if not note_name.endswith(".md"):
        note_name += ".md"

    # Sanitize filename (remove invalid characters)
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        note_name = note_name.replace(char, "_")

    notes_dir = ensure_notes_directory()
    filepath = os.path.join(notes_dir, note_name)

    # Check if file already exists
    if os.path.exists(filepath):
        st.error(f"Note '{note_name}' already exists.")
        return

    # Create empty note with header
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_content = f"# {note_name[:-3]}\n\nCreated: {timestamp}\n\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(initial_content)
        logger.info("Created new note: %s", note_name)
        # Clear the input field and set flag to trigger rerun
        st.session_state.new_note_name = ""
        st.session_state.rerun = True
    except Exception as e:
        logger.error("Failed to create note %s: %s", note_name, e)
        st.error(f"Failed to create note: {e}")


def organize_note_content(note_content: str) -> str:
    """
    Use LLM to organize and format note content.

    Args:
        note_content: The original note content to organize.

    Returns:
        The organized note content, or original content if organization fails.
    """
    if not note_content or not note_content.strip():
        logger.warning("Empty note content, skipping organization")
        return note_content

    try:
        logger.info("Starting AI note organization")

        # Create note organizer model
        model = create_note_organizer_model()

        # Get current date and time in YYYY-MM-DD HH:MM format
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Prepare messages with current date and time
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=f"[CURRENT_DATETIME: {current_datetime}]\n\n{note_content}"
            ),
        ]

        # Show loading indicator and invoke model
        st.toast("AI is organizing your note...", icon="🤖")
        result = model.invoke(messages)

        # Get content from result
        organized_content: str = getattr(result, "content", "")
        if not isinstance(organized_content, str):
            organized_content = str(organized_content)

        # Validate the result
        if not organized_content or not organized_content.strip():
            logger.error("Invalid response from LLM")
            st.error("Failed to organize note: Invalid response from AI")
            return note_content

        logger.info("AI note organization completed successfully")
        return organized_content

    except Exception as e:
        logger.error("Failed to organize note with AI: %s", e)
        st.error(f"Failed to organize note: {e}")
        return note_content


def _save_organized_note(
    filename: str,
    editor_key: str,
    organized_content: str,
) -> bool:
    """
    Save organized note to file.

    Args:
        filename: Name of the note file.
        editor_key: Session state key for the editor.
        organized_content: Organized note content to save.

    Returns:
        True if saved successfully, False otherwise.
    """
    # Update both current_note_content and editor's session state
    st.session_state.current_note_content = organized_content
    st.session_state[editor_key] = organized_content
    return save_note_content(filename, organized_content)


def render_ai_organize_button() -> None:
    """
    Render AI organize button and expander for note organization.

    This function provides a button that triggers AI note organization.
    When clicked, it organizes the current note content and displays the
    result in an expander where the user can choose to accept or reorganize.
    """
    if not st.session_state.current_note_filename:
        return

    # AI Organize button
    if st.button(
        ":material/auto_fix_high: AI Organize",
        key="ai_organize_button",
        help="Use AI to organize and format your note",
        use_container_width=True,
    ):
        # Set a flag to show the organizer expander
        st.session_state.show_ai_organizer = True
        st.rerun()

    # Show AI Organizer expander if flag is set
    if st.session_state.get("show_ai_organizer", False):
        with st.expander("🤖 AI Note Organization", expanded=True):
            # Define editor_key for use later in the function
            editor_key = (
                f"note_editor_{st.session_state.current_note_filename}"
                if st.session_state.current_note_filename
                else "note_editor_empty"
            )

            # Get current note content - prioritize current_note_content which is properly set
            original_content = st.session_state.current_note_content

            # Fallback to editor_key if current_note_content is empty
            if not original_content or not original_content.strip():
                original_content = st.session_state.get(editor_key, "")

            # Store organized content in session state if not already done
            if "organized_content" not in st.session_state:
                organized_content = organize_note_content(original_content)
                st.session_state.organized_content = organized_content
                st.session_state.original_content = original_content
            else:
                organized_content = st.session_state.organized_content
                original_content = st.session_state.original_content

            # Display comparison
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Original:**")
                st.text_area(
                    "Original Content",
                    value=original_content,
                    height=400,
                    key="organizer_original_content",
                    disabled=True,
                    label_visibility="collapsed",
                )
            with col2:
                st.markdown("**Organized:**")
                st.text_area(
                    "Organized Content",
                    value=organized_content,
                    height=400,
                    key="organizer_organized_content",
                    label_visibility="collapsed",
                )

            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "Reorganize",
                    key="organizer_reorganize_button",
                    use_container_width=True,
                ):
                    # Clear organized content to trigger reorganization
                    if "organized_content" in st.session_state:
                        del st.session_state.organized_content
                        del st.session_state.original_content
                    st.rerun()
            with col2:
                if st.button(
                    "Confirm & Apply",
                    key="organizer_confirm_button",
                    type="primary",
                    use_container_width=True,
                ):
                    if _save_organized_note(
                        st.session_state.current_note_filename,
                        editor_key,
                        organized_content,
                    ):
                        st.success("Note organized and saved!")
                        # Clear organizer state
                        st.session_state.show_ai_organizer = False
                        if "organized_content" in st.session_state:
                            del st.session_state.organized_content
                            del st.session_state.original_content
                        st.rerun()
                    else:
                        st.error("Failed to save organized note")

            # Close button
            if st.button(
                "Cancel",
                key="organizer_cancel_button",
                use_container_width=True,
            ):
                # Clear organizer state
                st.session_state.show_ai_organizer = False
                if "organized_content" in st.session_state:
                    del st.session_state.organized_content
                    del st.session_state.original_content
                st.rerun()


def auto_save_note() -> None:
    """Auto-save note content on text area change."""
    if st.session_state.current_note_filename:
        # Get the current content from the text area
        editor_key = (
            f"note_editor_{st.session_state.current_note_filename}"
            if st.session_state.current_note_filename
            else "note_editor_empty"
        )
        current_content = st.session_state.get(editor_key, "")

        # Save to file
        if save_note_content(st.session_state.current_note_filename, current_content):
            st.session_state.current_note_content = current_content
            logger.debug("Auto-saved note: %s", st.session_state.current_note_filename)


def render_notes_editor(
    container_height: int | None = None,
    show_title: bool = True,
) -> None:
    """
    Render the notes editor component.

    Args:
        container_height: Optional height for the editor. If None, will try to
                         get from session state with key "CONTAINER_HEIGHT".
        show_title: Whether to show the notes management title. Defaults to True.
    """
    # Initialize session state if not exists
    if "current_note_filename" not in st.session_state:
        st.session_state.current_note_filename = None
    if "current_note_content" not in st.session_state:
        st.session_state.current_note_content = ""
    if "new_note_name" not in st.session_state:
        st.session_state.new_note_name = ""

    # Check rerun flag set by callback functions
    if st.session_state.get("rerun", False):
        st.session_state.rerun = False
        st.rerun()

    # Get container height
    if container_height is None:
        container_height = st.session_state.get("CONTAINER_HEIGHT", 1000)

    # Get list of note files
    note_files = list_note_files()

    # Create two columns: Editor (left) and Notes Management (right)
    col_editor, col_management = st.columns([2, 1])

    # ===== Note Editor Column =====
    with col_editor:
        # Note editor
        if st.session_state.current_note_filename:
            st.markdown(
                f"#### :material/description: Editing: `{st.session_state.current_note_filename}`"
            )

            # Auto-save indicator
            st.caption(":material/check_circle: Auto-save enabled")

            # AI Organize button
            render_ai_organize_button()

            # Text area for note content (subtract 100px from CONTAINER_HEIGHT for UI elements)
            editor_height = container_height - 150
            editor_key = (
                f"note_editor_{st.session_state.current_note_filename}"
                if st.session_state.current_note_filename
                else "note_editor_empty"
            )
            st.text_area(
                "Note Content",
                value=st.session_state.current_note_content,
                height=editor_height,
                key=editor_key,
                label_visibility="collapsed",
                help="Write your notes here in Markdown format",
                on_change=auto_save_note,
            )
        else:
            st.info("Select or create a note to start editing.")

    # ===== Notes Management Column =====
    with col_management:
        with st.expander(":material/folder: Notes Management", expanded=True):
            # My Notes section (no container)
            st.markdown(
                '<span style="font-size: 14px; font-weight: bold;">📁 My Notes</span>',
                unsafe_allow_html=True,
            )

            if note_files:
                # Create selectbox for note selection with proper index tracking
                current_index = (
                    note_files.index(st.session_state.current_note_filename)
                    if st.session_state.current_note_filename in note_files
                    else 0
                )
                selected_note = st.selectbox(
                    "Select a note to edit:",
                    options=note_files,
                    key="note_selectbox",
                    index=current_index,
                    label_visibility="collapsed",
                )

                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    # Download button
                    st.download_button(
                        label=":material/download:",
                        data=st.session_state.current_note_content,
                        file_name=st.session_state.current_note_filename,
                        mime="text/markdown",
                        key="download_note_btn",
                        help="Download note file",
                        use_container_width=True,
                    )
                with col2:
                    # Delete button
                    delete_btn = st.popover(
                        ":material/delete:", use_container_width=True
                    )
                    with delete_btn:
                        st.write(f"Delete `{st.session_state.current_note_filename}`?")
                        st.write("This action cannot be undone.")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(
                                "Cancel",
                                key="cancel_popover_btn",
                                use_container_width=True,
                            ):
                                st.rerun()
                        with col2:
                            if st.button(
                                "Delete",
                                key="confirm_delete_btn_popover",
                                type="primary",
                                use_container_width=True,
                            ):
                                if delete_note_file(
                                    st.session_state.current_note_filename
                                ):
                                    st.success("Note deleted!")
                                    st.session_state.current_note_filename = None
                                    st.session_state.current_note_content = ""
                                    st.rerun()

                # Load selected note if different from current
                if selected_note != st.session_state.current_note_filename:
                    st.session_state.current_note_filename = selected_note
                    st.session_state.current_note_content = load_note_content(
                        selected_note
                    )
                    st.rerun()
            else:
                st.info("No notes found.")
                st.session_state.current_note_filename = None
                st.session_state.current_note_content = ""

            # Create New Note section
            st.markdown("---")
            st.markdown(
                '<span style="font-size: 14px; font-weight: bold;">:material/add_circle: Create New Note</span>',
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text_input(
                    "Note Name",
                    value=st.session_state.new_note_name,
                    placeholder="e.g., Network Fundamentals",
                    max_chars=40,
                    key="new_note_name_input",
                    help="Enter a name for your new note (.md will be added automatically)",
                    on_change=lambda: st.session_state.update(
                        {"new_note_name": st.session_state.new_note_name_input}
                    ),
                    label_visibility="collapsed",
                )
            with col2:
                st.button(
                    ":material/add:",
                    key="create_note_btn",
                    on_click=create_new_note_callback,
                    help="Create a new note file",
                    use_container_width=True,
                )
