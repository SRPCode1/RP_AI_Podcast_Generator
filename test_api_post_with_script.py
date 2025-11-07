#!/usr/bin/env python3
"""
Test API POST Trigger with Full Script in Body
Shows how to send complete podcast script via REST API
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_api_post_with_script():
    print("🎙️ API POST TEST - Script im Body 🎙️\n")
    
    # Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_OWNER = "SRPCode1"
    REPO_NAME = "RP_AI_Podcast_Generator"
    
    # Überprüfe Token
    if not GITHUB_TOKEN:
        print("❌ ERROR: GITHUB_TOKEN not found in .env")
        print("\n📋 So erstellst du einen Classic Token:")
        print("   1. Gehe zu: https://github.com/settings/tokens/new")
        print("   2. Wähle: 'Generate classic token'")
        print("   3. Scopes: ✅ repo (alle Optionen)")
        print("   4. Generate & kopiere den Token")
        print("   5. In .env speichern: GITHUB_TOKEN=ghp_...")
        return False
    
    # Full podcast script
    full_script = """Style: Vollständig via API
Speakers: Technical, Narrator

[INTRO]
Speaker 1: Willkommen zur Podcast-Episode via API.
Speaker 2: Dieses Skript wurde komplett im POST-Request gesendet.

[HAUPTTEIL]
Speaker 1: Das ist ein vollständiger Test.
Speaker 2: Mit mehreren Absätzen und Sprechern.

Speaker 1: Wir testen hier die Größenlimits.
Speaker 2: und die Zuverlässigkeit der API.

[WEITERE INHALTE]
Speaker 1: Man kann beliebig lange Skripte senden.
Speaker 2: Solange sie unter 65KB bleiben.

Speaker 1: Das ist genug für mehrere Episoden.
Speaker 2: oder sehr lange einzelne Episoden.

[OUTRO]
Speaker 1: Ende des Tests.
Speaker 2: Danke für's Zuhören!
Speaker 1: Tschüss!
"""
    
    script_size = len(full_script)
    print(f"📝 Script Größe: {script_size} bytes")
    print(f"   (GitHub API limit: ~65KB = 65.000 bytes)\n")
    
    if script_size > 65000:
        print("⚠️  WARNING: Script könnte zu groß sein!")
        print("   GitHub API hat ~65KB limit für POST body\n")
    
    # Prepare API call
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    payload = {
        "event_type": "generate_podcast",
        "client_payload": {
            "script": full_script,
            "email": "optional@email.com"  # Optional
        }
    }
    
    print("📤 Sende API POST Request...\n")
    print(f"URL: {url}")
    print(f"Token Format: {GITHUB_TOKEN[:20]}...{GITHUB_TOKEN[-10:]}")
    print(f"Payload Size: {len(json.dumps(payload))} bytes\n")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}\n")
        
        if response.status_code == 204:
            print("✅ SUCCESS! Repository dispatch triggered!")
            print("\n📋 Was passiert jetzt:")
            print("1. ⏱️  GitHub registriert den dispatch event")
            print("2. 🚀 Workflow startet automatisch (~5 Sekunden)")
            print("3. 🎙️  Podcast wird mit dem Script aus dem POST erstellt")
            print("4. 📦 Release wird erstellt")
            print("5. 📝 GitHub Issue Notification wird gesendet\n")
            print("🔗 Monitor: https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions\n")
            return True
            
        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"Response Body: {response.text}\n")
            
            if response.status_code == 401:
                print("🔑 Authentifizierungsfehler - Token ungültig")
                print("   → Prüfe ob Token in .env korrekt ist")
            elif response.status_code == 403:
                print("🔐 Permissions-Fehler - Token hat nicht genug Rechte")
                print("   → Du brauchst einen CLASSIC Token mit 'repo' Scope")
                print("   → Fine-grained tokens funktionieren nicht")
                print("   → Erstelle neuen Token: https://github.com/settings/tokens/new")
            elif response.status_code == 404:
                print("📍 Repository nicht gefunden")
                print("   → Prüfe REPO_OWNER und REPO_NAME")
            
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def show_size_comparison():
    """Zeige Größenvergleiche für verschiedene Skripttypen"""
    print("\n" + "="*60)
    print("📊 Script Size Vergleiche")
    print("="*60 + "\n")
    
    scripts = {
        "Kurzes Test-Skript": "Speaker 1: Test\nSpeaker 2: OK",
        "Mittlere Episode (5 min)": "Style: Normal\n\n" + "Speaker 1: Text\n" * 20,
        "Lange Episode (30 min)": "Style: Normal\n\n" + "Speaker 1: Text\n" * 150,
        "Sehr lange Episode (60 min)": "Style: Normal\n\n" + "Speaker 1: Text\n" * 300,
    }
    
    for name, content in scripts.items():
        size = len(content)
        percentage = (size / 65000) * 100
        status = "✅ OK" if size < 65000 else "⚠️ GRENZFALL" if size < 63000 else "❌ ZU GROSS"
        print(f"{name:30} | {size:6} bytes | {percentage:5.1f}% | {status}")
    
    print("\n💡 Empfehlung: Bleib unter 60KB um sicher zu sein")
    print("   = ~1.500 Zeilen Text oder ~30-45 min Audio\n")

if __name__ == "__main__":
    # Show size comparison first
    show_size_comparison()
    
    # Try API test
    print("="*60)
    print("🔬 Versuche API POST...")
    print("="*60 + "\n")
    
    success = test_api_post_with_script()
    
    if not success:
        print("\n⚠️  Wenn du API-Trigger nutzen möchtest:")
        print("    1. Gehe zu https://github.com/settings/tokens/new")
        print("    2. Wähle 'Generate classic token'")
        print("    3. Aktiviere ✅ repo scope (alle Optionen)")
        print("    4. Kopiere Token und ersetze in .env")
        print("    5. Starte dieses Script erneut\n")
    
    sys.exit(0 if success else 1)
