#!/bin/bash
# Complete job email scanner - fetches emails and updates dashboard
# Usage: ./update-jobs-from-email.sh

echo "🚀 Job Email Scanner"
echo "===================="
echo ""

# Step 1: Scan emails
node "$(dirname "$0")/scan-job-emails.js"

if [ $? -ne 0 ]; then
    echo "❌ Email scan failed"
    exit 1
fi

echo ""
echo "✅ Email scan complete!"
echo ""
echo "📧 To analyze and update job dashboard:"
echo "   Ask Rudro to analyze /tmp/job-emails.txt and update the job dashboard"
echo ""
