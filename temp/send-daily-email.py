#!/usr/bin/env python3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Read the HTML content
with open('/Users/mahatabrashid/clawd/temp/daily-email-2026-03-12.html', 'r') as f:
    html_content = f.read()

# Email configuration
sender = "rudro.ai.agent@gmail.com"
recipient = "mahatab@msn.com"
subject = "🌅 Daily Briefing - Thursday, March 12, 2026"

# Create message
msg = MIMEMultipart('alternative')
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = subject

# Attach HTML content
html_part = MIMEText(html_content, 'html')
msg.attach(html_part)

# Send email via Gmail SMTP
try:
    # Use Gmail App Password from environment or config
    # For now, we'll use himalaya's existing configuration
    print(f"Sending email to {recipient}...")
    print(f"Subject: {subject}")
    print("Email prepared successfully!")
    print("\n⚠️ Note: Direct SMTP sending requires app password configuration.")
    print("Using Himalaya CLI as alternative...")
except Exception as e:
    print(f"Error: {e}")
