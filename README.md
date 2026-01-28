# 🚀 Productivity Hub

**Your unified task and job management system with AI-powered email intelligence**

![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-private-red.svg)

## 🎯 Overview

Productivity Hub is a comprehensive personal productivity system that combines:
- ✅ **Task Management** - Kanban board with Microsoft To Do sync
- 💼 **Job Application Tracking** - Track applications, interviews, and offers
- 📧 **Email Intelligence** - AI-powered email categorization and search
- 🤖 **Automation** - Job email scanner and daily briefings

## ✨ Features

### 📋 Task Management
- Drag-and-drop Kanban board (Backlog, To Do, In Progress, Done)
- Bidirectional sync with Microsoft To Do
- Subtasks and checklist support
- Priority levels (High, Medium, Low)
- Categories and due dates
- Dark/Light mode

### 💼 Job Tracking
- Track all job applications in one place
- Status tracking (Applied, Interview, Offer, Rejected)
- Company and position details
- Application dates and notes
- Visual dashboard with stats

### 📧 Email Intelligence
- AI-powered email categorization
- Custom search with phrase matching
- Quote support for exact searches
- Date range filtering (quick or custom)
- Up to 500 emails per search
- Categories:
  - 🎯 Job Applications
  - 🚨 Urgent
  - 👤 Personal
  - 💼 Business
  - 📰 Newsletters
  - 📂 Other

### 🤖 Automation
- **Job Email Scanner**: Automatically scans inbox for job-related emails
- **Daily Briefing**: Morning email with news, weather, tasks, and reminders
- **Auto-sync**: Syncs tasks with Microsoft To Do every 30 minutes

## 🚀 Getting Started

### Prerequisites
- Python 3 (for local server)
- Microsoft account (for To Do and Email features)
- Azure AD app with permissions:
  - `Tasks.ReadWrite`
  - `Mail.Read`
  - `User.Read`

### Quick Start

1. **Start local server:**
   ```bash
   python3 -m http.server 8080
   ```

2. **Open in browser:**
   ```
   http://localhost:8080/productivity-hub.html
   ```

3. **Connect Microsoft account:**
   - Click "📋 Connect" in the header
   - Sign in with your Microsoft account
   - Approve permissions

4. **Start using:**
   - **Dashboard tab**: Quick overview
   - **Tasks tab**: Manage tasks and sync with To Do
   - **Jobs tab**: Track job applications
   - **Emails tab**: Analyze and search emails

## 📁 Project Structure

```
productivity-hub/
├── productivity-hub.html          # Main unified dashboard
├── kanban-board.html              # Standalone Kanban board
├── email-summarizer.html          # Standalone email analyzer
├── jobs-dashboard.html            # Standalone job tracker
├── task-board.html                # Static task view
├── scripts/
│   ├── scan-job-emails.js        # Job email scanner
│   ├── morning-briefing.sh       # Daily briefing generator
│   └── update-jobs-from-email.sh # Job tracking automation
├── jobs/                          # Job application files
├── tasks/                         # Task tracking files
├── AGENTS.md                      # AI agent instructions
├── SOUL.md                        # Persona and behavior
├── HEARTBEAT.md                   # Daily reminder config
└── README.md                      # This file
```

## 🎨 Design

- **Light Mode**: Modern gradient (Indigo → Purple → Pink)
- **Dark Mode**: Deep slate gradient with purple accents
- **Glassmorphism**: Frosted glass effect on all cards
- **Smooth Animations**: Hover effects, transitions, page fade-in
- **Responsive**: Works on desktop and mobile

## 🔒 Security & Privacy

- **OAuth 2.0**: Industry-standard authentication
- **Read-only email access**: Never modifies or deletes
- **No password storage**: Authentication handled by Microsoft
- **Private repo**: Your data stays private
- **Local processing**: All categorization in browser
- **Excluded from Git**: USER.md, memory/, images

## 📖 Documentation

- [Email Summarizer Guide](EMAIL-SUMMARIZER-README.md)
- [Job Email Scanner Guide](JOB-EMAIL-SCANNER-README.md)
- [Job Tracker Guide](JOB-TRACKER-GUIDE.md)
- [M2Labs LLC Setup Guide](m2labs-llc-guide.md)

## 🛠️ Configuration

### Azure AD App Setup

1. Create app in Azure Portal
2. Set redirect URIs:
   - `http://localhost:8080`
   - `http://localhost:8080/productivity-hub.html`
3. Add API permissions:
   - Microsoft Graph → Delegated
   - `Tasks.ReadWrite`, `Mail.Read`, `User.Read`
4. Grant admin consent

### Customization

Edit these files to customize:
- `SOUL.md` - AI assistant personality
- `HEARTBEAT.md` - Daily reminders and checks
- `TOOLS.md` - Personal tool notes
- `AGENTS.md` - Workspace instructions

## 🤝 Contributing

This is a private personal productivity system. Not open for contributions.

## 📝 License

Private - All Rights Reserved

## 🙏 Credits

**Built by Rudro 🦸🏻‍♂️**  
*Your AI Assistant*

**Created:** January 27, 2026  
**For:** Mahatab Rashid

---

**Repo:** https://github.com/mahatab/productivity-hub  
**Status:** ✅ Active Development
