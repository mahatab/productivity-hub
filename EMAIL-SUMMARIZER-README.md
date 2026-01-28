# 📧 Email Summarizer - AI-Powered Inbox Intelligence

A standalone web application that connects to your Outlook/MSN account and provides intelligent email summaries with job application tracking.

## ✨ Features

- **🔐 Secure OAuth Login** - Direct connection to mahatab@msn.com (no passwords stored)
- **🤖 AI-Powered Categorization** - Automatic email classification
- **🎯 Job Application Tracking** - Dedicated tracking for job-related emails
- **📊 Excel Export** - Export summaries to Excel for offline analysis
- **📈 Smart Categories**:
  - 🎯 Job Applications
  - 🚨 Urgent
  - 👤 Personal
  - 💼 Business
  - 📰 Newsletters
  - 📂 Other

## 🚀 How to Use

### 1. Setup

The app is ready to use! Just open it in a browser:

```bash
# Start local server (if not already running)
python3 -m http.server 8080

# Then open in browser:
http://localhost:8080/email-summarizer.html
```

### 2. Connect to Outlook

1. Click **"Connect to Outlook"**
2. Sign in with **mahatab@msn.com**
3. Approve permissions:
   - ✅ Read your mail
   - ✅ Read your basic profile

### 3. Analyze Emails

1. Select **Time Range** (last 24h, 3 days, 7 days, or 30 days)
2. Select **Max Emails** to analyze (25, 50, 100, or 200)
3. Click **"🔍 Analyze Emails"**
4. Wait for AI to categorize and summarize

### 4. Review Results

- **Stats Dashboard** - Quick overview of email categories
- **Expandable Categories** - Click to expand/collapse each category
- **Email Details** - Subject, sender, date, and preview for each email

### 5. Export to Excel

Click **"📊 Export to Excel"** to download a spreadsheet with:
- All emails from the summary
- Organized by category
- Includes: Subject, From, Date, Preview, Read status

## 🔒 Security & Privacy

- **OAuth 2.0** - Industry-standard secure authentication
- **Read-Only** - App only reads emails, never modifies or deletes
- **No Password Storage** - Authentication handled by Microsoft
- **Local Processing** - All categorization happens in your browser
- **No Server** - Direct browser-to-Microsoft connection

## 📊 Categories Explained

### 🎯 Job Applications
Detects emails containing:
- Keywords: job, application, interview, offer, career, position, recruiter, hiring
- From: career@, recruiting@, talent@, hr@
- **Use Case:** Track all job application responses in one place

### 🚨 Urgent
Detects emails with:
- Keywords: urgent, asap, important, action required
- **Use Case:** Never miss time-sensitive emails

### 👤 Personal
Emails from:
- Gmail, Yahoo, Hotmail, Outlook personal accounts
- **Use Case:** Separate personal from business communications

### 💼 Business
Professional emails from:
- Company domains (.com, .org, .net)
- **Use Case:** Business correspondence tracking

### 📰 Newsletters
Marketing and notifications:
- Contains: unsubscribe, newsletter
- From: noreply@, no-reply@, notifications@
- **Use Case:** Bulk manage promotional emails

### 📂 Other
Everything else that doesn't fit above categories

## 🎯 Job Application Tracking Features

The Job Applications category includes smart detection for:

**Application Confirmations:**
- "Thank you for applying"
- "Application received"
- "Your application to [Company]"

**Interview Invitations:**
- "Interview scheduled"
- "Next steps"
- "Let's talk"

**Offer/Rejection:**
- "We're pleased to offer"
- "Pursuing other candidates"
- "Application status update"

**Recruiter Outreach:**
- From recruiting agencies
- From company talent teams
- InMail and LinkedIn messages (if forwarded)

## 📈 Export Format

Excel export includes these columns:
- **Category** - Which category the email belongs to
- **Subject** - Email subject line
- **From** - Sender name
- **From Email** - Sender email address
- **Date** - When email was received
- **Preview** - First few lines of email body
- **Read** - Whether email has been read (Yes/No)

## 🔧 Customization

### Change Azure AD App Settings

The app uses the same OAuth client as Productivity Hub. Make sure redirect URIs include:
- `http://localhost:8080/email-summarizer.html`

### Modify Categories

Edit the `categorizeEmails()` function in `email-summarizer.html` to:
- Add new categories
- Change detection keywords
- Adjust priority order

### Adjust Time Ranges

Modify the `<select id="time-range">` options to add custom date ranges.

## 🛠️ Troubleshooting

### "Microsoft Authentication is not available"
- Make sure you have internet connection
- MSAL library failed to load - refresh page

### "Failed to connect" error
- Check you're using correct Microsoft account
- Verify you approved all permissions
- Try disconnecting and reconnecting

### "Failed to fetch emails" error
- Token may have expired - disconnect and reconnect
- Check Azure AD app permissions include `Mail.Read`

### No emails showing up
- Increase time range (try "Last 30 days")
- Increase max emails (try 200)
- Check the account has emails in the selected period

## 💡 Tips & Best Practices

1. **Daily Review** - Run analyzer each morning for inbox summary
2. **Job Hunting** - Check "Job Applications" category daily when actively applying
3. **Inbox Zero** - Use Excel export to batch-process emails
4. **Archive Strategy** - Export monthly summaries for record-keeping
5. **Time Management** - Set specific times to check email categories

## 🔄 Integration with Other Tools

### Works alongside:
- **Productivity Hub** - Same OAuth, compatible accounts
- **Job Email Scanner** - Complements automated job tracking
- **himalaya CLI** - Can compare with CLI-based email access

### Future Enhancements:
- Mark emails as read/unread from the app
- Move emails to folders
- Create tasks from emails
- Sync with productivity-hub.html job dashboard

## 📝 Notes

- First load may take a few seconds while fetching emails
- Larger email counts (200+) will take longer to analyze
- Categories are AI-estimated; you can always view all emails
- Export filename includes current date for easy organization

---

**Built by Rudro 🦸🏻‍♂️ | Your AI Assistant**

**Created:** January 27, 2026  
**For:** mahatab@msn.com inbox management & job tracking
