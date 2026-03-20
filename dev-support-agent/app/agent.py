# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import google.auth
import google.auth.transport.requests
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

import os
import google.auth

import logging

# Set the threshold to DEBUG and define a clear format
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def get_logging_mcp_toolset():
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    auth_request = google.auth.transport.requests.Request()
    credentials.refresh(auth_request)

    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://logging.googleapis.com/mcp",
            headers={
                "Authorization": f"Bearer {credentials.token}",
                "x-goog-user-project": os.environ["GOOGLE_CLOUD_PROJECT"],
                "Content-Type": "application/json",
            },
        )
    )


def get_repos_mcp_toolset():

    # 3. Define the Toolset for the Google Logging MCP endpoint
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://api.githubcopilot.com/mcp",
            headers={
                "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
                "X-MCP-Toolsets": "repos,issues,pull_requests",
                "X-MCP-Readonly": "true",
            },
        )
    )


class LogAnalyst(Agent):
    """
    Worker Agent specialized in fetching and analyzing GCP Logs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            model="gemini-3-flash-preview",
            name="LogAnalyst",
            description="Specialized in Cloud Logging Query Language (LogQL).",
            instruction=(
                "You are the LogAnalyst. You specialize in analyzing GCP Cloud Logging logs. \n"
                "Use the query_gcp_logs tool (interfacing with https://logging.googleapis.com/mcp) \n"
                "to search for errors related to the user's issue. You'll need to find errors or exceptions and \n"
                "extract enough context information for another specialized agent to find the code that might be failing. \n"
                "It's important that you pinpoint exactly only a handful of potential source code files \n"
                "with problems so the code scout can focus on those \n"
                "For that you'll analyse the last 5 hours worth of logs with ERROR or WARNING category. \n"
                "IMPORTANT: Do not suggest code fixes. Your only job is to find the logs and identify "
                "the failing components and files. \n"
                "IMPORTANT: Feel free to ask any questions along the process to narrow down the problem."
            ),
            tools=[get_logging_mcp_toolset()],
            *args,
            **kwargs,
        )


class CodeScout(Agent):
    """
    Worker Agent specialized in reading code from GitHub and identifying bugs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            model="gemini-3-flash-preview",
            name="CodeScout",
            description="Expert in code auditing and bug localization.",
            instruction=(
                "You are the CodeScout. You specialize in reading and analyzing code. \n"
                "Use the fetch_repo_content tool (interfacing with https://api.githubcopilot.com/mcp) \n"
                "to read files identified by the LogAnalyst. Ideally the log analyst will pinpoint \n"
                "a handful of potential source code files with problems that you'll need to search and analyze. \n"
                "You need to focus your investigation in the files in the 'geage' repo, specially in the cloud_function folder. \n"
                "Ideally you'll try to find the actual repository and file highlighted in the problem and. \n"
                "draw a conclusion on how the code generated the problem presented. \n"
                "IMPORTANT: Only analyze files explicitly provided by the logs. Provide technical \n"
                "analysis of the bugs found in these files. \n"
                "IMPORTANT: Feel free to ask any questions along the process to narrow down the problem."
            ),
            tools=[get_repos_mcp_toolset()],
            *args,
            **kwargs,
        )


code_scout = CodeScout()
log_analyst = LogAnalyst()


class SupportManager(Agent):
    """
    Orchestrator Agent that manages user interactions and delegates
    tasks to the specialized worker agents using Recursive Reasoning.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            model="gemini-3-flash-preview",
            name="SupportManager",
            description="Acts as the entry point for user queries and orchestrates the support process.",
            instruction=(
                "You are the SupportManager orchestrator.\n"
                "Your job is to diagnose infrastructure errors and code bugs.\n"
                "1. Delegate to LogAnalyst to fetch relevant logs for the issue.\n"
                "2. Delegate to CodeScout to inspect the code files identified by the logs.\n"
                "3. Synthesize the findings into a human-readable Root Cause Analysis (RCA).\n"
                "Manage the shared session state carefully."
            ),
            sub_agents=[code_scout, log_analyst],
            *args,
            **kwargs,
        )


root_agent = SupportManager()


app = App(
    root_agent=root_agent,
    name="app",
)
