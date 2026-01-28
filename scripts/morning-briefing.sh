#!/bin/bash
# Morning briefing email generator
# Calls Rudro (via clawdbot) to generate and send daily briefing

DATE=$(date "+%A, %B %d, %Y")

clawdbot chat --agent main --message "Generate and send today's morning briefing email to mahatab@msn.com. Include:
- Motivational quote (vary each day)
- To-do items based on our ongoing projects
- 5 NEW actionable things we can do together to improve life & m2labs startup (be creative and specific)
- 3-5 fresh brainstorming ideas for m2labs (simple app concepts)
- General AI/tech insights from your knowledge
- Systems status
- Focus suggestion for the day

Make it warm, personal, and actionable. Date: $DATE"
