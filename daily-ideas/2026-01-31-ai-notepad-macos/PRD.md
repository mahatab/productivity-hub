# Product Requirements Document (PRD)
# AI Notepad for macOS

**Version:** 1.0  
**Date:** January 31, 2026  
**Author:** m2labs  
**Status:** Draft - Ready for Development

---

## 1. Executive Summary

### 1.1 Product Vision
A minimal, native macOS text editor combining the simplicity of Windows Notepad with horizontal tab support and optional AI-powered writing assistance. Users control their own AI access via personal API keys, eliminating subscriptions and ensuring privacy.

### 1.2 Target Audience
- Windows → macOS switchers missing Notepad++
- Writers and note-takers seeking AI assistance without subscriptions
- Privacy-conscious users preferring local-only storage
- Minimalism enthusiasts tired of bloated note-taking apps
- Developers needing quick text editing with AI support

### 1.3 Success Metrics
- **Launch Goal:** 500 paid users in first 3 months
- **User Satisfaction:** 4.5+ stars on Mac App Store
- **Daily Active Users:** 60%+ of total user base
- **Revenue:** $7,500+ in first quarter ($14.99 × 500)

---

## 2. Product Overview

### 2.1 Problem Statement
Current macOS text editors fall into two camps:
1. **Too simple:** TextEdit lacks tabs and good UX
2. **Too complex:** Notion, Evernote overwhelm with features

AI writing assistants exist but are system-wide overlays, not integrated editors.

**Gap:** No app combines minimal editing + tabs + built-in AI in one package.

### 2.2 Solution
A native macOS app that:
- Opens instantly (< 0.5 seconds)
- Provides horizontal tabs for multi-document workflow
- Integrates AI generation/rephrasing via user's API key
- Stores everything locally (no cloud, no accounts)
- Respects macOS design language

### 2.3 Competitive Advantage
| Feature | NoteTabs | Plain Text Editor | AI Assistants | **Our App** |
|---------|----------|-------------------|---------------|-------------|
| Horizontal Tabs | ✅ | Partial | ❌ | ✅ |
| Minimal UI | ✅ | ✅ | ❌ | ✅ |
| Local Storage | ✅ | ✅ | Varies | ✅ |
| AI Text Gen | ❌ | ❌ | ✅ | ✅ |
| AI Rephrase | ❌ | ❌ | ✅ | ✅ |
| Own API Key | N/A | N/A | Some | ✅ |
| Spell Check | ? | Buggy | N/A | ✅ |

---

## 3. Functional Requirements

### 3.1 Core Editor Features

#### 3.1.1 Text Editing
- **Plain text only** (UTF-8 encoding)
- **Must Support:**
  - Standard text operations (type, delete, select, copy, paste, undo/redo)
  - Multi-line editing with scroll support
  - Text wrapping (soft wrap, no horizontal scroll)
  - Built-in macOS spell checker
  - Grammar checking (macOS native)
  - Find & Replace (case-sensitive/insensitive, whole word)
  
- **Must NOT Support:**
  - Rich text formatting (no bold, italic, colors)
  - Images or media embedding
  - Markdown syntax highlighting (future consideration)

#### 3.1.2 File Operations
- **Open:** Standard macOS file picker (⌘O)
- **Save:** Save current tab to disk (⌘S)
- **Save As:** Save with new name/location (⌘⇧S)
- **Auto-save:** Optional setting to save on change (debounced, 2s delay)
- **Unsaved indicator:** Visual marker on tab (e.g., dot or modified flag)
- **File format:** `.txt` files by default
- **Encoding:** UTF-8 (reject UTF-16, show error message)

#### 3.1.3 Tab Management
- **Horizontal tab bar** (always visible)
- **Tab actions:**
  - New tab (⌘T) - Creates "Untitled" document
  - Close tab (⌘W) - Prompts if unsaved
  - Switch tabs (⌘1-9 for first 9 tabs, or ⌃⇥/⌃⇧⇥)
  - Reorder tabs (drag & drop)
  - Close all tabs (⌘⌥W)
  
- **Tab states:**
  - Active (highlighted)
  - Inactive (dimmed)
  - Unsaved (visual indicator)
  - File path shown on hover (tooltip)
  
- **Limit:** Maximum 50 open tabs (warn user at 40)

#### 3.1.4 Session Restoration
- **Auto-restore:** On app launch, restore all tabs from last session
- **Content restoration:** Restore unsaved changes (stored in temp directory)
- **Cursor position:** Restore last cursor/scroll position per tab
- **User control:** Option to disable auto-restore in Preferences

---

### 3.2 AI Features

#### 3.2.1 AI Panel
- **Toggle:** Click "✨ AI Assistant" in status bar or ⌘⌥A
- **Position:** Bottom of window (like search bar in some apps)
- **Height:** 100-150px when open
- **Modes:**
  1. **Generate:** Create new text from prompt
  2. **Rephrase:** Rewrite selected text with instructions
  
#### 3.2.2 Text Generation
- **User flow:**
  1. User clicks "✨ AI Assistant"
  2. Panel opens with input field
  3. User types prompt (e.g., "Write a haiku about coffee")
  4. User clicks "Generate" button
  5. AI response inserts at cursor position (or replaces selection)
  
- **Technical:**
  - API call to user's configured provider (OpenAI, Anthropic, etc.)
  - Show loading indicator during generation
  - Cancel button to abort request
  - Error handling (API key invalid, rate limit, network error)
  - Token usage display (optional, for user awareness)

#### 3.2.3 Text Rephrasing
- **User flow:**
  1. User selects text in editor
  2. Opens AI panel (⌘⌥A)
  3. Types instruction (e.g., "make this more formal")
  4. Clicks "Rephrase"
  5. Original text replaced with AI output
  
- **Technical:**
  - Context-aware: Send selected text + instruction to API
  - Undo support (⌘Z to revert AI changes)
  - Show diff preview (optional, future enhancement)

#### 3.2.4 AI Configuration
- **API Providers:**
  - OpenAI (GPT-4, GPT-3.5-turbo)
  - Anthropic (Claude Sonnet, Haiku)
  - Local LLMs via Ollama (future phase 2)
  
- **User settings:**
  - API key storage (encrypted in macOS Keychain)
  - Model selection (dropdown)
  - Max tokens limit
  - Temperature slider (creativity control)
  
- **Validation:**
  - Test API key on save
  - Show error if invalid
  - Graceful degradation if AI unavailable (disable panel)

---

### 3.3 User Interface

#### 3.3.1 Window Structure
```
┌─────────────────────────────────────┐
│ ● ● ●         Untitled 1            │ ← Title bar (macOS native)
├─────────────────────────────────────┤
│ Untitled 1 │ Ideas.txt │ Notes.txt +│ ← Tab bar
├─────────────────────────────────────┤
│ 📄 New │ 💾 Save │ 🔍 Find │ ...    │ ← Toolbar (optional, collapsible)
├─────────────────────────────────────┤
│                                     │
│   [Text editing area]               │ ← Editor (majority of space)
│                                     │
├─────────────────────────────────────┤
│ [AI Panel - collapsible]            │ ← AI Assistant (bottom)
├─────────────────────────────────────┤
│ Lines: 23 │ Words: 142 │ ✨ AI      │ ← Status bar
└─────────────────────────────────────┘
```

#### 3.3.2 Visual Design
- **Aesthetic:** Windows Notepad minimalism + macOS native controls
- **Colors:**
  - Light mode: White background, black text, gray UI elements
  - Dark mode: Dark gray background, white text, darker UI elements
  - Accent: macOS system accent color (user's preference)
  
- **Typography:**
  - Editor: SF Mono 14pt (monospaced, like Xcode)
  - UI: SF Pro Text (system default)
  - Line height: 1.6 (readable)
  
- **Spacing:**
  - Editor padding: 20px all sides
  - Tab padding: 10px horizontal, 8px vertical
  - Button spacing: 8px between toolbar items

#### 3.3.3 Toolbar (Optional)
- **Default:** Visible
- **Toggle:** View → Hide Toolbar (⌘⌥T)
- **Buttons:**
  - New (📄)
  - Open (📂)
  - Save (💾)
  - Divider
  - Cut (✂️)
  - Copy (📋)
  - Paste (📌)
  - Divider
  - Find (🔍)
  
- **Fallback:** All actions accessible via menu bar if toolbar hidden

#### 3.3.4 Status Bar
- **Left side:**
  - Line count
  - Word count
  - Character count
  - Save status (✅ Saved / 📝 Unsaved)
  
- **Right side:**
  - AI Assistant toggle (✨ AI Assistant)
  
- **Behavior:**
  - Always visible
  - Updates in real-time as user types

---

### 3.4 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| **File** |
| New Tab | ⌘T |
| Open | ⌘O |
| Save | ⌘S |
| Save As | ⌘⇧S |
| Close Tab | ⌘W |
| Close All | ⌘⌥W |
| **Edit** |
| Undo | ⌘Z |
| Redo | ⌘⇧Z |
| Cut | ⌘X |
| Copy | ⌘C |
| Paste | ⌘V |
| Select All | ⌘A |
| Find | ⌘F |
| Find Next | ⌘G |
| Replace | ⌘⌥F |
| **View** |
| Toggle Toolbar | ⌘⌥T |
| Toggle AI Panel | ⌘⌥A |
| **Tabs** |
| Next Tab | ⌃⇥ |
| Previous Tab | ⌃⇧⇥ |
| Tab 1-9 | ⌘1-9 |
| **Window** |
| Minimize | ⌘M |
| Zoom | ⌘⌃F |

---

### 3.5 Preferences / Settings

#### 3.5.1 General
- **On Launch:**
  - [ ] Restore previous session
  - [ ] Open new empty document
  
- **Auto-save:**
  - [ ] Enable auto-save (delay: 2s)
  
- **Font:**
  - Font family dropdown (SF Mono, Menlo, Monaco, Courier)
  - Font size slider (10-24pt, default 14pt)

#### 3.5.2 AI Settings
- **Provider:** OpenAI / Anthropic / Ollama (future)
- **API Key:** [text field] (stored in Keychain)
- **Model:** Dropdown (GPT-4, GPT-3.5, Claude Sonnet, etc.)
- **Max Tokens:** Slider (100-4000, default 1000)
- **Temperature:** Slider (0.0-1.0, default 0.7)
- **Test Connection:** Button to validate API key

#### 3.5.3 Appearance
- **Theme:**
  - ( ) System (follow macOS)
  - ( ) Light
  - ( ) Dark
  
- **Show toolbar:** [x] Enabled by default
- **Tab bar position:** Top (fixed, no bottom option for simplicity)

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **Startup time:** < 0.5 seconds (cold launch)
- **Tab switching:** < 50ms (instant feel)
- **AI response time:** < 5 seconds for typical prompts (API-dependent)
- **File operations:** < 100ms for files up to 10MB
- **Memory usage:** < 50MB idle, < 200MB with 20 tabs open

### 4.2 Compatibility
- **macOS Version:** macOS 13 (Ventura) or later
- **Architecture:** Universal Binary (Intel + Apple Silicon)
- **File System:** Works with APFS, HFS+, external drives

### 4.3 Security & Privacy
- **Local storage:** All files stored on user's Mac (no cloud sync)
- **API keys:** Encrypted in macOS Keychain
- **Network:** Only outbound to AI APIs (user-initiated)
- **Permissions:** File system read/write only (no camera, mic, contacts)
- **Telemetry:** None (zero data collection)

### 4.4 Accessibility
- **VoiceOver:** Full support for screen readers
- **Keyboard navigation:** 100% keyboard-operable (no mouse required)
- **Contrast:** Meets WCAG 2.1 AA standards
- **Font scaling:** Respects macOS text size preferences

### 4.5 Reliability
- **Crash recovery:** Auto-save unsaved work every 30s to temp directory
- **Graceful degradation:** AI features disabled if API unavailable
- **Error handling:** User-friendly error messages (not technical jargon)

---

## 5. Technical Architecture

### 5.1 Technology Stack

#### 5.1.1 Core
- **Language:** Swift 5.9+
- **Framework:** SwiftUI (primary UI) + AppKit (where needed)
- **Minimum SDK:** macOS 13.0 (Ventura)
- **Build System:** Xcode 15+

#### 5.1.2 Text Editing
- **Component:** NSTextView (AppKit, for advanced text features)
- **Wrapper:** SwiftUI NSViewRepresentable
- **Spell Check:** NSSpellChecker (built-in macOS)

#### 5.1.3 AI Integration
- **HTTP Client:** URLSession (native)
- **JSON Parsing:** Codable (Swift standard)
- **APIs:**
  - OpenAI: https://api.openai.com/v1/chat/completions
  - Anthropic: https://api.anthropic.com/v1/messages
  
- **Libraries:**
  - None required (use native URLSession)
  - Optional: Alamofire for easier request handling (avoid if possible)

#### 5.1.4 Data Persistence
- **File I/O:** FileManager (Swift standard)
- **Session storage:** UserDefaults (tab paths, cursor positions)
- **Unsaved content:** Temporary directory (`~/Library/Application Support/[AppName]/Temp/`)
- **Settings:** UserDefaults + Keychain (for API keys)

### 5.2 Project Structure

```
AInotepad/
├── App/
│   ├── AInotpadApp.swift          # App entry point
│   └── AppDelegate.swift          # macOS lifecycle
├── Views/
│   ├── MainWindow.swift           # Main window container
│   ├── TabBarView.swift           # Tab management UI
│   ├── EditorView.swift           # Text editor wrapper
│   ├── ToolbarView.swift          # Toolbar buttons
│   ├── AIPanelView.swift          # AI assistant panel
│   └── StatusBarView.swift        # Bottom status bar
├── ViewModels/
│   ├── DocumentViewModel.swift    # Tab/document state
│   ├── EditorViewModel.swift      # Text editing logic
│   └── AIViewModel.swift          # AI interaction logic
├── Models/
│   ├── Document.swift             # Document data model
│   ├── AIProvider.swift           # AI provider enum
│   └── Settings.swift             # User preferences
├── Services/
│   ├── FileService.swift          # File open/save/auto-save
│   ├── AIService.swift            # AI API calls
│   ├── SessionService.swift       # Session restore/save
│   └── KeychainService.swift      # Secure API key storage
├── Utilities/
│   ├── Constants.swift            # App constants
│   └── Extensions.swift           # Swift extensions
└── Resources/
    ├── Assets.xcassets            # Icons, images
    └── Info.plist                 # App metadata
```

### 5.3 Data Models

#### 5.3.1 Document
```swift
struct Document: Identifiable, Codable {
    let id: UUID
    var title: String               // Tab title
    var content: String             // Text content
    var filePath: URL?              // Disk location (nil if unsaved)
    var isModified: Bool            // Unsaved changes flag
    var cursorPosition: Int         // For session restore
    var scrollPosition: CGFloat     // For session restore
    var createdAt: Date
    var modifiedAt: Date
}
```

#### 5.3.2 Settings
```swift
struct AppSettings: Codable {
    var restoreSession: Bool = true
    var autoSave: Bool = false
    var autoSaveDelay: Double = 2.0
    
    var fontFamily: String = "SF Mono"
    var fontSize: CGFloat = 14.0
    
    var aiProvider: AIProvider = .openai
    var aiModel: String = "gpt-4"
    var aiMaxTokens: Int = 1000
    var aiTemperature: Double = 0.7
    
    var theme: Theme = .system
    var showToolbar: Bool = true
}

enum AIProvider: String, Codable {
    case openai = "OpenAI"
    case anthropic = "Anthropic"
    case ollama = "Ollama"  // Future
}

enum Theme: String, Codable {
    case system = "System"
    case light = "Light"
    case dark = "Dark"
}
```

### 5.4 AI Service Implementation

#### 5.4.1 OpenAI Integration
```swift
class OpenAIService {
    func generateText(prompt: String, apiKey: String, model: String, maxTokens: Int, temperature: Double) async throws -> String {
        let url = URL(string: "https://api.openai.com/v1/chat/completions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "model": model,
            "messages": [
                ["role": "user", "content": prompt]
            ],
            "max_tokens": maxTokens,
            "temperature": temperature
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw AIError.apiError("Request failed")
        }
        
        let result = try JSONDecoder().decode(OpenAIResponse.self, from: data)
        return result.choices.first?.message.content ?? ""
    }
    
    func rephraseText(text: String, instruction: String, apiKey: String, model: String) async throws -> String {
        let prompt = "Rewrite the following text with this instruction: \(instruction)\n\nText: \(text)"
        return try await generateText(prompt: prompt, apiKey: apiKey, model: model, maxTokens: 1000, temperature: 0.7)
    }
}

struct OpenAIResponse: Codable {
    let choices: [Choice]
    
    struct Choice: Codable {
        let message: Message
    }
    
    struct Message: Codable {
        let content: String
    }
}

enum AIError: Error {
    case apiError(String)
    case invalidKey
    case networkError
}
```

#### 5.4.2 Anthropic Integration (Similar Pattern)
```swift
class AnthropicService {
    func generateText(prompt: String, apiKey: String, model: String) async throws -> String {
        // Similar to OpenAI, different endpoint/format
        // https://api.anthropic.com/v1/messages
        // Header: "x-api-key" instead of Authorization
    }
}
```

---

## 6. Development Phases

### Phase 1: MVP (Weeks 1-4)
**Goal:** Core editor functionality, no AI yet

- [x] Project setup (Xcode, SwiftUI structure)
- [ ] Main window with title bar
- [ ] Tab bar (create, switch, close tabs)
- [ ] Basic text editor (NSTextView wrapper)
- [ ] File operations (open, save, save as)
- [ ] Spell checking (macOS native)
- [ ] Status bar (word count, save status)
- [ ] Keyboard shortcuts
- [ ] Session restoration (restore tabs on launch)

**Deliverable:** Working text editor with tabs (like NoteTabs)

---

### Phase 2: AI Integration (Weeks 5-6)
**Goal:** Add AI features

- [ ] AI panel UI (bottom sheet)
- [ ] Settings panel (API key, provider, model)
- [ ] Keychain integration (secure key storage)
- [ ] OpenAI API integration
- [ ] Text generation from prompt
- [ ] Text rephrasing with instructions
- [ ] Error handling (API errors, network issues)
- [ ] Loading indicators

**Deliverable:** Full AI-powered text editor

---

### Phase 3: Polish & Testing (Weeks 7-8)
**Goal:** Bug fixes, UX improvements

- [ ] User testing with 10-20 beta testers
- [ ] Fix critical bugs
- [ ] Performance optimization (startup time, memory)
- [ ] Accessibility improvements (VoiceOver)
- [ ] Dark mode refinement
- [ ] Icon design (app icon, toolbar icons)
- [ ] Help documentation (in-app or website)

**Deliverable:** Release candidate

---

### Phase 4: Launch (Week 9)
**Goal:** Public release

- [ ] Mac App Store submission
- [ ] Product Hunt launch
- [ ] Landing page (m2labs.com/ainotpad)
- [ ] Press outreach (MacStories, The Verge)
- [ ] Social media promotion (Twitter, Reddit)

**Deliverable:** v1.0 on Mac App Store

---

### Phase 5: Post-Launch (Weeks 10+)
**Goal:** Iterate based on feedback

- [ ] Monitor App Store reviews
- [ ] Fix reported bugs (priority: crashes, data loss)
- [ ] Add top-requested features (if aligned with simplicity)
- [ ] Anthropic Claude integration
- [ ] Local LLM support (Ollama)
- [ ] Markdown preview (optional, future)

---

## 7. User Stories

### 7.1 Core Editing
1. **As a writer**, I want to open multiple text files in tabs so I can reference notes while writing.
2. **As a user**, I want spell checking to catch my typos automatically.
3. **As a Windows switcher**, I want horizontal tabs like Notepad++ so I feel at home on macOS.

### 7.2 AI Features
4. **As a blogger**, I want to generate blog post outlines from a prompt so I can overcome writer's block.
5. **As a student**, I want to rephrase my essay to sound more academic without rewriting manually.
6. **As a privacy advocate**, I want to use my own API key so my data doesn't go through a third party.

### 7.3 Workflow
7. **As a developer**, I want to quickly jot down ideas without opening a heavy IDE.
8. **As a distracted person**, I want a clean interface with no notifications or suggestions.
9. **As a forgetful user**, I want my tabs to restore when I reopen the app so I don't lose my place.

---

## 8. Edge Cases & Error Handling

### 8.1 File Operations
| Scenario | Expected Behavior |
|----------|-------------------|
| Open UTF-16 file | Show error: "Unsupported encoding. Please convert to UTF-8." |
| Open 100MB file | Show warning: "Large file may cause slowdowns. Continue?" |
| Save fails (disk full) | Show error: "Unable to save. Check disk space." Retry option. |
| File deleted externally | Detect on next save, prompt: "File no longer exists. Save as new file?" |

### 8.2 AI Operations
| Scenario | Expected Behavior |
|----------|-------------------|
| Invalid API key | Show error: "Invalid API key. Check Settings." Disable AI panel. |
| Network timeout | Show error: "Request timed out. Try again." Cancel button. |
| Rate limit hit | Show error: "API rate limit reached. Wait and retry." |
| Empty prompt | Show warning: "Please enter a prompt." |
| No text selected (rephrase) | Show warning: "Select text to rephrase." |

### 8.3 Session Restore
| Scenario | Expected Behavior |
|----------|-------------------|
| Corrupted session file | Fallback to empty state, log error for debugging. |
| File moved since last session | Show "(File not found)" in tab, allow user to locate or close. |
| 50+ tabs on restore | Warn: "Many tabs detected. This may slow startup. Restore anyway?" |

---

## 9. Testing Requirements

### 9.1 Unit Tests
- File service (open, save, auto-save)
- AI service (API calls, error handling)
- Session service (save/restore state)
- Keychain service (store/retrieve API key)

### 9.2 Integration Tests
- End-to-end tab workflow (create → edit → save → close)
- AI generation workflow (prompt → API call → insert text)
- Session restore (save state → quit → relaunch → verify tabs)

### 9.3 Manual Testing
- Test all keyboard shortcuts
- Test with 1, 10, 50 tabs
- Test with large files (1MB, 10MB)
- Test AI with various prompts
- Test dark mode switch
- Test with VoiceOver enabled

### 9.4 Performance Testing
- Measure startup time (target: < 0.5s)
- Measure tab switch time (target: < 50ms)
- Measure memory usage with 20 tabs (target: < 200MB)

---

## 10. Open Questions & Decisions

### 10.1 Deferred to Phase 2+
- **Markdown preview:** Not in MVP (adds complexity)
- **Cloud sync:** Never (conflicts with local-only philosophy)
- **Collaboration:** Not planned (out of scope)
- **Themes beyond light/dark:** Future enhancement

### 10.2 To Be Decided
- **App Name:** CleanSlate? TabText? NoteAI? SimpleScribe?
- **Pricing:** $14.99 one-time? $9.99 with $4.99 AI unlock?
- **Distribution:** Mac App Store only? Also direct download?

---

## 11. Success Criteria

### 11.1 Launch Criteria (Must-Have)
- ✅ All Phase 1 & 2 features complete
- ✅ Zero critical bugs (no crashes, no data loss)
- ✅ App Store review approved
- ✅ Positive feedback from 5+ beta testers

### 11.2 Post-Launch Goals (3 Months)
- 500+ paid users
- 4.5+ star rating on App Store
- Featured on Product Hunt (Top 5 of the day)
- Press coverage in 2+ tech publications

---

## 12. Appendix

### 12.1 References
- **Market Research:** `MARKET-RESEARCH.md`
- **Prototype:** `prototype.html`
- **Competitor Analysis:**
  - NoteTabs: https://notetabs.azurewebsites.net/
  - Plain Text Editor: https://sindresorhus.com/plain-text-editor
  - CotEditor: https://github.com/coteditor/CotEditor

### 12.2 Design Assets
- **Mockups:** See `prototype.html` for visual reference
- **Icons:** To be designed (macOS SF Symbols preferred)
- **Screenshots:** For App Store listing (to be captured from beta)

### 12.3 Development Resources
- **SwiftUI Documentation:** https://developer.apple.com/documentation/swiftui
- **OpenAI API Docs:** https://platform.openai.com/docs/api-reference
- **Anthropic API Docs:** https://docs.anthropic.com/claude/reference
- **macOS Human Interface Guidelines:** https://developer.apple.com/design/human-interface-guidelines/macos

---

**End of PRD**

**Ready for development. Share with Claude Code or development team to begin Phase 1.** 🚀
