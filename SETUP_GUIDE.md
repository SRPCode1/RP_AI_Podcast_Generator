# 🎯 Quick Start Guide: GitHub Actions Setup

## Required GitHub Secrets

Before the first run, configure these secrets in GitHub:

### Navigate to Secrets:
1. Go to your repository: https://github.com/SRPCode1/RP_AI_Podcast_Generator
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add These Secrets:

#### 1. GEMINI_API_KEY (Required)
- **Name**: `GEMINI_API_KEY`
- **Value**: Your Google Gemini API key (starts with `AIzaSy...`)
- **Get it from**: https://aistudio.google.com/app/apikey

#### 2. NOTIFICATION_EMAIL (Required)
- **Name**: `NOTIFICATION_EMAIL`
- **Value**: Your email address (e.g., `your-email@example.com`)

#### 3. SMTP Configuration (Required for Email)

**Option A: Gmail (Recommended)**
- **SMTP_HOST**: `smtp.gmail.com`
- **SMTP_PORT**: `587`
- **SMTP_USER**: Your Gmail address
- **SMTP_PASSWORD**: Gmail App Password (NOT your regular password!)
  - Generate at: https://myaccount.google.com/apppasswords
  - Requires 2FA enabled

**Option B: Outlook/Microsoft**
- **SMTP_HOST**: `smtp-mail.outlook.com`
- **SMTP_PORT**: `587`
- **SMTP_USER**: Your Outlook email
- **SMTP_PASSWORD**: Your Outlook password

**Option C: Custom SMTP**
- **SMTP_HOST**: Your SMTP server
- **SMTP_PORT**: Usually 587 or 465
- **SMTP_USER**: Your email username
- **SMTP_PASSWORD**: Your email password

---

## 🚀 How to Use

### Method 1: Manual Trigger (Recommended for Testing)

1. Go to **Actions** tab
2. Select "🎙️ Generate Podcast" workflow
3. Click **Run workflow**
4. Paste your script in the text field
5. (Optional) Enter email for notification
6. Click **Run workflow**
7. Wait for email with download link (~10-15 minutes)

### Method 2: Git Push (Automated)

```bash
# Edit your script
notepad script.txt

# Commit and push
git add script.txt
git commit -m "New podcast: My Topic"
git push

# Workflow triggers automatically
# Check email for download link
```

### Method 3: API Trigger (For External Systems)

```bash
curl -X POST \
  https://api.github.com/repos/SRPCode1/RP_AI_Podcast_Generator/dispatches \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{
    "event_type": "generate_podcast",
    "client_payload": {
      "script": "Speaker 1: Hello...",
      "email": "your-email@example.com"
    }
  }'
```

---

## 📧 Email Notification Example

After successful generation, you'll receive:

**Subject**: ✅ Podcast Generated Successfully - Episode 1

**Contains**:
- ✅ Direct download link
- 📊 Duration, file size, chunks count
- 🔗 Link to GitHub Release
- 🔗 Link to workflow run details

**Valid for**: 90 days (GitHub Release)

---

## 🧪 Test Your Setup

### Quick Test:
1. Go to Actions → Run workflow
2. Paste this minimal script:

```
Style: Test

Speaker 1: Hello, this is a test.

Speaker 2: Yes, this is working!

Speaker 1: Great!
```

3. Run and check email in ~5 minutes

---

## 🔧 Troubleshooting

### Email not received?
1. Check spam/junk folder
2. Verify SMTP secrets are correct
3. For Gmail: Make sure you used App Password, not regular password
4. Check workflow logs in Actions tab

### Workflow failed?
1. Check Actions tab for error logs
2. Most common: Invalid `GEMINI_API_KEY`
3. Verify all secrets are set correctly

### Quota exceeded?
- Free tier: 50 requests/day
- Wait for reset (midnight UTC)
- Or enable billing (very cheap: ~$0.002 per podcast)

---

## 📊 Monitoring

### View Workflow Status:
- **Actions tab**: Real-time progress
- **Releases page**: All generated podcasts
- **Email**: Summary after completion

### Download Options:
1. **GitHub Release**: Direct download (90 days)
2. **Artifacts**: Zip download (30 days)
3. **Email link**: Points to Release

---

## 💰 Cost Estimate

### GitHub Actions (Free Tier)
- ✅ 2,000 minutes/month
- ✅ ~15 min per podcast
- 📊 Capacity: ~130 podcasts/month

### Gemini API
- ✅ 50 free requests/day
- 💰 With billing: $0.002 per podcast
- 📊 Monthly (100 podcasts): ~$0.20

**Total**: Essentially free for moderate use! 🎉

---

## 🎯 Next Steps

1. ✅ Configure GitHub Secrets (above)
2. ✅ Run test workflow
3. ✅ Check email
4. ✅ Download and verify podcast
5. 🚀 Start generating production podcasts!

---

## 📞 Support

If you encounter issues:
1. Check this guide
2. Review workflow logs in Actions tab
3. Run `python diagnose_api.py` locally to test API key
4. Check GitHub Actions documentation

---

**Repository**: https://github.com/SRPCode1/RP_AI_Podcast_Generator
**Last Updated**: November 2025
