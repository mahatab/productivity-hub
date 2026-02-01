# Market Research: AI-Powered Tabbed Notepad for macOS

**Date:** January 31, 2026  
**Idea:** A minimalist macOS text editor with tabs, spell check, and optional AI (user's API key)

---

## 🎯 Your Vision

- **Plain text only** (no markdown, no rich text)
- **Tabs** for multi-document editing
- **Spell checking** built-in
- **AI features:**
  - Generate text from a prompt
  - Rephrase existing text with instructions
- **Local only** (no cloud sync)
- **Minimalist UI** like Windows Notepad

---

## 🔍 What Exists Today

### 1. **NoteTabs** (Very Recent - Dec 2024)
**Website:** https://notetabs.azurewebsites.net/  
**Status:** Just launched (1 month old on Product Hunt)

**What it does:**
- ✅ Native macOS app (Swift/SwiftUI - fast & lightweight)
- ✅ Horizontal tabs
- ✅ Auto-restore tabs and unsaved changes
- ✅ Local files only, no cloud
- ✅ Minimalist design, Dark Mode support
- ✅ Works directly with file system (no database)

**What it DOESN'T have:**
- ❌ AI features
- ❌ Built-in spell check mentioned
- ❌ API integration

**Pricing:** Not clearly listed (likely free or low-cost)

**Verdict:** **Direct competitor** but without AI. Very new, still gaining traction.

---

### 2. **Plain Text Editor** by Sindre Sorhus
**Website:** https://sindresorhus.com/plain-text-editor  
**App Store:** Available

**What it does:**
- ✅ Simple plain text editing
- ✅ Tab support (via macOS native tabs)
- ✅ Word count, optimal line spacing
- ✅ Stay on top, translucent background
- ✅ Brain dump mode

**What it DOESN'T have:**
- ❌ AI features
- ❌ Horizontal tabs (uses macOS native tabs - less visible)
- ⚠️ Spell checking buggy (macOS bug, per developer)

**Pricing:** Paid app (price not stated, typical Sindre apps are $5-15)

**Verdict:** Established, well-designed, but **no AI** and tabs are less prominent.

---

### 3. **CotEditor**
**Website:** https://github.com/coteditor/CotEditor  
**Status:** Open source, lightweight

**What it does:**
- ✅ Plain text editing
- ✅ Syntax highlighting (more for developers)
- ✅ Spell check
- ✅ Tabs

**What it DOESN'T have:**
- ❌ AI features
- ❌ Super minimalist (has more features for coding)

**Pricing:** Free (open source)

**Verdict:** Developer-focused, not the "disgustingly simple" vibe.

---

### 4. **TextEdit** (Built-in macOS)
**What it does:**
- ✅ Plain text mode
- ✅ Tabs (hidden by default)
- ✅ Spell check
- ✅ Free

**What it DOESN'T have:**
- ❌ AI features
- ❌ Good UX (tabs buried in menu)
- ❌ Minimalist (cluttered UI)

**Verdict:** Functional but **nobody loves it**.

---

## 🤖 AI Writing Assistants for macOS

### 5. **Writer's Brew**
- System-wide AI writing tool
- Works across all apps (not a dedicated editor)
- Uses OCR, external APIs
- **Not a notepad replacement**

### 6. **WritingTools** (GitHub)
- System-wide grammar assistant
- Free Gemini API, local LLMs
- Works in any app
- **Not a dedicated text editor**

### 7. **BoltAI, RewriteBar, Fluent, Cotypist, Fixkey**
- All are **system-wide AI assistants** or autocomplete tools
- None are dedicated tabbed text editors
- Require subscriptions or API keys
- Privacy-focused (local LLMs or encrypted API keys)

**Key insight:** AI writing tools exist but they're **add-ons to other apps**, not standalone minimalist editors.

---

## 🚀 What's Missing in the Market

### ✨ **Your Unique Combo:**

1. **NoteTabs-style simplicity** (tabs, local, fast) **+**  
2. **AI generation built-in** (prompt → text, rephrase with instructions) **+**  
3. **User-controlled API key** (no subscription lock-in) **+**  
4. **Windows Notepad aesthetic** (even more minimal than Mac apps)

### 🎯 **The Gap:**

| Feature | NoteTabs | Plain Text Editor | AI Assistants | **Your App** |
|---------|----------|-------------------|---------------|-------------|
| Horizontal Tabs | ✅ | Partial | ❌ | ✅ |
| Super Minimal UI | ✅ | ✅ | ❌ | ✅ |
| Local Only | ✅ | ✅ | Varies | ✅ |
| AI Text Gen | ❌ | ❌ | ✅ (system-wide) | ✅ (built-in) |
| AI Rephrase | ❌ | ❌ | ✅ (system-wide) | ✅ (built-in) |
| Own API Key | N/A | N/A | Some | ✅ |
| Spell Check | ? | Buggy | N/A | ✅ |

**Nobody has all of this in one simple app.**

---

## 💡 Competitive Advantages

### **Why people would choose your app:**

1. **NoteTabs users:** Get everything they have **+ AI** without leaving the app
2. **AI assistant users:** Get a **dedicated writing space** instead of system-wide overlay
3. **Notepad++ refugees:** Finally get tabs **+ modern AI** on macOS
4. **Privacy-conscious:** Own API key = no subscription, no data harvesting
5. **Simplicity seekers:** One app, one job, done perfectly

### **The m2labs Hook:**

> "NoteTabs meets ChatGPT, but simpler than both."

---

## 🛠️ Tech Stack Considerations

**Based on competitor analysis:**

- **Swift + SwiftUI** (like NoteTabs) = Native, fast, battery-efficient
- **No Electron** = Lightweight, instant start
- **Direct file system access** = No database bloat
- **OpenAI/Anthropic/Local LLM API** = Flexible AI backend

---

## 💰 Pricing Strategy

**What competitors charge:**

- **NoteTabs:** Unknown (new), likely $0-10
- **Plain Text Editor:** ~$5-15 (Sindre Sorhus typical pricing)
- **AI Assistants:** $5-20/month subscriptions OR free with own API key

**Suggested pricing:**

- **One-time:** $9.99 - $19.99 (aligns with Mac App Store expectations)
- **Freemium:** Free base app, $4.99 for AI features unlock
- **Pro tier:** $14.99 with advanced AI templates/presets

**m2labs philosophy:** One-time purchase > subscription (user freedom)

---

## 📊 Market Timing

**Why NOW is perfect:**

1. **NoteTabs just launched** (Dec 2024) → Market is **ready** for tabbed notepad alternatives
2. **AI writing tools exploding** → People want AI everywhere
3. **Subscription fatigue** → Users want own API key control
4. **macOS ecosystem growing** → More people switching from Windows

**Risk:** NoteTabs could add AI in 6-12 months. **First-mover advantage matters.**

---

## 🎬 Next Steps

1. **Build MVP prototype** (web version to visualize)
2. **Test with users** (Reddit r/MacOS, r/macapps)
3. **Name it** (ideas: CleanSlate, TabText, NoteAI, SimpleScribe)
4. **Learn Swift/SwiftUI** or hire developer
5. **Launch on Product Hunt** (NoteTabs got traction there)

---

## 🔥 Bottom Line

**The market wants this.** NoteTabs proved tabs + simplicity work. AI assistants proved people need AI writing help. **Nobody combined them yet.**

Your app is the **missing piece**: clean tabs + smart AI + zero bloat.

**Perfect for m2labs' first flagship product.** 🚀
