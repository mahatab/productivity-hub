# 📧 Automated Job Email Scanner

An AI-powered system that scans your inbox for job-related emails and automatically updates your job dashboard.

## ✨ Features

- **Read-only inbox access** - Scans without modifying emails
- **AI-powered detection** - Identifies job emails using intelligent filtering
- **Automatic extraction** - Extracts company, position, status, and dates
- **Dashboard updates** - Creates job files and updates tracking dashboard
- **No manual work** - Fully automated scanning and updates

## 🚀 How to Use

### Manual Scan

Run the scanner anytime to check for new job emails:

```bash
cd /Users/mahatabrashid/clawd
./scripts/update-jobs-from-email.sh
```

Or directly with Node.js:

```bash
node scripts/scan-job-emails.js
```

### What It Does

1. **Connects to your inbox** using `himalaya` (rudro.ai.agent@gmail.com)
2. **Scans recent emails** (last 100 emails) for job-related keywords
3. **Fetches full content** of potential job emails
4. **AI analyzes** each email to extract:
   - Company name
   - Position/role
   - Application status (applied/interview/offer/rejected)
   - Application date
5. **Creates job files** in `jobs/` directory
6. **Updates** `JOBS-DASHBOARD.md` with new entries

## 📊 Results

After the scan completes, Rudro will:
- ✅ Add NEW job applications to the dashboard
- 📝 Create detailed markdown files for each job
- 🔄 Update existing job statuses (e.g., applied → rejected)
- 📈 Update summary statistics

## 🤖 Automation (Coming Soon)

You can set up automatic scanning:

### Option 1: Cron Job (Daily at 9 AM)

```bash
crontab -e
# Add this line:
0 9 * * * cd /Users/mahatabrashid/clawd && ./scripts/update-jobs-from-email.sh
```

### Option 2: Clawdbot Heartbeat

Add to `HEARTBEAT.md`:

```markdown
## 📧 Job Email Monitoring
- Run job email scanner once daily
- Check for: new applications, status updates, interviews, rejections
- Update JOBS-DASHBOARD.md automatically
```

## 📝 Email Format

For best results, forward job emails to **rudro.ai.agent@gmail.com** with subject starting with:
- `job:` or `JOB:` - Guaranteed detection
- Or the system will auto-detect based on content

Example forwarded email subjects:
- `job: Application Confirmed - Google TPM`
- `JOB: Interview Scheduled - Microsoft`

## 🔍 Detection Keywords

The scanner looks for emails containing:
- application, applied, applying
- interview, interviewing
- offer, offered
- position, role, job
- career, careers
- hiring, recruiter, recruiting
- opportunity
- "thanks for applying"
- "application received"
- "next steps"

## 📂 Files Created

Each job creates:
- `jobs/YYYY-MM-DD-company-role.md` - Detailed job tracking file
- Updates to `JOBS-DASHBOARD.md` - Summary dashboard

## ⚙️ Technical Details

### Dependencies
- **himalaya** - Email CLI client (already configured)
- **Node.js** - Script runtime
- **Rudro AI** - Email content analysis

### Security
- **Read-only** - Never deletes or modifies emails
- **Local processing** - Email content stays on your machine
- **No external APIs** - Uses local himalaya client

## 🛠️ Troubleshooting

### "Failed to fetch emails"
- Check himalaya config: `himalaya account list`
- Test connection: `himalaya envelope list --account rudro --page-size 5`

### "No job emails found"
- Verify emails exist: Check inbox for job-related subjects
- Expand scan range: Edit `scan-job-emails.js` and increase `page-size`

### "AI analysis not working"
- Make sure Rudro is active
- Check temp file: `cat /tmp/job-emails.txt`

## 📊 Latest Scan Results

**Last scan:** 2026-01-28  
**Emails scanned:** 13  
**Job emails found:** 7  
**New jobs added:** 1 (MathWorks - Principal Program Manager)  
**Updated jobs:** 0  

---

**Built by Rudro 🦸🏻‍♂️ | Your AI Assistant**
