#!/usr/bin/env python3
"""
Example: Trigger podcast generation via API
Usage: python example_trigger_api.py
"""

import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "SRPCode1/RP_AI_Podcast_Generator"

# Read your script
with open("script.txt", "r", encoding="utf-8") as f:
    script_content = f.read()

# Trigger workflow
response = requests.post(
    f"https://api.github.com/repos/{REPO}/dispatches",
    headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    },
    json={
        "event_type": "generate_podcast",
        "client_payload": {
            "script": script_content,
            "email": "your-email@example.com"
        }
    }
)

if response.status_code == 204:
    print("✅ Podcast generation triggered!")
    print("Check: https://github.com/{}/actions".format(REPO))
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
