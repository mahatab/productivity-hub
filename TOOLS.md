# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## Email

**My address:** rudro.ai.agent@gmail.com  
**Big Giant Head's address:** mahatab@msn.com

### Email Processing Rules

When Big Giant Head forwards emails to me:

**Subject: `task: ...`**
- Extract task details
- Track in task management system
- Priority/deadline from email body if present

**Subject: `job: ...`**
- Extract from email body:
  - Job ID
  - Company name
  - Job title/role
  - Job description/details
  - Application date
- Create file: `jobs/YYYY-MM-DD-company-role.md`
- Update `JOBS-DASHBOARD.md` with new entry
- Track status: Applied → Interview → Offer/Rejected
- Keep searchable records of job search

### Email Skill

Using `himalaya` CLI for email management:
- Config: `~/.config/himalaya/config.toml`
- Account: `rudro` (default)
- Can read, send, reply, forward, search emails

## MSN/Outlook (mahatab@msn.com) - Read Only
- **Access:** OAuth2 via Microsoft Graph API (`Mail.Read` scope)
- **Azure App:** Client ID `7ed8b008-8f80-4c57-a7be-773210b67021` (public client, consumers tenant)
- **Token:** `~/.clawdbot/msn/token.json`
- **Helper script:** `~/clawd/scripts/msn-read.py`
- **Usage:** `python3 ~/clawd/scripts/msn-read.py [--count N] [--unread] [--search "query"] [--folder inbox]`

## Gmail (mahatab@gmail.com) - Read Only
- **Access:** OAuth2 readonly (`gmail.readonly` scope)
- **Credentials:** `~/.clawdbot/gmail/client_secret.json`
- **Token:** `~/.clawdbot/gmail/token.json`
- **Helper script:** `~/clawd/scripts/gmail-read.py`
- **Usage:** `python3 ~/clawd/scripts/gmail-read.py [--count N] [--unread] [--search "query"]`

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

---

Add whatever helps you do your job. This is your cheat sheet.
