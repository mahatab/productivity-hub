# TTS Configuration

## Setup Date
February 5, 2026 @ 2:23 AM PST

## Provider
**Edge TTS** (Microsoft Azure TTS)
- Free, unlimited usage
- No API key required
- High quality neural voices

## Selected Voice
**en-US-ChristopherNeural**
- Type: Male, professional
- Style: Reliable, authoritative
- Best for: News, business briefings, serious content

## Installation
```bash
pip3 install edge-tts
```

Installed at: `/Users/mahatabrashid/Library/Python/3.9/bin/edge-tts`

Added to PATH in `~/.zshrc`:
```bash
export PATH="/Users/mahatabrashid/Library/Python/3.9/bin:$PATH"
```

## Usage Configuration
**When to use voice:**
- Daily briefings (8 AM PST) sent via Telegram
- NOT for regular chat messages
- On-demand when requested

## Command Template
```bash
/Users/mahatabrashid/Library/Python/3.9/bin/edge-tts \
  --voice en-US-ChristopherNeural \
  --text "Your text here" \
  --write-media /path/to/output.mp3
```

## Alternative Voices Considered
- Guy (passionate) - too casual
- Jenny (friendly female) - good backup
- Aria (professional female) - good for variety
- Ryan (British male) - accent option

## Next Steps
- ✅ Installed Edge TTS
- ✅ Configured Christopher voice
- ✅ Updated HEARTBEAT.md
- ⏳ Test with tomorrow's daily briefing (Feb 5, 8 AM)
- 🔮 Future: Consider ElevenLabs for premium quality if needed
