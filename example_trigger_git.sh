#!/bin/bash
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
