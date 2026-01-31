#!/bin/bash

# Send Beautiful Daily Briefing Email
# Uses HTML template for rich formatting

TEMPLATE_PATH="$HOME/clawd/scripts/email-templates/daily-briefing.html"
TO_EMAIL="mahatab@msn.com"
SUBJECT="Daily Briefing - $(date '+%B %d, %Y')"

# Read template
TEMPLATE=$(cat "$TEMPLATE_PATH")

# Replace placeholders with actual content
# This would be called by Rudro with actual data
DATE=$(date '+%A, %B %d, %Y')

BRIEFING="${TEMPLATE//\{\{DATE\}\}/$DATE}"

# Create MML format for himalaya (supports HTML)
cat << EOF | himalaya template send
From: rudro.ai.agent@gmail.com
To: $TO_EMAIL
Subject: $SUBJECT
Content-Type: text/html; charset=utf-8

$BRIEFING
EOF

echo "✅ Beautiful briefing sent to $TO_EMAIL"
