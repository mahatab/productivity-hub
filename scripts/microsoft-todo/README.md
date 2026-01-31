# Microsoft To Do Sync

Direct integration with Microsoft To Do via Graph API.

## Setup (One-time)

### 1. Register Azure AD Application

Visit: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade

1. Click **"New registration"**
2. **Name**: "Rudro Microsoft To Do Sync"
3. **Supported account types**: "Accounts in any organizational directory and personal Microsoft accounts"
4. **Redirect URI**: 
   - Type: Public client/native (mobile & desktop)
   - URI: `http://localhost:8080/callback`
5. Click **"Register"**

### 2. Get Credentials

1. In app overview, copy **Application (client) ID**
2. Go to **"Certificates & secrets"** → **"New client secret"** → Copy the **secret VALUE**
3. Go to **"API permissions"** → **"Add a permission"**:
   - Microsoft Graph → Delegated permissions
   - Add: `Tasks.ReadWrite`, `User.Read`
   - Click **"Grant admin consent"** (recommended)

### 3. Run Setup Script

```bash
cd ~/clawd/scripts/microsoft-todo
node setup.js
```

Follow the prompts:
- Enter your Application (client) ID
- Enter your Client Secret
- Browser will open for Microsoft login
- After authorization, copy the redirect URL (with `?code=...`) and paste it

## Usage

### Manual Sync

```bash
cd ~/clawd/scripts/microsoft-todo
node sync-tasks.js
```

### Automatic Sync

The sync runs automatically during heartbeats (once per day, typically 8 AM).

## What It Does

1. Fetches all incomplete tasks from Microsoft To Do
2. Groups them by priority (High vs Normal)
3. Updates HEARTBEAT.md with a "📋 MICROSOFT TO DO (Synced)" section
4. Includes task list, due dates, and priorities

## Files

- `setup.js` - OAuth authentication setup
- `sync-tasks.js` - Main sync script
- `config.json` - Azure app credentials (created by setup)
- `token.json` - OAuth tokens (created by setup, auto-refreshed)

## Troubleshooting

**Token expired?**
The script automatically refreshes tokens. If it fails, delete `token.json` and run `node setup.js` again.

**Authentication failed?**
Make sure your Azure app has the correct permissions and redirect URI.

**Tasks not syncing?**
Check that tasks are marked as "incomplete" in Microsoft To Do.
