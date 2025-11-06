#!/usr/bin/env python3
"""
LIVE TEST: Trigger actual podcast generation via GitHub API
This will make a REAL API call to GitHub Actions
"""

import requests
import os
import time

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "SRPCode1/RP_AI_Podcast_Generator"

# Short test script for quick generation
TEST_SCRIPT = """Style: Test podcast for API validation

Speakers: Technical and friendly

Speaker 1: This is a live test of our GitHub Actions workflow.

Speaker 2: We're testing if the API trigger works correctly.

Speaker 1: The system should generate this audio and create a GitHub notification.

Speaker 2: Let's see if it works!

Speaker 1: Perfect. End of test.
"""

def trigger_podcast():
    """
    Trigger podcast generation via GitHub API
    """
    if not GITHUB_TOKEN:
        print("❌ ERROR: GITHUB_TOKEN not set!")
        print("\n📋 To set it:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select scopes: 'repo' (or 'public_repo' for public repos)")
        print("4. Copy token")
        print("5. Run: $env:GITHUB_TOKEN='your_token_here'  (PowerShell)")
        print("   Or:  export GITHUB_TOKEN='your_token_here'  (Bash)")
        return False
    
    print("\n" + "🎙️"*30)
    print("LIVE PODCAST GENERATION TEST")
    print("🎙️"*30)
    
    url = f"https://api.github.com/repos/{REPO}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "event_type": "generate_podcast",
        "client_payload": {
            "script": TEST_SCRIPT,
            "podcast_id": f"live-test-{int(time.time())}",
            "email": "test@example.com"
        }
    }
    
    print(f"\n📤 Sending POST request to GitHub...")
    print(f"   URL: {url}")
    print(f"   Script length: {len(TEST_SCRIPT)} characters")
    print(f"   Payload size: {len(str(payload))} bytes")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"\n📥 Response received:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 204:
            print("\n✅ SUCCESS! Podcast generation triggered!")
            print("\n📋 What happens next:")
            print("1. GitHub Actions workflow starts (~10 seconds)")
            print("2. Python environment setup (~30 seconds)")
            print("3. Podcast generation (~5-10 minutes)")
            print("4. GitHub Issue created with download link")
            print("5. GitHub Release created with podcast file")
            print("\n🔗 Monitor progress:")
            print(f"   Actions: https://github.com/{REPO}/actions")
            print(f"   Issues:  https://github.com/{REPO}/issues")
            print(f"   Releases: https://github.com/{REPO}/releases")
            
            print("\n🔔 Notifications:")
            print("   - Check your GitHub notifications (bell icon)")
            print("   - Look for new Issue: '✅ Podcast #X Ready'")
            print("   - Issue contains direct download link")
            
            if os.getenv("SMTP_HOST"):
                print("   - Email will also be sent (SMTP configured)")
            
            print("\n⏱️  Estimated time: 5-10 minutes")
            print("\n💡 Tip: Open GitHub in browser and watch the Actions tab!")
            
            return True
            
        elif response.status_code == 401:
            print("\n❌ AUTHENTICATION FAILED!")
            print("   Your GITHUB_TOKEN is invalid or expired.")
            print("   Generate a new one at: https://github.com/settings/tokens")
            
        elif response.status_code == 404:
            print("\n❌ REPOSITORY NOT FOUND!")
            print(f"   Check if {REPO} exists and you have access.")
            
        elif response.status_code == 403:
            print("\n❌ PERMISSION DENIED!")
            print("   Your token doesn't have 'repo' scope.")
            print("   Required scopes: repo or public_repo")
            
        else:
            print(f"\n❌ UNEXPECTED ERROR!")
            print(f"   Response: {response.text}")
            
        return False
        
    except requests.exceptions.Timeout:
        print("\n❌ REQUEST TIMEOUT!")
        print("   GitHub API didn't respond in time.")
        print("   Try again in a moment.")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ NETWORK ERROR: {e}")
        return False
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False


def check_workflow_status():
    """
    Check if workflow file exists and is valid
    """
    print("\n📋 Pre-flight checks:")
    
    # Check if workflow file exists in repo
    url = f"https://api.github.com/repos/{REPO}/contents/.github/workflows/generate_podcast.yml"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Workflow file exists in repository")
            return True
        else:
            print(f"   ❌ Workflow file not found (status: {response.status_code})")
            print("   Make sure the workflow was pushed to GitHub!")
            return False
    except Exception as e:
        print(f"   ⚠️  Couldn't verify workflow (continuing anyway): {e}")
        return True  # Continue anyway


def main():
    """
    Main test function
    """
    print("\n" + "="*60)
    print("GitHub Actions Podcast Generator - LIVE TEST")
    print("="*60)
    
    # Check workflow
    if not check_workflow_status():
        print("\n⚠️  Warning: Workflow might not exist yet!")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborting.")
            return
    
    # Trigger
    success = trigger_podcast()
    
    if success:
        print("\n" + "="*60)
        print("TEST SUCCESSFUL!")
        print("="*60)
        print("\n✅ Next steps:")
        print("1. Open: https://github.com/{}/actions".format(REPO))
        print("2. Watch the '🎙️ Generate Podcast' workflow run")
        print("3. Wait for GitHub notification (Issue)")
        print("4. Download podcast from Issue or Release")
        
    else:
        print("\n" + "="*60)
        print("TEST FAILED - See errors above")
        print("="*60)


if __name__ == "__main__":
    main()
