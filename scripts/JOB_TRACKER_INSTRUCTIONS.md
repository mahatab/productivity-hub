# Job Application Tracker Instructions
**OFFICIAL PROMPT - DO NOT DEVIATE**

## Task: MSN and Gmail Job Application Tracker with Google Sheets

### Step 1 - Setup:
Check if you have access to Google Sheets. If not, request authorization. Once authorized, create a new Google Sheet called "Mahatab - Job Applications Tracker" and set up a tab called "Applications" with the following columns:

| Column | Description |
|--------|-------------|
| Job ID | The job requisition or posting ID extracted from the email or application link |
| Company Name | The company I applied to |
| Position Title | The role I applied for |
| Date Applied | Date of the application confirmation email (MM/DD/YYYY) |
| Source/Platform | Where I applied (LinkedIn, company career site, etc.) |
| Email Account | Which email received the confirmation (mahatab@gmail.com or mahatab@msn.com) |
| Current Status | Applied, Rejected, Interview Scheduled, Under Review, No Response |
| Last Update Date | Date of the most recent email about this application |
| Follow-Up Needed | YES if no response received within 14 days of application, otherwise NO |
| Days Since Applied | Calculated number of days since Date Applied |
| Notes | Recruiter name, salary info, location, job ID URL, or next steps |

**Formatting requirements:**
- Freeze the header row
- Auto-resize columns to fit content
- Highlight rows where Follow-Up Needed is YES in light yellow
- Highlight rows where Current Status is "Rejected" in light gray
- Highlight rows where Current Status is "Interview Scheduled" in light green

### Step 2 - First Run Historical Scan (one time only, Nov 1, 2025 through today):

Search both mahatab@gmail.com and mahatab@msn.com for all emails from November 1, 2025 through today related to job applications I submitted. I primarily apply through LinkedIn and directly through company career sites (such as Google, Microsoft, Nvidia, etc.).

**Email Search Instructions:**

Search using the following subject line and body phrases:
- "Thanks for applying"
- "Thank you for applying"
- "Thank you for your interest"
- "Thanks for your interest"

Filter by sender patterns:
- Sender address starts with: career*, noreply*, no-reply*
- Sender address contains: job, hire, talent, recruit

Specific known senders:
- noreply@google.com
- no-reply@us.greenhouse-mail.io

Also look for:
- LinkedIn job application confirmations ("You applied for..." or "Your application was sent...")
- Direct company career site confirmations from ATS platforms like Workday, Greenhouse, Lever, iCIMS, SmartRecruiters, Taleo, and similar systems
- Application status updates (rejection, interview invite, assessment request, moved to next stage)
- Recruiter responses tied to a specific application

**Consolidation Rule:**
For applications with multiple emails (e.g., confirmation followed by rejection or interview invite), consolidate into a single row. Use the original application date as Date Applied and the latest status as Current Status.

Populate the Google Sheet with all results, sorted by Date Applied descending (newest first).

Mark Follow-Up Needed as YES for any application older than 14 days with no status update beyond the initial confirmation.

### Step 3 - Daily Recurring Run (every day after the first run):

Search both mahatab@gmail.com and mahatab@msn.com for job application related emails from the previous day only, using the same search phrases and sender patterns defined in Step 2.

For each:
- **New application found:** Add a new row to the sheet.
- **Status update on an existing application:** Update the Current Status, Last Update Date, and Notes columns of the matching row.
- Re-evaluate Follow-Up Needed for all rows where Current Status is still "Applied" or "No Response" and Days Since Applied exceeds 14.

---

**CRITICAL:** This is the ONLY instruction set for job tracking. Follow it exactly.
