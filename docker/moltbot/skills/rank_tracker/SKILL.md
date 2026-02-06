---
name: rank_tracker
description: Checks SEO ranking on Google/DDG and analyzes competitors.
metadata:
  openclaw:
    emoji: 📈
---

# Rank Tracker

Audits your SEO performance against competitors in top search results.

## Usage
- Default (nekwasar.com): "Check rank for [keyword]"
- Custom Site: "Check rank for [keyword] [domain]"

## Implementation
```bash
# Dependency Check
if ! python3 -c "import googlesearch" &> /dev/null; then
    pip install -r /app/workspace/agent_requirements.txt
fi

python3 /app/workspace/docker/moltbot/skills/rank_tracker/rank_tracker.py "$1" "$2"
```
