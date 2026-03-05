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
Automatic Documentation Update Script using DeepSeek API

This script has two modes:
1. Local mode: Creates PR with AI-generated title and description (no doc updates)
2. GitHub Actions mode: Updates documentation and creates PR comment

Usage:
    # Local mode - create PR
    export DEEPSEEK_API_KEY="your-api-key"
    export GITHUB_TOKEN="your-github-token"
    export REPO_OWNER="yueguobin"
    export REPO_NAME="gns3-copilot"
    python scripts/auto_update_docs.py
    
    # GitHub Actions mode - update docs and comment
    # Automatically triggered by PR to Development branch
"""

import os
import sys
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, will use environment variables directly
    pass

# Configuration with fallback support
# Priority: DEEPSEEK_* env vars > MODEL_* env vars (from .env) > defaults
DEEPSEEK_API_KEY = (
    os.getenv('DEEPSEEK_API_KEY') or 
    os.getenv('MODEL_API_KEY')
)
DEEPSEEK_MODEL = (
    os.getenv('DEEPSEEK_MODEL') or 
    os.getenv('MODEL_NAME', 'deepseek-chat')
)
DEEPSEEK_API_URL = (
    os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
)
PR_NUMBER = os.getenv('PR_NUMBER')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = os.getenv('REPO_OWNER')
REPO_NAME = os.getenv('REPO_NAME')


def get_changed_files(base_ref: str = 'origin/Development') -> List[str]:
    """Get list of changed files in the PR"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', f'{base_ref}...HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return [f for f in result.stdout.split('\n') if f]
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        return []


def get_commit_messages(base_ref: str = 'origin/Development') -> List[str]:
    """Get all commit messages in the PR"""
    try:
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%s', f'{base_ref}..HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        commits = [c.strip() for c in result.stdout.split('\n') if c.strip()]
        print(f"✓ Found {len(commits)} commits")
        return commits
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e}")
        return []


def read_existing_documentation(doc_file: str, section: str) -> str:
    """Read existing content from a documentation section"""
    doc_path = Path(doc_file)
    if not doc_path.exists():
        return ""
    
    content = doc_path.read_text(encoding='utf-8')
    
    # Define section mappings
    section_mappings = {
        "Core Features": ["Core Features", "Features"],
        "核心功能": ["核心功能", "功能列表"],
    }
    
    possible_sections = section_mappings.get(section, [section])
    
    for possible_section in possible_sections:
        # Look for section header
        pattern = r'(#{1,6}\s+' + re.escape(possible_section) + r'\s*$)'
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        
        if match:
            # Find the next section header (same or higher level)
            section_start = match.end()
            heading_level = len(match.group(1).split()[0])
            next_section_pattern = r'^#{1,' + str(heading_level) + r'}\s+\S'
            next_match = re.search(next_section_pattern, content[section_start:], re.MULTILINE)
            
            if next_match:
                section_end = section_start + next_match.start()
                return content[section_start:section_end].strip()
            else:
                return content[section_start:].strip()
    
    return ""


def get_relevant_files(changed_files: List[str]) -> Tuple[List[str], str]:
    """Get relevant files based on mode"""
    if PR_NUMBER:
        # GitHub Actions mode: only source code changes
        relevant = [f for f in changed_files if f.startswith('src/')]
        change_type = "source code"
    else:
        # Local mode: all project files
        supported_dirs = [
            'src/',
            'docs/',
            'scripts/',
            '.github/',
            'tests/',
        ]
        supported_files = ['pyproject.toml', 'Makefile', 'LICENSE']
        
        relevant = []
        for f in changed_files:
            if f.startswith(tuple(supported_dirs)) or f in supported_files:
                relevant.append(f)
        change_type = "project changes"
    
    return relevant, change_type


def get_diff_content(base_ref: str = 'origin/Development') -> str:
    """Get git diff content"""
    try:
        result = subprocess.run(
            ['git', 'diff', f'{base_ref}...HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting diff: {e}")
        return ""


def call_deepseek_api_for_pr(prompt: str) -> Optional[Dict]:
    """Call DeepSeek API for PR generation (local mode)"""
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not found")
        return None
    
    import urllib.request
    import urllib.error
    
    url = DEEPSEEK_API_URL
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": """You are creating a GitHub Pull Request for the GNS3 Copilot project.
Analyze the code changes and generate a PR title and description following this exact template:

## 🚀 Change Type
- [x] ✨ New Feature
- [ ] 🐞 Bug Fix
- [ ] 🔧 Refactor/Maintenance
- [ ] 📚 Documentation

## 📝 Description of Changes
[Write a detailed description here, explaining what changes were made and why]

## 🧪 Testing Verification
- [ ] Verified in local environment (Local GNS3/Nornir Test)
- [ ] Run pytest and passed
- [ ] mypy and ruff checks passed

## 🔗 Related Issues
Fixes #

Rules:
1. Automatically select and mark the appropriate Change Type with [x]
2. Keep the Testing Verification and Related Issues sections exactly as shown
3. Write a clear, detailed Description of Changes
4. PR title should be concise (max 72 characters)

Output ONLY valid JSON:
{
    "pr_title": "Concise PR title",
    "pr_description": "Full description following the template format"
}"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return None
            
    except urllib.error.HTTPError as e:
            print(f"API Error {e.code}: {e.read().decode('utf-8')}")
            return None
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return None


def call_deepseek_api_for_docs(
    prompt: str,
    commit_messages: List[str],
    existing_features_en: str = "",
    existing_features_zh: str = ""
) -> Optional[Dict]:
    """Call DeepSeek API for documentation updates (GitHub Actions mode)"""
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not found")
        return None
    
    import urllib.request
    import urllib.error
    
    url = DEEPSEEK_API_URL
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Build enhanced system prompt with context
    system_prompt = """You are a documentation assistant for GNS3 Copilot project. 
Analyze code changes and provide:
1. English change summary for PR comment
2. Chinese change summary for README_ZH.md
3. Documentation updates for README.md and README_ZH.md

IMPORTANT RULES for Documentation Updates:
- Use the EXACT section names: "Core Features" (not "Features") for README.md and "核心功能" (not "功能列表") for README_ZH.md
- Compare new features AGAINST the existing documentation provided below
- ONLY add features that are NOT already documented
- Aggregate related features from multiple commits into cohesive descriptions
- Each feature should be on a separate bullet point starting with - (dash) followed by an emoji
- Do NOT duplicate existing features - skip them completely
- If all features are already documented, return empty strings for content

EXTRACTED EXISTING FEATURES (English):
""" + (existing_features_en if existing_features_en else "(No existing features found)") + """

EXTRACTED EXISTING FEATURES (中文):
""" + (existing_features_zh if existing_features_zh else "(未找到现有功能)") + """

Output in JSON format:
{
    "english_summary": "English change summary for PR comment",
    "chinese_summary": "Chinese change summary",
    "doc_updates": {
        "README.md": {"section": "Core Features", "content": "new bullet points to add (only NEW features, not duplicates)"},
        "README_ZH.md": {"section": "核心功能", "content": "新增功能要点（仅新功能，不重复）"}
    }
}

Example output:
{
    "english_summary": "Added voice interaction support with TTS/STT",
    "chinese_summary": "添加语音交互支持，包括TTS/STT功能",
    "doc_updates": {
        "README.md": {"section": "Core Features", "content": "- 🗣️ **Voice Interaction**: Text-to-speech and speech-to-text support for hands-free operation"},
        "README_ZH.md": {"section": "核心功能", "content": "- 🗣️ **语音交互**：支持文本转语音和语音转文本，实现免提操作"}
    }
}
"""
    
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 4000
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from content
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return None
            
    except urllib.error.HTTPError as e:
            print(f"API Error {e.code}: {e.read().decode('utf-8')}")
            return None
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")
        return None


def update_documentation(doc_updates: Dict) -> Dict[str, str]:
    """Update documentation files"""
    updated_files = {}
    
    for doc_file, update_info in doc_updates.items():
        doc_path = Path(doc_file)
        
        if not doc_path.exists():
            print(f"Warning: {doc_file} not found, skipping")
            continue
        
        content = doc_path.read_text(encoding='utf-8')
        section = update_info.get('section', '')
        new_content = update_info.get('content', '')
        
        # Find and update section
        if section:
            # Define common section name mappings for README files
            # Map canonical section name to possible variations (without markdown prefixes)
            section_mappings = {
                "Core Features": [
                    "Core Features", 
                    "Features"
                ],
                "核心功能": [
                    "核心功能", 
                    "功能列表"
                ],
            }
            
            # Get possible section names
            possible_sections = section_mappings.get(section, [section])
            
            # Try each possible section name
            match = None
            for possible_section in possible_sections:
                # Look for section header (e.g., "## Core Features" or "### Core Features")
                # More flexible pattern that handles various markdown heading formats
                pattern = rf'(#{1,6}\s+{re.escape(possible_section)}\s*$)'
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    break
            
            if match:
                # Insert new content after the section header
                insert_pos = match.end()
                updated_content = content[:insert_pos] + new_content + '\n' + content[insert_pos:]
                doc_path.write_text(updated_content, encoding='utf-8')
                updated_files[doc_file] = "Section updated"
                print(f"✓ Updated {doc_file}")
            else:
                print(f"✗ Section '{section}' not found in {doc_file}")
                updated_files[doc_file] = "Section not found"
    
    return updated_files


def commit_changes(message: str) -> bool:
    """Commit changes to git (note: push is handled by GitHub Actions workflow)"""
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ Changes committed successfully")
            # Note: git push is handled by GitHub Actions workflow
            return True
        elif 'nothing to commit' in result.stdout.lower():
            print("No changes to commit")
            return True
        else:
            print(f"Commit failed: {result.stdout}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Error committing changes: {e}")
        return False


def create_pr_comment(summary: str) -> bool:
    """Create PR comment using GitHub API"""
    if not GITHUB_TOKEN or not PR_NUMBER:
        print("Missing GITHUB_TOKEN or PR_NUMBER, skipping PR comment")
        return False
    
    import urllib.request
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    data = {
        "body": f"""## 📝 Documentation Update Summary

{summary}

---
*This comment was automatically generated by DeepSeek API*"""
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✓ PR comment created (#{PR_NUMBER})")
            return True
            
    except Exception as e:
        print(f"Error creating PR comment: {e}")
        return False


def create_pull_request(title: str, description: str, base_branch: str = 'Development') -> Optional[int]:
    """Create Pull Request using GitHub API"""
    if not GITHUB_TOKEN:
        print("Missing GITHUB_TOKEN, skipping PR creation")
        return None
    
    # Get current branch name
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        head_branch = result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Failed to get current branch name")
        return None
    
    import urllib.request
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "body": description,
        "head": head_branch,
        "base": base_branch
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            pr_number = result.get('number')
            print(f"✓ Pull Request created: #{pr_number}")
            print(f"  URL: {result.get('html_url')}")
            return pr_number
            
    except Exception as e:
        print(f"Error creating Pull Request: {e}")
        return None


def main():
    """Main execution"""
    print("=" * 60)
    print("GNS3 Copilot - Automatic Documentation Update")
    print("=" * 60)
    print()
    
    # Get code changes
    print("📋 Analyzing code changes...")
    changed_files = get_changed_files()
    diff_content = get_diff_content()
    
    if not changed_files:
        print("No changed files detected. Exiting.")
        return 0
    
    print(f"✓ Found {len(changed_files)} changed files")
    print(f"  Files: {', '.join(changed_files[:5])}...")
    print()
    
    # Filter relevant files based on mode
    relevant_files, change_type = get_relevant_files(changed_files)
    if not relevant_files:
        print(f"No {change_type} detected. Exiting.")
        return 0
    
    print(f"✓ Found {len(relevant_files)} {change_type}")
    print()
    
    # Two modes: Local (create PR) vs GitHub Actions (update docs)
    if PR_NUMBER:
        # GitHub Actions mode: Update documentation and create comment
        print(f"🤖 GitHub Actions mode detected (PR #{PR_NUMBER})")
        
        # Get commit messages for better context
        print("📜 Fetching commit messages...")
        commit_messages = get_commit_messages()
        
        # Read existing documentation to avoid duplicates
        print("📖 Reading existing documentation...")
        existing_features_en = read_existing_documentation('README.md', 'Core Features')
        existing_features_zh = read_existing_documentation('README_ZH.md', '核心功能')
        
        print(f"✓ Found {len(existing_features_en)} characters in existing English features")
        print(f"✓ Found {len(existing_features_zh)} characters in existing Chinese features")
        print()
        
        # Build comprehensive prompt
        prompt = f"""Analyze the following code changes in the GNS3 Copilot project:

Changed files: {', '.join(relevant_files)}

Commit messages (for context):
{chr(10).join([f"- {msg}" for msg in commit_messages])}

Git diff (for detailed analysis):
{diff_content[:8000]}

Based on the commit messages and code changes, provide:
1. English summary of changes for PR comment
2. Chinese summary for README_ZH.md
3. Documentation updates for README.md and README_ZH.md (only NEW features not already documented)
"""
        
        print(f"🤖 Calling DeepSeek {DEEPSEEK_MODEL} API for documentation updates...")
        api_response = call_deepseek_api_for_docs(
            prompt,
            commit_messages=commit_messages,
            existing_features_en=existing_features_en,
            existing_features_zh=existing_features_zh
        )
        
        if not api_response:
            print("✗ Failed to get response from DeepSeek API")
            return 1
        
        print("✓ Received response from DeepSeek API")
        print()
        
        english_summary = api_response.get('english_summary', 'No summary available')
        chinese_summary = api_response.get('chinese_summary', '')
        doc_updates = api_response.get('doc_updates', {})
        
        print("📄 English Summary:")
        print(english_summary)
        print()
        
        if chinese_summary:
            print("📝 Chinese Summary:")
            print(chinese_summary)
            print()
        
        # Log documentation update suggestions
        if doc_updates:
            print("📝 Documentation update suggestions:")
            for doc_file, update_info in doc_updates.items():
                section = update_info.get('section', '')
                content = update_info.get('content', '')
                if content:
                    print(f"  {doc_file} ({section}):")
                    print(f"    {content[:100]}...")
                    if len(content) > 100:
                        print(f"    ({len(content)} characters total)")
                else:
                    print(f"  {doc_file}: No new content (all features already documented)")
            print()
        
        # Update documentation
        if doc_updates:
            print("📚 Updating documentation...")
            updated_files = update_documentation(doc_updates)
            print()
            
            if updated_files:
                # Check if any actual updates were made
                actual_updates = {k: v for k, v in updated_files.items() if v == "Section updated"}
                
                if actual_updates:
                    # Commit changes
                    commit_msg = f"docs: auto-update documentation\n\n[skip ci]\nSummary: {english_summary[:100]}"
                    commit_changes(commit_msg)
                else:
                    print("ℹ️  All features already documented, no updates needed")
            else:
                print("No documentation updates applied")
        else:
            print("No documentation updates suggested")
        
        # Create PR comment
        print("💬 Creating PR comment...")
        create_pr_comment(english_summary)
        print()
        
    else:
        # Local mode: Create PR only (no documentation updates)
        print("🤖 Local mode detected (creating PR)")
        
        # Get commit messages for better context
        print("📜 Fetching commit messages...")
        commit_messages = get_commit_messages()
        print()
        
        print(f"🤖 Calling DeepSeek {DEEPSEEK_MODEL} API for PR generation...")
        
        # Build enhanced prompt with commit messages
        commit_list = "\n".join([f"- {msg}" for msg in commit_messages]) if commit_messages else "No commits found"
        
        prompt = f"""Analyze the following code changes in the GNS3 Copilot project:

Changed files: {', '.join(relevant_files)}

Commit messages (for understanding the full scope of changes):
{commit_list}

Git diff (for detailed code analysis):
{diff_content[:8000]}

IMPORTANT: Focus on identifying NEW FEATURES and FUNCTIONAL CHANGES in the code,
not just documentation updates. The PR should describe the actual code functionality improvements.

Prioritize:
1. New tools or functions added
2. Major refactoring or architectural changes
3. Bug fixes and improvements
4. Configuration or dependency changes

Generate a PR title and description following the provided template format.
"""
        
        api_response = call_deepseek_api_for_pr(prompt)
        
        if not api_response:
            print("✗ Failed to get response from DeepSeek API")
            return 1
        
        print("✓ Received response from DeepSeek API")
        print()
        
        pr_title = api_response.get('pr_title', 'Documentation update')
        pr_description = api_response.get('pr_description', 'See description in PR')
        
        print("📄 PR Title:")
        print(f"  {pr_title}")
        print()
        
        print("📄 PR Description (first 500 chars):")
        print("  " + pr_description[:500].replace('\n', '\n  '))
        if len(pr_description) > 500:
            print("  ...")
        print()
        
        # Create PR
        print("🔀 Creating Pull Request...")
        pr_num = create_pull_request(pr_title, pr_description)
        if pr_num:
            print()
            print(f"✓ PR #{pr_num} created successfully!")
            print("  Documentation will be updated by GitHub Actions when PR is opened.")
        else:
            print()
            print("⚠ Could not create PR automatically.")
            print(f"  Please create PR manually with:")
            print(f"    Title: {pr_title}")
            print(f"    Description: {pr_description[:200]}...")
        print()
    
    print("=" * 60)
    print("✓ Operation completed successfully")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
