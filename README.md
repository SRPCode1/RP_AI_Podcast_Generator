# 🎙️ RP AI Podcast Generator

Automated podcast generation service using Google Gemini TTS API. Converts text scripts into natural-sounding multi-speaker audio podcasts with German language support.

## 📋 Project Purpose

This project automates the creation of professional podcast episodes from text scripts. It uses Google's Gemini 2.5 Flash TTS model with multi-speaker voice synthesis (Sulafat & Sadachbia voices) to generate engaging conversational audio content.

**Current State**: Standalone Python scripts  
**Future Vision**: Fully automated microservice with GitHub Actions

---

## 🏗️ Architecture

### Current Architecture (v1.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                     LOCAL EXECUTION                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  script.txt                                                       │
│      │                                                            │
│      ▼                                                            │
│  ┌──────────────────────────────────────┐                       │
│  │  IVSC_Podcast_German_flash.py        │                       │
│  │  - Load script                        │                       │
│  │  - Chunk text (1500 chars)           │                       │
│  │  - Generate TTS per chunk            │                       │
│  └──────────────┬───────────────────────┘                       │
│                 │                                                 │
│                 ▼                                                 │
│  ┌──────────────────────────────────────┐                       │
│  │  Google Gemini API                   │                       │
│  │  - Model: gemini-2.5-flash-tts      │                       │
│  │  - Speaker 1: Sulafat                │                       │
│  │  - Speaker 2: Sadachbia              │                       │
│  └──────────────┬───────────────────────┘                       │
│                 │                                                 │
│                 ▼                                                 │
│  Podcast_Audio_0.wav                                             │
│  Podcast_Audio_1.wav                                             │
│  Podcast_Audio_2.wav                                             │
│  ...                                                              │
│  Podcast_Audio_9.wav                                             │
│                 │                                                 │
│                 ▼                                                 │
│  ┌──────────────────────────────────────┐                       │
│  │  WAV Concatenation                   │                       │
│  │  - Merge all chunks                  │                       │
│  │  - Validate audio params             │                       │
│  └──────────────┬───────────────────────┘                       │
│                 │                                                 │
│                 ▼                                                 │
│  Podcast_Audio_full.wav ✅                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Planned Microservice Architecture (v2.0)

```
┌────────────────────────────────────────────────────────────────────────┐
│                          GITHUB ACTIONS MICROSERVICE                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  TRIGGER OPTIONS:                                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐       │
│  │ 1. Manual UI    │  │ 2. Git Push     │  │ 3. API Webhook   │       │
│  │    Dispatch     │  │    (script.txt) │  │    (External)    │       │
│  └────────┬────────┘  └────────┬────────┘  └────────┬─────────┘       │
│           │                    │                     │                  │
│           └────────────────────┼─────────────────────┘                  │
│                                ▼                                         │
│                  ┌──────────────────────────────┐                       │
│                  │   GitHub Actions Workflow    │                       │
│                  │   - Validate script          │                       │
│                  │   - Set up Python 3.11       │                       │
│                  │   - Install dependencies     │                       │
│                  └──────────────┬───────────────┘                       │
│                                 │                                        │
│                                 ▼                                        │
│                  ┌──────────────────────────────┐                       │
│                  │   Podcast Generation         │                       │
│                  │   - Load script.txt          │                       │
│                  │   - Call Gemini API          │                       │
│                  │   - Generate chunks          │                       │
│                  │   - Concatenate audio        │                       │
│                  └──────────────┬───────────────┘                       │
│                                 │                                        │
│                                 ▼                                        │
│                  ┌──────────────────────────────┐                       │
│                  │   Post-Processing            │                       │
│                  │   - Upload to Artifacts      │                       │
│                  │   - Create GitHub Release    │                       │
│                  │   - Generate download link   │                       │
│                  └──────────────┬───────────────┘                       │
│                                 │                                        │
│                                 ▼                                        │
│                  ┌──────────────────────────────┐                       │
│                  │   Notification               │                       │
│                  │   - Send email with link     │                       │
│                  │   - Clean temp files         │                       │
│                  └──────────────────────────────┘                       │
│                                 │                                        │
│                                 ▼                                        │
│                         📧 Email with 🔗                                │
│                    Download: Podcast_Audio_full.wav                     │
│                                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Usage

### Current Usage (Local)

```bash
# 1. Set up environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt

# 2. Configure API key
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Prepare your script
# Edit script.txt with your podcast content

# 4. Generate podcast
python IVSC_Podcast_German_flash.py

# 5. Find output
# Podcast_Audio_full.wav (complete podcast)
# Podcast_Audio_*.wav (individual chunks)
```

### Planned Usage (Microservice)

#### Method 1: GitHub Web UI
1. Go to **Actions** tab in GitHub
2. Select "Generate Podcast" workflow
3. Click "Run workflow"
4. Paste your script content
5. Wait for email notification with download link

#### Method 2: Git Push
```bash
# Edit script.txt with your content
git add script.txt
git commit -m "New podcast: [Topic Name]"
git push

# Workflow triggers automatically
# Receive email with download link when complete
```

#### Method 3: API Trigger (External Systems)
```bash
curl -X POST https://api.github.com/repos/SRPCode1/RP_AI_Podcast_Generator/dispatches \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{
    "event_type": "generate_podcast",
    "client_payload": {
      "script": "Speaker 1: Hello...",
      "podcast_id": "episode-001",
      "email": "your-email@example.com"
    }
  }'
```

#### Method 4: Python Client
```python
import requests

def trigger_podcast(script_content, email):
    response = requests.post(
        "https://api.github.com/repos/SRPCode1/RP_AI_Podcast_Generator/dispatches",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        json={
            "event_type": "generate_podcast",
            "client_payload": {
                "script": script_content,
                "podcast_id": f"podcast-{datetime.now().isoformat()}",
                "email": email
            }
        }
    )
    return response.status_code == 204

with open("script.txt") as f:
    trigger_podcast(f.read(), "you@example.com")
```

---

## 🔧 Configuration

### Required Secrets (GitHub)
Configure these in: **Settings → Secrets → Actions**

| Secret Name | Description | Required |
|------------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |
| `NOTIFICATION_EMAIL` | Your email for notifications | ✅ Yes |
| `SMTP_HOST` | Email server (e.g., smtp.gmail.com) | ✅ Yes |
| `SMTP_PORT` | Email port (usually 587) | ✅ Yes |
| `SMTP_USER` | Email account username | ✅ Yes |
| `SMTP_PASSWORD` | Email account password/app password | ✅ Yes |

### Script Format

Your `script.txt` should follow this format:

```
Style: [Description of tone and style]

Speakers: [Speaker characteristics]

Tonality: [Desired tonality]

Speaker 1: [First speaker's dialogue]

Speaker 2: [Second speaker's dialogue]

Speaker 1: [Continue conversation...]
```

**Example:**
```
Style: Factual, competent, and future-oriented.

Speakers: Calm, level-headed, and trustworthy tone. Experts preparing a complex topic for colleagues.

Tonality: Not promotional, but competent and radiating a positive yet realistic vision for the future.

Speaker 1: You can barely open a professional journal these days without stumbling over Artificial Intelligence.

Speaker 2: That is exactly the bridge from theory to practice that we are building in our HypZert Perspective Paper.
```

---

## 🧹 Repository Cleanup Strategy

The workflow automatically cleans up after each run:

### During Generation
```yaml
- Chunk files: Podcast_Audio_0.wav to Podcast_Audio_N.wav (temporary)
- Concatenation lists: ff_concat_list.txt (temporary)
```

### After Completion
1. **Upload final file** to GitHub Artifacts (30-day retention)
2. **Create GitHub Release** with final podcast file
3. **Delete temporary files**:
   - All `Podcast_Audio_*.wav` chunks
   - Concatenation helper files
   - Python cache files
4. **Send email** with download link
5. **Clean workspace** for next run

### Retention Policy
- **Artifacts**: 30 days (configurable)
- **Releases**: Permanent (tagged by run number)
- **Logs**: 90 days (GitHub default)

### Manual Cleanup
```bash
# Local cleanup
git clean -fdx
rm -rf venv/
rm -rf __pycache__/
rm Podcast_Audio_*.wav
```

---

## 📧 Email Notification

After successful generation, you receive:

**Subject:** `✅ Podcast Generated Successfully - Run #123`

**Body:**
```
Your podcast has been generated successfully!

📊 Details:
- Podcast ID: episode-001
- Duration: ~22 minutes
- Chunks: 10
- Total Size: 65.8 MB

🔗 Download Links:
- Full Podcast: https://github.com/SRPCode1/RP_AI_Podcast_Generator/releases/download/podcast-123/Podcast_Audio_full.wav
- Artifacts (30 days): https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions/runs/123

The download link is valid for 90 days.

---
Generated by RP AI Podcast Generator
```

---

## 📊 Cost Analysis

### Free Tier (GitHub Actions)
- ✅ 2,000 minutes/month free for public repos
- ✅ 500 MB storage for artifacts
- ⚠️ ~10-15 minutes per podcast generation
- **Capacity**: ~130-200 podcasts/month free

### API Costs (Google Gemini)
- **Flash Model**: $0.00015 per 1,000 characters
- **Average podcast** (12,000 chars): ~$0.002 (0.2 cents)
- **100 podcasts/month**: ~$0.20

**Total Monthly Cost**: ~$0.20 (essentially free) 💰

---

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **TTS Engine** | Google Gemini 2.5 Flash TTS | Text-to-speech generation |
| **Voices** | Sulafat & Sadachbia | Multi-speaker synthesis |
| **Language** | Python 3.11 | Core logic |
| **Audio Processing** | WAV manipulation | Chunking & concatenation |
| **CI/CD** | GitHub Actions | Automation & deployment |
| **Storage** | GitHub Artifacts + Releases | File distribution |
| **Notification** | SMTP | Email delivery |

---

## 📁 Project Structure

```
RP_AI_Podcast_Generator/
│
├── .github/
│   └── workflows/
│       └── generate_podcast.yml          # Main workflow (planned)
│
├── venv/                                  # Virtual environment (not in git)
│
├── IVSC_Podcast_German_flash.py          # Main generator (Flash model)
├── IVSC_Podcast_German.py                # Alternative (Pro model)
├── generate_missing_chunks.py            # Regenerate specific chunks
├── concat_partial.py                     # Manual concatenation helper
├── diagnose_api.py                       # API diagnostics
├── check_wav_headers.py                  # Audio validation
├── resample_chunks.py                    # Audio resampling utility
├── local_tts_fallback.py                 # Offline TTS backup
│
├── script.txt                            # Input script
├── .env                                  # API keys (not in git)
├── .gitignore                            # Git ignore rules
├── requirements.txt                      # Python dependencies
└── README.md                             # This file
```

---

## 🔮 Roadmap

### Phase 1: Current (v1.0) ✅
- [x] Local script execution
- [x] Multi-speaker TTS
- [x] Chunking & concatenation
- [x] Error handling & retries

### Phase 2: Microservice (v2.0) 🚧
- [ ] GitHub Actions workflow
- [ ] Automated triggers
- [ ] Email notifications
- [ ] Artifact management
- [ ] Auto-cleanup

### Phase 3: Enhancement (v3.0) 📋
- [ ] Multiple voice profiles
- [ ] Custom voice training
- [ ] Background music mixing
- [ ] Multiple output formats (MP3, OGG)
- [ ] Parallel chunk generation
- [ ] Web dashboard

### Phase 4: Scale (v4.0) 🎯
- [ ] Batch processing
- [ ] Podcast RSS feed generation
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Cloud storage integration (S3/GCS)

---

## 🤝 Contributing

This is a private project for automated podcast generation. For questions or suggestions, contact the repository owner.

---

## 📄 License

Private project - All rights reserved.

---

## 🆘 Troubleshooting

### Issue: Quota exceeded (429 error)
**Solution**: Wait until quota resets (midnight UTC) or enable billing in Google AI Studio

### Issue: Audio chunks have different sample rates
**Solution**: Run `python resample_chunks.py` to normalize to 24000 Hz

### Issue: Missing chunks in final podcast
**Solution**: Run `python generate_missing_chunks.py` to regenerate

### Issue: Email not received
**Solution**: Check spam folder, verify SMTP credentials in GitHub Secrets

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Run `python diagnose_api.py` to validate configuration
3. Check GitHub Actions logs for detailed error messages
4. Contact repository owner

---

**Last Updated**: November 2025  
**Status**: Active Development 🚀
