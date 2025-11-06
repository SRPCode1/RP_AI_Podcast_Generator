#!/bin/bash
# Example: Trigger podcast generation via curl
# Usage: GITHUB_TOKEN=your_token ./example_trigger_curl.sh

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN not set"
    echo "Usage: GITHUB_TOKEN=your_token ./example_trigger_curl.sh"
    exit 1
fi

SCRIPT_CONTENT=$(cat script.txt)

curl -X POST \
  https://api.github.com/repos/SRPCode1/RP_AI_Podcast_Generator/dispatches \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d "{
    \"event_type\": \"generate_podcast\",
    \"client_payload\": {
      \"script\": \"$SCRIPT_CONTENT\",
      \"email\": \"your-email@example.com\"
    }
  }"

echo "✅ Request sent!"
echo "Check: https://github.com/SRPCode1/RP_AI_Podcast_Generator/actions"
