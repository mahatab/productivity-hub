# AI Notepad for macOS - m2labs Project

**Date:** January 31, 2026  
**Status:** Research & Prototype Complete  
**Next:** Development / MVP Build

---

## 🎯 The Vision

A **disgustingly simple** text editor for macOS that combines:
- Windows Notepad-style minimalism
- Horizontal tabs (like NoteTabs/Notepad++)
- Built-in spell checking
- AI text generation & rephrasing (user's own API key)
- Local-only storage (no cloud, no subscriptions)

**The m2labs Philosophy:** One problem, solved perfectly. No bloat, no lock-in, no nonsense.

---

## 📁 Files in This Folder

1. **MARKET-RESEARCH.md** - Competitive analysis of existing apps
2. **prototype.html** - Interactive web prototype (proof of concept)
3. **README.md** - This file

---

## 🔍 Key Findings from Research

### What Exists:
- **NoteTabs** (Dec 2024) - New, minimal, tabs + local files. **No AI.**
- **Plain Text Editor** (Sindre Sorhus) - Minimal, tabs via macOS. **No AI.**
- **CotEditor** - Developer-focused, free. **No AI.**
- **AI Writing Assistants** (Writer's Brew, BoltAI, etc.) - System-wide, **not dedicated editors**.

### The Gap:
**Nobody offers tabs + minimal UI + built-in AI in one simple package.**

### The Opportunity:
- NoteTabs proved demand for tabbed minimal editors
- AI assistants proved demand for AI writing help
- Nobody combined them yet → **first-mover advantage**

---

## 🚀 Competitive Advantages

| Feature | NoteTabs | Plain Text Editor | AI Assistants | **Our App** |
|---------|----------|-------------------|---------------|-------------|
| Horizontal Tabs | ✅ | Partial | ❌ | ✅ |
| Super Minimal UI | ✅ | ✅ | ❌ | ✅ |
| Local Only | ✅ | ✅ | Varies | ✅ |
| AI Text Gen | ❌ | ❌ | ✅ (system-wide) | ✅ (built-in) |
| AI Rephrase | ❌ | ❌ | ✅ (system-wide) | ✅ (built-in) |
| Own API Key | N/A | N/A | Some | ✅ |
| Spell Check | ? | Buggy | N/A | ✅ |

**We're the only ones with all of this.**

---

## 💡 Prototype Features

The web prototype demonstrates:

1. **macOS-style window** (traffic lights, title bar)
2. **Horizontal tab bar** (multiple documents, easy switching)
3. **Clean toolbar** (New, Open, Save, Find, etc.)
4. **Minimal editor area** (just text, no distractions)
5. **AI panel** (toggleable, bottom of screen)
   - Text generation from prompts
   - Rephrase selection with instructions
   - User's own API key (configured in settings)
6. **Status bar** (line/word/char count, saved status)

### Screenshots:
- `prototype.html` - Open in browser to interact
- Shows tab switching, AI panel toggle, clean interface

---

## 🛠️ Tech Stack (Recommended)

Based on competitor success:

- **Swift + SwiftUI** (like NoteTabs)
  - Native macOS performance
  - Fast startup, battery-efficient
  - Direct file system access (no database)
  - Lightweight (not Electron)

- **AI Integration**
  - OpenAI API
  - Anthropic Claude API
  - Local LLMs (Ollama) for privacy-first users
  - User provides their own API key (no subscription)

- **Core Features**
  - NSTextView for editing
  - Built-in macOS spell checker
  - Tab management (SwiftUI TabView or custom)
  - File I/O via FileManager

---

## 💰 Pricing Strategy

**Options:**

1. **One-time purchase:** $14.99 (aligns with Mac App Store expectations)
2. **Freemium:** Free base editor, $9.99 for AI unlock
3. **Pay-what-you-want:** Minimum $5, suggested $15

**m2labs Principle:** One-time > subscription. Users own the app, not rent it.

**Revenue Potential:**
- NoteTabs: New, gaining traction on Product Hunt
- Plain Text Editor: Successful indie app
- Market: macOS text editor users + AI enthusiasts + Notepad++ refugees

---

## 🎯 Target Audience

1. **Windows → macOS switchers** missing Notepad++ tabs
2. **Writers & note-takers** wanting AI help without subscriptions
3. **Privacy-conscious users** who want local-only storage
4. **Minimalism lovers** tired of bloated apps (Notion, Evernore)
5. **Developers** wanting quick text editing with AI (for READMEs, docs, etc.)

---

## 📊 Next Steps

### Phase 1: MVP Development
- [ ] Learn Swift/SwiftUI (or hire developer)
- [ ] Build core editor (tabs, open/save, spell check)
- [ ] Integrate OpenAI API (basic text generation)
- [ ] Test with 10-20 users (Reddit, Product Hunt)

### Phase 2: AI Polish
- [ ] Add rephrase feature
- [ ] Support Anthropic Claude
- [ ] Add local LLM support (Ollama)
- [ ] Settings panel for API key management

### Phase 3: Launch
- [ ] Final name (ideas: CleanSlate, TabText, NoteAI, SimpleScribe)
- [ ] App icon & branding
- [ ] Product Hunt launch
- [ ] Mac App Store submission
- [ ] Landing page (m2labs.com)

### Phase 4: Growth
- [ ] User feedback & iteration
- [ ] Feature refinements (no bloat!)
- [ ] Community building (Discord/Reddit)
- [ ] Press coverage (The Verge, MacStories, etc.)

---

## 🏆 Why This Matters for m2labs

This is the **perfect flagship product**:

1. **Proves the m2labs philosophy** - Simplicity beats feature bloat
2. **Solves a real problem** - Market gap confirmed by research
3. **Sustainable business model** - One-time purchase, no subscriptions
4. **Scalable** - Mac App Store distribution, low overhead
5. **Differentiated** - Nobody else has tabs + AI + minimalism together

**The tagline:**  
> "NoteTabs meets ChatGPT, but simpler than both."

---

## 📝 Notes & Ideas

- **Name brainstorm:** CleanSlate, TabText, NoteAI, SimpleScribe, QuickAI, TextFlow
- **Future features:** Markdown preview (optional), themes (light/dark), keyboard shortcuts
- **Marketing angle:** "The text editor that respects your time and intelligence"

---

**Ready to build this?** 🚀
