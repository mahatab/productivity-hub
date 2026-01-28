# 🔄 Auto-Deploy Workflow

**Rudro's Workflow:** Automatically deploy to Firebase when tasks or jobs are updated.

## When to Auto-Deploy

Deploy to Firebase automatically when:

1. ✅ **New task added** (via `task: ...` message)
2. ✅ **Task updated** (status changed, marked complete, etc.)
3. ✅ **New job added** (via email scanner or manual)
4. ✅ **Job status updated** (Applied → Interview → Offer/Rejected)
5. ✅ **Dashboard files modified** (productivity-hub.html, etc.)
6. ✅ **HEARTBEAT.md updated** (tasks added/removed)
7. ✅ **Any workspace file that affects the dashboard**

## Deployment Process

After making changes, Rudro will:

1. **Save changes** to files (tasks/, jobs/, HEARTBEAT.md, etc.)
2. **Commit to Git** with descriptive message
3. **Push to GitHub** (backup)
4. **Deploy to Firebase** (make live)
5. **Confirm** deployment complete

## Automatic Execution

**Rudro runs:**
```bash
cd ~/clawd
./scripts/deploy-to-firebase.sh "Description of changes"
```

**What this does:**
1. Commits changes to Git
2. Pushes to GitHub
3. Deploys to Firebase hosting
4. Confirms deployment

## User Experience

**Before (manual):**
- Add task → See on Mac only
- Need to manually deploy to see on phone

**After (automatic):**
- Add task → Rudro auto-deploys
- Changes live on phone/PC in ~30 seconds ✨

## Deployment Confirmation

After deployment, Rudro will say:
```
✅ Deployed to Firebase!
🌐 Live at: https://productivity-hub-mahatab.web.app
📱 Refresh your dashboard on other devices to see changes
```

## Exception: Don't Deploy

**Skip deployment for:**
- ❌ Memory updates (memory/*.md) - private data
- ❌ Temporary experiments
- ❌ When user says "don't deploy yet"

## Manual Deployment

Big Giant Head can also deploy manually:
```bash
cd ~/clawd
firebase deploy
```

Or with the helper script:
```bash
./scripts/deploy-to-firebase.sh "My custom message"
```

## Rollback (if needed)

If something breaks:
```bash
# See versions
firebase hosting:releases

# Rollback to previous
firebase hosting:rollback
```

---

**Created:** 2026-01-27  
**Purpose:** Keep Firebase dashboard in sync with local changes  
**By:** Rudro 🦸🏻‍♂️
