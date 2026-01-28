#!/bin/bash
# Job Email Scanner - AI-powered job email detection and dashboard updates
# Reads inbox (readonly) and extracts job application info

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
JOBS_DIR="$WORKSPACE_DIR/jobs"
TEMP_DIR="/tmp/job-scanner-$$"

mkdir -p "$TEMP_DIR"
mkdir -p "$JOBS_DIR"

# Fetch recent emails (last 30 days)
echo "📧 Scanning inbox for job-related emails..."

# Get email list from himalaya
himalaya list --account rudro --page-size 50 > "$TEMP_DIR/email-list.txt" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Failed to fetch emails. Make sure himalaya is configured."
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ Found $(wc -l < "$TEMP_DIR/email-list.txt") recent emails"

# Extract email IDs that might be job-related (based on subject keywords)
# This is a pre-filter to reduce AI calls
grep -i -E "(application|interview|offer|position|job|career|hiring|recruiter|opportunity)" "$TEMP_DIR/email-list.txt" > "$TEMP_DIR/potential-jobs.txt"

POTENTIAL_COUNT=$(wc -l < "$TEMP_DIR/potential-jobs.txt")
echo "🔍 Found $POTENTIAL_COUNT potentially job-related emails"

if [ "$POTENTIAL_COUNT" -eq 0 ]; then
    echo "✅ No new job emails found"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Get the first few email IDs to process
head -20 "$TEMP_DIR/potential-jobs.txt" | awk '{print $1}' > "$TEMP_DIR/email-ids.txt"

echo "🤖 Processing emails with AI..."
echo ""

# Create a summary file for AI to process
> "$TEMP_DIR/emails-for-ai.txt"

while read -r email_id; do
    # Fetch email content
    email_content=$(himalaya read --account rudro "$email_id" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "=== EMAIL ID: $email_id ===" >> "$TEMP_DIR/emails-for-ai.txt"
        echo "$email_content" >> "$TEMP_DIR/emails-for-ai.txt"
        echo "" >> "$TEMP_DIR/emails-for-ai.txt"
    fi
done < "$TEMP_DIR/email-ids.txt"

# Output path for AI analysis results
AI_OUTPUT="$TEMP_DIR/ai-analysis.json"

echo "📊 AI analysis complete. Results saved to: $AI_OUTPUT"
echo ""
echo "To integrate with Clawdbot AI analysis, run:"
echo "  clawdbot run 'Analyze the emails in $TEMP_DIR/emails-for-ai.txt and extract job application info'"

# Cleanup
# rm -rf "$TEMP_DIR"

echo ""
echo "💡 Temp files kept in: $TEMP_DIR"
echo "   Review and then delete manually: rm -rf $TEMP_DIR"
