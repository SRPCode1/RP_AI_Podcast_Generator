# GitHub Token Setup Guide

## 1. Create GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: `Podcast Generator API`
4. Select scopes:
   - ✅ **repo** (Full control of private repositories)
     - This includes: repo:status, repo_deployment, public_repo, repo:invite, security_events
5. Click **"Generate token"**
6. **COPY THE TOKEN** (you won't see it again!)

## 2. Set Token in PowerShell

```powershell
# Set for current session
$env:GITHUB_TOKEN = "ghp_your_token_here"

# Verify it's set
echo $env:GITHUB_TOKEN

# Test the trigger
python test_live_trigger.py
```

## 3. Alternative: Save in .env (for repeated use)

**IMPORTANT: Never commit this to git!**

```bash
# Add to .env file (already in .gitignore)
echo GITHUB_TOKEN=ghp_your_token_here >> .env
```

Then in Python:
```python
from dotenv import load_dotenv
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
```

## 4. Test the API Trigger

```powershell
# Make sure token is set
$env:GITHUB_TOKEN = "ghp_your_token_here"

# Run the live test
python test_live_trigger.py
```

## Expected Output:

```
🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️
LIVE PODCAST GENERATION TEST
🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️🎙️

📤 Sending POST request to GitHub...

✅ SUCCESS! Podcast generation triggered!

📋 What happens next:
1. GitHub Actions workflow starts (~10 seconds)
2. Python environment setup (~30 seconds)
3. Podcast generation (~5-10 minutes)
4. GitHub Issue created with download link
5. GitHub Release created with podcast file

🔗 Monitor progress:
   Actions: https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions
   Issues:  https://github.com/SRPCode1/RP_AI_Podcast_Generator/issues
```

## Troubleshooting

### Error: 401 Authentication Failed
- Token is invalid or expired
- Generate a new token

### Error: 403 Permission Denied
- Token doesn't have 'repo' scope
- Re-create token with correct scopes

### Error: 404 Not Found
- Repository doesn't exist or you don't have access
- Check repository name

## Security Notes

- ⚠️ **Never share your token**
- ⚠️ **Never commit token to git**
- ⚠️ **.env is in .gitignore** - don't remove it!
- ✅ Token gives full access to your repos
- ✅ You can revoke it anytime at: https://github.com/settings/tokens
