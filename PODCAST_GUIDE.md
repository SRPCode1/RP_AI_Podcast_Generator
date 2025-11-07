# 🎙️ QUICK START - Regelmäßige Podcast-Erstellung

## 🚀 Deine 3 Optionen im Überblick

| Methode | Best für | Setup | Größenlimit | Automation |
|---------|----------|-------|-------------|-----------|
| **Git Push** | Regelmäßig + Archivierung | ✅ Ready | ∞ | ⭐⭐⭐ |
| **Manual UI** | Tests, einzeln | ✅ Ready | 5000 chars | ⭐ |
| **API POST** | Automatisierung, Tools | ⚠️ Token nötig | ~65KB | ⭐⭐⭐ |

---

## 1️⃣ GIT PUSH (EMPFOHLEN für täglich/wöchentlich)

### Setup (einmalig)
```bash
# Repo bereits geclont? ✅ Fertig!
git config user.name "Your Name"
git config user.email "your.email@github.com"
```

### Podcast erstellen (immer gleich)
```powershell
# 1. Script schreiben
notepad script.txt

# 2. Inhalt eingeben:
# ---
# Style: Normal
# 
# Speaker 1: Hallo, das ist Episode 1.
# Speaker 2: Willkommen zum Podcast!
# ---

# 3. Pushen (fertig!)
git add script.txt
git commit -m "Podcast: Episode 1 - Mein erstes Abenteuer"
git push
```

### Was passiert automatisch
```
script.txt pushed
    ↓ (~5 Sekunden)
GitHub erkennt Änderung
    ↓
Workflow startet automatisch
    ↓ (~5-10 Minuten)
Podcast generiert
    ↓
GitHub Release erstellt
    ↓
GitHub Issue Notification (in deinem Notifications Bell)
    ↓
Download Link verfügbar
```

### Vorteile
✅ **Keine Tools/Tokens nötig**  
✅ **Git-Historie** - alle Episoden gespeichert  
✅ **Unbegrenzte Dateigröße** - auch 50-Seiten-Skripte  
✅ **Offline möglich** - nur bei `push` lädt es  
✅ **Zuverlässig** - wird immer getriggert  

### Praktische Tipps
```powershell
# Schnell mehrere Episoden batch-erstellen:

# Episode 1
"Style: Episode 1`n`nSpeaker 1: Text..." | Out-File script.txt
git add script.txt; git commit -m "EP1"; git push
Start-Sleep -Seconds 10

# Episode 2
"Style: Episode 2`n`nSpeaker 1: Text..." | Out-File script.txt
git add script.txt; git commit -m "EP2"; git push
```

---

## 2️⃣ MANUAL UI (für Tests/Experimente)

### Wie es funktioniert
```
1. Gehe zu: https://github.com/SRPCode1/RP_AI_Podcast_Generator
2. Oben: "Actions" Tab
3. Links: "Generate Podcast"
4. Blauer Button: "Run workflow"
5. Textarea: Script kopieren-einfügen
6. Optional: Email eingeben
7. "Run workflow" klicken
8. Fertig! (Workflow läuft)
```

### Vorteile
✅ **Keine Kommandozeile nötig**  
✅ **Schnell für Tests**  
✅ **Browser-basiert**  

### Nachteile
❌ **Manuell jedesmal**  
❌ **Script-Größe begrenzt** (~5000 Zeichen in der UI)  

---

## 3️⃣ API POST (für Automatisierung/Integration)

### Setup (einmalig - 2 Minuten)

**Schritt 1: Erstelle einen Classic GitHub Token**
```
1. Gehe zu: https://github.com/settings/tokens/new
2. Wähle: "Generate classic token"
3. Name: "Podcast Generator API"
4. Scopes: ✅ Aktiviere "repo" (alle Optionen)
5. Generate & kopiere Token
```

**Schritt 2: Speichere in .env**
```bash
# .env
GITHUB_TOKEN=ghp_xxxxx_neu_kopiert_xxxxx

# Wichtig: NICHT die alte fine-grained PAT!
# Diese war: GITHUB_TOKEN = "github_pat_..."
# Ersetze durch die neue Classic Token!
```

**Schritt 3: Teste es**
```powershell
python test_api_post_with_script.py
```

### Script via API senden

**Python-Beispiel:**
```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "SRPCode1/RP_AI_Podcast_Generator"

script_content = """Style: Via API
Speaker 1: Das ist ein Test
Speaker 2: per API Request!"""

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

payload = {
    "event_type": "generate_podcast",
    "client_payload": {
        "script": script_content
    }
}

response = requests.post(
    f"https://api.github.com/repos/{REPO}/dispatches",
    json=payload,
    headers=headers
)

if response.status_code == 204:
    print("✅ Podcast-Workflow gestartet!")
else:
    print(f"❌ Fehler: {response.status_code}")
```

**cURL-Beispiel:**
```bash
curl -X POST \
  https://api.github.com/repos/SRPCode1/RP_AI_Podcast_Generator/dispatches \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -d '{
    "event_type": "generate_podcast",
    "client_payload": {
      "script": "Speaker 1: Hello\nSpeaker 2: World"
    }
  }'
```

### Größenlimits für API

```
📊 GitHub API POST Limit: ~65 KB

Beispiele:
├─ Kurzes Skript (1-2 min)      →  500 bytes    ✅ OK
├─ Normale Episode (5-10 min)   →  5-10 KB      ✅ OK
├─ Lange Episode (30 min)       →  20-30 KB     ✅ OK
├─ Sehr lange (45-60 min)       →  40-50 KB     ✅ OK
└─ Extremfall (100 min)         →  80+ KB       ❌ ZU GROSS

💡 Faustregel: Bleib unter 60 KB um sicher zu sein
```

### Für externe Tools/Integration

**Discord Bot Beispiel:**
```python
@bot.command()
async def podcast(ctx, *, script):
    response = requests.post(
        f"https://api.github.com/repos/{REPO}/dispatches",
        json={
            "event_type": "generate_podcast",
            "client_payload": {"script": script}
        },
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    if response.status_code == 204:
        await ctx.send("🎙️ Podcast wird generiert...")
    else:
        await ctx.send("❌ Fehler beim API-Call")
```

### Vorteile
✅ **Vollständig automatisierbar**  
✅ **Script im POST-Body** - beliebige Länge (bis 65KB)  
✅ **Integration mit anderen Tools möglich**  
✅ **Programmatisch kontrollierbar**  

### Nachteile
❌ **Token nötig** (Classic Token mit repo scope)  
❌ **Größenlimit ~65KB** (aber OK für 60 min Audio)  

---

## 📋 Größenlimit-Details

### Git Push vs API POST
```
┌─────────────────────────┬──────────────┬────────────┐
│ Methode                 │ Limit        │ Empfehlung │
├─────────────────────────┼──────────────┼────────────┤
│ Git Push (script.txt)   │ ∞ (unbegrenzt) │ BEST     │
│ Manual UI               │ ~5000 chars  │ Tests nur  │
│ API POST                │ ~65 KB       │ Gut       │
└─────────────────────────┴──────────────┴────────────┘

Größenvergleich:
┌─────────────────────────────────┬─────────┬────────────┐
│ Audio-Länge                     │ Bytes   │ % API Limit│
├─────────────────────────────────┼─────────┼────────────┤
│ 1 Minute Dialog                 │ ~1 KB   │ 0.002%    │
│ 10 Minuten (Mittelepisode)      │ ~10 KB  │ 0.02%     │
│ 30 Minuten (normale Podcast)    │ ~30 KB  │ 0.05%     │
│ 60 Minuten (lange Podcast)      │ ~60 KB  │ 0.1%      │
│ 100+ Minuten (zu lang)          │ ~100 KB │ 0.15%     │
└─────────────────────────────────┴─────────┴────────────┘

⭐ Für tägliche Episoden: Git Push ist ideal
⭐ Für Automatisierung: API POST ist super
⭐ Beide: 0 Größenlimit-Probleme für normale Podcasts
```

---

## 🎯 Was du JETZT tun kannst

### Sofort (keine Setup nötig)
```powershell
# 1. Erstelle Episode
notepad script.txt

# 2. Schreib Inhalt, speichern, dann:
git add script.txt
git commit -m "Podcast: Meine erste Episode"
git push

# 3. Fertig! Starte die Actions Seite:
Start-Process "https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions"
```

### Für regelmäßige Episoden (Script)
Erstelle `gen_podcast.ps1`:
```powershell
# PowerShell Script zum schnell Podcasts erstellen

param(
    [Parameter(Mandatory=$true)]
    [string]$Title,
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Script
)

$content = $Script -join " "

# Zu script.txt schreiben
$content | Out-File -Encoding UTF8 script.txt

# Pushen
git add script.txt
git commit -m "Podcast: $Title"
git push

Write-Host "✅ Episode gepushed: $Title"
Write-Host "🔗 https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions"
```

**Nutzung:**
```powershell
.\gen_podcast.ps1 -Title "Episode 1" "Speaker 1: Text..." "Speaker 2: Antwort..."
```

---

## 🔔 Notifications bekommen

### GitHub Notifications (automatisch)
```
✅ Wenn Podcast fertig: GitHub Issue wird erstellt
✅ Du bekommst Notification im Bell-Icon (🔔)
✅ Issue hat direkten Download-Link
```

### Optional: Email Notifications
Falls du `.env` SMTP-Secrets hast:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dein@gmail.com
SMTP_PASSWORD=dein-app-password
NOTIFICATION_EMAIL=empfänger@example.com
```

---

## ❓ FAQ

**F: Kann ich mehrere Episoden gleichzeitig starten?**  
A: Ja! Jeder `git push` triggert einen neuen Workflow. Sie laufen parallel.

**F: Wo finde ich die finalen MP3/WAV Dateien?**  
A: GitHub Release unter https://github.com/SRPCode1/RP_AI_Podcast_Generator/releases

**F: Wie lange dauert es?**  
A: ~5-10 Minuten von Push bis fertige Audio

**F: Kann ich die Voices ändern?**  
A: Ja, in `IVSC_Podcast_German_flash.py` Zeile ~20: `voice1_name = "Sulafat"` etc.

**F: Kann ich lokale Dateien hochladen?**  
A: Nur über Git Push. Für API: Script muss im POST-Body sein.

**F: Was wenn der Workflow fehlschlägt?**  
A: Check Actions → Details → Logs. Häufig: API-Quota (dann Flash statt Pro) oder fehlender GEMINI_API_KEY

---

## 🚀 Für Experten: Workflows kombinieren

```powershell
# Tägliche Episoden automatisch via Cron + API
# (Braucht separaten Server oder IFTTT)

# Beispiel: Windows Task Scheduler
$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM
$action = New-ScheduledTaskAction -Script ".\generate_podcast.ps1"
Register-ScheduledTask -TaskName "DailyPodcast" -Trigger $trigger -Action $action
```

---

**Viel Erfolg mit deinen Podcasts! 🎙️**
