# 💼 Job Application Tracker Guide

**Created:** 2026-01-27  
**Location:** `/Users/mahatabrashid/clawd/job-tracker.csv`

---

## 📊 Spreadsheet Columns

| Column | Description | Example |
|--------|-------------|---------|
| **Job ID** | Unique identifier | JOB-001, JOB-002, etc. |
| **Application Date** | When you applied | 2026-01-27 |
| **Company Name** | Company name | Microsoft, Amazon, etc. |
| **Job Title** | Position title | Senior TPM, Support Lead |
| **Job Type** | Category | TPM, Support Leadership, Escalation Engineer, AI |
| **Location** | Job location | Seattle, WA / Remote |
| **Salary Range** | Expected salary | $150k-180k |
| **Job URL** | Link to posting | https://... |
| **Status** | Current status | Applied, Interview, Offer, Rejected, Withdrawn |
| **Contact Person** | Recruiter/Hiring Manager | John Smith |
| **Contact Email** | Their email | recruiter@company.com |
| **Interview Date** | Scheduled interview | 2026-02-05 |
| **Follow-up Date** | When to follow up | 2026-02-10 |
| **Notes** | Additional info | Referred by Jane, Benefits good, etc. |
| **Source** | Where you found it | LinkedIn, Indeed, Referral |

---

## 🎯 Status Values

- **Applied** - Application submitted
- **Under Review** - Company reviewing
- **Phone Screen** - Initial call scheduled
- **Interview** - In interview process
- **Final Round** - Last interview stage
- **Offer** - Offer received
- **Accepted** - Offer accepted
- **Rejected** - Not selected
- **Withdrawn** - You withdrew
- **Ghosted** - No response

---

## 📝 How I Can Help

### 1. Add New Applications
**You send via email:**
```
Subject: job: Applied to Microsoft - Senior TPM

Job ID: JOB-042
Company: Microsoft
Title: Senior Technical Program Manager
Location: Redmond, WA
Applied: 2026-01-27
Salary: $160k-190k
URL: https://careers.microsoft.com/...
Source: LinkedIn
Notes: Referred by Sarah from team
```

**I automatically:**
- Parse the email
- Add to spreadsheet
- Track in system

### 2. Update Status
Tell me: "Update JOB-042: Interview scheduled for Feb 5"

### 3. Generate Reports
- "Show me all active applications"
- "Which companies haven't responded?"
- "What's my interview schedule this week?"

### 4. Follow-up Reminders
- I'll remind you to follow up after 1-2 weeks
- Track interview dates
- Alert about upcoming deadlines

### 5. Analytics
- Success rate by job type
- Average response time by company
- Salary range analysis

---

## 🚀 Quick Commands

**Add job manually:**
```
Task: Add job - [Company] [Title]
Job ID: JOB-XXX
Details: [paste job info]
```

**Update existing:**
```
Update JOB-042: Status = Interview, Interview Date = 2026-02-05
```

**View active:**
```
Show my active job applications
```

**Generate report:**
```
Job application summary
```

---

## 📧 Email Integration

When you forward job-related emails to rudro.ai.agent@gmail.com with subject starting with "job:", I will automatically:

1. Extract relevant information
2. Generate Job ID
3. Add to tracker
4. Create task file in `/jobs/` folder
5. Confirm via Telegram

---

## 📊 Opening the Spreadsheet

**CSV format (current):**
```bash
open /Users/mahatabrashid/clawd/job-tracker.csv
```
Opens in Excel, Numbers, or Google Sheets

**To convert to Excel manually:**
1. Open CSV in Excel
2. Save As → .xlsx format

**Or I can convert it:**
Just say "Convert job tracker to Excel"

---

## 🔄 Sync & Backup

- CSV auto-saves when updated
- Backed up in git (if you commit)
- Can export to Google Sheets if needed

---

## 💡 Tips

1. **Update regularly** - Keep status current
2. **Add notes** - Any detail might be useful later
3. **Track everything** - Even rejections teach patterns
4. **Follow up** - Set reminder dates
5. **Use Job ID** - Makes updates easier

---

*Your job search, organized. Let's land you that perfect role! 🎯*

**Need help?** Just ask Rudro!
