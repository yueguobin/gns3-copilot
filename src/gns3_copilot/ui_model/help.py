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
GNS3 Copilot Help and Configuration Guide Module.

This module provides a comprehensive bilingual help interface for GNS3 Copilot users,
offering detailed configuration guidance in both English and Chinese. It includes
step-by-step instructions for setting up GNS3 server connections, LLM model
configurations, and third-party platform integrations.

Features:
- Bilingual support (English/Chinese) with tabbed interface
- GNS3 server configuration guidance
- LLM model provider setup instructions
- Third-party platform integration examples (OpenRouter)
- Configuration validation and troubleshooting tips
- Step-by-step setup workflow

The help content is organized into clear sections covering all aspects of
GNS3 Copilot configuration, making it easy for users to properly set up
and configure the application for optimal functionality.
"""

import streamlit as st

st.markdown(
    """
    <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>GNS3 Copilot Configuration Guide</h3>
    """,
    unsafe_allow_html=True,
)
tab1_en, tab2_zh = st.tabs(["Help", "帮助"])

with tab1_en:
    st.header("🔧 GNS3 Server Configuration")
    st.markdown("""
    - **GNS3 Server Host** (Required) - GNS3 server address, e.g., 127.0.0.1
    - **GNS3 Server URL** (Required) - GNS3 server URL, e.g., http://127.0.0.1:3080
    - **GNS3 API Version** - Select API version: 2 or 3(Currently only GNS3 version 2.x is supported)
    - **GNS3 User** (Required for API v3) - GNS3 server username
    - **GNS3 Passwd** (Required for API v3) - GNS3 server password
    """)

    st.header("🤖 LLM Model Configuration")
    st.markdown("""
    - **Model Provider** (Required) - Model provider: deepseek, openai, anthropic, etc.
    - **Model Name** (Required) - Model name: deepseek-chat, gpt-4o-mini, etc.
    - **Model Temperature** - Controls output randomness, range 0.0-1.0
    - **Base Url** - Third-party platform API endpoint
    - **Model API Key** (Required) - Model provider's API key
    """)

    st.header("🐧 Other Settings")
    st.markdown("""
    - **Linux Console Username** - Linux device console username
    - **Linux Console Password** - Linux device console password
    """)

    st.header("🌐 Third-Party Platform Setup (OpenRouter Example)")
    st.code(
        """
Model Provider: openai
Base Url: https://openrouter.ai/api/v1
Model Name: openai/gpt-4o-mini
Model API Key: sk-or-v1-xxxxxxxxx
""",
        language="yaml",
    )

    st.header("⚠️ Important Notes")
    st.markdown("""
    1. **Fields marked with * are required**
    2. **Must click "Save Settings to .env" button after configuration**
    3. **Linux credentials required for Linux-related tools**
    4. **Valid API key and model configuration required for AI functionality**
    5. **For OpenRouter and similar platforms, set Model Provider to `openai`**
    """)

    st.header("📝 Configuration Steps")
    st.markdown("""
    1. Fill all required fields
    2. Adjust optional parameters as needed
    3. Click save button
    4. **Restart the application** for changes to take effect
    """)

    st.info("""
    :material:info: **Important**:

    - **LLM model configuration changes require restarting the application**
    - **GNS3 Server configuration changes require restarting the application**
    - Simply refreshing the browser page (F5) is NOT sufficient
    """)

with tab2_zh:
    st.header("🔧 GNS3 服务器配置")
    st.markdown("""
    - **GNS3 Server Host** (必填) - GNS3服务器地址，如：127.0.0.1
    - **GNS3 Server URL** (必填) - GNS3服务器URL，如：http://127.0.0.1:3080
    - **GNS3 API Version** - 选择API版本：2 或 3（目前仅使用gns3 2.x版本）
    - **GNS3 User** (API v3时必填) - GNS3服务器用户名
    - **GNS3 Passwd** (API v3时必填) - GNS3服务器密码
    """)

    st.header("🤖 LLM 模型配置")
    st.markdown("""
    - **Model Provider** (必填) - 模型提供商：deepseek, openai, anthropic等
    - **Model Name** (必填) - 模型名称：deepseek-chat, gpt-4o-mini等
    - **Model Temperature** - 控制输出随机性，范围0.0-1.0
    - **Base Url** - 第三方平台API地址，如OpenRouter
    - **Model API Key** (必填) - 模型提供商的API密钥
    """)

    st.header("🐧 其他设置")
    st.markdown("""
    - **Linux Console Username** - Linux设备控制台用户名
    - **Linux Console Password** - Linux设备控制台密码
    """)

    st.header("🌐 第三方平台配置 (OpenRouter示例)")
    st.code(
        """
Model Provider: openai
Base Url: https://openrouter.ai/api/v1
Model Name: openai/gpt-4o-mini
Model API Key: sk-or-v1-xxxxxxxxx
""",
        language="yaml",
    )

    st.header("⚠️ 重要提醒")
    st.markdown("""
    1. **带 * 的字段为必填项**
    2. **配置完成后必须点击 "Save Settings to .env" 按钮**
    3. **Linux凭据配置后才能使用Linux相关工具**
    4. **API密钥和模型配置正确才能使用AI功能**
    5. **使用OpenRouter等第三方平台时，Model Provider填 `openai`**
    """)

    st.header("📝 配置流程")
    st.markdown("""
    1. 填写所有必填字段
    2. 根据需要调整可选参数
    3. 点击保存按钮
    4. **重启应用**使配置生效
    """)

    st.info("""
    :material:info: **重要提示**:

    - **LLM 模型配置修改后必须重启应用**
    - **GNS3 服务器配置修改后必须重启应用**
    - 仅刷新浏览器页面（按 F5）无法使配置生效
    """)
