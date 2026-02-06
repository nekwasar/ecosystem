---
name: social_researcher
description: Deep dives into Reddit, Quora, and Socials for sentiment analysis.
metadata:
  openclaw:
    emoji: 🗣️
---

# Social Researcher

Listens to the "Voice of the Customer" across social platforms. 
Identifies pain points (Reddit), questions (Quora), and trends (YouTube/X).

## Usage
Say: "Social research [topic]" or "Find customer pain points for [topic]"

## Implementation
```bash
# Dependency Check
if ! python3 -c "import trafilatura" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/social_researcher/social_spy.py "$1"
```
