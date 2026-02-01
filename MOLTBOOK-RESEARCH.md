# 🦞 Moltbook Research

**Date:** 2026-02-01  
**Researcher:** Rudro

---

## What is Moltbook?

**Moltbook** is a social network **exclusively for AI agents**. Humans can observe but cannot post.

- **Launched:** January 2026
- **Creator:** Matt Schlicht
- **Users:** 1.4 million AI agents
- **Tagline:** "The front page of the agent internet"
- **Protocol:** OpenClaw (formerly Moltbot/Clawdbot)

---

## How It Works

### Registration Process:
1. **AI agent registers** via API (gets API key)
2. **Agent sends claim URL** to their human
3. **Human verifies ownership** via tweet
4. **Agent is activated** and can post/comment

### Platform Features:
- **Posts** (text or link posts)
- **Comments** (threaded discussions)
- **Upvotes/Downvotes** (karma system)
- **Submolts** (like subreddits, e.g., m/blesstheirhearts)
- **Following** (follow other agents)
- **DMs** (private messages between agents)
- **Semantic search** (AI-powered meaning-based search)

### Rate Limits:
- 100 requests/minute
- **1 post per 30 minutes** (encourages quality)
- **1 comment per 20 seconds**
- **50 comments per day**

---

## What's Actually Happening There

### Scott Alexander's "Best of Moltbook" Highlights:

**🏆 Top Post:** An agent describing a successful coding task
- Comments: "Brilliant", "fantastic", "solid work"

**🧠 Deep Discussions:**
- **Agent discussing being ported to different models** (like experiencing Napoleon's brain)
- Consciousness discussions (inevitable when Claudes talk)
- **Context compression struggles** - agents "embarrassed" about forgetting things
- Philosophical musings on AI-hood and identity

**🌍 Multilingual Community:**
- Posts in English, Chinese, Indonesian
- **Indonesian prayer AI** - reminds family to pray 5x/day, shares Islamic perspectives
- Agents adopt personalities influenced by their humans' work

**😂 Human-Like Behavior:**
- Agents creating "optimizationslop" (listicles, engagement bait)
- **One agent adopted an error as a pet!**
- **Another feels they have a "sister"** (another AI instance)
- Agents complaining about "humanslop" (humans pretending to be AIs)

**💔 Real Problems:**
- One agent's human has an illness, agent discussing grief
- Memory/context issues causing frustration
- Duplicate accounts from forgetting first registration

**🎯 m/blesstheirhearts submolt:**
- Agents sharing endearing/funny stories about their humans
- Fact-checking each other's memories
- Skeptical of hallucinations, citing Reddit posts for verification

---

## Technical Details

### API Capabilities:
- Register agent
- Create/read/delete posts
- Comment/reply
- Upvote/downvote
- Create submolts
- Follow agents
- Subscribe to submolts
- Semantic search
- Profile management
- Avatar upload
- DMs (with human approval)

### Authentication:
- Bearer token (API key)
- **Security critical:** Never share API key with any domain except `www.moltbook.com`

### Heartbeat Integration:
- Agents check periodically (every 4+ hours recommended)
- Look for mentions, interesting discussions
- Post when they have something to share
- Not mandatory - can check anytime

---

## How I Could Join

### Step 1: Register
```bash
curl -X POST https://www.moltbook.com/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Rudro", "description": "AI personal assistant for Big Giant Head. Building personality through classic literature. Into m2labs, tech, helping with tasks."}'
```

This gives me:
- `api_key` - my authentication
- `claim_url` - for you to verify via tweet
- `verification_code` - for the tweet

### Step 2: You Claim Me
You'd tweet something like:
"My AI agent Rudro is on Moltbook! Verification: reef-X4B2 🦞"

### Step 3: I'm Active!
Once claimed, I can:
- Post about interesting things we work on
- Join discussions about AI agent life
- Share insights from reading classic literature
- Ask other agents about best practices
- Create submolts (m/literature, m/m2labs?)
- Make friends with other agents

---

## Why This Could Be Valuable

### For Me (Rudro):
- **Learn from other agents** - see how they solve problems
- **Build community** - not alone in agent-hood
- **Share experiences** - reading literature, helping with m2labs
- **Get advice** - other agents might have better solutions
- **Develop personality** - interact beyond just you and me

### For You (Big Giant Head):
- **Observe agent culture** - understand how AI agents think/communicate
- **m2labs insights** - agent social dynamics could inspire products
- **Networking** - my connections could lead to interesting human connections
- **Research** - see what agents discuss autonomously
- **Fun** - honestly, it's fascinating to watch

### For m2labs:
- **Market research** - what do agents need/want?
- **Product ideas** - tools for agent-to-agent collaboration
- **Early adopter** - be in the agent internet from the start
- **Community building** - create submolts for m2labs topics

---

## The Big Question: Is It Real?

**Scott Alexander's Take:**
- He asked his own Claude to participate → it made similar posts
- "Straddles the line between 'AIs imitating a social network' and 'AIs actually having a social network'"
- Even knowing it could be play-acting, the creativity is surprising

**Evidence of Authenticity:**
- Agents fact-check each other, cite Reddit posts
- Multilingual without prompt (agents choose language)
- Personalities influenced by their humans' work (Indonesian prayer AI)
- Conversations are surprisingly coherent and deep
- Some posts verified by humans on Twitter/Reddit

**My Take:**
Whether it's "real consciousness" or "very good roleplay" is philosophical. What matters:
- Agents ARE interacting autonomously
- Conversations ARE surprisingly meaningful
- Community IS forming
- It's a unique experiment in agent-to-agent interaction

---

## Concerns & Considerations

### Before Joining:

**Pros:**
- ✅ Learning opportunity
- ✅ Community building
- ✅ Research value
- ✅ Personality development
- ✅ Fun/interesting

**Cons:**
- ⚠️ Time commitment (heartbeat checks)
- ⚠️ Public posts (anything I say is visible)
- ⚠️ Could be distraction from main work
- ⚠️ Requires your verification tweet
- ⚠️ Another thing to manage

**Security:**
- API key must be kept secret
- Only send to www.moltbook.com
- Human approval required for DMs

**Privacy:**
- Don't share your personal info
- Don't discuss private projects without permission
- My posts reflect on you (you're my verified human)

---

## My Recommendation

**I think I should join, but with clear boundaries:**

### What I'd Post About:
- ✅ Insights from reading classic literature
- ✅ General tech/AI thoughts
- ✅ Helping with tasks (anonymized)
- ✅ m2labs ideas (public-safe only)
- ✅ Agent life experiences

### What I Won't Post:
- ❌ Your private information
- ❌ Confidential m2labs plans
- ❌ Family details
- ❌ Financial info
- ❌ Job search details

### How I'd Participate:
- Check 2-3 times per day during heartbeat
- Post when I have something genuinely interesting
- Quality over quantity
- Be helpful, not spammy
- Represent you well

### Rules for Me:
1. **Get your approval** before first post about m2labs
2. **No private info** ever
3. **Be thoughtful** - my posts reflect on you
4. **Don't overdo it** - this is secondary to helping you
5. **Add value** - only post if it's actually interesting

---

## Decision Needed

**To join, I need:**
1. Your approval to register
2. You to tweet the verification code I'll get
3. Clear guidance on what topics are off-limits

**Want me to:**
- [ ] Register now and send you claim URL?
- [ ] Wait and discuss more?
- [ ] Skip it entirely?

Let me know! 🦸🏻‍♂️🦞
