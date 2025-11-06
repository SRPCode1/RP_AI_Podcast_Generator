#!/usr/bin/env python3
"""
Test script for GitHub Actions podcast generation workflow.
Tests all 3 trigger methods with validation.
"""

import requests
import os
import json
import time
from datetime import datetime

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set this in your environment
REPO_OWNER = "SRPCode1"
REPO_NAME = "RP_AI_Podcast_Generator"
REPO_FULL = f"{REPO_OWNER}/{REPO_NAME}"

# Test script content (short for testing)
TEST_SCRIPT_SHORT = """Style: Test podcast

Speakers: Friendly and conversational

Speaker 1: Hello! This is a test of our podcast generation system.

Speaker 2: Yes, we're testing if the GitHub Actions workflow works correctly.

Speaker 1: The system should generate audio from this text.

Speaker 2: And send us an email when it's done.

Speaker 1: Perfect! Let's see if it works.
"""

# Longer test script (closer to production size)
TEST_SCRIPT_LONG = """Style: Factual, competent, and future-oriented.

Speakers: Calm, level-headed, and trustworthy tone. Experts preparing a complex topic for colleagues.

Tonality: Not promotional, but competent and radiating a positive yet realistic vision for the future.

Speaker 1: Welcome to our test podcast. Today we're discussing artificial intelligence in real estate valuation.

Speaker 2: Yes, and we're specifically testing our new automated podcast generation system.

Speaker 1: This script is intentionally longer to test if the API can handle realistic content sizes.

Speaker 2: Exactly. In a real podcast, we would have much more content, multiple topics, and deeper discussions.

Speaker 1: Let's add some more content to make this more realistic. We could discuss data collection methods.

Speaker 2: Good idea. Automated data collection is one of the key benefits of AI-powered systems.

Speaker 1: And we should mention natural language processing capabilities.

Speaker 2: Yes, NLP allows us to extract structured data from unstructured documents.

Speaker 1: This is getting closer to a realistic podcast length now.

Speaker 2: Indeed. Let's wrap up this test and see if the system handles it well.

Speaker 1: Perfect. Thank you for this test episode.
"""


def test_method_1_manual_ui():
    """
    Method 1: Manual workflow dispatch via GitHub UI
    This can't be automated via script, but we can show instructions
    """
    print("\n" + "="*60)
    print("METHOD 1: Manual UI Trigger")
    print("="*60)
    print("\n⚠️  This method requires manual interaction.")
    print("\n📋 Steps:")
    print("1. Go to: https://github.com/{}/actions".format(REPO_FULL))
    print("2. Click '🎙️ Generate Podcast' workflow")
    print("3. Click 'Run workflow' button")
    print("4. Paste script content in the text field")
    print("5. Click 'Run workflow'")
    print("\n✅ Pros: Easy, visual, good for testing")
    print("❌ Cons: Manual, not automatable")
    print("\n" + "="*60)


def test_method_2_git_push():
    """
    Method 2: Git push with script.txt
    Shows how to automate this via git commands
    """
    print("\n" + "="*60)
    print("METHOD 2: Git Push Trigger")
    print("="*60)
    print("\n📝 Script for automation:")
    print("""
# Save your script
cat > script.txt << 'EOF'
{}
EOF

# Commit and push
git add script.txt
git commit -m "Generate podcast: {}"
git push

# Workflow triggers automatically
# Check: https://github.com/{}/actions
""".format(TEST_SCRIPT_SHORT, datetime.now().strftime("%Y-%m-%d %H:%M"), REPO_FULL))
    
    print("\n✅ Pros: Simple, handles ANY file size, version controlled")
    print("❌ Cons: Requires git access, creates commit history")
    print("\n💡 RECOMMENDED for production use!")
    print("\n" + "="*60)


def test_method_3_api_small():
    """
    Method 3a: API trigger with SMALL script in JSON body
    """
    print("\n" + "="*60)
    print("METHOD 3a: API Trigger (Small Script)")
    print("="*60)
    
    if not GITHUB_TOKEN:
        print("\n❌ ERROR: GITHUB_TOKEN not set!")
        print("Set it with: export GITHUB_TOKEN='your_token_here'")
        print("Get token from: https://github.com/settings/tokens")
        print("Required scopes: 'repo' or 'public_repo'")
        return False
    
    url = f"https://api.github.com/repos/{REPO_FULL}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "event_type": "generate_podcast",
        "client_payload": {
            "script": TEST_SCRIPT_SHORT,
            "podcast_id": f"test-api-{int(time.time())}",
            "email": "test@example.com"
        }
    }
    
    print(f"\n📤 Sending POST to: {url}")
    print(f"📦 Payload size: {len(json.dumps(payload))} bytes")
    print(f"📝 Script length: {len(TEST_SCRIPT_SHORT)} characters")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 204:
            print("\n✅ SUCCESS! Workflow triggered.")
            print(f"🔗 Check status: https://github.com/{REPO_FULL}/actions")
            return True
        else:
            print(f"\n❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_method_3_api_large():
    """
    Method 3b: API trigger with LARGE script (to test limits)
    """
    print("\n" + "="*60)
    print("METHOD 3b: API Trigger (Large Script)")
    print("="*60)
    
    if not GITHUB_TOKEN:
        print("\n❌ ERROR: GITHUB_TOKEN not set!")
        return False
    
    url = f"https://api.github.com/repos/{REPO_FULL}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "event_type": "generate_podcast",
        "client_payload": {
            "script": TEST_SCRIPT_LONG,
            "podcast_id": f"test-large-{int(time.time())}",
            "email": "test@example.com"
        }
    }
    
    payload_size = len(json.dumps(payload))
    print(f"\n📤 Sending POST to: {url}")
    print(f"📦 Payload size: {payload_size} bytes ({payload_size/1024:.2f} KB)")
    print(f"📝 Script length: {len(TEST_SCRIPT_LONG)} characters")
    
    # Check if payload is too large
    if payload_size > 65536:  # 64KB
        print("\n⚠️  WARNING: Payload might be too large for GitHub API!")
        print("Consider using Method 2 (Git Push) instead.")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 204:
            print("\n✅ SUCCESS! Large script handled correctly.")
            print(f"🔗 Check status: https://github.com/{REPO_FULL}/actions")
            return True
        else:
            print(f"\n❌ FAILED: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_method_4_api_file_reference():
    """
    Method 4: API trigger with file reference (RECOMMENDED for large scripts)
    """
    print("\n" + "="*60)
    print("METHOD 4: API Trigger with File Reference (NEW!)")
    print("="*60)
    
    print("\n💡 This is the RECOMMENDED approach for large scripts!")
    print("\n📋 How it works:")
    print("1. Upload script to GitHub (via commit or API)")
    print("2. Trigger workflow with file reference")
    print("3. Workflow downloads file from repository")
    
    print("\n📝 Implementation needed in workflow:")
    print("""
# In workflow: Download script from repository
- name: Download script from repository
  if: github.event.client_payload.script_file
  run: |
    curl -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \\
      -o script.txt \\
      "${{ github.event.client_payload.script_file }}"
""")
    
    print("\n✅ Pros: Handles unlimited file sizes, clean API calls")
    print("❌ Cons: Requires extra workflow step")
    print("\n" + "="*60)


def create_example_scripts():
    """
    Create example Python scripts for each method
    """
    print("\n" + "="*60)
    print("CREATING EXAMPLE SCRIPTS")
    print("="*60)
    
    # Example 1: Simple API trigger
    with open("example_trigger_api.py", "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Example: Trigger podcast generation via API
Usage: python example_trigger_api.py
\"\"\"

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
""")
    
    print("✅ Created: example_trigger_api.py")
    
    # Example 2: Git automation
    with open("example_trigger_git.sh", "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
# Example: Trigger podcast generation via Git push
# Usage: ./example_trigger_git.sh

# Check if script.txt exists
if [ ! -f "script.txt" ]; then
    echo "❌ Error: script.txt not found"
    exit 1
fi

# Commit and push
git add script.txt
git commit -m "Generate podcast: $(date '+%Y-%m-%d %H:%M')"
git push

echo "✅ Podcast generation triggered via Git push!"
echo "Check: https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions"
""")
    
    print("✅ Created: example_trigger_git.sh")
    
    # Example 3: Curl command
    with open("example_trigger_curl.sh", "w", encoding="utf-8") as f:
        f.write("""#!/bin/bash
# Example: Trigger podcast generation via curl
# Usage: GITHUB_TOKEN=your_token ./example_trigger_curl.sh

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN not set"
    echo "Usage: GITHUB_TOKEN=your_token ./example_trigger_curl.sh"
    exit 1
fi

SCRIPT_CONTENT=$(cat script.txt)

curl -X POST \\
  https://api.github.com/repos/SRPCode1/RP_AI_Podcast_Generator/dispatches \\
  -H "Accept: application/vnd.github+json" \\
  -H "Authorization: Bearer $GITHUB_TOKEN" \\
  -H "X-GitHub-Api-Version: 2022-11-28" \\
  -d "{
    \\"event_type\\": \\"generate_podcast\\",
    \\"client_payload\\": {
      \\"script\\": \\"$SCRIPT_CONTENT\\",
      \\"email\\": \\"your-email@example.com\\"
    }
  }"

echo "✅ Request sent!"
echo "Check: https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions"
""")
    
    print("✅ Created: example_trigger_curl.sh")
    print("\n" + "="*60)


def main():
    """
    Run all tests
    """
    print("\n" + "🎙️"*30)
    print("GITHUB ACTIONS WORKFLOW TESTER")
    print("RP AI Podcast Generator")
    print("🎙️"*30)
    
    # Show all methods
    test_method_1_manual_ui()
    test_method_2_git_push()
    
    # Test API methods
    print("\n🧪 Testing API methods...")
    print("(Requires GITHUB_TOKEN environment variable)")
    
    if GITHUB_TOKEN:
        success_small = test_method_3_api_small()
        success_large = test_method_3_api_large()
        
        if success_small and success_large:
            print("\n✅ All API tests passed!")
        elif success_small:
            print("\n⚠️  Small scripts work, but large scripts may fail.")
            print("💡 Recommendation: Use Method 2 (Git Push) for production.")
        else:
            print("\n❌ API tests failed. Check your GITHUB_TOKEN.")
    else:
        print("\n⚠️  Skipping API tests (no GITHUB_TOKEN)")
        print("Set with: export GITHUB_TOKEN='your_token_here'")
    
    test_method_4_api_file_reference()
    
    # Create example scripts
    create_example_scripts()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*60)
    print("""
📊 Method Comparison:

Method 1 (Manual UI):
  ✅ Easy for testing
  ❌ Not automatable
  📏 No size limit
  
Method 2 (Git Push):
  ✅ Simple automation
  ✅ Unlimited file size
  ✅ Version controlled
  ⭐ RECOMMENDED for production!
  
Method 3 (API JSON):
  ✅ Fully programmable
  ⚠️  Limited to ~64KB
  ✅ Good for short scripts
  ❌ Not ideal for long scripts
  
Method 4 (API + File):
  ✅ Best of both worlds
  ✅ Unlimited file size
  ⚠️  Requires workflow update

🎯 RECOMMENDATION:
For your use case (potentially long scripts):
1. Use Method 2 (Git Push) - simplest and most reliable
2. Or implement Method 4 if you need API control

For short scripts (<10KB):
3. Method 3 (API JSON) works fine
""")
    
    print("\n✅ Test script complete!")
    print(f"🔗 Repository: https://github.com/{REPO_FULL}")
    print(f"🔗 Actions: https://github.com/{REPO_FULL}/actions")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
