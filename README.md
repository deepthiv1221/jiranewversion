# Simple Jira Agent

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://www.python.org/)  
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)  

A lightweight Python script to automate Jira issue management — create, update, and query issues easily.

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Configuration](#configuration)  
- [Dependencies](#dependencies)  
- [Quick Start Example](#quick-start-example)  
- [Contributing](#contributing)  
- [License](#license)  
- [Contact](#contact)  

---

## Overview

`simple_jira_agent.py` is a Python utility that simplifies Jira tasks for developers and QA engineers.  
It allows you to:

- Create Jira issues  
- Fetch issues assigned to a user  

This reduces repetitive manual work and makes Jira project management faster.

---

## Features

- Create new Jira issues easily  
- Fetch your assigned Jira issues  
- Lightweight and easy to set up  

---

## Installation

1. Clone the repository:
git clone https://github.com/deepthiv1221/jiranewversion.git
cd jiranewversion

2. (Optional) Create a virtual environment:

# Linux / Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

3.Install the required library:
pip install -r requirements_simple.txt

4. Usage
from simple_jira_agent import SimpleJiraAgent

# Initialize Jira Agent
agent = SimpleJiraAgent(
    jira_url="https://your-jira-domain.atlassian.net",
    username="your-email@example.com",
    api_token="your-api-token"
)

# Create a new Jira issue
issue = agent.create_issue(
    project_key="PROJ",
    summary="Sample Issue",
    description="This is a test issue created using Simple Jira Agent.",
    issue_type="Task"
)

print(f"Issue created: {issue.key}")

# Fetch issues assigned to the user
issues = agent.get_my_issues()
for i in issues:
    print(i.key, i.fields.summary)


5. Configuration
Before using the agent, you need:
Jira URL – Your Jira instance URL
Username – Your Jira login email
API Token – Generated from Jira account settings
⚠️ Keep your API token safe and do not share it publicly.

6. Dependencies
Python 3.8+
jira Python library
Install manually if needed:
pip install jira

7. Quick Start Example
Create a script, test_agent.py:

from simple_jira_agent import SimpleJiraAgent
agent = SimpleJiraAgent(
    jira_url="https://your-jira-domain.atlassian.net",
    username="your-email@example.com",
    api_token="your-api-token"
)
# Fetch all issues assigned to you
issues = agent.get_my_issues()
for i in issues:
    print(i.key, i.fields.summary)

Run the script:
python test_agent.py

You should see a list of Jira issues assigned to you printed in the terminal.
<img width="1046" height="244" alt="image" src="https://github.com/user-attachments/assets/65840f10-4957-4644-9f70-7d571b49cb58" />

8.Contributing
Contributions are welcome! To contribute:
Fork the repository
Create a branch (git checkout -b feature/my-feature)
Make your changes and commit (git commit -m 'Add feature')
Push to your branch (git push origin feature/my-feature)
Open a Pull Request

9.Output - snapshots 
Here’s what the output will look like when fetching your Jira issues:
If you create a new issue, you will see:
<img width="1233" height="255" alt="image" src="https://github.com/user-attachments/assets/d41bb8a3-1fdc-4d9e-baee-d928b97e39a7" />
<img width="1148" height="486" alt="image" src="https://github.com/user-attachments/assets/48fc6afe-69e0-40b6-aa11-21c301df490b" />
<img width="1074" height="506" alt="image" src="https://github.com/user-attachments/assets/833f7e42-717b-42c8-9c39-3ab2e992849a" />
<img width="1243" height="388" alt="image" src="https://github.com/user-attachments/assets/9f4e3a4b-efce-4b70-b325-4d1b64adaa85" />
<img width="1487" height="559" alt="image" src="https://github.com/user-attachments/assets/fa827328-5562-4aa5-9045-6102f6143a4e" />
<img width="854" height="149" alt="image" src="https://github.com/user-attachments/assets/75ca81a0-24bd-48d4-96a4-060a502e5136" />

Operations 6 and 7 are not currently wokring because the quota if openapi and gemini api are over so , other option is buidling llm 
